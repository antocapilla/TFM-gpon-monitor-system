"""Smoke tests del paquete de propagación.

Se ejecutan sin red ni GPU. El motor analítico se prueba siempre; el de Sionna RT
solo si la librería está instalada en el entorno.

Uso:  python -m tests.test_propagation        (desde backend/)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from propagation import SimulationParams, channels, sionna_engine
from propagation import engine


def sample_floor():
    """Una planta rectangular sencilla con un tabique interior (coords en píxeles)."""
    w, h = 200, 150  # píxeles
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": {"material": "concrete"},
             "geometry": {"type": "Polygon", "coordinates": [[
                 [0, 0], [w, 0], [w, h], [0, h], [0, 0]]]}},
            {"type": "Feature", "properties": {"material": "brick"},
             "geometry": {"type": "LineString", "coordinates": [[w / 2, 0], [w / 2, h * 0.7]]}},
        ],
    }
    onts = [{"serial": "ONT-A", "x": 50, "y": 75},
            {"serial": "ONT-B", "x": 150, "y": 75}]
    scale = 0.05  # 0.05 m/píxel -> planta de 10 x 7.5 m
    return geojson, onts, scale


def _check_result(result, expected_engine):
    assert result["engine"] == expected_engine, result["engine"]
    assert result["heatmapData"], "heatmap vacío"
    values = [p["value"] for p in result["heatmapData"]]
    assert all(-120 <= v <= 0 for v in values), (min(values), max(values))
    assert len(result["channelAllocation"]) == 2
    chans = {c["channel2_4"] for c in result["channelAllocation"]}
    # Dos APs cercanos e interferentes deben recibir canales distintos.
    assert len(chans) == 2, chans
    print(f"  [{expected_engine}] celdas={len(values)} "
          f"RSS {min(values):.1f}..{max(values):.1f} dBm  "
          f"canales={[c['channel2_4'] for c in result['channelAllocation']]}")


def test_analytical():
    geojson, onts, scale = sample_floor()
    fast = SimulationParams(resolution_m=0.5)
    result = engine.run(geojson, onts, scale, params=fast, force_engine="analytical")
    _check_result(result, "analytical")


def test_sionna():
    if not sionna_engine.is_available():
        print("  [sionna] no instalado -> omitido")
        return
    geojson, onts, scale = sample_floor()
    fast = SimulationParams(resolution_m=0.5, samples_per_tx=200_000, max_depth=3)
    result = engine.run(geojson, onts, scale, params=fast, force_engine="sionna")
    _check_result(result, "sionna")


def test_channels_coloring():
    onts = [{"serial": f"O{i}", "x": x, "y": 0} for i, x in enumerate([0, 100, 200, 300])]
    alloc = channels.allocate_channels(onts, scale=0.05)  # 5 m de separación
    assert len(alloc) == 4
    print(f"  [channels] {[a['channel2_4'] for a in alloc]}")


if __name__ == "__main__":
    print("Running propagation smoke tests...")
    test_analytical()
    test_sionna()
    test_channels_coloring()
    print("OK")
