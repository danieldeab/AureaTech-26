/*
 * ============================================================
 *  SMART CITY - ESP32 FIRMWARE
 * ============================================================
 *  Placa: ESP32 DevKit
 *  Sensores: LDR, MQ2, HC-SR04, DHT22
 *  Actuadores: 3 LEDs (estado + 2 de acciÃ³n) + buzzer
 *  ComunicaciÃ³n: directa a MariaDB en puerto 3310
 *
 *  Flujo general:
 *    setup() -> conecta WiFi -> conecta BBDD -> carga reglas/estados
 *               -> aplica estados iniciales -> entra al loop
 *    loop()  -> lee sensores en sus intervalos -> evalÃºa reglas
 *               -> hace polling de cambios manuales -> recarga
 *                  reglas cada 15 min
 *
 *  LibrerÃ­as necesarias (Arduino IDE -> Library Manager):
 *    - MySQL_Connector_Arduino (por Bogdan Necula)
 *    - DHT sensor library (por Adafruit)
 *    - Adafruit Unified Sensor
 *    - ESP32Servo
 * ============================================================
 */

#include <WiFi.h>
#include <MySQL_Connection.h>
#include <MySQL_Cursor.h>
#include <DHT.h>
#include <ESP32Servo.h>

// ============================================================
//  CONFIGURACIÃ“N
// ============================================================

// --- WiFi ---
#define WIFI_SSID         "Walter"
#define WIFI_PASSWORD     "REDACTED_WIFI_PASSWORD"
#define WIFI_TIMEOUT_MS   20000

// --- Base de datos ---
IPAddress DB_HOST(192, 168, 1, 100);    // IP del servidor MariaDB
#define DB_PORT           3310
#define DB_USER           "esp32_user"
#define DB_PASSWORD       "REDACTED_DB_PASSWORD"
#define DB_NAME           "smartcity"

// --- IdentificaciÃ³n ---
#define COMMUNITY_ID      1

// IDs de sensores en BBDD. Deben coincidir con docs/db.sql.
#define SENSOR_ID_LDR       5
#define SENSOR_ID_ULTRASON  6
#define SENSOR_ID_MQ2       9
#define SENSOR_ID_DHT_TEMP  1
#define SENSOR_ID_DHT_HUM   2

// IDs de actuadores en BBDD. El LED de estado es solo local del firmware.
#define ACTUATOR_ID_LED_STATUS    0   // LED de estado del sistema, no persistido en BBDD
#define ACTUATOR_ID_LED_ACTION_1  1   // LED de accion 1
#define ACTUATOR_ID_LED_ACTION_2  2   // LED de accion 2
#define ACTUATOR_ID_BUZZER        5   // Buzzer

// --- Pines GPIO ---
#define PIN_LDR             34   // ADC1_CH6
#define PIN_MQ2             32   // ADC1_CH4
#define PIN_ULTRASON_TRIG   5
#define PIN_ULTRASON_ECHO   17
#define PIN_DHT22           4

#define PIN_LED_STATUS      16   // LED de estado (gestionado por firmware)
#define PIN_LED_ACTION_1    15   // LED de acciÃ³n 1
#define PIN_LED_ACTION_2    13   // LED de acciÃ³n 2
#define PIN_BUZZER          2
#define PIN_SERVO           14   // Servo puerta garaje

// --- Frecuencias (ms) ---
#define INTERVAL_LDR_MS           2000
#define INTERVAL_ULTRASON_MS      1000
#define INTERVAL_MQ2_MS           2000
#define INTERVAL_DHT_MS           120000
#define INTERVAL_POLL_CMDS_MS     2000
#define INTERVAL_RELOAD_RULES_MS  900000   // 15 min

// --- LÃ­mites en RAM ---
#define MAX_RULES     20
#define MAX_ACTIONS   40
#define MAX_ACTUATORS 5

// --- MÃ©tricas (deben coincidir con automation_rule.metric_key) ---
#define METRIC_LUMINOSITY   "light"
#define METRIC_DISTANCE     "distance"
#define METRIC_AIR_QUALITY  "smoke"
#define METRIC_TEMPERATURE  "temperature"
#define METRIC_HUMIDITY     "humidity"

// --- Unidades para tabla reading ---
#define UNIT_RAW   "raw"
#define UNIT_CM    "cm"
#define UNIT_C     "C"
#define UNIT_PCT   "%"

// --- Servo puerta garaje ---
#define SERVO_CLOSED_ANGLE  0
#define SERVO_OPEN_ANGLE    90

// ============================================================
//  ESTRUCTURAS DE DATOS EN MEMORIA
// ============================================================

struct Rule {
  int    rule_id;
  int    sensor_id;
  char   metric_key[32];
  char   comparison_operator[4];   // ">", "<", ">=", "<=", "==", "!="
  float  threshold_value;
  bool   was_triggered;            // estado anterior, para detectar flancos
};

struct Action {
  int   rule_id;
  int   actuator_id;
  char  command_type[16];          // "SET", "BLINK", "BEEP", "TOGGLE"
  char  target_state[32];          // "ON", "OFF", "500", etc.
};

struct ActuatorState {
  int   actuator_id;
  char  current_state[32];         // Ãºltimo estado conocido en BBDD
  unsigned long last_changed_at_ms; // timestamp de la Ãºltima vez que aplicamos
};

// ============================================================
//  VARIABLES GLOBALES
// ============================================================

Rule          g_rules[MAX_RULES];
int           g_rules_count = 0;
Action        g_actions[MAX_ACTIONS];
int           g_actions_count = 0;
ActuatorState g_actuators[MAX_ACTUATORS];
int           g_actuators_count = 0;
int           g_garage_servo_actuator_id = -1;

bool g_db_connected = false;
bool g_fallback_mode = false;     // true si estamos sin BBDD usando reglas hardcodeadas

// Timestamps de Ãºltima ejecuciÃ³n de cada tarea (millis)
unsigned long g_last_ldr_ms = 0;
unsigned long g_last_ultrason_ms = 0;
unsigned long g_last_mq2_ms = 0;
unsigned long g_last_dht_ms = 0;
unsigned long g_last_poll_cmds_ms = 0;
unsigned long g_last_reload_rules_ms = 0;

// Estado actual de los actuadores (lo que estÃ¡ aplicado fÃ­sicamente)
struct LedRuntime {
  bool   blinking;
  unsigned long blink_interval_ms;
  unsigned long last_blink_toggle_ms;
  bool   blink_state;     // estado actual del parpadeo (HIGH/LOW)
  bool   fixed_state;     // si no estÃ¡ parpadeando, el estado fijo
};
LedRuntime g_led_status   = {false, 0, 0, false, false};
LedRuntime g_led_action_1 = {false, 0, 0, false, false};
LedRuntime g_led_action_2 = {false, 0, 0, false, false};

bool g_buzzer_active = false;
unsigned long g_buzzer_end_ms = 0;

// Cliente DHT
DHT dht(PIN_DHT22, DHT22);

// Servo puerta garaje
Servo garage_servo;

// Cliente MySQL (se crea/destruye por query, pero el WiFiClient es persistente)
WiFiClient wifi_client;

// Reglas de fallback hardcodeadas (cuando no hay conexiÃ³n a BBDD)
struct FallbackRule {
  int   sensor_id;
  const char *metric_key;
  const char *op;
  float threshold;
  int   actuator_id;
  const char *command;
  const char *target;
};

const FallbackRule FALLBACK_RULES[] = {
  // Reglas fallback alineadas con las reglas semilla de docs/db.sql
  { SENSOR_ID_DHT_TEMP,  METRIC_TEMPERATURE, ">", 38.0,  ACTUATOR_ID_BUZZER,       "SET", "ON" },
  { SENSOR_ID_LDR,       METRIC_LUMINOSITY,  "<", 50.0,  ACTUATOR_ID_LED_ACTION_1, "SET", "ON" },
  { SENSOR_ID_LDR,       METRIC_LUMINOSITY,  "<", 50.0,  ACTUATOR_ID_LED_ACTION_2, "SET", "ON" },
  { SENSOR_ID_MQ2,       METRIC_AIR_QUALITY, ">", 180.0, ACTUATOR_ID_BUZZER,       "SET", "ON" }
};
const int FALLBACK_RULES_COUNT = sizeof(FALLBACK_RULES) / sizeof(FallbackRule);

// ============================================================
//  PATRONES DE LED DE ESTADO (BLOQUEANTES, USO EN SETUP)
// ============================================================

void ledStatusOn()  { digitalWrite(PIN_LED_STATUS, HIGH); }
void ledStatusOff() { digitalWrite(PIN_LED_STATUS, LOW); }

void patternConnectingWiFi() {
  // 1 Hz: 500ms ON, 500ms OFF
  ledStatusOn();  delay(500);
  ledStatusOff(); delay(500);
}

void patternConnectingDB() {
  // 2 Hz: 250ms ON, 250ms OFF
  ledStatusOn();  delay(250);
  ledStatusOff(); delay(250);
}

void patternAllOK() {
  // 3 parpadeos rÃ¡pidos y se queda apagado
  for (int i = 0; i < 3; i++) {
    ledStatusOn();  delay(150);
    ledStatusOff(); delay(150);
  }
}

void patternErrorWiFi() {
  // 5 Hz: 100ms ON, 100ms OFF
  ledStatusOn();  delay(100);
  ledStatusOff(); delay(100);
}

void patternErrorDB() {
  // 2 parpadeos largos + pausa 3s
  for (int i = 0; i < 2; i++) {
    ledStatusOn();  delay(500);
    ledStatusOff(); delay(300);
  }
  delay(3000);
}

// ============================================================
//  LEDs Y BUZZER NO BLOQUEANTES (USO EN LOOP)
// ============================================================

// Devuelve puntero al runtime del LED segÃºn pin
LedRuntime* getLedRuntime(int pin) {
  if (pin == PIN_LED_STATUS)   return &g_led_status;
  if (pin == PIN_LED_ACTION_1) return &g_led_action_1;
  if (pin == PIN_LED_ACTION_2) return &g_led_action_2;
  return nullptr;
}

void ledSet(int pin, bool on) {
  LedRuntime *rt = getLedRuntime(pin);
  if (!rt) return;
  rt->blinking = false;
  rt->fixed_state = on;
  digitalWrite(pin, on ? HIGH : LOW);
}

void ledToggle(int pin) {
  LedRuntime *rt = getLedRuntime(pin);
  if (!rt) return;
  rt->blinking = false;
  rt->fixed_state = !rt->fixed_state;
  digitalWrite(pin, rt->fixed_state ? HIGH : LOW);
}

void ledBlink(int pin, unsigned long interval_ms) {
  LedRuntime *rt = getLedRuntime(pin);
  if (!rt) return;
  rt->blinking = true;
  rt->blink_interval_ms = interval_ms;
  rt->last_blink_toggle_ms = millis();
  rt->blink_state = true;
  digitalWrite(pin, HIGH);
}

// Llamar en cada loop() para actualizar parpadeos en curso
void ledsUpdate() {
  unsigned long now = millis();
  int pins[]    = {PIN_LED_STATUS, PIN_LED_ACTION_1, PIN_LED_ACTION_2};
  LedRuntime *rts[] = {&g_led_status, &g_led_action_1, &g_led_action_2};
  for (int i = 0; i < 3; i++) {
    if (rts[i]->blinking && (now - rts[i]->last_blink_toggle_ms >= rts[i]->blink_interval_ms)) {
      rts[i]->blink_state = !rts[i]->blink_state;
      digitalWrite(pins[i], rts[i]->blink_state ? HIGH : LOW);
      rts[i]->last_blink_toggle_ms = now;
    }
  }
}

void buzzerBeep(unsigned long duration_ms) {
  digitalWrite(PIN_BUZZER, HIGH);
  g_buzzer_active = true;
  g_buzzer_end_ms = millis() + duration_ms;
}

void buzzerSet(bool on) {
  digitalWrite(PIN_BUZZER, on ? HIGH : LOW);
  g_buzzer_active = on;
  g_buzzer_end_ms = 0;
}

void garageOpen() {
  garage_servo.write(SERVO_OPEN_ANGLE);
}

void garageClose() {
  garage_servo.write(SERVO_CLOSED_ANGLE);
}

void buzzerUpdate() {
  if (g_buzzer_active && g_buzzer_end_ms > 0 && millis() >= g_buzzer_end_ms) {
    digitalWrite(PIN_BUZZER, LOW);
    g_buzzer_active = false;
    g_buzzer_end_ms = 0;
  }
}

// ============================================================
//  LECTURA DE SENSORES
// ============================================================

int readLDR() {
  return analogRead(PIN_LDR);   // 0-4095
}

int readMQ2() {
  return analogRead(PIN_MQ2);   // 0-4095
}

// Devuelve distancia en cm. -1 si timeout.
float readUltrasonic() {
  digitalWrite(PIN_ULTRASON_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_ULTRASON_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_ULTRASON_TRIG, LOW);
  long duration = pulseIn(PIN_ULTRASON_ECHO, HIGH, 30000); // 30ms timeout = ~5m
  if (duration == 0) return -1.0;
  return duration * 0.0343 / 2.0;
}

// Lee temp/hum. Devuelve true si lectura OK.
bool readDHT(float &temperature, float &humidity) {
  humidity    = dht.readHumidity();
  temperature = dht.readTemperature();
  return !isnan(humidity) && !isnan(temperature);
}

// ============================================================
//  EJECUCIÃ“N DE ACCIONES SOBRE ACTUADORES
// ============================================================

// Mapea actuator_id de BBDD a pin fÃ­sico. Devuelve -1 si no se conoce.
int actuatorIdToPin(int actuator_id) {
  if (actuator_id == g_garage_servo_actuator_id) return PIN_SERVO;

  switch (actuator_id) {
    case ACTUATOR_ID_LED_STATUS:   return PIN_LED_STATUS;
    case ACTUATOR_ID_LED_ACTION_1: return PIN_LED_ACTION_1;
    case ACTUATOR_ID_LED_ACTION_2: return PIN_LED_ACTION_2;
    case ACTUATOR_ID_BUZZER:       return PIN_BUZZER;
    default:                       return -1;
  }
}

bool isLed(int actuator_id) {
  return actuator_id == ACTUATOR_ID_LED_STATUS ||
         actuator_id == ACTUATOR_ID_LED_ACTION_1 ||
         actuator_id == ACTUATOR_ID_LED_ACTION_2;
}

// Aplica fÃ­sicamente una acciÃ³n y devuelve el estado resultante para BBDD
String executeAction(int actuator_id, const char *command, const char *target) {
  int pin = actuatorIdToPin(actuator_id);
  if (pin < 0) return "";

  String resulting_state = "";

  if (strcmp(command, "SET") == 0) {
    if (actuator_id == g_garage_servo_actuator_id) {
      if (strcmp(target, "OPEN") == 0 || strcmp(target, "ON") == 0) {
        garageOpen();
        resulting_state = "OPEN";
      } else if (strcmp(target, "CLOSED") == 0 || strcmp(target, "OFF") == 0) {
        garageClose();
        resulting_state = "CLOSED";
      }
      return resulting_state;
    }

    bool on = (strcmp(target, "ON") == 0);
    if (isLed(actuator_id)) {
      ledSet(pin, on);
    } else if (actuator_id == ACTUATOR_ID_BUZZER) {
      buzzerSet(on);
    }
    resulting_state = on ? "ON" : "OFF";
  }
  else if (strcmp(command, "TOGGLE") == 0) {
    if (isLed(actuator_id)) {
      ledToggle(pin);
      LedRuntime *rt = getLedRuntime(pin);
      resulting_state = rt->fixed_state ? "ON" : "OFF";
    }
  }
  else if (strcmp(command, "BLINK") == 0) {
    unsigned long interval = atol(target);
    if (interval == 0) interval = 500;
    if (isLed(actuator_id)) {
      ledBlink(pin, interval);
      resulting_state = "BLINKING";
    }
  }
  else if (strcmp(command, "BEEP") == 0) {
    unsigned long duration = atol(target);
    if (duration == 0) duration = 200;
    if (actuator_id == ACTUATOR_ID_BUZZER) {
      buzzerBeep(duration);
      resulting_state = "BEEPING";
    }
  }

  return resulting_state;
}

// ============================================================
//  BASE DE DATOS - HELPERS DE CONEXIÃ“N
// ============================================================

// Ejecuta una query sin esperar resultados (INSERT, UPDATE).
// Abre conexiÃ³n, ejecuta, cierra.
bool dbExecute(const char *query) {
  MySQL_Connection conn(&wifi_client);
  if (!conn.connect(DB_HOST, DB_PORT, (char*)DB_USER, (char*)DB_PASSWORD, (char*)DB_NAME)) {
    g_db_connected = false;
    return false;
  }
  MySQL_Cursor cur(&conn);
  cur.execute(query);
  conn.close();
  g_db_connected = true;
  return true;
}

// ============================================================
//  BBDD - INSERT READINGS
// ============================================================

void insertReading(int sensor_id, float value, const char *unit) {
  char q[200];
  snprintf(q, sizeof(q),
    "INSERT INTO smartcity.reading (sensor_id, reading_value, unit, recorded_at) "
    "VALUES (%d, %.2f, '%s', NOW())",
    sensor_id, value, unit);
  if (!dbExecute(q)) {
    Serial.print("[DB] Fallo INSERT reading sensor ");
    Serial.println(sensor_id);
  }
}

// ============================================================
//  BBDD - UPDATE ACTUATOR (tras aplicar acciÃ³n)
// ============================================================

void updateActuatorState(int actuator_id, const String &state) {
  char q[200];
  snprintf(q, sizeof(q),
    "UPDATE smartcity.actuator SET current_state='%s', last_changed_at=NOW() "
    "WHERE actuator_id=%d",
    state.c_str(), actuator_id);
  dbExecute(q);
}

// ============================================================
//  BBDD - CARGAR REGLAS, ACCIONES Y ACTUADORES
// ============================================================

void loadRulesAndActions() {
  g_rules_count = 0;
  g_actions_count = 0;

  MySQL_Connection conn(&wifi_client);
  if (!conn.connect(DB_HOST, DB_PORT, (char*)DB_USER, (char*)DB_PASSWORD, (char*)DB_NAME)) {
    Serial.println("[DB] No se pudo conectar para cargar reglas");
    g_db_connected = false;
    return;
  }

  // --- Cargar reglas activas para sensores de esta comunidad ---
  {
    char q[400];
    snprintf(q, sizeof(q),
      "SELECT ar.rule_id, ar.sensor_id, ar.metric_key, ar.comparison_operator, ar.threshold_value "
      "FROM smartcity.automation_rule ar "
      "JOIN smartcity.sensor s ON s.sensor_id = ar.sensor_id "
      "WHERE ar.is_enabled = 1 AND s.community_id = %d AND s.is_enabled = 1",
      COMMUNITY_ID);
    MySQL_Cursor cur(&conn);
    cur.execute(q);
    column_names *cols = cur.get_columns();
    (void)cols;
    row_values *row;
    while ((row = cur.get_next_row()) != NULL && g_rules_count < MAX_RULES) {
      Rule &r = g_rules[g_rules_count++];
      r.rule_id   = atoi(row->values[0]);
      r.sensor_id = atoi(row->values[1]);
      strncpy(r.metric_key, row->values[2], sizeof(r.metric_key) - 1);
      r.metric_key[sizeof(r.metric_key) - 1] = '\0';
      strncpy(r.comparison_operator, row->values[3], sizeof(r.comparison_operator) - 1);
      r.comparison_operator[sizeof(r.comparison_operator) - 1] = '\0';
      r.threshold_value = atof(row->values[4]);
      r.was_triggered = false;
    }
  }

  // --- Cargar acciones de esas reglas ---
  {
    char q[400];
    snprintf(q, sizeof(q),
      "SELECT raa.rule_id, raa.actuator_id, raa.command_type, raa.target_state "
      "FROM smartcity.rule_actuator_action raa "
      "JOIN smartcity.automation_rule ar ON ar.rule_id = raa.rule_id "
      "JOIN smartcity.sensor s ON s.sensor_id = ar.sensor_id "
      "WHERE ar.is_enabled = 1 AND s.community_id = %d",
      COMMUNITY_ID);
    MySQL_Cursor cur(&conn);
    cur.execute(q);
    row_values *row;
    while ((row = cur.get_next_row()) != NULL && g_actions_count < MAX_ACTIONS) {
      Action &a = g_actions[g_actions_count++];
      a.rule_id     = atoi(row->values[0]);
      a.actuator_id = atoi(row->values[1]);
      strncpy(a.command_type, row->values[2], sizeof(a.command_type) - 1);
      a.command_type[sizeof(a.command_type) - 1] = '\0';
      strncpy(a.target_state, row->values[3], sizeof(a.target_state) - 1);
      a.target_state[sizeof(a.target_state) - 1] = '\0';
    }
  }

  conn.close();
  g_db_connected = true;
  Serial.print("[DB] Reglas cargadas: "); Serial.println(g_rules_count);
  Serial.print("[DB] Acciones cargadas: "); Serial.println(g_actions_count);
}

void loadActuatorStates() {
  g_actuators_count = 0;
  g_garage_servo_actuator_id = -1;

  MySQL_Connection conn(&wifi_client);
  if (!conn.connect(DB_HOST, DB_PORT, (char*)DB_USER, (char*)DB_PASSWORD, (char*)DB_NAME)) {
    g_db_connected = false;
    return;
  }

  char q[200];
  snprintf(q, sizeof(q),
    "SELECT actuator_id, actuator_type, current_state FROM smartcity.actuator WHERE community_id=%d",
    COMMUNITY_ID);
  MySQL_Cursor cur(&conn);
  cur.execute(q);
  row_values *row;
  while ((row = cur.get_next_row()) != NULL && g_actuators_count < MAX_ACTUATORS) {
    ActuatorState &s = g_actuators[g_actuators_count++];
    s.actuator_id = atoi(row->values[0]);
    const char *actuator_type = row->values[1] ? row->values[1] : "";
    if (strcmp(actuator_type, "SERVOMOTOR") == 0 && g_garage_servo_actuator_id < 0) {
      g_garage_servo_actuator_id = s.actuator_id;
    }
    if (row->values[2]) {
      strncpy(s.current_state, row->values[2], sizeof(s.current_state) - 1);
      s.current_state[sizeof(s.current_state) - 1] = '\0';
    } else {
      strcpy(s.current_state, "OFF");
    }
    s.last_changed_at_ms = millis();
  }
  conn.close();

  // Aplicar fÃ­sicamente los estados iniciales (sin tocar LED de estado en arranque)
  for (int i = 0; i < g_actuators_count; i++) {
    if (g_actuators[i].actuator_id == ACTUATOR_ID_LED_STATUS) continue;
    // Solo aplicamos estados simples ON/OFF al inicio
    if (strcmp(g_actuators[i].current_state, "ON") == 0) {
      executeAction(g_actuators[i].actuator_id, "SET", "ON");
    } else if (strcmp(g_actuators[i].current_state, "OFF") == 0) {
      executeAction(g_actuators[i].actuator_id, "SET", "OFF");
    } else if (strcmp(g_actuators[i].current_state, "OPEN") == 0) {
      executeAction(g_actuators[i].actuator_id, "SET", "OPEN");
    } else if (strcmp(g_actuators[i].current_state, "CLOSED") == 0) {
      executeAction(g_actuators[i].actuator_id, "SET", "CLOSED");
    }
  }

  g_db_connected = true;
}

// ============================================================
//  BBDD - POLLING DE COMANDOS MANUALES
// ============================================================

// Devuelve puntero al ActuatorState local, o nullptr
ActuatorState* findActuatorState(int actuator_id) {
  for (int i = 0; i < g_actuators_count; i++) {
    if (g_actuators[i].actuator_id == actuator_id) return &g_actuators[i];
  }
  return nullptr;
}

void pollManualCommands() {
  MySQL_Connection conn(&wifi_client);
  if (!conn.connect(DB_HOST, DB_PORT, (char*)DB_USER, (char*)DB_PASSWORD, (char*)DB_NAME)) {
    g_db_connected = false;
    return;
  }

  char q[200];
  snprintf(q, sizeof(q),
    "SELECT actuator_id, current_state FROM smartcity.actuator WHERE community_id=%d",
    COMMUNITY_ID);
  MySQL_Cursor cur(&conn);
  cur.execute(q);
  row_values *row;
  while ((row = cur.get_next_row()) != NULL) {
    int aid = atoi(row->values[0]);
    const char *new_state = row->values[1] ? row->values[1] : "OFF";

    // No tocamos el LED de estado por polling (lo gestiona el firmware)
    if (aid == ACTUATOR_ID_LED_STATUS) continue;

    ActuatorState *st = findActuatorState(aid);
    if (st && strcmp(st->current_state, new_state) != 0) {
      // Cambio detectado: aplicar fÃ­sicamente
      Serial.print("[POLL] Cambio manual actuator ");
      Serial.print(aid); Serial.print(": ");
      Serial.print(st->current_state); Serial.print(" -> ");
      Serial.println(new_state);

      if (strcmp(new_state, "ON") == 0) {
        executeAction(aid, "SET", "ON");
      } else if (strcmp(new_state, "OFF") == 0) {
        executeAction(aid, "SET", "OFF");
      } else if (strcmp(new_state, "BLINKING") == 0) {
        executeAction(aid, "BLINK", "500");
      } else if (strcmp(new_state, "OPEN") == 0) {
        executeAction(aid, "SET", "OPEN");
      } else if (strcmp(new_state, "CLOSED") == 0) {
        executeAction(aid, "SET", "CLOSED");
      }
      strncpy(st->current_state, new_state, sizeof(st->current_state) - 1);
      st->current_state[sizeof(st->current_state) - 1] = '\0';
    }
  }
  conn.close();
  g_db_connected = true;
}

// ============================================================
//  MOTOR DE REGLAS
// ============================================================

bool evaluateCondition(float value, const char *op, float threshold) {
  if (strcmp(op, ">")  == 0) return value >  threshold;
  if (strcmp(op, "<")  == 0) return value <  threshold;
  if (strcmp(op, ">=") == 0) return value >= threshold;
  if (strcmp(op, "<=") == 0) return value <= threshold;
  if (strcmp(op, "==") == 0) return value == threshold;
  if (strcmp(op, "!=") == 0) return value != threshold;
  return false;
}

// Ejecuta todas las acciones asociadas a una regla y persiste el estado
void triggerRuleActions(int rule_id) {
  for (int i = 0; i < g_actions_count; i++) {
    if (g_actions[i].rule_id != rule_id) continue;
    Action &a = g_actions[i];
    String result = executeAction(a.actuator_id, a.command_type, a.target_state);
    if (result.length() > 0) {
      if (g_db_connected) updateActuatorState(a.actuator_id, result);
      ActuatorState *st = findActuatorState(a.actuator_id);
      if (st) {
        strncpy(st->current_state, result.c_str(), sizeof(st->current_state) - 1);
        st->current_state[sizeof(st->current_state) - 1] = '\0';
      }
      Serial.print("[RULE] Regla "); Serial.print(rule_id);
      Serial.print(" -> actuator "); Serial.print(a.actuator_id);
      Serial.print(" "); Serial.print(a.command_type);
      Serial.print(" "); Serial.println(a.target_state);
    }
  }
}

// EvalÃºa todas las reglas activas para un sensor concreto y una mÃ©trica.
// Solo dispara acciones cuando hay flanco (transiciÃ³n no-cumplida -> cumplida)
// para evitar spam de updates a BBDD cada lectura.
void evaluateRulesForMetric(int sensor_id, const char *metric_key, float value) {
  if (g_fallback_mode) {
    // En modo fallback usamos reglas hardcodeadas, sin detecciÃ³n de flanco
    for (int i = 0; i < FALLBACK_RULES_COUNT; i++) {
      const FallbackRule &fr = FALLBACK_RULES[i];
      if (fr.sensor_id == sensor_id && strcmp(fr.metric_key, metric_key) == 0) {
        if (evaluateCondition(value, fr.op, fr.threshold)) {
          executeAction(fr.actuator_id, fr.command, fr.target);
        }
      }
    }
    return;
  }

  for (int i = 0; i < g_rules_count; i++) {
    Rule &r = g_rules[i];
    if (r.sensor_id != sensor_id) continue;
    if (strcmp(r.metric_key, metric_key) != 0) continue;
    bool triggered_now = evaluateCondition(value, r.comparison_operator, r.threshold_value);
    if (triggered_now && !r.was_triggered) {
      // Flanco de subida (la regla acaba de empezar a cumplirse)
      triggerRuleActions(r.rule_id);
    }
    r.was_triggered = triggered_now;
  }
}

// ============================================================
//  TAREAS DE MEDIDA (llamadas desde loop segÃºn intervalo)
// ============================================================

void taskLDR() {
  int v = readLDR();
  Serial.print("[LDR] "); Serial.println(v);
  if (g_db_connected) insertReading(SENSOR_ID_LDR, v, UNIT_RAW);
  evaluateRulesForMetric(SENSOR_ID_LDR, METRIC_LUMINOSITY, v);
}

void taskUltrasonic() {
  float d = readUltrasonic();
  if (d < 0) return;   // timeout, no enviamos
  Serial.print("[ULTRASON] "); Serial.print(d); Serial.println(" cm");
  if (g_db_connected) insertReading(SENSOR_ID_ULTRASON, d, UNIT_CM);
  evaluateRulesForMetric(SENSOR_ID_ULTRASON, METRIC_DISTANCE, d);
}

void taskMQ2() {
  int v = readMQ2();
  Serial.print("[MQ2] "); Serial.println(v);
  if (g_db_connected) insertReading(SENSOR_ID_MQ2, v, UNIT_RAW);
  evaluateRulesForMetric(SENSOR_ID_MQ2, METRIC_AIR_QUALITY, v);
}

void taskDHT() {
  float t, h;
  if (!readDHT(t, h)) {
    Serial.println("[DHT] Lectura invÃ¡lida");
    return;
  }
  Serial.print("[DHT] T="); Serial.print(t); Serial.print("C  H="); Serial.print(h); Serial.println("%");
  if (g_db_connected) {
    insertReading(SENSOR_ID_DHT_TEMP, t, UNIT_C);
    insertReading(SENSOR_ID_DHT_HUM, h, UNIT_PCT);
  }
  evaluateRulesForMetric(SENSOR_ID_DHT_TEMP, METRIC_TEMPERATURE, t);
  evaluateRulesForMetric(SENSOR_ID_DHT_HUM, METRIC_HUMIDITY, h);
}

// ============================================================
//  CONEXIÃ“N WiFi
// ============================================================

bool connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - start > WIFI_TIMEOUT_MS) return false;
    patternConnectingWiFi();   // parpadeo 1 Hz mientras conecta
  }
  Serial.print("[WIFI] Conectado: ");
  Serial.println(WiFi.localIP());
  return true;
}

bool connectDB() {
  MySQL_Connection conn(&wifi_client);
  bool ok = conn.connect(DB_HOST, DB_PORT, (char*)DB_USER, (char*)DB_PASSWORD, (char*)DB_NAME);
  if (ok) conn.close();
  return ok;
}

// ============================================================
//  SETUP
// ============================================================

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\n=== Smart City ESP32 ===");

  // --- Pines como salida ---
  pinMode(PIN_LED_STATUS,   OUTPUT);
  pinMode(PIN_LED_ACTION_1, OUTPUT);
  pinMode(PIN_LED_ACTION_2, OUTPUT);
  pinMode(PIN_BUZZER,       OUTPUT);
  pinMode(PIN_ULTRASON_TRIG, OUTPUT);
  pinMode(PIN_ULTRASON_ECHO, INPUT);

  digitalWrite(PIN_LED_STATUS,   LOW);
  digitalWrite(PIN_LED_ACTION_1, LOW);
  digitalWrite(PIN_LED_ACTION_2, LOW);
  digitalWrite(PIN_BUZZER,       LOW);
  garage_servo.attach(PIN_SERVO);
  garageClose();

  // --- DHT22 ---
  dht.begin();

  // --- ADC config (resoluciÃ³n por defecto 12 bits ya en ESP32) ---
  analogReadResolution(12);

  // --- Conectar WiFi ---
  if (!connectWiFi()) {
    Serial.println("[WIFI] FALLO - entrando en modo fallback");
    g_fallback_mode = true;
    // PatrÃ³n de error WiFi durante 3s y arrancamos en fallback
    unsigned long t0 = millis();
    while (millis() - t0 < 3000) patternErrorWiFi();
  }

  // --- Conectar BBDD ---
  if (!g_fallback_mode) {
    bool db_ok = false;
    for (int i = 0; i < 3; i++) {
      patternConnectingDB();
      if (connectDB()) { db_ok = true; break; }
    }
    if (!db_ok) {
      Serial.println("[DB] FALLO - entrando en modo fallback");
      g_fallback_mode = true;
      unsigned long t0 = millis();
      while (millis() - t0 < 3000) patternErrorDB();
    } else {
      g_db_connected = true;
      // Cargar reglas y estados iniciales
      loadRulesAndActions();
      loadActuatorStates();
    }
  }

  // --- SeÃ±al de fin de arranque ---
  if (!g_fallback_mode) {
    patternAllOK();
  }

  Serial.println("=== Arranque completado ===");
}

// ============================================================
//  LOOP
// ============================================================

void loop() {
  unsigned long now = millis();

  // --- Actualizar LEDs en parpadeo y buzzer temporizado ---
  ledsUpdate();
  buzzerUpdate();

  // --- Modo fallback: solo medimos sensores y aplicamos reglas locales ---
  if (g_fallback_mode) {
    // PatrÃ³n de latido para indicar fallback (no bloqueante: 50ms ON cada 5s)
    static unsigned long fb_last = 0;
    if (now - fb_last > 5000) {
      digitalWrite(PIN_LED_STATUS, HIGH);
      delay(50);
      digitalWrite(PIN_LED_STATUS, LOW);
      fb_last = now;
    }
    // Intentar reconectar BBDD cada 30 segundos
    static unsigned long last_db_retry = 0;
    if (now - last_db_retry > 30000) {
      last_db_retry = now;
      if (WiFi.status() == WL_CONNECTED && connectDB()) {
        Serial.println("[DB] Reconectado, saliendo de fallback");
        g_fallback_mode = false;
        g_db_connected = true;
        loadRulesAndActions();
        loadActuatorStates();
      }
    }
  }

  // --- Tareas de medida segÃºn intervalo ---
  if (now - g_last_ldr_ms >= INTERVAL_LDR_MS) {
    g_last_ldr_ms = now;
    taskLDR();
  }
  if (now - g_last_ultrason_ms >= INTERVAL_ULTRASON_MS) {
    g_last_ultrason_ms = now;
    taskUltrasonic();
  }
  if (now - g_last_mq2_ms >= INTERVAL_MQ2_MS) {
    g_last_mq2_ms = now;
    taskMQ2();
  }
  if (now - g_last_dht_ms >= INTERVAL_DHT_MS) {
    g_last_dht_ms = now;
    taskDHT();
  }

  // --- Polling de comandos manuales (solo si conectados) ---
  if (!g_fallback_mode && now - g_last_poll_cmds_ms >= INTERVAL_POLL_CMDS_MS) {
    g_last_poll_cmds_ms = now;
    pollManualCommands();
  }

  // --- Recarga de reglas cada 15 min ---
  if (!g_fallback_mode && now - g_last_reload_rules_ms >= INTERVAL_RELOAD_RULES_MS) {
    g_last_reload_rules_ms = now;
    loadRulesAndActions();
  }
}

