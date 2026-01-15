# Reporte de Análisis de Nube de Puntos LiDAR Aerotransportado

## 1. Introducción

Este reporte documenta el análisis completo de una nube de puntos LiDAR obtenida mediante sensor aerotransportado (dron) en un área semiurbana. El objetivo es transformar datos brutos en información topográfica confiable mediante limpieza, clasificación y generación de modelos de elevación digital.

**Área de estudio:** Zona semiurbana con vegetación, estructuras verticales y variaciones topográficas.

---

## 2. Herramientas de Software Utilizadas

### Lenguaje Principal
- **Python 3.x** - Lenguaje de programación base para todo el análisis

### Librerías Especializadas

| Librería | Versión | Función |
|----------|---------|---------|
| **laspy** | Latest | Lectura/escritura de archivos LAS (formato LiDAR) |
| **numpy** | 1.20+ | Operaciones numéricas y manipulación de arrays |
| **pandas** | 1.3+ | Análisis y gestión de datos tabulares |
| **scipy** | 1.7+ | Interpolación espacial (griddata) y estructuras espaciales (cKDTree) |
| **scikit-learn** | 0.24+ | Algoritmos ML: NearestNeighbors, DBSCAN clustering |
| **rasterio** | 1.2+ | Lectura/escritura de archivos GeoTIFF georreferenciados |
| **matplotlib** | 3.3+ | Visualización de datos |


---

## 3. Flujo de Trabajo y Metodología

### 3.1 Esquema General

```
[Archivos LAS] 
    ↓
[Carga de datos] → numpy arrays (x, y, z)
    ↓
[LIMPIEZA 1: Filtro Z global] → ±3σ desv. estándar
    ↓
[LIMPIEZA 2: Filtro kNN] → Distancia a vecinos cercanos
    ↓
[CLASIFICACIÓN] → Ground vs. Non-Ground (grilla XY)
    ↓
[NORMALIZACIÓN] → Altura respecto a terreno local (cKDTree)
    ↓
[SEGREGACIÓN] → Ground, Vegetación baja, Vegetación alta, Edificios
    ↓
[INTERPOLACIÓN] → DTM, DSM (griddata)
    ↓
[DIFERENCIA] → nDSM = DSM - DTM
    ↓
[SEGMENTACIÓN] → DBSCAN para edificios individuales
    ↓
[EXPORTACIÓN] → GeoTIFF + CSV (métricas)
```

---

## 4. Descripción Detallada de Cada Fase

### 4.1 FASE 1: Carga de Datos

**Entrada:** Archivos `.las` del directorio `data/`

**Proceso:**
```python
las = laspy.read(las_path)
x, y, z = np.asarray(las.x), np.asarray(las.y), np.asarray(las.z)
```

**Salida:** Arrays numpy con coordenadas 3D

**Estadísticas típicas esperadas:**
- Millones de puntos por archivo (dependiendo de resolución del dron)
- Valores Z en rango típico del terreno (ej. 500-1500 m sobre nivel del mar)
- Densidad variable según cobertura y altitud del vuelo

---

### 4.2 FASE 2: Limpieza de Outliers (Doble Filtro)

#### 4.2.1 Filtro Global por Z (Filtro Estadístico)

**Problema:** Puntos con elevaciones extremas (errores de sensor, rebotes, ruido)

**Solución:**
- Calcula media y desviación estándar de Z
- Elimina puntos donde: `|z - z_mean| > 3 × σ`

**Parámetro:** `z_thresh = 3.0` (3 desviaciones estándar)

**Impacto esperado:** Elimina ~0.3% de puntos (extremos estadísticos)

**Código:**
```python
z_mean = np.mean(z)
z_std = np.std(z)
z_min = z_mean - 3.0 * z_std
z_max = z_mean + 3.0 * z_std
mask_z = (z >= z_min) & (z <= z_max)
```

#### 4.2.2 Filtro de Vecindad (kNN - k-Nearest Neighbors)

**Problema:** Puntos aislados ruidosos que pasan el filtro Z global

**Solución:**
- Para cada punto, calcula distancia a sus k=8 vecinos más cercanos
- Promedia estas distancias
- Elimina puntos cuya distancia media > umbral adaptativo

**Umbral:** `mean_dist + 2.5 × std(mean_dist)`

**Ventaja:** Detecta outliers locales (ej. puntos erráticos cerca de vegetación densa)

**Impacto esperado:** Elimina ~1-3% de puntos (outliers locales)

**Parámetros configurables:**
- `k = 8`: Número de vecinos (ajustar según densidad)
- `knn_mult = 2.5`: Sensibilidad (valores mayores = más permisivo)

**Reporte de limpieza:**
```
Total puntos iniciales: X
Puntos limpios: Y (Y/X %)
Puntos removidos: Z (Z/X %)
```

---

### 4.3 FASE 3: Clasificación Ground/Non-Ground

**Problema:** Diferenciar terreno de vegetación/estructuras

**Método: Grilla XY + Percentil**

**Algoritmo:**
1. Divide área en grilla de celdas 2m × 2m
2. En cada celda, calcula percentil 5 de elevaciones: `z_ground_local`
3. Clasifica como "ground" si: `z ≤ z_ground_local + 0.5m`

**Justificación:**
- Percentil 5 captura puntos más bajos (probablemente suelo)
- Umbral de 0.5m permite pequeñas irregularidades del terreno
- Robusto a vegetación densa

**Parámetros:**
- `cell_size = 2.0 m` - Tamaño de celda (ajustar por resolución del dron)
- `z_threshold = 0.5 m` - Margen vertical para clasificar como suelo
- `ground_percentile = 5` - Percentil para estimar elevación del terreno

**Reporte esperado:**
```
Puntos clasificados como ground: X (X% del total)
Puntos no-ground (vegetación/edificios): Y (Y% del total)
```

---

### 4.4 FASE 4: Normalización de Alturas

**Objetivo:** Calcular altura respecto al terreno local, no al nivel del mar

**Fórmula:** `h_norm = z - z_terreno_local`

**Método:**
- Construye árbol espacial (cKDTree) desde puntos de suelo
- Para cada punto, consulta los k=8 vecinos más cercanos del suelo
- Estima terreno local como **mediana** de esos vecinos
- Calcula altura normalizada

**Resultado:** Array `h_norm` con alturas normalizadas (0 en suelo, 30+ m en edificios altos)

---

### 4.5 FASE 5: Segregación de Coberturas

**Objetivo:** Clasificar 4 tipos de cobertura

#### Reglas de Clasificación

| Cobertura | Criterios | Color en mapa |
|-----------|-----------|---------------|
| **Ground** | Clasificado como suelo en Fase 3 | Marrón (`saddlebrown`) |
| **Vegetación Baja** | 0.3m < h_norm ≤ 2.0m | Verde claro (`limegreen`) |
| **Vegetación Alta** | h_norm > 2.0m AND rugosidad > 0.5m | Verde oscuro (`darkgreen`) |
| **Edificios** | h_norm > 2.0m AND rugosidad < 0.5m | Gris (`gray`) |

#### Cálculo de Rugosidad

**Problema:** Diferenciar árbol (rugoso) de edificio (liso)

**Método:**
- Para cada punto, consulta vecinos en radio r=1.5m
- Calcula desviación estándar de h_norm en esa vecindad
- Rugosidad baja (< 0.5m) → Edificio
- Rugosidad alta (> 0.5m) → Árbol/Vegetación

**Lógica:** Árboles tienen puntos dispersos (hojas, ramas) → rugosidad alta
Edificios tienen superficies planas → rugosidad baja

---

### 4.6 FASE 6: Generación de Modelos de Elevación

#### 4.6.1 DTM (Modelo Digital del Terreno)

**Entrada:** Solo puntos clasificados como "ground"

**Proceso:**
- Interpolación lineal mediante triangulación de Delaunay
- Resolución: 1.0m × 1.0m

**Fórmula:**
```python
grid_z = griddata((x, y), z, (grid_x, grid_y), method='linear')
```

**Interpretación:** Superficie continua del terreno sin edificios ni vegetación

**Uso:** Referencia para normalizar alturas, análisis de drenaje

#### 4.6.2 DSM (Modelo Digital de Superficie)

**Entrada:** Todos los puntos (ground + no-ground)

**Proceso:**
- Interpolación "nearest neighbor" (vecino más cercano)
- Resolución: 1.0m × 1.0m

**Fórmula:**
```python
grid_z = griddata((x, y), z, (grid_x, grid_y), method='nearest')
```

**Interpretación:** Superficie visible (primer retorno LiDAR)

#### 4.6.3 nDSM (Modelo Digital Normalizado / CHM)

**Definición:** 
```
nDSM = DSM - DTM
```

**Interpretación:** Altura de objetos sobre el terreno

| Valor nDSM | Interpretación |
|------------|----------------|
| 0-0.3m | Suelo/Pasto (misma altura que DTM) |
| 0.3-2.0m | Vegetación baja (arbustos) |
| 2.0-10m | Árboles medianos / edificios bajos |
| >10m | Árboles altos / edificios altos |

**Aplicación:** Detección de vegetación, cálculo de volúmenes de biomasa, análisis urbano

---

### 4.7 FASE 7: Segmentación de Edificios

**Objetivo:** Identificar edificios individuales

**Método: DBSCAN (Density-Based Spatial Clustering)**

**Algoritmo:**
1. Filtra puntos clasificados como "building"
2. Aplica clustering DBSCAN en coordenadas (X, Y)
3. Cada cluster = un edificio

**Parámetros:**
- `eps = 2.0 m` - Distancia máxima para considerar vecinos
- `min_samples = 50` - Mínimo de puntos para formar cluster


**Reporte:** 
- Número de edificios detectados
- ID único para cada edificio

---

### 4.8 FASE 8: Extracción de Métricas de Edificios

Para cada edificio detectado, se calculan:

**Métricas:**
```
area_m2 = número_puntos × (resolución_grilla)²
height_mean = promedio de alturas normalizadas
height_max = altura máxima del edificio
```

**Tabla de salida (CSV):**
```
file, building_id, area_m2, height_mean, height_max
archivo1.las, 0, 245.3, 8.2, 12.1
archivo1.las, 1, 156.7, 5.9, 9.3
...
```

**Aplicaciones:**
- Inventario de estructuras
- Estimación de densidad urbana
- Validación de catastros

---

### 4.9 FASE 9: Exportación de Resultados

#### Outputs GeoTIFF
```
outputs/
├── archivo1_DTM.tif    ← Modelo Digital del Terreno
├── archivo1_DSM.tif    ← Modelo Digital de Superficie
├── archivo1_nDSM.tif   ← Modelo de Altura Normalizada
├── archivo2_DTM.tif
├── archivo2_DSM.tif
├── archivo2_nDSM.tif
└── ...
```

**Formato:** GeoTIFF con georreferenciación (transform automático)

**Compatible con:** QGIS, ArcGIS, GDAL, plugins SIG

#### Outputs CSV
```
outputs/
├── summary_lidar.csv        ← Resumen de coberturas por archivo
└── buildings_metrics.csv    ← Métricas de edificios
```

---

## 5. Hallazgos, Anomalías y Desafíos

### 5.1 Objetos Difíciles de Clasificar Automáticamente

#### **Desafío 1: Vegetación Densa vs. Suelo**

**Problema:**
- Bajo vegetación espesa (bosque denso), LiDAR penetra poco
- Puntos retornos pueden ser ramas bajas, no suelo
- Resultado: DTM sobrestimado (más alto de lo real)

**Síntomas observados:**
- Gradiente de alturas suave en zonas de bosque
- Clasificación incorrecta de suelo a puntos que son ramas

**Solución implementada:**
- Umbral de percentil 5 tiende a capturar el mínimo local
- Margen de 0.5m permite cierta flexibilidad
- Post-procesamiento manual en áreas críticas si es necesario

**Mejoras sugeridas:**
- Usar algoritmos más avanzados (ej. Multi-scale Curvature Classification)
- Validar con puntos de control terrestre (GPS)
- Ajustar percentil según cobertura (más bajo en bosque denso)

---

#### **Desafío 2: Vegetación Alta vs. Edificios**

**Problema:**
- Ambos tienen h_norm > 2.0m
- Diferenciarlos solo por altura es insuficiente

**Síntomas observados:**
- Árboles clasificados como edificios en presencia de dosel denso
- Edificios confundidos con vegetación si tienen texturas irregulares

**Solución implementada:**
- **Rugosidad local:** Árboles = rugosos (hojas dispersas), Edificios = lisos (tejas, hormigón)
- Umbral de rugosidad = 0.5m (ajustable)
- Cálculo en radio 1.5m alrededor de cada punto

**Limitaciones:**
- Árboles podados o uniformes pueden parecer lisos
- Edificios con texturas complejas (fachadas con relieves) pueden parecer rugosos

**Soluciones alternativas:**
- Usar índices espectrales (si se dispone de datos multiespectrales)
- Análisis de forma (perímetro/área, rectilínearidad)
- Machine Learning supervisado (entrenar con muestras etiquetadas)

---

#### **Desafío 3: Puntos de Borde y Transiciones**

**Problema:**
- En bordes de edificios/vegetación, el sensor LiDAR crea puntos "fantasma"
- Pulso del láser intercepta esquina → punto intermedio
- Difícil de filtrar automáticamente

**Síntomas observados:**
- Puntos aislados en aire (sin vecinos cercanos)
- Discontinuidades en superficies

**Solución implementada:**
- Filtro kNN detecta algunos puntos aislados
- DBSCAN descarta clusters muy pequeños (< 50 puntos)

**Mejoras sugeridas:**
- Algoritmo "alpha-shapes" para detectar puntos en vacíos
- Morphological filtering (erosión/dilatación) post-interpolación
- Validación visual y corrección manual en áreas críticas

---

#### **Desafío 4: Cables, Antenas y Objetos Lineales**

**Problema:**
- Cables eléctricos, antenas, tuberías: muy delgados
- LiDAR captura pocos puntos
- Difícil de clasificar

**Síntomas observados:**
- Puntos dispersos a altura media (2-10m)
- No suficientes para formar cluster DBSCAN
- Pueden quedar como "non-ground" sin categoría clara

**Solución implementada:**
- Filtro tamaño de cluster: clusters < 50 puntos ignorados
- Estos objetos no aparecen en segmentación de edificios

**Nota:** No hay clasificación explícita de cables en el análisis actual
- Requerirían post-procesamiento especializado
- O entrada adicional (ortofoto, datos catastrales)

---

#### **Desafío 5: Ruido en Bordes del Área de Vuelo**

**Problema:**
- Dron captura datos menos densos en bordes
- Mayor número de outliers

**Síntomas observados:**
- Puntos dispersos y extremos en perímetro de nube
- Pueden afectar interpolación de DTM/DSM en bordes

**Solución implementada:**
- Filtro Z global y kNN eliminan muchos outliers
- Interpolación "nearest neighbor" (DSM) más robusta a bordes

**Mejoras sugeridas:**
- Aplicar buffer de seguridad (ignorar borde exterior)
- Usar máscara de confianza (densidad de puntos)

---

### 5.2 Anomalías Detectadas en Datos Típicos

| Anomalía | Causa probable | Impacto | Acción |
|----------|----------------|--------|--------|
| Picos aislados muy altos | Rebotes en cables / reflejos | DTM/DSM inflados en puntos | Filtro Z global |
| Vacíos en vegetación densa | Poca penetración LiDAR | DTM con agujeros | Interpolación "nearest" en DSM |
| Puntos bajo suelo real | Reflejos especulares | DTM subestimado | Validación con GPS |
| Bordes difusos de edificios | Múltiples retornos | Dimensiones imprecisas | Buffer alrededor de resultados |

---

### 5.3 Métricas de Calidad del Análisis

**Tasas de Eliminación Típicas:**
- Filtro Z global: 0.1 - 0.5% de puntos
- Filtro kNN: 1.0 - 3.0% de puntos
- **Total eliminado: 1.1 - 3.5%**
- Puntos limpios: **96.5 - 98.9%** del original

**Distribución típica de coberturas:**
- Ground: 40 - 60% (mayor en áreas despejadas)
- Vegetación baja: 10 - 25% (arbustos, pasto)
- Vegetación alta: 15 - 35% (árboles)
- Edificios: 5 - 15% (según densidad urbana)

