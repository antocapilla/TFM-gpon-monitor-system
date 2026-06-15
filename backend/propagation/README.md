# Módulo de propagación de señal (`propagation/`)

Simulación de cobertura RF (WiFi 2.4/5 GHz) sobre las plantas del edificio y
asignación de canales WiFi. Sustituye al antiguo `signal_strength_simulation/`
(prototipos de ray launching 2D) y a `co_channel_interference/`.

## Arquitectura

```
GeoJSON (px) ─▶ geometry.py ─▶ FloorGeometry (m)
                                   │
                 ┌─────────────────┴──────────────────┐
                 ▼                                     ▼
        sionna_engine.py                      analytical_engine.py
   (Sionna RT, ray tracing 3D)            (multi-pared COST-231/ITU)
                 └─────────────────┬──────────────────┘
                                   ▼
                              engine.run()  ─▶  heatmap + canales
```

| Fichero | Responsabilidad |
|---|---|
| `geometry.py` | GeoJSON (píxeles) → paredes y bounds en metros (`scale` = m/píxel). |
| `materials.py` | Catálogo de materiales: material radio ITU (Sionna) + atenuación por pared (modelo analítico). |
| `scene_builder.py` | Extruye las paredes 2D a una escena 3D Mitsuba (XML) para Sionna RT. |
| `sionna_engine.py` | **Motor principal**: mapa de cobertura con `RadioMapSolver`. |
| `analytical_engine.py` | **Respaldo**: FSPL + Σ atenuación de paredes atravesadas (LOS). |
| `channels.py` | Asignación de canales WiFi por coloreo de grafos. |
| `params.py` | Parámetros (frecuencia, potencia, alturas, resolución, profundidad de rayos). |
| `engine.py` | Orquestador: elige motor, combina por *mejor servidor* y formatea la salida. |

## Selección de motor

`engine.run()` usa **Sionna RT** si está instalado; si no, recurre
automáticamente al **modelo analítico multi-pared** (registrando un warning).
Esto permite desplegar el backend sin GPU obteniendo resultados razonables, y
activar el ray tracing completo cuando hay hardware disponible.

```python
from propagation import run, SimulationParams
result = run(geojson, onts, scale, params=SimulationParams(frequency_hz=5e9))
result["engine"]  # "sionna" | "analytical"
```

## Sionna RT (motor principal)

- Requiere `sionna-rt` (Mitsuba 3 + Dr.Jit + TensorFlow/PyTorch). Se beneficia
  mucho de **GPU**; en CPU funciona pero es más lento.
- Modela LOS, reflexión especular, refracción (transmisión) y difracción.
- Materiales radio ITU-R P.2040 (`itu-radio-material`).

Para forzar GPU, fija `CUDA_VISIBLE_DEVICES` antes de arrancar el backend.

## Modelo analítico (respaldo)

Modelo multi-pared estilo COST-231 / ITU-R P.1238:

```
PL(dB) = 20·log10(4π·d/λ) + Σ atenuación_de_cada_pared_atravesada
RSS    = P_tx − PL          (combinación: mejor servidor)
```

Determinista y rápido (vectorizado en NumPy), sin multitrayecto.

## Tests

```bash
cd backend
python -m tests.test_propagation
```

Prueba el motor analítico siempre y el de Sionna RT si está instalado.
