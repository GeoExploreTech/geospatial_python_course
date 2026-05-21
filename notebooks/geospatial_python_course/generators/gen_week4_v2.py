import json
import uuid
from pathlib import Path
from textwrap import dedent


def cell_id():
    return uuid.uuid4().hex[:12]


def md(src: str, cid=None) -> dict:
    lines = src.split("\n")
    source = [l + "\n" for l in lines[:-1]] + [lines[-1]]
    return {"cell_type": "markdown", "id": cid or cell_id(), "metadata": {}, "source": source}


def code(src: str, cid=None) -> dict:
    lines = src.split("\n")
    source = [l + "\n" for l in lines[:-1]] + [lines[-1]]
    return {
        "cell_type": "code",
        "id": cid or cell_id(),
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": source,
    }


def s(text: str) -> str:
    return dedent(text).strip("\n")


def section_md(num: int, title: str, intro: str, subtopic: str, detail: str) -> dict:
    return md(
        f"---\n## 📖 Section {num} — {title}\n\n{intro}\n\n### {num}.1 {subtopic}\n{detail}"
    )


def exercise_md(num: int, title: str, task: str, steps, hint: str) -> dict:
    step_lines = "\n".join(f"{i}. {step}" for i, step in enumerate(steps, start=1))
    return md(
        f"### 🎯 Exercise {num} — {title}\n\n**Task:** {task}\n\n**Steps:**\n{step_lines}\n\n```python\n{hint}\n```"
    )


def exercise_stub(num: int, comments) -> dict:
    body = "\n".join(f"# {i}. {comment}" for i, comment in enumerate(comments, start=1))
    return code(
        f"# 🎯 Exercise {num} — your code here ────────────────────────────────────────────\n{body}"
    )


def solution_code(num: int, body: str) -> dict:
    return code(
        f"# ✅ Exercise {num} — Solution ────────────────────────────────────────────────────\n{body}"
    )


def lesson_code(label: str, title: str, body: str) -> dict:
    return code(
        f"# 💻 {label}  {title}\n# ─────────────────────────────────────────────────────────────────────────────\n{body}"
    )


def lab_step(num: int, title: str, body: str) -> dict:
    return code(
        f"# 🔬 Step {num} — {title}\n# ─────────────────────────────────────────────────────────────────────────────\n{body}"
    )


REPO_ROOT = Path(__file__).resolve().parents[3]
OUT = REPO_ROOT / 'notebooks' / 'geospatial_python_course' / 'week_04_geospatial_foundations.ipynb'

metadata = {
    'kernelspec': {
        'display_name': 'Python 3 (ipykernel)',
        'language': 'python',
        'name': 'python3',
    },
    'language_info': {
        'codemirror_mode': {'name': 'ipython', 'version': 3},
        'file_extension': '.py',
        'mimetype': 'text/x-python',
        'name': 'python',
        'pygments_lexer': 'ipython3',
        'version': '3.11.0',
    },
    'toc-autonumbering': False,
}

week_title = md(s('''
# 🌍 Week 4 — Geospatial Foundations
### Geospatial Python Mastery | Module B: Data Structures and File I/O

---

|  |  |
|---|---|
| **Course** | Geospatial Python Mastery |
| **Week** | 4 of 10 |
| **Theme** | Geospatial Foundations — Coordinates, Projections, CRS |
| **Duration** | ~4 contact hours + 4 hours self-study |
| **Practice Outcome** | Mini-Lab: Compare WGS84 and UTM 31N workflows for Netherlands cities |
| **Next week** | Spatial libraries — GeoPandas, Shapely full API, Rasterio, Fiona |

---

> 🗺️ **Why this week matters**
> Coordinates only become meaningful when you know the datum, the axis order, and the
> units behind them. Week 4 connects geography and code: you will inspect CRS metadata,
> transform Dutch city coordinates into projected systems, compare distance methods, and
> use Shapely geometry objects to reason about topology before moving into full GeoPandas workflows.

---

## 📋 Table of Contents

| Section | Topic |
|---------|-------|
| [1 — Environment Setup](#section-1) | Auto-install, imports, data dirs |
| [2 — Coordinate Systems Basics](#section-2) | WGS84, lat/lon, geographic vs projected |
| [3 — PyProj CRS](#section-3) | EPSG inspection, axis order, units |
| [4 — Coordinate Transformations](#section-4) | `Transformer.from_crs(always_xy=True)` |
| [5 — Distance Comparison](#section-5) | Haversine, `Geod.inv`, UTM Euclidean |
| [6 — Shapely Geometry Types](#section-6) | Point, LineString, Polygon properties |
| [7 — Topology and Spatial Predicates](#section-7) | `contains`, `within`, `touches`, DE-9IM |
| [8 — Reusable Module](#section-8) | Write and import `crs_utils.py` |
| [9 — File Formats](#section-9) | Save and reload WKT, GeoJSON, CSV |
| [10 — Logging and Testing](#section-10) | Log transforms and test helper functions |

---

## 🗺️ Symbol Guide

| Symbol | Meaning |
|--------|---------|
| 💻 | Runnable code cell |
| 🎯 | Exercise — write your own code |
| ✅ | Solution — run after attempting |
| 🔬 | Mini-Lab step |
| 📖 | Explanatory section |
| 💡 | Tip or best practice |
| ⚠️ | Common mistake or warning |

> **Keyboard shortcuts:** `Shift+Enter` run cell · `b` insert cell below · `m` convert to Markdown · `Esc` command mode
'''))

objectives = [
    'Explain latitude, longitude, and altitude in the WGS84 datum',
    'Distinguish **geographic** (degree-based) from **projected** (metre-based) CRS',
    'Use `pyproj.CRS` to inspect EPSG codes, axis order, and units',
    'Transform coordinates with `pyproj.Transformer.from_crs(always_xy=True)`',
    'Create Shapely **Point**, **LineString**, and **Polygon** objects and read their properties',
    'Test spatial relationships: `contains`, `intersects`, `within`, `touches`',
    'Build a reusable `crs_utils.py` module with validation and transform helpers',
    'Export geometry data to WKT, GeoJSON, and CSV and re-read it portably',
]
objective_rows = '\n'.join(f'| {i} | {text} |' for i, text in enumerate(objectives, start=1))
learning_objectives = md(s(f'''
## 🎯 Learning Objectives

By the end of this notebook you will be able to:

| # | Objective |
|---|-----------|
{objective_rows}

### How to use this notebook

- Run cells **top to bottom** in sequence
- **Attempt** each 🎯 exercise before looking at the ✅ solution
- The 🔬 **Mini-Lab** at the end ties all skills together
- Tick each box in the ☑️ checklist before moving to the next week
'''))

environment = code(s('''
# 💻 Environment check and auto-install
# ─────────────────────────────────────────────────────────────────────────────
import sys, subprocess, importlib, platform

try:
    import google.colab
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

OS_NAME = platform.system()

print("=" * 60)
print("  Geospatial Python Mastery — Week 4 Environment Check")
print("=" * 60)
print(f"  Environment : {'Google Colab' if IN_COLAB else 'Local Jupyter'}")
print(f"  Python      : {sys.version.split()[0]}")
print(f"  OS          : {OS_NAME}")

REQUIRED = [
    ("math",     "",        ""),
    ("json",     "",        ""),
    ("csv",      "",        ""),
    ("logging",  "",        ""),
    ("unittest", "",        ""),
    ("pyproj",   "pyproj",  "3.0"),
    ("shapely",  "shapely", "2.0"),
]

for import_name, pip_name, min_ver in REQUIRED:
    try:
        mod = importlib.import_module(import_name)
        ver = getattr(mod, "__version__", "stdlib")
        print(f"  ✅ {import_name:<20} {ver}")
    except ImportError:
        pkg = pip_name or import_name
        print(f"  ⬇  Installing {pkg}…")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg])
        print(f"  ✅ {pkg} installed")

if OS_NAME == "Windows":
    print("\\n  ℹ  Windows note: use 'python -m jupyter notebook' to launch Jupyter")

print("\\n✅ Environment check complete — ready for Week 4!")
'''))

imports = lesson_code('0.1', 'Import CRS, geometry, and file helpers', s('''
import csv
import json
import logging
import math
import sys
import unittest
from importlib import reload
from pathlib import Path
from pprint import pprint

from pyproj import CRS, Geod, Transformer
from shapely import from_wkt, to_wkt
from shapely.geometry import LineString, Point, Polygon, mapping, shape

print('Imports loaded successfully.')
'''))

setup_dirs = lesson_code('0.2', 'Create data, logs, modules, and test folders', s('''
def find_repo_root(start: Path) -> Path:
    start = start.resolve()
    for candidate in [start, *start.parents]:
        if (candidate / 'notebooks').exists() and (candidate / 'instructions').exists():
            return candidate
    return start

PROJECT_ROOT = find_repo_root(Path.cwd())
COURSE_DIR = PROJECT_ROOT / 'notebooks' / 'geospatial_python_course'
WEEK_DIR = COURSE_DIR / 'data' / 'week_04'
INPUT_DIR = WEEK_DIR / 'input'
OUTPUT_DIR = WEEK_DIR / 'output'
LOG_DIR = COURSE_DIR / 'logs'
MODULE_DIR = COURSE_DIR / 'local_modules'
TEST_DIR = COURSE_DIR / 'tests'

for path in [WEEK_DIR, INPUT_DIR, OUTPUT_DIR, LOG_DIR, MODULE_DIR, TEST_DIR]:
    path.mkdir(parents=True, exist_ok=True)

print('Project root :', PROJECT_ROOT)
print('Week 4 input :', INPUT_DIR)
print('Week 4 output:', OUTPUT_DIR)
'''))

sections = [
    {
        'title': 'Environment Setup',
        'intro': 'Create a predictable workspace before you start transforming coordinates or writing geometry files.',
        'subtopic': 'Course folders and starter city data',
        'detail': 'We keep raw inputs, exported outputs, test files, and local utility modules in stable locations so later spatial workflows stay portable.',
        'code1_label': '1.1',
        'code1_title': 'Inspect shared folders and CRS targets',
        'code1_body': s('''
workspace = {
    'input': INPUT_DIR,
    'output': OUTPUT_DIR,
    'logs': LOG_DIR,
    'modules': MODULE_DIR,
    'tests': TEST_DIR,
}
for label, path in workspace.items():
    print(f'{label:<8} -> {path}')

WGS84 = 4326
UTM31N = 32631
RD_NEW = 28992
print('\\nTarget EPSG codes:', WGS84, UTM31N, RD_NEW)
'''),
        'code2_label': '1.2',
        'code2_title': 'Create a starter CSV of Dutch cities in WGS84',
        'code2_body': s('''
dutch_cities = [
    {'city': 'Amsterdam', 'lon': 4.9041, 'lat': 52.3676, 'country': 'NL'},
    {'city': 'Rotterdam', 'lon': 4.4777, 'lat': 51.9244, 'country': 'NL'},
    {'city': 'Utrecht', 'lon': 5.1214, 'lat': 52.0907, 'country': 'NL'},
    {'city': 'Groningen', 'lon': 6.5665, 'lat': 53.2194, 'country': 'NL'},
    {'city': 'Eindhoven', 'lon': 5.4697, 'lat': 51.4416, 'country': 'NL'},
]

city_csv_path = INPUT_DIR / 'netherlands_cities_wgs84.csv'
with city_csv_path.open('w', newline='', encoding='utf-8') as fh:
    writer = csv.DictWriter(fh, fieldnames=['city', 'country', 'lon', 'lat'])
    writer.writeheader()
    writer.writerows(dutch_cities)

print('Saved starter CSV to:', city_csv_path)
pprint(dutch_cities)
'''),
        'exercise_title': 'Create a CRS manifest file',
        'exercise_task': 'Use `pathlib` and `json` to write a manifest describing the EPSG codes and data files used this week.',
        'exercise_steps': [
            'Create a Python dictionary with keys like `source_crs`, `projected_targets`, and `input_file`.',
            'Write the manifest to `INPUT_DIR / "week4_manifest.json"`.',
        ],
        'exercise_hint': '# Hint\nmanifest = {"source_crs": 4326, "projected_targets": [32631, 28992]}',
        'exercise_comments': ['Create the manifest dictionary.', 'Save it to JSON.'],
        'solution_body': s('''
manifest = {
    'source_crs': WGS84,
    'projected_targets': [UTM31N, RD_NEW],
    'input_file': city_csv_path.name,
}
manifest_path = INPUT_DIR / 'week4_manifest.json'
manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')

print('Manifest saved to:', manifest_path)
print(manifest_path.read_text(encoding='utf-8'))
'''),
    },
    {
        'title': 'Coordinate Systems Basics',
        'intro': 'Coordinates are only numbers until you attach meaning: datum, axis order, units, and area of use.',
        'subtopic': 'Geographic vs projected CRS',
        'detail': 'A geographic CRS stores angular coordinates on an ellipsoid, while a projected CRS converts those angles into planar x/y values measured in metres or feet.',
        'code1_label': '2.1',
        'code1_title': 'Review WGS84 latitude and longitude values',
        'code1_body': s('''
print('City              lon (°)    lat (°)')
print('-' * 38)
for row in dutch_cities:
    print(f"{row['city']:<12} {row['lon']:>7.4f}   {row['lat']:>7.4f}")

print('\\nWGS84 is geographic: units are degrees, not metres.')
print('Altitude can be added as a third value, but most vector workflows begin with lon/lat.')
'''),
        'code2_label': '2.2',
        'code2_title': 'Compare angular and metric thinking',
        'code2_body': s('''
print("""Geographic CRS (WGS84)\n  x = longitude in degrees\n  y = latitude in degrees\nProjected CRS (UTM / RD New)\n  x = easting in metres\n  y = northing in metres""")

amsterdam = dutch_cities[0]
rotterdam = dutch_cities[1]
lon_delta = abs(amsterdam['lon'] - rotterdam['lon'])
lat_delta = abs(amsterdam['lat'] - rotterdam['lat'])
print(f'\\nAmsterdam ↔ Rotterdam degree delta: lon={lon_delta:.4f}, lat={lat_delta:.4f}')
print('Those degree differences are useful for storage, but not a direct metric distance.')
'''),
        'exercise_title': 'Describe coordinate meaning',
        'exercise_task': 'Pick two cities from `dutch_cities`, compute the raw degree deltas, and explain in a comment why that is not the same as a true ground distance.',
        'exercise_steps': [
            'Subtract longitude and latitude values for any city pair.',
            'Add a short code comment explaining why projection or geodesic distance is needed.',
        ],
        'exercise_hint': '# Hint\nd_lon = city_a["lon"] - city_b["lon"]',
        'exercise_comments': ['Compute longitude and latitude deltas.', 'Write a comment about degrees versus metres.'],
        'solution_body': s('''
city_a = dutch_cities[2]
city_b = dutch_cities[4]
d_lon = abs(city_a['lon'] - city_b['lon'])
d_lat = abs(city_a['lat'] - city_b['lat'])

# Degrees are angular measurements on the ellipsoid, so they do not give a single metric distance.
print(f"{city_a['city']} ↔ {city_b['city']} degree delta: lon={d_lon:.4f}, lat={d_lat:.4f}")
'''),
    },
    {
        'title': 'PyProj CRS',
        'intro': '`pyproj.CRS` turns an EPSG code into structured metadata you can inspect directly in Python.',
        'subtopic': 'Names, axes, and units',
        'detail': 'CRS inspection is how you confirm whether a coordinate system is geographic or projected before you compute lengths or areas.',
        'code1_label': '3.1',
        'code1_title': 'Inspect WGS84 and UTM 31N objects',
        'code1_body': s('''
crs_wgs84 = CRS.from_epsg(WGS84)
crs_utm31n = CRS.from_epsg(UTM31N)

print('WGS84 name       :', crs_wgs84.name)
print('WGS84 is geographic:', crs_wgs84.is_geographic)
print('WGS84 axis info  :', [(axis.name, axis.unit_name) for axis in crs_wgs84.axis_info])
print('\\nUTM31N name      :', crs_utm31n.name)
print('UTM31N projected :', crs_utm31n.is_projected)
print('UTM31N axis info :', [(axis.name, axis.unit_name) for axis in crs_utm31n.axis_info])
'''),
        'code2_label': '3.2',
        'code2_title': 'Inspect RD New and export WKT',
        'code2_body': s('''
crs_rd_new = CRS.from_epsg(RD_NEW)
print('RD New name      :', crs_rd_new.name)
print('RD New axis info :', [(axis.name, axis.unit_name) for axis in crs_rd_new.axis_info])
print('Equals EPSG string:', crs_utm31n.equals(CRS.from_user_input('EPSG:32631')))
print('\\nFirst 220 characters of WKT:')
print(crs_rd_new.to_wkt()[:220] + '...')
'''),
        'exercise_title': 'Inspect an EPSG code',
        'exercise_task': 'Create a `CRS` object for EPSG:28992 and print its name, whether it is projected, and its unit.',
        'exercise_steps': [
            'Use `CRS.from_epsg(28992)`.',
            'Read metadata from `.name`, `.is_projected`, and `.axis_info`.',
        ],
        'exercise_hint': '# Hint\nrd = CRS.from_epsg(28992)',
        'exercise_comments': ['Create the CRS object.', 'Print the key metadata fields.'],
        'solution_body': s('''
rd = CRS.from_epsg(28992)
print('Name        :', rd.name)
print('Projected   :', rd.is_projected)
print('Unit        :', rd.axis_info[0].unit_name)
'''),
    },
    {
        'title': 'Coordinate Transformations',
        'intro': 'Transformations convert the same location into a coordinate system that matches the measurement task you want to perform.',
        'subtopic': 'Using Transformer with always_xy=True',
        'detail': 'Set `always_xy=True` so you consistently provide longitude first and latitude second, even for CRS definitions that advertise latitude-first axis order.',
        'code1_label': '4.1',
        'code1_title': 'Transform Amsterdam from WGS84 to UTM 31N',
        'code1_body': s('''
transformer_utm = Transformer.from_crs(WGS84, UTM31N, always_xy=True)
transformer_rd = Transformer.from_crs(WGS84, RD_NEW, always_xy=True)

ams = dutch_cities[0]
ams_x_utm, ams_y_utm = transformer_utm.transform(ams['lon'], ams['lat'])
ams_x_rd, ams_y_rd = transformer_rd.transform(ams['lon'], ams['lat'])

print('Amsterdam WGS84 :', (ams['lon'], ams['lat']))
print('Amsterdam UTM31N:', (round(ams_x_utm, 2), round(ams_y_utm, 2)))
print('Amsterdam RD New:', (round(ams_x_rd, 2), round(ams_y_rd, 2)))
'''),
        'code2_label': '4.2',
        'code2_title': 'Batch-transform all Dutch cities',
        'code2_body': s('''
transformed_cities = []
for row in dutch_cities:
    x_utm, y_utm = transformer_utm.transform(row['lon'], row['lat'])
    x_rd, y_rd = transformer_rd.transform(row['lon'], row['lat'])
    transformed_cities.append({
        **row,
        'utm31n_x': round(x_utm, 2),
        'utm31n_y': round(y_utm, 2),
        'rd_x': round(x_rd, 2),
        'rd_y': round(y_rd, 2),
    })

pprint(transformed_cities)
'''),
        'exercise_title': 'Transform a city with always_xy=True',
        'exercise_task': 'Transform the WGS84 coordinate pair for Utrecht into UTM 31N and print the result.',
        'exercise_steps': [
            'Build a transformer from EPSG:4326 to EPSG:32631 with `always_xy=True`.',
            'Pass longitude first and latitude second.',
        ],
        'exercise_hint': '# Hint\ntransformer = Transformer.from_crs(4326, 32631, always_xy=True)',
        'exercise_comments': ['Create the transformer.', 'Transform Utrecht and print x/y.'],
        'solution_body': s('''
utrecht = next(row for row in dutch_cities if row['city'] == 'Utrecht')
exercise_transformer = Transformer.from_crs(4326, 32631, always_xy=True)
utrecht_x, utrecht_y = exercise_transformer.transform(utrecht['lon'], utrecht['lat'])
print('Utrecht UTM31N:', round(utrecht_x, 2), round(utrecht_y, 2))
'''),
    },
    {
        'title': 'Distance Comparison',
        'intro': 'Different distance methods answer slightly different questions because they assume different geometry models.',
        'subtopic': 'Haversine, geodesic, and projected Euclidean distance',
        'detail': 'Haversine approximates Earth as a sphere, `Geod.inv` uses the ellipsoid, and Euclidean distance assumes your projected CRS is appropriate for the study area.',
        'code1_label': '5.1',
        'code1_title': 'Compare Haversine and Geod.inv',
        'code1_body': s('''
def haversine_km(lon1, lat1, lon2, lat2):
    radius_km = 6371.0088
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * radius_km * math.asin(math.sqrt(a))

geod = Geod(ellps='WGS84')
rotterdam = dutch_cities[1]

haversine_distance_km = haversine_km(ams['lon'], ams['lat'], rotterdam['lon'], rotterdam['lat'])
_, _, geodesic_distance_m = geod.inv(ams['lon'], ams['lat'], rotterdam['lon'], rotterdam['lat'])
print('Haversine km :', round(haversine_distance_km, 3))
print('Geodesic km  :', round(geodesic_distance_m / 1000, 3))
'''),
        'code2_label': '5.2',
        'code2_title': 'Compute Euclidean distance in UTM 31N',
        'code2_body': s('''
city_lookup = {row['city']: row for row in transformed_cities}
ams_utm = city_lookup['Amsterdam']
rot_utm = city_lookup['Rotterdam']
utm_distance_m = math.dist((ams_utm['utm31n_x'], ams_utm['utm31n_y']), (rot_utm['utm31n_x'], rot_utm['utm31n_y']))

print('UTM Euclidean km:', round(utm_distance_m / 1000, 3))
print('Why the numbers differ: different Earth models and projection assumptions.')
'''),
        'exercise_title': 'Measure another city pair',
        'exercise_task': 'Compute the geodesic and UTM Euclidean distance between Utrecht and Eindhoven.',
        'exercise_steps': [
            'Use `Geod.inv` on the WGS84 coordinates.',
            'Use `math.dist` on the UTM coordinates from `transformed_cities`.',
        ],
        'exercise_hint': '# Hint\n_, _, d_m = geod.inv(lon1, lat1, lon2, lat2)',
        'exercise_comments': ['Look up Utrecht and Eindhoven.', 'Compute geodesic and projected distances.'],
        'solution_body': s('''
utrecht = city_lookup['Utrecht']
eindhoven = city_lookup['Eindhoven']
_, _, geodesic_m = geod.inv(utrecht['lon'], utrecht['lat'], eindhoven['lon'], eindhoven['lat'])
projected_m = math.dist((utrecht['utm31n_x'], utrecht['utm31n_y']), (eindhoven['utm31n_x'], eindhoven['utm31n_y']))

print('Geodesic km :', round(geodesic_m / 1000, 3))
print('UTM km      :', round(projected_m / 1000, 3))
'''),
    },
    {
        'title': 'Shapely Geometry Types',
        'intro': 'Shapely stores geometry objects and exposes methods for length, area, and coordinate access.',
        'subtopic': 'Point, LineString, and Polygon construction',
        'detail': 'Geometry operations are only as meaningful as the CRS of the numbers you feed into them, so we will use projected coordinates for metric properties.',
        'code1_label': '6.1',
        'code1_title': 'Create Point, LineString, and Polygon objects',
        'code1_body': s('''
ams_point_utm = Point(ams_utm['utm31n_x'], ams_utm['utm31n_y'])
rot_point_utm = Point(rot_utm['utm31n_x'], rot_utm['utm31n_y'])
route_line = LineString([ams_point_utm, rot_point_utm])
city_polygon = Polygon([
    (ams_utm['utm31n_x'] - 20000, ams_utm['utm31n_y'] - 15000),
    (ams_utm['utm31n_x'] + 20000, ams_utm['utm31n_y'] - 15000),
    (ams_utm['utm31n_x'] + 20000, ams_utm['utm31n_y'] + 15000),
    (ams_utm['utm31n_x'] - 20000, ams_utm['utm31n_y'] + 15000),
])

print('Point type    :', ams_point_utm.geom_type)
print('Line type     :', route_line.geom_type)
print('Polygon type  :', city_polygon.geom_type)
'''),
        'code2_label': '6.2',
        'code2_title': 'Inspect geometry coordinates and measurements',
        'code2_body': s('''
print('Point coords   :', list(ams_point_utm.coords))
print('Line length km :', round(route_line.length / 1000, 3))
print('Polygon area km²:', round(city_polygon.area / 1_000_000, 3))
print('Polygon bounds :', city_polygon.bounds)
'''),
        'exercise_title': 'Create a metric buffer',
        'exercise_task': 'Create a 50 km buffer around Amsterdam in UTM 31N and print its area in square kilometres.',
        'exercise_steps': [
            'Use the UTM Point for Amsterdam.',
            'Call `.buffer(50_000)` and divide the area by `1_000_000`.',
        ],
        'exercise_hint': '# Hint\nbuffer_geom = ams_point_utm.buffer(50_000)',
        'exercise_comments': ['Create the 50 km buffer.', 'Print the area in km².'],
        'solution_body': s('''
ams_buffer_50km = ams_point_utm.buffer(50_000)
print('Buffered geometry type:', ams_buffer_50km.geom_type)
print('Area km²             :', round(ams_buffer_50km.area / 1_000_000, 2))
'''),
    },
    {
        'title': 'Topology and Spatial Predicates',
        'intro': 'Topology asks how geometries relate: overlap, containment, touching boundaries, and shared interiors.',
        'subtopic': 'contains, within, intersects, touches, and DE-9IM',
        'detail': 'Predicate methods convert geometry relationships into boolean answers you can use in filters, joins, and QA checks.',
        'code1_label': '7.1',
        'code1_title': 'Check predicate results between a buffer and city points',
        'code1_body': s('''
other_city_points = {
    row['city']: Point(row['utm31n_x'], row['utm31n_y'])
    for row in transformed_cities
}

for city_name, geom in other_city_points.items():
    if city_name == 'Amsterdam':
        continue
    print(
        city_name,
        'within buffer =', geom.within(ams_buffer_50km),
        '| intersects =', geom.intersects(ams_buffer_50km),
    )
'''),
        'code2_label': '7.2',
        'code2_title': 'Use touches and DE-9IM relate strings',
        'code2_body': s('''
buffer_boundary = ams_buffer_50km.boundary
rotterdam_tiny_buffer = rot_point_utm.buffer(1000)

print('Boundary touches Amsterdam point:', buffer_boundary.touches(ams_point_utm))
print('Amsterdam buffer relates Rotterdam point:', ams_buffer_50km.relate(rot_point_utm))
print('Amsterdam buffer intersects Rotterdam 1 km buffer:', ams_buffer_50km.intersects(rotterdam_tiny_buffer))
'''),
        'exercise_title': 'Test two predicate pairs',
        'exercise_task': 'Evaluate two predicate checks: whether Rotterdam is within Amsterdam\'s 50 km buffer, and whether the buffer contains the Amsterdam point.',
        'exercise_steps': [
            'Use the `within()` method on the Rotterdam point.',
            'Use `contains()` on the Amsterdam buffer.',
        ],
        'exercise_hint': '# Hint\nams_buffer_50km.contains(ams_point_utm)',
        'exercise_comments': ['Test Rotterdam against the buffer.', 'Test Amsterdam against the same buffer.'],
        'solution_body': s('''
print('Rotterdam within Amsterdam buffer:', rot_point_utm.within(ams_buffer_50km))
print('Amsterdam buffer contains Amsterdam point:', ams_buffer_50km.contains(ams_point_utm))
'''),
    },
    {
        'title': 'Reusable Module',
        'intro': 'A local helper module makes CRS-aware validation and transformation reusable in notebooks, scripts, and tests.',
        'subtopic': 'Writing `crs_utils.py`',
        'detail': 'The goal is a small toolkit: validate source records, transform them with a `Transformer`, and compute an XY bounding box.',
        'code1_label': '8.1',
        'code1_title': 'Write the crs_utils.py module',
        'code1_body': s('''
crs_utils_path = MODULE_DIR / 'crs_utils.py'
crs_utils_source = """
from pyproj import Transformer


class CRSValidationError(Exception):
    pass


def validate_wgs84_record(record):
    lon = float(record['lon'])
    lat = float(record['lat'])
    if not (-180 <= lon <= 180):
        raise CRSValidationError(f'Longitude out of range: {lon}')
    if not (-90 <= lat <= 90):
        raise CRSValidationError(f'Latitude out of range: {lat}')
    normalized = dict(record)
    normalized['lon'] = lon
    normalized['lat'] = lat
    return normalized


def transform_record(record, transformer, x_key='x', y_key='y'):
    normalized = validate_wgs84_record(record)
    x, y = transformer.transform(normalized['lon'], normalized['lat'])
    result = dict(normalized)
    result[x_key] = x
    result[y_key] = y
    return result


def bbox_xy(records, x_key='x', y_key='y'):
    xs = [row[x_key] for row in records]
    ys = [row[y_key] for row in records]
    return min(xs), min(ys), max(xs), max(ys)
"""
crs_utils_path.write_text(crs_utils_source.strip() + '\\n', encoding='utf-8')
print('Module written to:', crs_utils_path)
'''),
        'code2_label': '8.2',
        'code2_title': 'Import and use crs_utils helpers',
        'code2_body': s('''
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import crs_utils
crs_utils = reload(crs_utils)

validated_ams = crs_utils.validate_wgs84_record(dutch_cities[0])
transformed_ams = crs_utils.transform_record(validated_ams, transformer_utm, x_key='utm_x', y_key='utm_y')
print(validated_ams)
print(transformed_ams)
'''),
        'exercise_title': 'Reuse crs_utils.py',
        'exercise_task': 'Use `crs_utils.transform_record()` to transform Groningen to RD New, then compute the bounding box of Amsterdam and Groningen in RD New coordinates.',
        'exercise_steps': [
            'Transform Groningen with `transformer_rd` and custom key names.',
            'Pass two transformed records into `bbox_xy()`.',
        ],
        'exercise_hint': '# Hint\ncrs_utils.bbox_xy(records, x_key="rd_x", y_key="rd_y")',
        'exercise_comments': ['Transform Groningen into RD New.', 'Compute a small bounding box.'],
        'solution_body': s('''
groningen = next(row for row in dutch_cities if row['city'] == 'Groningen')
ams_rd = crs_utils.transform_record(dutch_cities[0], transformer_rd, x_key='rd_x', y_key='rd_y')
groningen_rd = crs_utils.transform_record(groningen, transformer_rd, x_key='rd_x', y_key='rd_y')
print('RD bbox:', crs_utils.bbox_xy([ams_rd, groningen_rd], x_key='rd_x', y_key='rd_y'))
'''),
    },
    {
        'title': 'File Formats',
        'intro': 'Spatial workflows often move the same geometry between text, JSON, and tabular formats.',
        'subtopic': 'Exporting and reloading WKT, GeoJSON, and CSV',
        'detail': 'Portable exports are useful for debugging, quick sharing, and interfacing with non-Python tools like PostGIS or spreadsheets.',
        'code1_label': '9.1',
        'code1_title': 'Save geometry data in multiple formats',
        'code1_body': s('''
route_wkt_path = OUTPUT_DIR / 'amsterdam_rotterdam_route.wkt'
route_geojson_path = OUTPUT_DIR / 'amsterdam_point.geojson'
route_csv_path = OUTPUT_DIR / 'city_points_projected.csv'

route_wkt_path.write_text(to_wkt(route_line), encoding='utf-8')
route_geojson_path.write_text(
    json.dumps({'type': 'Feature', 'properties': {'city': 'Amsterdam'}, 'geometry': mapping(ams_point_utm)}, indent=2),
    encoding='utf-8',
)
with route_csv_path.open('w', newline='', encoding='utf-8') as fh:
    writer = csv.DictWriter(fh, fieldnames=['city', 'lon', 'lat', 'utm31n_x', 'utm31n_y'])
    writer.writeheader()
    writer.writerows([{k: row[k] for k in ['city', 'lon', 'lat', 'utm31n_x', 'utm31n_y']} for row in transformed_cities])

print('Saved WKT, GeoJSON, and CSV exports.')
'''),
        'code2_label': '9.2',
        'code2_title': 'Reload geometry from WKT and GeoJSON',
        'code2_body': s('''
loaded_line = from_wkt(route_wkt_path.read_text(encoding='utf-8'))
loaded_feature = json.loads(route_geojson_path.read_text(encoding='utf-8'))
loaded_point = shape(loaded_feature['geometry'])

print('Loaded line type :', loaded_line.geom_type)
print('Loaded point type:', loaded_point.geom_type)
print('Loaded point XY  :', list(loaded_point.coords)[0])
'''),
        'exercise_title': 'Round-trip another geometry',
        'exercise_task': 'Export the Rotterdam point to GeoJSON and then reload it with `shape()`.',
        'exercise_steps': [
            'Create a GeoJSON feature dict using `mapping(rot_point_utm)`.',
            'Write it to disk, read it back, and convert the geometry with `shape()`.',
        ],
        'exercise_hint': '# Hint\nfeature = {"type": "Feature", "geometry": mapping(rot_point_utm), ...}',
        'exercise_comments': ['Write a Rotterdam GeoJSON file.', 'Reload it and inspect the geometry type.'],
        'solution_body': s('''
rotterdam_geojson_path = OUTPUT_DIR / 'rotterdam_point.geojson'
rotterdam_feature = {
    'type': 'Feature',
    'properties': {'city': 'Rotterdam'},
    'geometry': mapping(rot_point_utm),
}
rotterdam_geojson_path.write_text(json.dumps(rotterdam_feature, indent=2), encoding='utf-8')
reloaded_rotterdam = shape(json.loads(rotterdam_geojson_path.read_text(encoding='utf-8'))['geometry'])
print('Reloaded geometry:', reloaded_rotterdam.geom_type, list(reloaded_rotterdam.coords)[0])
'''),
    },
    {
        'title': 'Logging and Testing',
        'intro': 'Spatial code should be observable and verifiable, especially when transformations feed later analysis or database loads.',
        'subtopic': 'Log transform steps and test CRS helpers',
        'detail': 'We log what happened to each record and then prove the helper module behaves correctly with automated tests.',
        'code1_label': '10.1',
        'code1_title': 'Configure a Week 4 logger and log a transform pipeline',
        'code1_body': s('''
log_path = LOG_DIR / 'week4.log'
logger = logging.getLogger('gpm.week4')
logger.setLevel(logging.DEBUG)
logger.handlers.clear()

formatter = logging.Formatter('%(levelname)s | %(asctime)s | %(message)s')
file_handler = logging.FileHandler(log_path, encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

for row in dutch_cities:
    transformed = crs_utils.transform_record(row, transformer_utm, x_key='utm_x', y_key='utm_y')
    logger.info('Transformed %s to UTM31N: (%.2f, %.2f)', transformed['city'], transformed['utm_x'], transformed['utm_y'])

print('Log file:', log_path)
'''),
        'code2_label': '10.2',
        'code2_title': 'Write and run unit tests for crs_utils.py',
        'code2_body': s('''
test_file_path = TEST_DIR / 'test_crs_utils.py'
test_file_source = """
import sys
import unittest
from pathlib import Path
from pyproj import Transformer

COURSE_DIR = Path(__file__).resolve().parents[1]
MODULE_DIR = COURSE_DIR / 'local_modules'
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import crs_utils


class TestCRSUtils(unittest.TestCase):
    def setUp(self):
        self.record = {'city': 'Amsterdam', 'lon': 4.9041, 'lat': 52.3676}
        self.bad_record = {'city': 'Broken', 'lon': 500.0, 'lat': 52.0}
        self.transformer = Transformer.from_crs(4326, 32631, always_xy=True)

    def test_validate_wgs84_record_normalizes_floats(self):
        result = crs_utils.validate_wgs84_record(self.record)
        self.assertIsInstance(result['lon'], float)
        self.assertEqual(result['city'], 'Amsterdam')

    def test_validate_wgs84_record_rejects_invalid_lon(self):
        with self.assertRaises(crs_utils.CRSValidationError):
            crs_utils.validate_wgs84_record(self.bad_record)

    def test_transform_record_adds_projected_keys(self):
        result = crs_utils.transform_record(self.record, self.transformer, x_key='utm_x', y_key='utm_y')
        self.assertIn('utm_x', result)
        self.assertIn('utm_y', result)


if __name__ == '__main__':
    unittest.main()
"""
test_file_path.write_text(test_file_source.strip() + '\\n', encoding='utf-8')

suite = unittest.defaultTestLoader.discover(str(TEST_DIR), pattern='test_crs_utils.py')
runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)
'''),
        'exercise_title': 'Add one assertRaises check',
        'exercise_task': 'Write an inline `unittest.TestCase` that confirms `validate_wgs84_record()` raises `CRSValidationError` when latitude is outside -90..90.',
        'exercise_steps': [
            'Create a small `unittest.TestCase` subclass.',
            'Use `self.assertRaises(...)` in one test method.',
        ],
        'exercise_hint': '# Hint\nwith self.assertRaises(crs_utils.CRSValidationError):\n    crs_utils.validate_wgs84_record(...)',
        'exercise_comments': ['Define the inline test class.', 'Run the test suite.'],
        'solution_body': s('''
class InlineCRSTests(unittest.TestCase):
    def test_invalid_latitude_raises(self):
        with self.assertRaises(crs_utils.CRSValidationError):
            crs_utils.validate_wgs84_record({'city': 'Broken', 'lon': 4.9, 'lat': 123.0})

unittest.TextTestRunner(verbosity=2).run(
    unittest.defaultTestLoader.loadTestsFromTestCase(InlineCRSTests)
)
'''),
    },
]

lab_intro = md(s('''
---
## 🔬 Mini-Lab — Netherlands Cities CRS Comparison

**Scenario:** You are preparing a briefing for a Dutch planning team. They need to understand how the same five city locations behave in WGS84, UTM 31N, and RD New before they commit to a national analysis workflow.

**Tasks:**
1. Create a list of 5 Dutch cities with WGS84 coordinates
2. Validate all coordinates with `crs_utils`
3. Transform to UTM 31N (`EPSG:32631`) and to RD New (`EPSG:28992`)
4. Compute Amsterdam→Rotterdam distance with `Geod.inv` AND UTM Euclidean
5. Create a 50 km Shapely buffer around Amsterdam in UTM 31N
6. Check which other cities fall within the buffer
7. Export results to a GeoJSON file
'''))

lab_steps = [
    lab_step(1, 'Create five Dutch city records', s('''
lab_cities = [dict(row) for row in dutch_cities]
pprint(lab_cities)
''')),
    lab_step(2, 'Validate all coordinates with crs_utils', s('''
validated_lab_cities = [crs_utils.validate_wgs84_record(row) for row in lab_cities]
print('Validated records:', len(validated_lab_cities))
''')),
    lab_step(3, 'Transform to UTM 31N and RD New', s('''
lab_transformed = []
for row in validated_lab_cities:
    utm_row = crs_utils.transform_record(row, transformer_utm, x_key='utm_x', y_key='utm_y')
    rd_row = crs_utils.transform_record(row, transformer_rd, x_key='rd_x', y_key='rd_y')
    lab_transformed.append({**utm_row, 'rd_x': rd_row['rd_x'], 'rd_y': rd_row['rd_y']})

pprint(lab_transformed)
''')),
    lab_step(4, 'Compute Amsterdam→Rotterdam distances', s('''
lab_lookup = {row['city']: row for row in lab_transformed}
ams_lab = lab_lookup['Amsterdam']
rot_lab = lab_lookup['Rotterdam']
_, _, geodesic_m = geod.inv(ams_lab['lon'], ams_lab['lat'], rot_lab['lon'], rot_lab['lat'])
projected_m = math.dist((ams_lab['utm_x'], ams_lab['utm_y']), (rot_lab['utm_x'], rot_lab['utm_y']))

print('Geod.inv km :', round(geodesic_m / 1000, 3))
print('UTM km      :', round(projected_m / 1000, 3))
''')),
    lab_step(5, 'Create a 50 km Amsterdam buffer in UTM 31N', s('''
ams_lab_point = Point(ams_lab['utm_x'], ams_lab['utm_y'])
ams_lab_buffer = ams_lab_point.buffer(50_000)
print('Buffer area km²:', round(ams_lab_buffer.area / 1_000_000, 2))
''')),
    lab_step(6, 'Check which cities fall within the buffer', s('''
within_results = []
for row in lab_transformed:
    if row['city'] == 'Amsterdam':
        continue
    point = Point(row['utm_x'], row['utm_y'])
    within_results.append({'city': row['city'], 'within_50km': point.within(ams_lab_buffer)})

pprint(within_results)
''')),
    lab_step(7, 'Export comparison results to GeoJSON', s('''
lab_geojson_features = []
for row in lab_transformed:
    point = Point(row['utm_x'], row['utm_y'])
    feature = {
        'type': 'Feature',
        'properties': {
            'city': row['city'],
            'lon': row['lon'],
            'lat': row['lat'],
            'utm_x': row['utm_x'],
            'utm_y': row['utm_y'],
            'rd_x': row['rd_x'],
            'rd_y': row['rd_y'],
        },
        'geometry': mapping(point),
    }
    lab_geojson_features.append(feature)

lab_geojson_path = OUTPUT_DIR / 'lab_netherlands_cities_utm31n.geojson'
lab_geojson_path.write_text(
    json.dumps({'type': 'FeatureCollection', 'features': lab_geojson_features}, indent=2),
    encoding='utf-8',
)
print('Exported lab GeoJSON:', lab_geojson_path)
''')),
]

extension = md(s('''
### 🚀 Extension Ideas

- Compare UTM 31N with Web Mercator (EPSG:3857) to see distortion more clearly
- Add an RD New polygon study area and test `intersects()` with city buffers
- Export the same cities to a PostGIS-ready CSV with `srid` metadata
'''))

summary_topics = [
    ('WGS84 datum', 'Longitude, latitude, and ellipsoidal thinking for global storage'),
    ('geographic CRS', 'Angular coordinates, axis metadata, and degree units'),
    ('projected CRS', 'Planar x/y coordinates in metres for local measurement'),
    ('PyProj CRS', '`CRS.from_epsg()`, axis info, units, WKT export'),
    ('Transformer', '`Transformer.from_crs(..., always_xy=True)` for safe reprojection'),
    ('Geod.inv', 'Ellipsoidal distance measurement in metres and kilometres'),
    ('Shapely geometry', 'Point, LineString, Polygon creation plus length and area'),
    ('topology predicates', '`contains`, `within`, `intersects`, `touches`, `relate`'),
    ('crs_utils module', 'Reusable validation, transform, and bounding-box helpers'),
    ('file export', 'Portable WKT, GeoJSON, and CSV round-tripping'),
]
summary_rows = '\n'.join(f'| {topic} | {concepts} |' for topic, concepts in summary_topics)
preview_topics = [
    ('GeoPandas GeoDataFrame', 'Create spatial tables with geometry columns and CRS metadata'),
    ('read_file / to_file', 'Load and export vector data with GeoPandas and Fiona'),
    ('Shapely advanced ops', 'Buffer, overlay, dissolve, and union workflows'),
    ('spatial joins', 'Match features by location instead of just attribute keys'),
    ('Rasterio basics', 'Open raster grids and inspect bands, transforms, and metadata'),
]
preview_rows = '\n'.join(f'| {topic} | {detail} |' for topic, detail in preview_topics)
reading_rows = '\n'.join([
    '| [PyProj docs](https://pyproj4.github.io/pyproj/stable/) | CRS metadata, transformers, and geodesic tools |',
    '| [Shapely docs](https://shapely.readthedocs.io/) | Geometry creation, predicates, and measurements |',
    '| [EPSG registry](https://epsg.io/) | Look up CRS definitions and metadata by code |',
    '| [Understanding map projections](https://www.axismaps.com/guide/map-projections) | Intuition for distortion and projection choices |',
    '| [GeoJSON spec](https://geojson.org/) | Geometry and feature structure for interchange |',
    '| [Real Python coordinate transforms](https://realpython.com/python-geocoding/) | Broader context for coordinates and geocoding workflows |',
])

final_summary = md(s(f'''
---
## ✅ Week 4 Summary

| Topic | Key concepts mastered |
|-------|-----------------------|
{summary_rows}

---

### ☑️ Self-assessment checklist

- [ ] Explain the difference between geographic and projected CRS without notes
- [ ] Create a `pyproj.CRS` from an EPSG code and read its name and unit
- [ ] Transform a WGS84 lon/lat pair to UTM 31N using `always_xy=True`
- [ ] Compute a geodesic distance with `pyproj.Geod.inv` in kilometres
- [ ] Create a Shapely Point, buffer it by 50 km in UTM, and read the area
- [ ] Test `polygon.contains(point)` for two different pairs
- [ ] Import and use a function from your local `crs_utils.py`
- [ ] Save a Shapely geometry to GeoJSON and reload it with `shape()`

---

## 📚 Week 5 Preview

| Topic | What you will learn |
|-------|---------------------|
{preview_rows}

---

## 📖 Further Reading

| Resource | Why |
|----------|-----|
{reading_rows}

---

*Geospatial Python Mastery — Week 4 of 10*
*For educational use. Please keep feedback to help improve future iterations.*
'''))

C = [week_title, learning_objectives, environment, imports, setup_dirs]
for idx, section in enumerate(sections, start=1):
    C.append(section_md(idx, section['title'], section['intro'], section['subtopic'], section['detail']))
    C.append(lesson_code(section['code1_label'], section['code1_title'], section['code1_body']))
    C.append(lesson_code(section['code2_label'], section['code2_title'], section['code2_body']))
    C.append(exercise_md(idx, section['exercise_title'], section['exercise_task'], section['exercise_steps'], section['exercise_hint']))
    C.append(exercise_stub(idx, section['exercise_comments']))
    C.append(solution_code(idx, section['solution_body']))

C.append(lab_intro)
C.extend(lab_steps)
C.append(extension)
C.append(final_summary)

notebook = {
    'cells': C,
    'metadata': metadata,
    'nbformat': 4,
    'nbformat_minor': 5,
}

OUT.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(f'Wrote {OUT} with {len(C)} cells')
