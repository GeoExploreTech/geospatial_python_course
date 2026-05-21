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
OUT = REPO_ROOT / 'notebooks' / 'geospatial_python_course' / 'week_03_json_file_processing.ipynb'

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
# 🌍 Week 3 — JSON and File Processing
### Geospatial Python Mastery | Module B: Data Structures and File I/O

---

|  |  |
|---|---|
| **Course** | Geospatial Python Mastery |
| **Week** | 3 of 10 |
| **Theme** | JSON and File Processing for Geospatial Data |
| **Duration** | ~4 contact hours + 4 hours self-study |
| **Practice Outcome** | Mini-Lab: Build a robust GeoJSON validator and batch processor |
| **Next week** | Geospatial foundations — coordinates, projections, CRS theory |

---

> 🗺️ **Why this week matters**
> Geospatial analysis depends on reliable file handling. GeoJSON, CSV, logs, and test files
> are the plumbing behind every later workflow in GeoPandas, PostGIS, and CityJSON.
> This week turns raw text files into structured Python objects, validates coordinates and
> geometry types, and packages the logic into reusable functions you can trust.

---

## 📋 Table of Contents

| Section | Topic |
|---------|-------|
| [1 — Environment Setup](#section-1) | Auto-install, imports, data dirs |
| [2 — pathlib Basics](#section-2) | Path objects, mkdir, glob, read_text/write_text |
| [3 — Working with CSV Files](#section-3) | DictReader, DictWriter, coordinate validation |
| [4 — JSON and GeoJSON](#section-4) | loads, dumps, FeatureCollection structure |
| [5 — GeoJSON Validation](#section-5) | Coordinate checks and geometry rules |
| [6 — Building a Reusable Module](#section-6) | Write and import `geo_file_tools.py` |
| [7 — Error Handling](#section-7) | Custom exceptions and resilient pipelines |
| [8 — Logging](#section-8) | FileHandler, levels, audit trail |
| [9 — Unit Testing](#section-9) | `unittest.TestCase`, setUp, assertRaises |
| [10 — Batch Processing](#section-10) | Process many files and save a summary |

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
    'Use Python\'s `pathlib` module to manage file paths portably across operating systems',
    'Read and write **CSV** files with the `csv` module (`DictReader`, `DictWriter`)',
    'Parse and generate **JSON** and **GeoJSON** programmatically with the `json` module',
    'Validate coordinate ranges and geometry types in GeoJSON `FeatureCollection` objects',
    'Build a reusable `geo_file_tools.py` module with `load_features`, `extract_valid_points`, and `save_geojson`',
    'Handle file I/O errors with `try/except` and custom exceptions',
    'Add structured **logging** to a file-processing pipeline',
    'Write `unittest` tests for file utility functions',
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
print("  Geospatial Python Mastery — Week 3 Environment Check")
print("=" * 60)
print(f"  Environment : {'Google Colab' if IN_COLAB else 'Local Jupyter'}")
print(f"  Python      : {sys.version.split()[0]}")
print(f"  OS          : {OS_NAME}")

REQUIRED = [
    ("pathlib",  "",          ""),
    ("csv",      "",          ""),
    ("json",     "",          ""),
    ("logging",  "",          ""),
    ("unittest", "",          ""),
    ("uuid",     "",          ""),
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

print("\\n✅ Environment check complete — ready for Week 3!")
'''))

imports = lesson_code('0.1', 'Import core libraries used this week', s('''
import csv
import json
import logging
import sys
import unittest
import uuid
from importlib import reload
from pathlib import Path
from pprint import pprint

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
WEEK_DIR = COURSE_DIR / 'data' / 'week_03'
INPUT_DIR = WEEK_DIR / 'input'
OUTPUT_DIR = WEEK_DIR / 'output'
LOG_DIR = COURSE_DIR / 'logs'
MODULE_DIR = COURSE_DIR / 'local_modules'
TEST_DIR = COURSE_DIR / 'tests'

for path in [WEEK_DIR, INPUT_DIR, OUTPUT_DIR, LOG_DIR, MODULE_DIR, TEST_DIR]:
    path.mkdir(parents=True, exist_ok=True)

print('Project root :', PROJECT_ROOT)
print('Course dir   :', COURSE_DIR)
print('Week data    :', WEEK_DIR)
print('Output dir   :', OUTPUT_DIR)
print('Log file dir :', LOG_DIR)
'''))

sections = [
    {
        'title': 'Environment Setup',
        'intro': 'Start with a stable workspace: known folders, predictable filenames, and reproducible sample data.',
        'subtopic': 'Project folders and starter files',
        'detail': 'Everything this week lives under `data/week_03/`, while reusable modules and unit tests stay beside the notebook for easy imports.',
        'code1_label': '1.1',
        'code1_title': 'Inspect the workspace layout',
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

print('\\nCurrent contents of the input directory:')
print(list(INPUT_DIR.iterdir()))
'''),
        'code2_label': '1.2',
        'code2_title': 'Seed example CSV and GeoJSON files',
        'code2_body': s('''
seed_rows = [
    {'city': 'Amsterdam', 'lon': '4.9041', 'lat': '52.3676', 'country': 'NL'},
    {'city': 'Rotterdam', 'lon': '4.4777', 'lat': '51.9244', 'country': 'NL'},
    {'city': 'BadTown', 'lon': '190.0000', 'lat': '95.0000', 'country': '??'},
]

sample_csv_path = INPUT_DIR / 'city_points.csv'
with sample_csv_path.open('w', newline='', encoding='utf-8') as fh:
    writer = csv.DictWriter(fh, fieldnames=['city', 'lon', 'lat', 'country'])
    writer.writeheader()
    writer.writerows(seed_rows)

starter_geojson = {
    'type': 'FeatureCollection',
    'features': [
        {
            'type': 'Feature',
            'properties': {'city': 'Amsterdam', 'country': 'NL'},
            'geometry': {'type': 'Point', 'coordinates': [4.9041, 52.3676]},
        },
        {
            'type': 'Feature',
            'properties': {'city': 'Rotterdam', 'country': 'NL'},
            'geometry': {'type': 'Point', 'coordinates': [4.4777, 51.9244]},
        },
        {
            'type': 'Feature',
            'properties': {'city': 'BadTown', 'country': '??'},
            'geometry': {'type': 'Point', 'coordinates': [190.0, 95.0]},
        },
    ],
}

starter_geojson_path = INPUT_DIR / 'starter_points.geojson'
starter_geojson_path.write_text(json.dumps(starter_geojson, indent=2), encoding='utf-8')
run_manifest = {
    'week': 3,
    'run_id': uuid.uuid4().hex[:8],
    'input_files': [sample_csv_path.name, starter_geojson_path.name],
}
(INPUT_DIR / 'run_manifest.json').write_text(json.dumps(run_manifest, indent=2), encoding='utf-8')

print('Wrote:', sample_csv_path.name, starter_geojson_path.name, 'and run_manifest.json')
'''),
        'exercise_title': 'Create a scratch workspace',
        'exercise_task': 'Use `pathlib` to create a scratch folder inside `INPUT_DIR`, then write a JSON manifest describing the files you want to process.',
        'exercise_steps': [
            'Create `INPUT_DIR / "scratch"` if it does not already exist.',
            'Write a `scratch_manifest.json` file with a short description and a list of filenames.',
        ],
        'exercise_hint': "# Hint\nscratch_dir = INPUT_DIR / 'scratch'",
        'exercise_comments': ['Create the directory.', 'Write the manifest JSON file.'],
        'solution_body': s('''
scratch_dir = INPUT_DIR / 'scratch'
scratch_dir.mkdir(parents=True, exist_ok=True)

scratch_manifest = {
    'description': 'Temporary staging area for Week 3 file practice.',
    'files': ['city_points.csv', 'starter_points.geojson'],
}
manifest_path = scratch_dir / 'scratch_manifest.json'
manifest_path.write_text(json.dumps(scratch_manifest, indent=2), encoding='utf-8')

print('Scratch manifest saved to:', manifest_path)
print(manifest_path.read_text(encoding='utf-8'))
'''),
    },
    {
        'title': 'pathlib Basics',
        'intro': '`Path` objects replace fragile string concatenation and make your scripts portable.',
        'subtopic': 'Joining paths, checking files, and discovering data',
        'detail': 'With `pathlib` you can create directories, iterate over files, and read or write text without worrying about slash direction.',
        'code1_label': '2.1',
        'code1_title': 'Inspect Path object behaviour',
        'code1_body': s('''
print('Sample CSV name   :', sample_csv_path.name)
print('Sample CSV suffix :', sample_csv_path.suffix)
print('Sample CSV parent :', sample_csv_path.parent)
print('Resolved path     :', sample_csv_path.resolve())

archive_path = OUTPUT_DIR / 'archive' / 'city_points_backup.csv'
archive_path.parent.mkdir(parents=True, exist_ok=True)
print('Joined path       :', archive_path)
'''),
        'code2_label': '2.2',
        'code2_title': 'Use glob, write_text, and read_text',
        'code2_body': s('''
notes_path = OUTPUT_DIR / 'week3_notes.txt'
notes_path.write_text(
    'Week 3 focuses on pathlib, CSV, JSON, GeoJSON, logging, and unittest.\\n',
    encoding='utf-8',
)

print('Files in input folder:')
for path in sorted(INPUT_DIR.glob('*')):
    print(' -', path.name)

print('\\nSaved note contents:')
print(notes_path.read_text(encoding='utf-8'))
'''),
        'exercise_title': 'Preview every GeoJSON file',
        'exercise_task': 'Discover all `.geojson` files in `INPUT_DIR` and print the first 120 characters from each file.',
        'exercise_steps': [
            'Use `INPUT_DIR.glob("*.geojson")` to get candidate files.',
            'Loop over the files and print a short preview from `read_text()`.',
        ],
        'exercise_hint': '# Hint\nfor path in INPUT_DIR.glob("*.geojson"):\n    ...',
        'exercise_comments': ['Find all GeoJSON files.', 'Read and preview each file.'],
        'solution_body': s('''
for path in sorted(INPUT_DIR.glob('*.geojson')):
    preview = path.read_text(encoding='utf-8')[:120]
    print(f'\\n{path.name}')
    print(preview + '...')
'''),
    },
    {
        'title': 'Working with CSV Files',
        'intro': 'CSV files are common for tabular location data because they are simple, transparent, and easy to exchange.',
        'subtopic': 'Reading rows into dictionaries',
        'detail': 'Use `csv.DictReader` when your file has headers. It returns each row as a dict, which makes later validation and conversion much easier.',
        'code1_label': '3.1',
        'code1_title': 'Read CSV rows and coerce lon/lat values',
        'code1_body': s('''
def coordinate_is_valid(lon: float, lat: float) -> bool:
    return -180 <= lon <= 180 and -90 <= lat <= 90

csv_records = []
with sample_csv_path.open('r', newline='', encoding='utf-8') as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        lon = float(row['lon'])
        lat = float(row['lat'])
        record = {
            'city': row['city'],
            'country': row['country'],
            'lon': lon,
            'lat': lat,
            'is_valid': coordinate_is_valid(lon, lat),
        }
        csv_records.append(record)

pprint(csv_records)
'''),
        'code2_label': '3.2',
        'code2_title': 'Write cleaned and rejected CSV files',
        'code2_body': s('''
clean_csv_path = OUTPUT_DIR / 'city_points_clean.csv'
rejected_csv_path = OUTPUT_DIR / 'city_points_rejected.csv'
fieldnames = ['city', 'country', 'lon', 'lat', 'is_valid']

with clean_csv_path.open('w', newline='', encoding='utf-8') as clean_fh, rejected_csv_path.open('w', newline='', encoding='utf-8') as bad_fh:
    clean_writer = csv.DictWriter(clean_fh, fieldnames=fieldnames)
    bad_writer = csv.DictWriter(bad_fh, fieldnames=fieldnames)
    clean_writer.writeheader()
    bad_writer.writeheader()
    for record in csv_records:
        target = clean_writer if record['is_valid'] else bad_writer
        target.writerow(record)

print('Clean CSV   :', clean_csv_path)
print('Rejected CSV:', rejected_csv_path)
'''),
        'exercise_title': 'Build a validated CSV export',
        'exercise_task': 'Read `city_points.csv`, convert longitude and latitude strings to floats, and write a new CSV containing only valid rows.',
        'exercise_steps': [
            'Use `csv.DictReader` to iterate over rows.',
            'Convert `lon` and `lat` to floats and keep only valid coordinate pairs.',
        ],
        'exercise_hint': '# Hint\nvalid_rows = []\nwith sample_csv_path.open(...) as fh:\n    ...',
        'exercise_comments': ['Read rows from the CSV file.', 'Write only valid rows to a new CSV file.'],
        'solution_body': s('''
valid_rows = []
with sample_csv_path.open('r', newline='', encoding='utf-8') as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        lon = float(row['lon'])
        lat = float(row['lat'])
        if coordinate_is_valid(lon, lat):
            valid_rows.append({'city': row['city'], 'country': row['country'], 'lon': lon, 'lat': lat})

validated_csv_path = OUTPUT_DIR / 'validated_points.csv'
with validated_csv_path.open('w', newline='', encoding='utf-8') as fh:
    writer = csv.DictWriter(fh, fieldnames=['city', 'country', 'lon', 'lat'])
    writer.writeheader()
    writer.writerows(valid_rows)

print('Validated rows:', len(valid_rows))
print('Saved to       :', validated_csv_path)
'''),
    },
    {
        'title': 'JSON and GeoJSON',
        'intro': 'JSON gives structure to nested data, while GeoJSON adds a standard way to describe geometry and properties.',
        'subtopic': 'Parsing JSON text and inspecting a FeatureCollection',
        'detail': 'A GeoJSON FeatureCollection is just JSON with agreed keys like `type`, `features`, `properties`, and `geometry`.',
        'code1_label': '4.1',
        'code1_title': 'Load JSON text into Python dictionaries',
        'code1_body': s('''
raw_geojson_text = starter_geojson_path.read_text(encoding='utf-8')
parsed_geojson = json.loads(raw_geojson_text)

print('Top-level type :', parsed_geojson['type'])
print('Feature count  :', len(parsed_geojson['features']))
print('\\nFirst feature pretty-print:')
print(json.dumps(parsed_geojson['features'][0], indent=2))
'''),
        'code2_label': '4.2',
        'code2_title': 'Generate GeoJSON programmatically from CSV rows',
        'code2_body': s('''
geojson_from_csv = {
    'type': 'FeatureCollection',
    'features': [
        {
            'type': 'Feature',
            'properties': {'city': row['city'], 'country': row['country']},
            'geometry': {'type': 'Point', 'coordinates': [row['lon'], row['lat']]},
        }
        for row in csv_records
        if row['is_valid']
    ],
}

clean_geojson_path = OUTPUT_DIR / 'clean_points.geojson'
clean_geojson_path.write_text(json.dumps(geojson_from_csv, indent=2), encoding='utf-8')
print('Saved clean GeoJSON to:', clean_geojson_path)
'''),
        'exercise_title': 'Create a one-feature GeoJSON object',
        'exercise_task': 'Turn a single city dictionary into a valid GeoJSON `FeatureCollection` and pretty-print it.',
        'exercise_steps': [
            'Start from a small Python dict containing `city`, `country`, `lon`, and `lat`.',
            'Wrap the resulting feature inside a `FeatureCollection` with one entry.',
        ],
        'exercise_hint': '# Hint\nfeature = {"type": "Feature", ...}',
        'exercise_comments': ['Create one feature dict.', 'Wrap it in a FeatureCollection and print it.'],
        'solution_body': s('''
city_record = {'city': 'Utrecht', 'country': 'NL', 'lon': 5.1214, 'lat': 52.0907}
feature = {
    'type': 'Feature',
    'properties': {'city': city_record['city'], 'country': city_record['country']},
    'geometry': {'type': 'Point', 'coordinates': [city_record['lon'], city_record['lat']]},
}
one_feature_collection = {'type': 'FeatureCollection', 'features': [feature]}

print(json.dumps(one_feature_collection, indent=2))
'''),
    },
    {
        'title': 'GeoJSON Validation',
        'intro': 'Validation protects downstream analysis from subtle geometry errors and impossible coordinate values.',
        'subtopic': 'Checking geometry type and coordinate ranges',
        'detail': 'For this week we focus on GeoJSON `Point` features, require a `Feature` wrapper, and enforce global WGS84 bounds.',
        'code1_label': '5.1',
        'code1_title': 'Create a reusable feature validator',
        'code1_body': s('''
class GeoJSONValidationError(Exception):
    """Raised when a GeoJSON feature breaks an expected rule."""

ALLOWED_GEOMETRY_TYPES = {'Point'}


def validate_feature(feature: dict) -> None:
    if feature.get('type') != 'Feature':
        raise GeoJSONValidationError('Feature must declare type="Feature".')

    geometry = feature.get('geometry') or {}
    geometry_type = geometry.get('type')
    if geometry_type not in ALLOWED_GEOMETRY_TYPES:
        raise GeoJSONValidationError(f'Unsupported geometry type: {geometry_type}')

    coordinates = geometry.get('coordinates')
    if not isinstance(coordinates, (list, tuple)) or len(coordinates) != 2:
        raise GeoJSONValidationError('Point coordinates must be a two-item list.')

    lon, lat = coordinates
    if not coordinate_is_valid(float(lon), float(lat)):
        raise GeoJSONValidationError(f'Coordinate out of range: {(lon, lat)}')
'''),
        'code2_label': '5.2',
        'code2_title': 'Validate a whole FeatureCollection',
        'code2_body': s('''
def split_valid_and_invalid_features(collection: dict):
    valid_features = []
    invalid_features = []
    for feature in collection.get('features', []):
        try:
            validate_feature(feature)
            valid_features.append(feature)
        except GeoJSONValidationError as exc:
            invalid_features.append({'feature': feature, 'error': str(exc)})
    return valid_features, invalid_features

valid_features, invalid_details = split_valid_and_invalid_features(parsed_geojson)
print('Valid features  :', len(valid_features))
print('Invalid features:', len(invalid_details))
pprint(invalid_details)
'''),
        'exercise_title': 'Reject bad GeoJSON features',
        'exercise_task': 'Run `validate_feature()` against one good feature and one bad feature, then confirm that the bad one raises your custom exception.',
        'exercise_steps': [
            'Create a valid point feature and an invalid point feature.',
            'Use `try/except` to show the error message for the invalid one.',
        ],
        'exercise_hint': '# Hint\ntry:\n    validate_feature(bad_feature)\nexcept GeoJSONValidationError as exc:\n    ...',
        'exercise_comments': ['Validate a good feature.', 'Catch the exception from a bad feature.'],
        'solution_body': s('''
good_feature = {
    'type': 'Feature',
    'properties': {'city': 'Leiden'},
    'geometry': {'type': 'Point', 'coordinates': [4.4970, 52.1601]},
}
bad_feature = {
    'type': 'Feature',
    'properties': {'city': 'Broken'},
    'geometry': {'type': 'Point', 'coordinates': [222.0, 91.0]},
}

validate_feature(good_feature)
print('Good feature passed validation.')

try:
    validate_feature(bad_feature)
except GeoJSONValidationError as exc:
    print('Bad feature failed as expected:', exc)
'''),
    },
    {
        'title': 'Building a Reusable Module',
        'intro': 'Notebooks are great for learning, but reusable modules keep logic tidy, testable, and importable.',
        'subtopic': 'Writing `geo_file_tools.py` from notebook code',
        'detail': 'We will export a small utility module that hides file parsing details behind clean function names.',
        'code1_label': '6.1',
        'code1_title': 'Write the geo_file_tools.py module',
        'code1_body': s('''
geo_file_tools_path = MODULE_DIR / 'geo_file_tools.py'
geo_file_tools_source = """
import json
from pathlib import Path


class GeoFileToolsError(Exception):
    pass


class GeoJSONValidationError(GeoFileToolsError):
    pass


ALLOWED_GEOMETRY_TYPES = {'Point'}


def _validate_feature(feature: dict) -> None:
    if feature.get('type') != 'Feature':
        raise GeoJSONValidationError('Expected a GeoJSON Feature object.')
    geometry = feature.get('geometry') or {}
    if geometry.get('type') not in ALLOWED_GEOMETRY_TYPES:
        raise GeoJSONValidationError('Only Point geometry is supported in Week 3.')
    coords = geometry.get('coordinates')
    if not isinstance(coords, (list, tuple)) or len(coords) != 2:
        raise GeoJSONValidationError('Point coordinates must contain lon and lat.')
    lon, lat = coords
    if not (-180 <= float(lon) <= 180 and -90 <= float(lat) <= 90):
        raise GeoJSONValidationError(f'Coordinates out of range: {(lon, lat)}')


def load_features(path):
    path = Path(path)
    payload = json.loads(path.read_text(encoding='utf-8'))
    return payload.get('features', [])


def extract_valid_points(features):
    valid = []
    for feature in features:
        _validate_feature(feature)
        valid.append(feature)
    return valid


def save_geojson(features, path):
    path = Path(path)
    collection = {'type': 'FeatureCollection', 'features': list(features)}
    path.write_text(json.dumps(collection, indent=2), encoding='utf-8')
    return path
"""
geo_file_tools_path.write_text(geo_file_tools_source.strip() + '\\n', encoding='utf-8')
print('Module written to:', geo_file_tools_path)
'''),
        'code2_label': '6.2',
        'code2_title': 'Import and use the module functions',
        'code2_body': s('''
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import geo_file_tools
geo_file_tools = reload(geo_file_tools)

module_loaded_features = geo_file_tools.load_features(clean_geojson_path)
module_valid_points = geo_file_tools.extract_valid_points(module_loaded_features)
module_output_path = OUTPUT_DIR / 'module_valid_points.geojson'
geo_file_tools.save_geojson(module_valid_points, module_output_path)

print('Features loaded :', len(module_loaded_features))
print('Valid points    :', len(module_valid_points))
print('Saved output to :', module_output_path)
'''),
        'exercise_title': 'Reuse your local module',
        'exercise_task': 'Import `geo_file_tools.py`, load features from `clean_points.geojson`, and save only the first two features to a new file.',
        'exercise_steps': [
            'Import the module from `MODULE_DIR`.',
            'Slice the loaded features list and pass it to `save_geojson()`.',
        ],
        'exercise_hint': '# Hint\nsubset = features[:2]\ngeo_file_tools.save_geojson(subset, OUTPUT_DIR / "subset.geojson")',
        'exercise_comments': ['Import the module and load the features.', 'Save a subset to a new GeoJSON file.'],
        'solution_body': s('''
subset_features = module_loaded_features[:2]
subset_output_path = OUTPUT_DIR / 'subset_points.geojson'
geo_file_tools.save_geojson(subset_features, subset_output_path)

print('Subset feature count:', len(subset_features))
print('Subset path         :', subset_output_path)
'''),
    },
    {
        'title': 'Error Handling',
        'intro': 'Broken paths and malformed JSON are normal in real data pipelines, so your code should fail clearly instead of mysteriously.',
        'subtopic': 'Custom exceptions for missing files and bad JSON',
        'detail': 'A small exception hierarchy gives you better control over how to stop, retry, or log a failure.',
        'code1_label': '7.1',
        'code1_title': 'Wrap file problems in named exceptions',
        'code1_body': s('''
class GeoFilePipelineError(Exception):
    pass


class MissingInputFileError(GeoFilePipelineError):
    pass


class InvalidJSONError(GeoFilePipelineError):
    pass


def read_json_file(path: Path) -> dict:
    if not path.exists():
        raise MissingInputFileError(f'Missing input file: {path.name}')
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise InvalidJSONError(f'Bad JSON in {path.name}: {exc.msg}') from exc
'''),
        'code2_label': '7.2',
        'code2_title': 'Handle failures without stopping the whole pipeline',
        'code2_body': s('''
broken_json_path = INPUT_DIR / 'broken.geojson'
broken_json_path.write_text('{"type": "FeatureCollection", bad json}', encoding='utf-8')

for candidate in [starter_geojson_path, broken_json_path, INPUT_DIR / 'missing.geojson']:
    try:
        payload = read_json_file(candidate)
        print(f'Loaded {candidate.name}: {payload.get("type", "unknown")}')
    except GeoFilePipelineError as exc:
        print(f'Handled error for {candidate.name}: {exc}')
'''),
        'exercise_title': 'Catch JSON failures gracefully',
        'exercise_task': 'Attempt to read a missing file and a malformed JSON file, then print clear messages instead of crashing.',
        'exercise_steps': [
            'Call `read_json_file()` inside a `try/except` block.',
            'Catch `GeoFilePipelineError` and print the exception text.',
        ],
        'exercise_hint': '# Hint\ntry:\n    read_json_file(path)\nexcept GeoFilePipelineError as exc:\n    print(exc)',
        'exercise_comments': ['Try to read a file.', 'Catch and print the error.'],
        'solution_body': s('''
for path in [INPUT_DIR / 'missing_again.geojson', broken_json_path]:
    try:
        read_json_file(path)
    except GeoFilePipelineError as exc:
        print('Graceful failure:', exc)
'''),
    },
    {
        'title': 'Logging',
        'intro': 'Logs create a timeline of what happened, which file was processed, and which records failed validation.',
        'subtopic': 'Configuring console and file logging',
        'detail': 'Use a `FileHandler` to persist diagnostics and a formatter to make each line easy to scan later.',
        'code1_label': '8.1',
        'code1_title': 'Configure a logger for Week 3',
        'code1_body': s('''
log_path = LOG_DIR / 'week3.log'
logger = logging.getLogger('gpm.week3')
logger.setLevel(logging.DEBUG)
logger.handlers.clear()

formatter = logging.Formatter('%(levelname)s | %(asctime)s | %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)

file_handler = logging.FileHandler(log_path, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)
logger.info('Week 3 logger initialised.')
print('Log file:', log_path)
'''),
        'code2_label': '8.2',
        'code2_title': 'Log a validation pass over the starter GeoJSON',
        'code2_body': s('''
def log_validation_run(features, logger):
    summary = {'valid': 0, 'invalid': 0}
    for feature in features:
        city_name = feature.get('properties', {}).get('city', 'unknown')
        try:
            validate_feature(feature)
            summary['valid'] += 1
            logger.debug('Accepted feature for %s', city_name)
        except GeoJSONValidationError as exc:
            summary['invalid'] += 1
            logger.warning('Rejected feature for %s: %s', city_name, exc)
    logger.info('Validation summary: %s', summary)
    return summary

logged_summary = log_validation_run(parsed_geojson['features'], logger)
print(logged_summary)
'''),
        'exercise_title': 'Add warnings for invalid features',
        'exercise_task': 'Loop through the starter features and write a warning to `logs/week3.log` whenever a feature is invalid.',
        'exercise_steps': [
            'Use `validate_feature()` inside a `try/except` block.',
            'Call `logger.warning()` with the city name and error message.',
        ],
        'exercise_hint': '# Hint\nlogger.warning("Rejected %s: %s", city_name, exc)',
        'exercise_comments': ['Loop over the features.', 'Log a warning when validation fails.'],
        'solution_body': s('''
for feature in parsed_geojson['features']:
    city_name = feature.get('properties', {}).get('city', 'unknown')
    try:
        validate_feature(feature)
    except GeoJSONValidationError as exc:
        logger.warning('Exercise warning for %s: %s', city_name, exc)

print('Recent log lines:')
print('\\n'.join(log_path.read_text(encoding='utf-8').splitlines()[-4:]))
'''),
    },
    {
        'title': 'Unit Testing',
        'intro': 'Automated tests give you confidence that utility functions behave the same tomorrow as they do today.',
        'subtopic': 'Writing a `unittest.TestCase` for file helpers',
        'detail': 'We test happy paths and failure paths: successful loads, valid point extraction, and rejection of bad coordinates.',
        'code1_label': '9.1',
        'code1_title': 'Write a test module for geo_file_tools.py',
        'code1_body': s('''
test_file_path = TEST_DIR / 'test_geo_file_tools.py'
test_file_source = """
import sys
import unittest
from pathlib import Path

COURSE_DIR = Path(__file__).resolve().parents[1]
MODULE_DIR = COURSE_DIR / 'local_modules'
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import geo_file_tools


class TestGeoFileTools(unittest.TestCase):
    def setUp(self):
        self.good_feature = {
            'type': 'Feature',
            'properties': {'city': 'Delft'},
            'geometry': {'type': 'Point', 'coordinates': [4.3571, 52.0116]},
        }
        self.bad_feature = {
            'type': 'Feature',
            'properties': {'city': 'Broken'},
            'geometry': {'type': 'Point', 'coordinates': [999.0, 999.0]},
        }

    def test_extract_valid_points_returns_input_feature(self):
        result = geo_file_tools.extract_valid_points([self.good_feature])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['properties']['city'], 'Delft')

    def test_extract_valid_points_raises_on_bad_coords(self):
        with self.assertRaises(geo_file_tools.GeoJSONValidationError):
            geo_file_tools.extract_valid_points([self.bad_feature])

    def test_save_geojson_writes_feature_collection(self):
        out_dir = COURSE_DIR / 'tests' / '_artifacts'
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / 'test_points.geojson'
        geo_file_tools.save_geojson([self.good_feature], out_path)
        self.assertTrue(out_path.exists())
        self.assertIn('FeatureCollection', out_path.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
"""
test_file_path.write_text(test_file_source.strip() + '\\n', encoding='utf-8')
print('Wrote test file:', test_file_path)
'''),
        'code2_label': '9.2',
        'code2_title': 'Run the unittest suite from the notebook',
        'code2_body': s('''
suite = unittest.defaultTestLoader.discover(str(TEST_DIR), pattern='test_geo_file_tools.py')
runner = unittest.TextTestRunner(verbosity=2)
test_result = runner.run(suite)
print('Successful:', test_result.wasSuccessful())
'''),
        'exercise_title': 'Write an assertRaises test',
        'exercise_task': 'Create a tiny `unittest.TestCase` that confirms `validate_feature()` raises `GeoJSONValidationError` for invalid coordinates.',
        'exercise_steps': [
            'Subclass `unittest.TestCase`.',
            'Write one method that uses `self.assertRaises(...)`.',
        ],
        'exercise_hint': '# Hint\nwith self.assertRaises(GeoJSONValidationError):\n    validate_feature(bad_feature)',
        'exercise_comments': ['Define a small test case.', 'Run the suite and inspect the result.'],
        'solution_body': s('''
class InlineValidationTests(unittest.TestCase):
    def test_invalid_coordinates_raise(self):
        with self.assertRaises(GeoJSONValidationError):
            validate_feature({
                'type': 'Feature',
                'properties': {'city': 'Nowhere'},
                'geometry': {'type': 'Point', 'coordinates': [181.0, 45.0]},
            })

inline_suite = unittest.defaultTestLoader.loadTestsFromTestCase(InlineValidationTests)
unittest.TextTestRunner(verbosity=2).run(inline_suite)
'''),
    },
    {
        'title': 'Batch Processing',
        'intro': 'Real projects rarely stop at one file. Batch processing applies the same validation rules across a whole folder.',
        'subtopic': 'Summarising many input files',
        'detail': 'The core pattern is: discover files → validate each file → accumulate summary rows → write outputs.',
        'code1_label': '10.1',
        'code1_title': 'Process every GeoJSON file in the input folder',
        'code1_body': s('''
def batch_validate_geojson_files(input_dir: Path):
    summary_rows = []
    combined_valid_features = []

    for path in sorted(input_dir.glob('*.geojson')):
        try:
            payload = read_json_file(path)
            valid, invalid = split_valid_and_invalid_features(payload)
            summary_rows.append({
                'file_name': path.name,
                'valid_features': len(valid),
                'invalid_features': len(invalid),
            })
            combined_valid_features.extend(valid)
        except GeoFilePipelineError as exc:
            summary_rows.append({
                'file_name': path.name,
                'valid_features': 0,
                'invalid_features': 0,
            })
            logger.error('Batch read failure for %s: %s', path.name, exc)

    return summary_rows, combined_valid_features

batch_rows, combined_valid_features = batch_validate_geojson_files(INPUT_DIR)
pprint(batch_rows)
'''),
        'code2_label': '10.2',
        'code2_title': 'Write the batch summary CSV and combined GeoJSON',
        'code2_body': s('''
batch_summary_path = OUTPUT_DIR / 'batch_summary.csv'
with batch_summary_path.open('w', newline='', encoding='utf-8') as fh:
    writer = csv.DictWriter(fh, fieldnames=['file_name', 'valid_features', 'invalid_features'])
    writer.writeheader()
    writer.writerows(batch_rows)

combined_geojson_path = OUTPUT_DIR / 'combined_valid_points.geojson'
geo_file_tools.save_geojson(combined_valid_features, combined_geojson_path)

print('Batch summary CSV   :', batch_summary_path)
print('Combined valid file :', combined_geojson_path)
'''),
        'exercise_title': 'Report files that need attention',
        'exercise_task': 'Loop through the batch summary rows and print only the files where `invalid_features` is greater than zero.',
        'exercise_steps': [
            'Iterate over `batch_rows`.',
            'Check the `invalid_features` value and print matching rows.',
        ],
        'exercise_hint': '# Hint\nif row["invalid_features"] > 0:\n    print(row)',
        'exercise_comments': ['Loop over the summary rows.', 'Print rows that contain invalid features.'],
        'solution_body': s('''
for row in batch_rows:
    if row['invalid_features'] > 0:
        print('Needs attention:', row)
'''),
    },
]

lab_intro = md(s('''
---
## 🔬 Mini-Lab — GeoJSON QA Pipeline

**Scenario:** You have inherited a folder of GeoJSON point files from different colleagues. Some are clean, some contain impossible coordinates, and some mix good and bad data in the same file. Your job is to build a repeatable quality-assurance pipeline.

**Tasks:**
1. Create 3 sample input files (1 clean, 1 with bad coords, 1 mixed)
2. Run batch validation with logging
3. Count valid/invalid per file
4. Save `batch_summary.csv`
5. Build combined valid GeoJSON from all clean features
6. Write a quick unit test for the pipeline
'''))

lab_steps = [
    lab_step(1, 'Create three lab input files', s('''
lab_files = {
    'lab_clean.geojson': {
        'type': 'FeatureCollection',
        'features': [
            {'type': 'Feature', 'properties': {'city': 'Haarlem'}, 'geometry': {'type': 'Point', 'coordinates': [4.6462, 52.3874]}},
            {'type': 'Feature', 'properties': {'city': 'Leiden'}, 'geometry': {'type': 'Point', 'coordinates': [4.4970, 52.1601]}},
        ],
    },
    'lab_bad_coords.geojson': {
        'type': 'FeatureCollection',
        'features': [
            {'type': 'Feature', 'properties': {'city': 'BadCoord'}, 'geometry': {'type': 'Point', 'coordinates': [250.0, 95.0]}},
        ],
    },
    'lab_mixed.geojson': {
        'type': 'FeatureCollection',
        'features': [
            {'type': 'Feature', 'properties': {'city': 'Zwolle'}, 'geometry': {'type': 'Point', 'coordinates': [6.0944, 52.5168]}},
            {'type': 'Feature', 'properties': {'city': 'BrokenAgain'}, 'geometry': {'type': 'Point', 'coordinates': [-190.0, 12.0]}},
        ],
    },
}

for filename, payload in lab_files.items():
    path = INPUT_DIR / filename
    path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print('Created', path.name)
''')),
    lab_step(2, 'Run batch validation with logging', s('''
lab_logger = logging.getLogger('gpm.week3.lab')
lab_logger.setLevel(logging.DEBUG)
lab_logger.handlers.clear()
lab_file_handler = logging.FileHandler(log_path, encoding='utf-8')
lab_file_handler.setFormatter(formatter)
lab_logger.addHandler(lab_file_handler)
lab_logger.info('Mini-Lab batch validation started.')
''')),
    lab_step(3, 'Count valid and invalid features per file', s('''
lab_results = []
lab_combined_valid = []
for path in sorted(INPUT_DIR.glob('lab_*.geojson')):
    payload = read_json_file(path)
    valid, invalid = split_valid_and_invalid_features(payload)
    lab_results.append({
        'file_name': path.name,
        'valid_features': len(valid),
        'invalid_features': len(invalid),
    })
    lab_combined_valid.extend(valid)
    lab_logger.info('Mini-Lab processed %s -> valid=%s invalid=%s', path.name, len(valid), len(invalid))

pprint(lab_results)
''')),
    lab_step(4, 'Save batch_summary.csv', s('''
lab_summary_path = OUTPUT_DIR / 'lab_batch_summary.csv'
with lab_summary_path.open('w', newline='', encoding='utf-8') as fh:
    writer = csv.DictWriter(fh, fieldnames=['file_name', 'valid_features', 'invalid_features'])
    writer.writeheader()
    writer.writerows(lab_results)

print('Mini-Lab summary saved to:', lab_summary_path)
''')),
    lab_step(5, 'Build a combined valid GeoJSON file', s('''
lab_combined_path = OUTPUT_DIR / 'lab_combined_valid.geojson'
geo_file_tools.save_geojson(lab_combined_valid, lab_combined_path)

print('Combined valid feature count:', len(lab_combined_valid))
print('Combined file path          :', lab_combined_path)
''')),
    lab_step(6, 'Write a quick unit test for the pipeline', s('''
class BatchPipelineTests(unittest.TestCase):
    def test_lab_results_include_invalid_records(self):
        indexed = {row['file_name']: row for row in lab_results}
        self.assertGreater(indexed['lab_bad_coords.geojson']['invalid_features'], 0)
        self.assertEqual(indexed['lab_clean.geojson']['invalid_features'], 0)

unittest.TextTestRunner(verbosity=2).run(
    unittest.defaultTestLoader.loadTestsFromTestCase(BatchPipelineTests)
)
''')),
]

extension = md(s('''
### 🚀 Extension Ideas

- Add polygon and line support to `geo_file_tools.py`
- Include a UUID per output feature for traceability
- Turn the batch pipeline into a command-line script with `argparse`
'''))

summary_topics = [
    ('pathlib', '`Path`, `mkdir`, `glob`, `read_text`, `write_text`'),
    ('csv module', '`DictReader`, `DictWriter`, explicit field names'),
    ('json module', '`loads`, `dumps`, pretty-printing nested objects'),
    ('GeoJSON structure', '`FeatureCollection`, `Feature`, `properties`, `geometry`'),
    ('validation', 'Coordinate range checks and geometry-type rules'),
    ('modules', 'Writing and importing `geo_file_tools.py`'),
    ('exceptions', 'Custom error classes for missing files and malformed JSON'),
    ('logging', '`FileHandler`, levels, formatted audit messages'),
    ('unittest', '`TestCase`, `setUp`, `assertEqual`, `assertRaises`'),
    ('batch processing', 'Folder loops, summary CSV output, combined GeoJSON export'),
]
summary_rows = '\n'.join(f'| {topic} | {concepts} |' for topic, concepts in summary_topics)
preview_topics = [
    ('coordinate systems and EPSG codes', 'Why CRS identifiers matter and how to read them'),
    ('WGS84 vs projected CRS', 'Why degrees and metres answer different questions'),
    ('PyProj Transformer', 'Safe coordinate transforms with `always_xy=True`'),
    ('Shapely geometry objects', 'Points, lines, polygons, buffers, and properties'),
    ('topology predicates', '`contains`, `within`, `intersects`, and `touches`'),
]
preview_rows = '\n'.join(f'| {topic} | {detail} |' for topic, detail in preview_topics)
reading_rows = '\n'.join([
    '| [Python pathlib docs](https://docs.python.org/3/library/pathlib.html) | Portable path handling and file utilities |',
    '| [Python csv docs](https://docs.python.org/3/library/csv.html) | Official reference for CSV readers and writers |',
    '| [Python json docs](https://docs.python.org/3/library/json.html) | Parse and serialise structured data |',
    '| [GeoJSON RFC 7946](https://www.rfc-editor.org/rfc/rfc7946) | Formal GeoJSON rules and coordinate expectations |',
    '| [Python logging HOWTO](https://docs.python.org/3/howto/logging.html) | Configure handlers, formatters, and log levels |',
    '| [Real Python unittest guide](https://realpython.com/python-testing/) | Friendly introduction to Python testing patterns |',
])

final_summary = md(s(f'''
---
## ✅ Week 3 Summary

| Topic | Key concepts mastered |
|-------|-----------------------|
{summary_rows}

---

### ☑️ Self-assessment checklist

- [ ] Create/read/write files with `pathlib` without hard-coded paths
- [ ] Read a CSV with `csv.DictReader` and convert lon/lat strings to floats
- [ ] Build and save a valid GeoJSON `FeatureCollection` from Python dicts
- [ ] Write `validate_feature()` that raises a custom exception on bad input
- [ ] Add a `FileHandler` logger that writes to `logs/week3.log`
- [ ] Import a function from a local `.py` module you wrote yourself
- [ ] Write a `unittest.TestCase` with at least three test methods
- [ ] Run a batch loop over multiple files and write a CSV summary

---

## 📚 Week 4 Preview

| Topic | What you will learn |
|-------|---------------------|
{preview_rows}

---

## 📖 Further Reading

| Resource | Why |
|----------|-----|
{reading_rows}

---

*Geospatial Python Mastery — Week 3 of 10*
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
