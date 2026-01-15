# Propuesta Teórica: Posicionamiento y Medición en Dron para Espacios Confinados



---

## 1. Planteamiento del Problema

### 1.1 ¿Por qué GNSS No es Viable en Espacios Confinados?

#### Limitaciones Fundamentales de GNSS

**GNSS (Global Navigation Satellite System)** requiere:
- Línea de vista directa a satélites
- Señal de radiofrecuencia de banda L (1-2 GHz)
- Mínimo 4 satélites simultáneos (mejor con 6-8)

**En espacios confinados:**

| Escenario | Problema | Impacto |
|-----------|----------|--------|
| **Túneles** | Paredes de roca/hormigón bloquean señal | Pérdida completa de GPS |
| **Ductos subterráneos** | Enterrados a 10-100 m de profundidad | Atenuación >30 dB |
| **Interiores industriales** | Techos metálicos, estructuras de acero | Reflexión y multitrayecto |
| **Galerías/cavernas** | Geometría compleja, múltiples paredes | Señal dispersa, ruido elevado |
| **Espacios con agua** | Salinidad, sedimentos | Absorción de RF |

#### Pérdida de Señal Típica

```
Exterior abierto:      0 dB (referencia)
Bajo techo ligero:    -5 a -10 dB
Bajo hormigón 30cm:  -20 a -30 dB
Túnel de roca:       -40 a -60 dB
Ducto profundo:      >-80 dB (irrecuperable)
```

**Conclusión:** GNSS es **prácticamente inútil** a profundidades >5 m o bajo estructuras densas.

---

### 1.2 Principales Desafíos de Navegación y Medición

#### Desafío 1: Acumulación de Errores Inerciales

**Problema:**
- Sin referencia externa (GNSS), el dron depende de sensores inerciales (IMU)
- Error de drift: 0.1-1% por segundo (según calidad)

**Ejemplo:**
```
Velocidad: 1 m/s
Error IMU: 0.5% por segundo
Después de 100 segundos:
  Error acumulado = 1 m/s × 0.5% × 100 s = 0.5 m
Después de 10 minutos:
  Error acumulado = 1 m/s × 0.5% × 600 s = 3 m (inaceptable)
```

**Impacto:** Posición estimada diverge progresivamente del valor real

---

#### Desafío 2: Entorno Complejo y Dinámico

**En espacios confinados:**
- Geometría irregular (no lineal)
- Obstáculos impredecibles
- Cambios de iluminación (oscuridad total posible)
- Superficies reflectantes o absorbentes
- Presencia de agua, polvo, gases

**Impacto en sensores:**
- Sensores ópticos: inutilizables en oscuridad
- LIDAR 2D: información limitada a un plano
- Cámaras térmicas: interferencia por condensación
- Sensores ultrasónicos: dispersión en aire húmedo

---

#### Desafío 3: Comunicaciones Limitadas

**Problema:**
- RF a través de paredes: atenuación extrema
- Cables tethered: riesgo de enredo, limita alcance
- WiFi/BLE: rango típico 10-50 m en línea recta

**Impacto:** 
- Difícil transmitir datos en tiempo real
- Almacenamiento local en dron es crítico
- Decisiones deben ser autónomas

---

#### Desafío 4: Calibración y Validación

**En laboratorio:** Posición conocida, errores medibles  
**En campo:** Imposible validar "verdad de terreno" sin salir del espacio confinado

**Impacto:**
- No hay referencia externa para corregir errores
- Validación posterior compleja y costosa

---

## 2. Propuesta de Sensores (Nivel Teórico)

### 2.1 Arquitectura Sensorial Recomendada

#### Stack de Sensores Propuesto

```
┌─────────────────────────────────────────────────────┐
│         DRON PARA ESPACIOS CONFINADOS                │
├─────────────────────────────────────────────────────┤
│                                                      │
│  POSICIONAMIENTO RELATIVO                            │
│  ├─ IMU (9-DOF: acelerómetro + giroscopio)          │
│  ├─ Odometría visual (cámara monocular/estéreo)     │
│  └─ Rueda encoders (si aplica configuración)        │
│                                                      │
│  MEDICIÓN DE DISTANCIAS                              │
│  ├─ LIDAR 3D (nube de puntos)                        │
│  ├─ Sensores ultrasónicos (apoyo en áreas ciegas)   │
│  └─ Cámara estéreo (disparidad para profundidad)    │
│                                                      │
│  RECONSTRUCCIÓN DEL ENTORNO                          │
│  ├─ Cámara RGB (mapeo visual)                        │
│  ├─ IMU (orientación espacial)                       │
│  └─ LIDAR 3D (mapeo de obstáculos)                   │
│                                                      │
│  VALIDACIÓN Y CORRECCIÓN                             │
│  ├─ Barométro (altura relativa)                      │
│  └─ Brújula magnética (orientación - en entornos      │
│      sin interferencia magnética)                     │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

### 2.2 Descripción Detallada de Cada Sensor

#### **1. IMU (Inertial Measurement Unit) - 9-DOF**

**Componentes:**
- Acelerómetro 3-axis (mide aceleración linear)
- Giroscopio 3-axis (mide velocidad angular)
- Magnetómetro 3-axis (brújula)

**Función en el sistema:**
- Estimación de orientación (roll, pitch, yaw)
- Detección de movimiento e inercia
- Retroalimentación para control de vuelo

**Parámetros críticos:**
- Rango aceleración: ±16 g (típico para drones)
- Rango giroscopio: ±2000°/s
- Ruido aceleración: <100 mg/√Hz
- Ruido giroscopio: <0.05°/s/√Hz

**Limitaciones:**
- Drift de orientación: ~0.1-0.5°/minuto (sin corrección)
- No proporciona posición absoluta
- Necesita fusión sensorial para corrección

**Ventaja:** Funciona en cualquier condición (oscuridad, agua, polvo)

---

#### **2. LIDAR 3D (Light Detection and Ranging)**

**Tipos recomendados:**
- **LIDAR de barrido mecánico** (32-64 líneas): Precisión submétrica, rango 100-200 m
- **LIDAR de estado sólido** (solid-state): Más compacto, pero menor rango

**Función:**
- Mapeo 3D del entorno
- Detección de obstáculos en 360°
- Generación de nube de puntos

**Parámetros:**
- Rango: 5-150 m (varía por modelo)
- Resolución angular: 0.1-0.4° (típico)
- Frecuencia: 10-20 Hz
- Puntos/segundo: ~600k-2M

**Ventajas:**
- Funciona en oscuridad total
- Independiente de textura de superficies
- Proporciona información 3D rica
- Permite detección de pequeños obstáculos (cables)

**Limitaciones:**
- Costo elevado
- Consumo de potencia significativo
- Agua/niebla pueden degradar datos
- Superficies muy reflectantes o absorbentes

**Aplicación en posicionamiento:**
- **Loop Closure:** Cuando dron revisita zona anterior, LIDAR reconoce similitud
  - Usado para corregir drift acumulado
- **Mapeo SLAM:** Simultaneous Localization and Mapping
  - Construye mapa mientras estima posición

---

#### **3. Cámara (RGB + Estéreo)**

**Configuración recomendada:**
- Par estéreo de cámaras (baseline 10-20 cm)
- Resolución: 640×480 a 1280×960 (balance velocidad/precisión)
- Frame rate: 30-60 FPS

**Función:**
- Odometría visual: rastreo de características de imagen
- Cálculo de profundidad: disparity matching entre imágenes izq/dcha
- Mapeo visual para SLAM

**Parámetros:**
- Rango de profundidad: baseline × f / disparidad
  - Ejemplo: baseline 0.1m, focal length 500px → rango 1-20 m
- Precisión: 1-5% de distancia

**Ventajas:**
- Proporciona texture/color (útil para mapeo)
- Funciona a corto rango incluso en luz difusa
- Bajo costo (comparado con LIDAR)
- Permite detección de características naturales

**Limitaciones:**
- No funciona en oscuridad total (sin iluminación IR)
- Sensible a cambios de iluminación
- Disparidad cálculo demanda computación significativa
- Ambigüedad en superficies sin textura

**Aplicación:**
- Validación de obstáculos pequeños
- Extracción de características (bordes, esquinas)
- Verificación de estado de paredes (grietas, corrosión)

---

#### **4. Sensores Ultrasónicos (Ultrasonic Range Sensors)**

**Configuración:**
- Array de 4-6 sensores (arriba, abajo, frente, atrás, laterales)
- Rango: 0.3-4 m (típico para espacios confinados)
- Frecuencia: 40 kHz

**Función:**
- Detección rápida de obstáculos cercanos
- Mapeo de superficies planas/lisas
- Ayuda en hovering estable

**Ventajas:**
- Bajo costo (~$5-20 por sensor)
- Bajo consumo energético
- Insensible a luz, polvo
- Rápido (tiempo de vuelo ~25 ms)

**Limitaciones:**
- Rango limitado (< 5 m)
- Pobre resolución angular (~15°)
- No funciona bien con superficies blandas/absorbentes
- Interferencia cruzada si múltiples sensores activados

**Aplicación:**
- Detección de colisión (control de reflexión automático)
- Medición de altura sobre suelo/techo en ductos
- Validación de espacios libres

---

#### **5. Barométro (Pressure Sensor)**

**Función:**
- Estimación de altura relativa basada en presión
- Referencia de altura local

**Parámetro:**
- Precisión: ±0.5-2 m (en condiciones estables)
- Sensibilidad: ~12 Pa por metro

**Ventaja:**
- Muy bajo costo y consumo
- Buena estabilidad en condiciones de presión constante

**Limitación:**
- Variaciones de presión local (viento, temperatura) causan error
- Requiere calibración frecuente

**Aplicación:**
- Corrección de altura estimada por IMU
- Detección de cambios de nivel en túneles

---



## 3. Estimación de Posicionamiento

### 3.1 Enfoque Teórico: Fusión Sensorial (Sensor Fusion)

#### Problema Fundamental

Con sensores independientes:
- **IMU solo:** Excelente resolución temporal, pero drift fatal
- **LIDAR/Cámara solo:** Buena corrección, pero lento y dependiente de features

**Solución:** Fusionar múltiples sensores en sistema probabilístico

---

### 3.2 Arquitectura de Fusión: Extended Kalman Filter (EKF)

#### Concepto Básico

**Ecuación de estado:**
```
x[n+1] = f(x[n], u[n]) + w[n]

Donde:
  x[n] = vector de estado [x, y, z, vx, vy, vz, roll, pitch, yaw]
  f() = modelo de movimiento (cinemática)
  u[n] = entrada de control (comando de aceleración)
  w[n] = ruido de proceso (gaussiano)
```

**Ecuación de medición:**
```
z[n] = h(x[n]) + v[n]

Donde:
  z[n] = vector de mediciones (de todos los sensores)
  h() = función que transforma estado a observables
  v[n] = ruido de medición (gaussiano)
```

#### Ciclo de EKF (2 pasos)

**PASO 1: Predicción (usando IMU)**
```
x_pred[n] = f(x_est[n-1], aceleración_IMU)
P_pred[n] = F·P[n-1]·F^T + Q

F = Jacobiano de f
Q = covarianza de ruido de proceso
P = covarianza de error de estimación
```

**Resultado:** Predicción de posición a alta frecuencia (200+ Hz)

**PASO 2: Corrección (usando LIDAR/Cámara)**
```
Cada 5-10 frames de LIDAR (más lento):
  
  innovación = z_medido - h(x_pred)
  
  K = (P_pred·H^T) / (H·P_pred·H^T + R)  [Ganancia de Kalman]
  
  x_corregido = x_pred + K·innovación
  P_corregido = (I - K·H)·P_pred
```

**Resultado:** Corrección de drift IMU, reset de covarianza

---

### 3.3 Flujo de Datos de Sensores

```
┌─────────────────────────────────────────────────────┐
│ SENSORES DE ENTRADA                                  │
├─────────────────────────────────────────────────────┤
│                                                      │
│  IMU (200 Hz)          Cámara (30 Hz)               │
│    │                        │                         │
│    ├─ Aceleración       ├─ Optical flow              │
│    ├─ Velocidad angular │  (movimiento imagen)       │
│    └─ Orientación       └─ Disparidad (profundidad)  │
│         │                      │                      │
│         │          LIDAR (10 Hz)│                     │
│         │               │       │                     │
│         │               ├─ Nube de puntos             │
│         │               └─ Curvatura/features        │
│         │                      │                      │
│         └──────────┬───────────┘                      │
│                    │                                  │
│            ┌───────▼────────┐                        │
│            │ EXTENDED        │                        │
│            │ KALMAN FILTER   │                        │
│            └───────┬────────┘                        │
│                    │                                  │
│         ┌──────────▼──────────┐                      │
│         │ ESTIMACIÓN DE POSE  │                      │
│         │ [x,y,z,R,P,Y]       │                      │
│         └────────────────────┘                       │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

### 3.4 Reducción de Error Acumulado

#### Estrategia 1: Loop Closure Detection (SLAM)

**Concepto:**
Cuando dron regresa a zona visitada anteriormente, LIDAR/Cámara reconocen características similares.

**Ejecución:**
```
1. Mantener mapa de características con coordenadas
   Feature = {posición en mapa, descriptor visual}

2. Comparar características nuevas con antiguas
   Similitud = SSD (Sum of Squared Differences)

3. Si similitud > umbral:
   → Loop closure detectado
   → Aplicar corrección global a toda trayectoria
   → Re-estimar posiciones previas
```

**Beneficio:** 
- Reduce drift a 0.1-0.5% (vs 0.5-1% sin loop closure)
- Ejemplo: túnel 1 km → error <5 m (aceptable)

---

#### Estrategia 2: Anclaje Artificial (Fiducial Markers)

**Concepto:**
Colocar marcadores conocidos en el entorno antes de vuelo.

**Implementación:**
```
Marcador ArUco (pequeño código QR):
  ├─ Tamaño: 10×10 cm
  ├─ Costo: $1
  ├─ Detectado por cámara a rango: 1-10 m
  └─ Proporciona pose relativa exacta

Procedimiento:
  1. Dron detecta marcador en imagen
  2. Calcula pose relativa respecto a marcador
  3. Si pose del marcador conocida (GPS previo):
     → Corrección instantánea de posición absoluta
```

**Beneficio:**
- Reset de drift a cero
- Apenas afecta tiempo de misión

**Limitación:**
- Requiere instalación previa
- Múltiples marcadores para cobertura

---

#### Estrategia 3: Mapeo Incremental con Validación

**Concepto:**
Verificar consistencia del mapa mientras se construye.

**Ejecución:**
```
Durante mapeo:
  Cada 10-20 frames:
    ├─ Comparar nueva nube LIDAR con mapa acumulado
    ├─ Estimar transformación (ICP - Iterative Closest Point)
    ├─ Si error > umbral: rechazar frame (posible fallo sensorial)
    └─ Si error < umbral: aceptar y actualizar mapa
```

**Beneficio:**
- Detección de anomalías
- Corrección proactiva

---

## 4. Cálculo de Distancias y Medidas

### 4.1 Distancia a Obstáculos

#### Método 1: LIDAR 3D (Más preciso)

**Procedimiento:**
```
1. Dron apunta LIDAR hacia obstáculo
2. Nube de puntos LIDAR captura superficie
3. Para cada punto (x, y, z) en nube:
   - Transformar a coordenadas del dron
   - Calcular distancia: d = sqrt(x² + y² + z²)
4. Ordenar distancias y seleccionar mínimo

Resultado: d_min (distancia al obstáculo más cercano)
```

**Precision:**
- LIDAR típico: ±0.05-0.1 m @ 10 m de distancia
- Peor caso: ±0.2 m @ 50 m

**Ventaja:** Información rica 3D, múltiples superficies simultáneamente

---

#### Método 2: Ultrasónicos (Rápido, bajo costo)

**Procedimiento:**
```
1. Enviar pulso ultrasónico (40 kHz)
2. Esperar retorno del eco
3. Calcular distancia: d = (velocidad_sonido × tiempo) / 2

Velocidad del sonido en aire:
  - A 20°C, humedad 50%: 343 m/s
  - A 40°C, humedad 80%: 354 m/s
  - Error potencial: ±2% por temperatura/humedad
```

**Procedimiento mejorado:**
```
1. Medir temperatura local (termómetro IR integrado)
2. Ajustar velocidad del sonido por temperatura
3. Tomar múltiples mediciones (N=5), promedio
4. Descartar outliers (mediana robusta)

Distancia final = mediana(d1, d2, d3, d4, d5)
```

**Precisión:**
- Ideal: ±0.01 m @ 1 m
- Rango 4 m: ±0.05 m

**Ventaja:** Bajo costo, actualizacion rápida (50 Hz)

---

#### Método 3: Cámara Estéreo (Visual Depth)

**Procedimiento:**
```
1. Capturar imágenes simultáneas izq/dcha
2. Para cada píxel, calcular disparidad (d) = x_izq - x_dcha
3. Estimar profundidad: Z = (baseline × focal_length) / disparidad

Parámetros calibración:
  - baseline: distancia entre cámaras (0.1-0.2 m)
  - focal_length: distancia focal en píxeles (~500-800)
```

**Mejoras:**
```
- Semi-global matching (SGM): reduce ruido de disparidad
- Median filtering: suaviza estimación de profundidad
- Cost aggregation: mejora consistencia

Resultado: mapa de profundidad denso (640×480 píxeles)
```

**Precisión:**
- Corto rango (1-5 m): ±0.05-0.1 m
- Medio rango (5-20 m): ±0.5-1 m

**Ventaja:** Información densa, bajo costo

---

### 4.2 Dimensiones de Características (Ancho, Altura, Volumen)

#### Escenario: Medición de Abertura de Túnel

**Objetivo:** Calcular ancho y altura de entrada/sección

**Procedimiento:**

**PASO 1: Adquisición de Datos**
```
Dron se posiciona frente a abertura:
  - Distancia: d (estimada)
  - Orientación: perpendicular a pared
  - LIDAR captura nube de puntos de la cara
```

**PASO 2: Segmentación de Puntos Perimetrales**
```
Filtrar puntos que corresponden a bordes de abertura:
  - Aplicar detector de bordes en nube (curvatura, normal discontinuidad)
  - Resultado: conjunto de puntos en perímetro
```

**PASO 3: Ajuste Geométrico**
```
Para abertura rectangular:
  - Ajustar rectángulo mínimo a puntos de borde
  - Calcular dimensiones: ancho (W), alto (H)

Para abertura circular:
  - Ajustar círculo por mínimos cuadrados
  - Calcular radio (R), diámetro (D = 2R)
```

**PASO 4: Corrección por Distancia y Ángulo**
```
Dimensión real = Dimensión medida × (d_real / d_estimada)
                 × corrección_ángulo

Donde corrección_ángulo = cos(θ) para pequeños ángulos
```

**PASO 5: Validación Múltiple**
```
- Medir desde 2-3 ángulos diferentes
- Calcular promedio ponderado por precisión
- Estimar incertidumbre (desviación estándar)
```

---

#### Escenario: Cálculo de Volumen de Cavidad

**Objetivo:** Estimar volumen de caverna/cámara

**Procedimiento:**

**PASO 1: Mapeo Completo**
```
Dron vuela alrededor de cavidad, capturando:
  - Múltiples nubes de puntos LIDAR (diferentes posiciones)
  - Fusión de nubes: merge en sistema coordenado único
  - Resultado: nube de puntos densa 3D de toda cavidad
```

**PASO 2: Reconstrucción de Malla**
```
A partir de nube de puntos:
  
  Poisson Surface Reconstruction:
    1. Estimar normales de cada punto
    2. Crear función signed distance field (SDF)
    3. Extraer superficie como isosuperficie
    4. Generar malla triangular

  Resultado: malla cerrada que aproxima forma de cavidad
```

**PASO 3: Cálculo de Volumen**
```
Volumen = suma de volúmenes de tetraedros
          desde un punto arbitrario a cada triángulo

V = (1/6) × Σ det([v1, v2, v3])

Donde v1, v2, v3 son vértices de cada triángulo
```

**PASO 4: Estimación de Incertidumbre**
```
σ_volumen = Sensibilidad del volumen a errores de posicionamiento
            Ejemplo: ±0.1 m en posición → ±2-5% en volumen
```

---

### 4.3 Ejemplo Integrado: Medición de Daño en Tubo

**Escenario:** Inspeccionar tubo de agua con oxidación

**Datos disponibles:**
- Nube LIDAR de interior de tubo
- Cámara RGB para textura
- Posición estimada del dron

**Procedimiento:**

```
1. SEGMENTACIÓN:
   - Detectar área oxidada (color marrón en RGB)
   - Aislar puntos LIDAR correspondientes
   
2. MEDICIÓN GEOMÉTRICA:
   - Diámetro nominal del tubo: D (catálogo)
   - Puntos de oxidación: conjunto P
   - Profundidad de pérdida: h = D/2 - distancia(P a eje)
   
3. AREA AFECTADA:
   - Proyectar puntos P sobre superficie cilindrica
   - Calcular área de polígono convexo
   
4. VOLUMEN DE PÉRDIDA:
   - Aproximar perfil de daño como semicírculo
   - Volumen = (π/4) × h² × longitud_afectada
   
5. REPORTE:
   - Profundidad máxima de corrosión
   - Área total afectada
   - Volumen de metal perdido
   - Estimación de vida útil residual
```

---

## 5. Limitaciones y Validación

### 5.1 Principales Fuentes de Error

#### Tabla de Errores Sistemáticos y Aleatorios

| Fuente | Tipo | Magnitud | Causa | Mitigación |
|--------|------|----------|-------|-----------|
| **Drift IMU** | Sistemático | 0.1-1°/min (rotación) | Integración de ruido | Loop closure, barométro |
| **Calibración cámara** | Sistemático | 0.5-2% | Distorsión óptica | Calibración previa |
| **LIDAR en agua** | Aleatorio | 10-30% | Absorción/refracción | No usar en agua |
| **Ultrasónico temp** | Sistemático | 2-4% | Variación V.sonido | Compensación térmica |
| **Computación visual** | Aleatorio | 5-10% | Matching de features | Multi-escala |
| **Drift de posición acumulado** | Sistemático | 0.3-1% de distancia recorrida | Integración de velocidad | Loop closure, marcadores |

---

#### Error Acumulado Típico (sin corrección)

```
Misión: Túnel recto 1 km

Fuente primaria: Acelerómetro drift
  - Error: 0.05 m/s² (muy pequeño)
  - Integración: 0.05 × t²/2
  - A t=100s: 0.05×10000/2 = 250 m de error

Conclusión: Imposible confiar solo en IMU

Con corrección (loop closure, LIDAR matching):
  - Error residual: ~0.5-1% de distancia
  - Túnel 1 km: error final 5-10 m (aceptable)
```

---

### 5.2 Validación Experimental

#### Método 1: Validación en Laboratorio

**Setup:**
```
- Área controlada (20×20×5 m)
- Paredes conocidas (medidas con cinta)
- Puntos de referencia marcados
```

**Procedimiento:**
```
1. Medir distancias con cinta métrica (verdad de terreno)
2. Ejecutar dron con sistema de posicionamiento propuesto
3. Registrar trayectoria estimada
4. Comparar con verdad de terreno
5. Calcular métricas de error:
   - RMSE (Root Mean Square Error)
   - MAE (Mean Absolute Error)
   - Máximo error puntual
```

**Métricas esperadas:**
```
RMSE posición: < 0.5 m (dentro de 1% de recorrido)
RMSE orientación: < 5° (después de 10 min vuelo)
Error distancia a obstáculo: < 0.1 m
```

---

#### Método 2: Validación en Campo (Túnel Real)

**Setup:**
```
- Túnel conocido con mapas previos
- Instalación de puntos de control (GPS anterior, planos arquitectónicos)
- Seguridad: tether de emergencia, personal de apoyo
```

**Procedimiento:**
```
1. Pre-vuelo:
   - Instalar 3-5 marcadores ArUco en túnel
   - Documentar posición exacta de marcadores
   
2. Vuelo:
   - Ejecutar misión de exploración
   - Registrar datos de sensores
   
3. Post-procesamiento:
   - Procesar LIDAR + Cámara offline
   - Generar mapa 3D final
   
4. Comparación:
   - Superponer mapa generado con planos arquitectónicos
   - Calcular desviación de características (muros, curvas)
   - Validar mediciones de dimensiones (secciones transversales)
```

**Aceptación:**
```
- Desviación < 0.5 m en planos grandes (túnel largo)
- Desviación < 0.05 m en características pequeñas
- Cierre de loop < 5% de circuito
```

---

#### Método 3: Validación de Mediciones Específicas

**Ejemplo: Medición de Daño en Estructura**

```
1. Seleccionar característica conocida (grieta, corrosión)
2. Medir manualmente con aparatos de precisión:
   - Profundidad: calibrador digital (±0.1 mm)
   - Área: fotografía + planimetría digital
   
3. Medir con dron:
   - LIDAR + Cámara según procedimiento 4.2
   
4. Comparar:
   - Diferencia en profundidad
   - Diferencia en área
   - Calcular error relativo
   
Criterio aceptación:
  - Error < 5% para características > 10 cm
  - Error < 10% para características < 10 cm
```

---

### 5.3 Protocolo de Validación Continua

**Durante operación:**

```
POST-MISIÓN:
├─ Revisar logs de sensor
│  ├─ IMU: ¿drift razonable?
│  ├─ LIDAR: ¿densidad de puntos adecuada?
│  └─ Cámara: ¿suficientes features para VO?
│
├─ Verificar cierre de trayectoria
│  └─ Dron debería retornar a punto inicial
│      Error: (x_final - x_inicial)
│
├─ Validar contra marcadores
│  └─ Comparar posición estimada vs posición real marcador
│      Si > 0.5m: investigar causa
│
└─ Auditar mapa generado
   └─ ¿Es topológicamente consistente?
      ¿Paredes rectas son rectas?
      ¿Ángulos son correctos?
```

---

## 6. Arquitectura Completa Propuesta

### 6.1 Diagrama de Sistema Integrado

```
┌──────────────────────────────────────────────────────────────┐
│                    DRON AUTÓNOMO                              │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ SENSORES PRIMARIOS                                     │  │
│  │ ├─ IMU 9-DOF (200 Hz)                                  │  │
│  │ ├─ LIDAR 3D (10 Hz)                                    │  │
│  │ ├─ Cámara estéreo (30 Hz)                              │  │
│  │ ├─ Ultrasónicos ×6 (50 Hz)                             │  │
│  │ └─ Barométro (5 Hz)                                    │  │
│  └────────────────┬───────────────────────────────────────┘  │
│                   │                                            │
│  ┌────────────────▼───────────────────────────────────────┐  │
│  │ PROCESAMIENTO EN TIEMPO REAL (Edge Computing)          │  │
│  │ ├─ Extended Kalman Filter (EKF)                        │  │
│  │ ├─ Odometría visual (VO)                               │  │
│  │ ├─ Detección de loop closure                           │  │
│  │ ├─ Control de colisión (ultrasónico)                   │  │
│  │ └─ Mapeo SLAM incremental                              │  │
│  └────────────────┬───────────────────────────────────────┘  │
│                   │                                            │
│  ┌────────────────▼───────────────────────────────────────┐  │
│  │ MÓDULO DE MEDICIÓN                                     │  │
│  │ ├─ Cálculo distancia a obstáculos (LIDAR+ultrasónico) │  │
│  │ ├─ Estimación dimensiones (ancho, alto, volumen)      │  │
│  │ ├─ Detección de anomalías (daños, corrosión)          │  │
│  │ └─ Generación de reportes métricos                     │  │
│  └────────────────┬───────────────────────────────────────┘  │
│                   │                                            │
│  ┌────────────────▼───────────────────────────────────────┐  │
│  │ ALMACENAMIENTO Y CONTROL                               │  │
│  │ ├─ SSD local (mapas, logs, mediciones)                 │  │
│  │ ├─ Control de vuelo autónomo                           │  │
│  │ ├─ Planificación de ruta                               │  │
│  │ └─ Monitoreo de batería/recursos                       │  │
│  └────────────────┬───────────────────────────────────────┘  │
│                   │                                            │
└───────────────────┼────────────────────────────────────────────┘
                    │
         Tether (comunicación + potencia)
                    │
┌───────────────────▼────────────────────────────────────────────┐
│          ESTACIÓN BASE (en entrada de espacios confinados)      │
│                                                                 │
│  ├─ Operador (control manual de emergencia)                     │
│  ├─ Modem Tether para datos en tiempo real                      │
│  ├─ Suministro de potencia (batería o AC)                       │
│  ├─ Carrete de tether (1-2 km capacidad típica)                │
│  └─ Módulo post-procesamiento (generación de reportes finales) │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 6.2 Flujo de Procesamiento de Datos

```
ADQUISICIÓN → FUSIÓN → LOCALIZACIÓN → MAPEO → MEDICIÓN → SALIDA

┌─────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────┐
│ Sensores    │──▶│ EKF + VO     │──▶│ SLAM         │──▶│ Mapa │
│             │   │              │   │              │   │ 3D   │
│ IMU         │   │ Fusión datos │   │ Optimización │   └──┬───┘
│ LIDAR       │   │              │   │ de pose      │      │
│ Cámara      │   └──────────────┘   └──────────────┘      │
│ Ultrasónico │                                            │
└─────────────┘                                            │
                                                           │
       ┌─────────────────────────────────────────────────┘
       │
       ▼
   ┌──────────────────────────────────────┐
   │ MÓDULO DE MEDICIÓN                   │
   ├──────────────────────────────────────┤
   │                                      │
   │ ├─ Distancia a obstáculos            │
   │ ├─ Dimensiones geométricas           │
   │ ├─ Volúmenes                         │
   │ └─ Detección de anomalías            │
   │                                      │
   └──────────────┬───────────────────────┘
                  │
       ┌──────────▼──────────┐
       │ REPORTE FINAL       │
       ├─────────────────────┤
       │ • Mapa 3D (LAS)     │
       │ • Mediciones (CSV)  │
       │ • Fotografías       │
       │ • Análisis (PDF)    │
       └─────────────────────┘
```

