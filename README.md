# AureaTech Drivers

AureaTech is a Flet desktop application for a smart residential community. The current repo is DB-backed: users, readings, alerts, automation rules, chats, plates, camera events, logs, and actuators are stored in MariaDB/MySQL through repository and service layers.

The app is built around the `docs/Drivers.docx` target, with ESP32 sensor/actuator integration and plate-recognition support.

## Current Stack

- Python with Flet `0.22.0`
- MariaDB/MySQL local database
- MVC-style app structure under `app/`
- Repository/service boundaries for DB access and business rules
- PBKDF2 password hashes for seeded users
- Optional YOLO plate-recognition model under `app/infraestructure/vision/`
- ESP32 firmware under `docs/smartcity_esp32.ino`

## Project Layout

```text
app.py                         Flet app entry point
app/controller/                UI orchestration and navigation
app/model/                     Domain models
app/repository/                DB repositories
app/service/                   Business services and integrations
app/view/                      Flet views and reusable UI
app/infraestructure/db.py      MariaDB/MySQL adapter
app/infraestructure/vision/    Plate recognizer and model files
docs/db.sql                    Fresh DB schema and seed data
docs/migration.sql             Migration for existing DBs
docs/smartcity_esp32.ino       ESP32 firmware
sim/                           Data generation helpers
tests/                         Pytest coverage
```

## Setup

Use a virtual environment. Do not install dependencies globally.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks venv activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Database

Run a local MariaDB/MySQL server first. The app reads DB connection settings from:

```text
data/auth.txt
```

Expected format:

```text
host=127.0.0.1
port=3306
user=admin
password=admin
database=pii26_aureatech
```

Create and seed a fresh database:

```powershell
mysql -u root -p pii26_aureatech < docs\db.sql
```

`docs/db.sql` includes schema, users, communities, sensors, actuators, automation rules, plate records, chats, alerts, camera events, logs, and seeded readings. Run the migration after backing up:

```powershell
mysql -u root -p pii26_aureatech < docs\migration.sql
```

The migration normalizes plates without spaces, moves seeded users to PBKDF2 hashes, inserts extra demo users, adds the community garage servomotor if needed, and inserts app-owned actuator rule actions.

### Seed More Readings

The static seed includes sample readings, but charts and day/week comparisons work better with generated time-series data. After loading the DB and confirming `data/auth.txt` points to it, run one of:

```powershell
.\.venv\Scripts\python.exe sim\generate_readings.py --hours 30 --interval-min 30
```

For broader week-level comparisons:

```powershell
.\.venv\Scripts\python.exe sim\generate_readings.py --hours 200 --interval-min 30
```

Use the 30-hour seed for daily dashboard testing and the 200-hour seed when validating 7-day aggregation.

## Seeded Users

Seeded user counts:

- 5 admins
- 5 technicians
- 9 neighbors

Passwords:

- Admin users: `admin`
- Technician users: `tech`
- Neighbor users: email prefix, for example `aurea`, `juan`, `pepe`, `lucia`

Example logins:

```text
admin@test.com / admin
tech1@test.com / tech
aurea@tech.com / aurea
juan@juan.com / juan
```

## Run The App

From the repo root with the venv active:

```powershell
python app.py
```

The app expects the DB to be running and `data/auth.txt` to point to the seeded database.

## Optional Vision Endpoint

The normal Flet app owns the business workflow. A small local HTTP wrapper is available when the camera/model flow needs to post detections into the same services:

```powershell
python -m app.vision_server
```

With the local YOLO model loaded:

```powershell
python -m app.vision_server --with-model
```

Endpoint:

```text
POST /plate-detections
```

Allowed plate detections create a `camera_event` and open the community `SERVOMOTOR` garage actuator. Unauthorized plate detections create technician alerts.

## ESP32 Firmware

Firmware lives in:

```text
docs/smartcity_esp32.ino
```

Install Arduino libraries:

- `MySQL_Connector_Arduino`
- `DHT sensor library`
- `Adafruit Unified Sensor`
- `ESP32Servo`

Current expected IDs:

```cpp
#define SENSOR_ID_DHT_TEMP  1
#define SENSOR_ID_DHT_HUM   2
#define SENSOR_ID_LDR       5
#define SENSOR_ID_ULTRASON  6
#define SENSOR_ID_MQ2       9

#define ACTUATOR_ID_LED_STATUS    0
#define ACTUATOR_ID_LED_ACTION_1  1
#define ACTUATOR_ID_LED_ACTION_2  2
#define ACTUATOR_ID_BUZZER        5

#define METRIC_LUMINOSITY   "light"
#define METRIC_DISTANCE     "distance"
#define METRIC_AIR_QUALITY  "smoke"
```

The status LED is firmware-local and is not persisted as a DB actuator. The garage servo is discovered from the community `SERVOMOTOR` actuator row and reacts to `OPEN` / `CLOSED`.

## Tests

Run the full suite:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Run the model smoke test explicitly:

```powershell
$env:RUN_VISION_MODEL_TEST='1'
.\.venv\Scripts\python.exe -m pytest app\infraestructure\vision\test_plate_recognizer.py -q
```

The model smoke test is skipped by default because it loads the local YOLO model.

## Main Workflows

- Authentication: PBKDF2 hashes with legacy SHA-256 upgrade support.
- Dashboards: role-specific admin, technician, and neighbor views.
- Readings: DB-backed readings, statistics, chart aggregation, and history.
- Automation: `automation_rule`, `rule_alert_action`, and `rule_actuator_action` are enforced by services.
- Alerts: DB alerts with user deliveries and read status.
- Plates: stored and compared without spaces, with approval workflow.
- Garage: allowed neighbor/technician plates in-community and admin plates globally open the garage servomotor.
- Chat: DB-backed neighbor/technician threads and messages.
- Exports: CSV exports for readings, logs, errors, users, chats, and scoped role workflows.

## Notes

- Keep SQL access in repositories.
- Keep business rules in services.
- Keep `docs/db.sql` as the fresh schema/seed source and `docs/migration.sql` for existing DBs.
- Use the venv and pinned `requirements.txt`.
