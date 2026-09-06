/*
  HAADS SIH 26050 - Wokwi ESP32 Simulation Firmware with MQTT Heartbeat
  Board: ESP32 DevKit V1
  Sensors: MPU6050 (IMU), BME280 (Temp/Press), 4 Potentiometers
  Actuators: Pan Servo (GPIO 26), Tilt Servo (GPIO 27)
  Connectivity: WiFi (Wokwi-GUEST) + Public MQTT Broker (broker.hivemq.com)
  Topic: isr/sih/26050/telemetry

  Wokwi Circuit Connections:
  - MPU6050: SDA -> GPIO 21, SCL -> GPIO 22
  - BME280: SDA -> GPIO 21, SCL -> GPIO 22
  - Temperature Pot: SIG -> GPIO 34
  - Pressure Pot: SIG -> GPIO 35
  - Wind Pot: SIG -> GPIO 32
  - Vibration Pot: SIG -> GPIO 33
  - Pan Servo: SIG -> GPIO 26
  - Tilt Servo: SIG -> GPIO 27
*/

#include <Wire.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

// WiFi & MQTT Configuration
const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* mqtt_topic_telemetry = "isr/sih/26050/telemetry";
const char* mqtt_topic_servo = "isr/sih/26050/servo";

WiFiClient espClient;
PubSubClient mqttClient(espClient);

// Pin Definitions
#define POT_TEMP_PIN      34
#define POT_PRESS_PIN     35
#define POT_WIND_PIN      32
#define POT_VIB_PIN       33

#define SERVO_PAN_PIN     26
#define SERVO_TILT_PIN    27

// Sensor & Servo Objects
Adafruit_MPU6050 mpu;
Adafruit_BME280 bme;
Servo panServo;
Servo tiltServo;

bool mpuOK = false;
bool bmeOK = false;

// Telemetry State Variables
float sim_temperature = 20.0;
float sim_pressure = 950.0;
float sim_wind_speed = 5.0;
float sim_vibration = 0.1;
String sim_vibration_str = "LOW";

int pan_angle = 90;
int tilt_angle = 90;
unsigned long lastTelemetryTime = 0;

void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  message.trim();
  
  if (message.startsWith("SERVO:")) {
    int commaIndex = message.indexOf(',');
    if (commaIndex > 0) {
      pan_angle = message.substring(6, commaIndex).toInt();
      tilt_angle = message.substring(commaIndex + 1).toInt();
      pan_angle = constrain(pan_angle, 0, 180);
      tilt_angle = constrain(tilt_angle, 0, 180);
      panServo.write(pan_angle);
      tiltServo.write(tilt_angle);
    }
  }
}

void setupWiFi() {
  delay(10);
  Serial.println("[ESP32] Connecting to WiFi (Wokwi-GUEST)...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(250);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[ESP32] WiFi Connected!");
    Serial.print("[ESP32] IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[ESP32] WiFi connection pending, proceeding with offline hardware loop.");
  }
}

void reconnectMQTT() {
  if (WiFi.status() != WL_CONNECTED) return;
  
  if (!mqttClient.connected()) {
    Serial.print("[ESP32] Attempting MQTT connection to ");
    Serial.print(mqtt_server);
    Serial.println("...");

    String clientId = "HAADS-ESP32-Wokwi-";
    clientId += String(random(0xffff), HEX);

    if (mqttClient.connect(clientId.c_str())) {
      Serial.println("[ESP32] MQTT Connected!");
      mqttClient.subscribe(mqtt_topic_servo);
    } else {
      Serial.print("[ESP32] MQTT Connect failed, rc=");
      Serial.println(mqttClient.state());
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("==============================================");
  Serial.println("HAADS WOKWI HARDWARE SIMULATION WITH MQTT");
  Serial.println("==============================================");

  // Initialize Wire (I2C)
  Wire.begin(21, 22);

  // MPU6050 Init
  if (mpu.begin()) {
    mpuOK = true;
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    Serial.println("[ESP32] MPU6050 initialized.");
  } else {
    Serial.println("[ESP32] MPU6050 I2C not found.");
  }

  // BME280 Init
  if (bme.begin(0x76) || bme.begin(0x77)) {
    bmeOK = true;
    Serial.println("[ESP32] BME280 initialized.");
  } else {
    Serial.println("[ESP32] BME280 I2C not found.");
  }

  // Servo Setup
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  panServo.setPeriodHertz(50);
  tiltServo.setPeriodHertz(50);
  panServo.attach(SERVO_PAN_PIN, 500, 2400);
  tiltServo.attach(SERVO_TILT_PIN, 500, 2400);
  panServo.write(pan_angle);
  tiltServo.write(tilt_angle);

  pinMode(POT_TEMP_PIN, INPUT);
  pinMode(POT_PRESS_PIN, INPUT);
  pinMode(POT_WIND_PIN, INPUT);
  pinMode(POT_VIB_PIN, INPUT);

  setupWiFi();
  mqttClient.setServer(mqtt_server, mqtt_port);
  mqttClient.setCallback(callback);
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    if (!mqttClient.connected()) {
      reconnectMQTT();
    }
    mqttClient.loop();
  }

  // Read Potentiometers & Map Values
  int raw_temp = analogRead(POT_TEMP_PIN);
  int raw_press = analogRead(POT_PRESS_PIN);
  int raw_wind = analogRead(POT_WIND_PIN);
  int raw_vib = analogRead(POT_VIB_PIN);

  // Temp map: 0..4095 -> -30.0 .. +30.0 °C
  sim_temperature = -30.0 + (raw_temp / 4095.0) * 60.0;

  // Pressure map: 0..4095 -> 500.0 .. 1000.0 hPa
  sim_pressure = 500.0 + (raw_press / 4095.0) * 500.0;

  // Wind speed map: 0..4095 -> 0.0 .. 60.0 km/h
  sim_wind_speed = (raw_wind / 4095.0) * 60.0;

  // Vibration magnitude: 0.0 .. 1.0
  sim_vibration = raw_vib / 4095.0;

  // Read Serial Commands (Fallback Pan/Tilt control)
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    if (input.startsWith("SERVO:")) {
      int commaIndex = input.indexOf(',');
      if (commaIndex > 0) {
        pan_angle = input.substring(6, commaIndex).toInt();
        tilt_angle = input.substring(commaIndex + 1).toInt();
        pan_angle = constrain(pan_angle, 0, 180);
        tilt_angle = constrain(tilt_angle, 0, 180);
        panServo.write(pan_angle);
        tiltServo.write(tilt_angle);
      }
    }
  }

  // Publish MQTT Telemetry Heartbeat every 1.5 seconds
  if (millis() - lastTelemetryTime > 1500) {
    lastTelemetryTime = millis();

    String jsonPayload = "{";
    jsonPayload += "\"device\":\"wokwi-esp32\",";
    jsonPayload += "\"status\":\"online\",";
    jsonPayload += "\"temperature\":" + String(sim_temperature, 1) + ",";
    jsonPayload += "\"pressure\":" + String(sim_pressure, 1) + ",";
    jsonPayload += "\"wind\":" + String(sim_wind_speed, 1) + ",";
    jsonPayload += "\"vibration\":" + String(sim_vibration, 2) + ",";
    jsonPayload += "\"pan\":" + String(pan_angle) + ",";
    jsonPayload += "\"tilt\":" + String(tilt_angle) + ",";
    jsonPayload += "\"timestamp\":" + String(millis());
    jsonPayload += "}";

    if (mqttClient.connected()) {
      mqttClient.publish(mqtt_topic_telemetry, jsonPayload.c_str());
      Serial.println("[ESP32 -> MQTT] Telemetry Published: " + jsonPayload);
    } else {
      Serial.println("[ESP32 Serial Telemetry] " + jsonPayload);
    }
  }

  delay(50);
}
