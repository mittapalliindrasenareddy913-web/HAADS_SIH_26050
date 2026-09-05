/*
  HAADS SIH 26050 - Wokwi ESP32 Simulation Firmware
  Board: ESP32 DevKit V1
  Sensors: MPU6050 (IMU), BME280 (Temp/Press), 4 Potentiometers
  Actuators: Pan Servo (GPIO 26), Tilt Servo (GPIO 27)

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
#include <ESP32Servo.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

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

// Variables
float sim_temperature = 20.0;
float sim_pressure = 950.0;
float sim_wind_speed = 5.0;
String sim_vibration = "LOW";

int pan_angle = 90;
int tilt_angle = 90;
unsigned long lastTelemetryTime = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("==============================================");
  Serial.println("HAADS WOKWI HARDWARE SIMULATION");
  Serial.println("==============================================");

  // Initialize Wire (I2C)
  Wire.begin(21, 22);

  // MPU6050 Init
  if (mpu.begin()) {
    mpuOK = true;
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    Serial.println("[ESP32] MPU6050 initialized successfully.");
  } else {
    Serial.println("[ESP32] MPU6050 I2C not found (Simulated fallback active).");
  }

  // BME280 Init
  if (bme.begin(0x76) || bme.begin(0x77)) {
    bmeOK = true;
    Serial.println("[ESP32] BME280 initialized successfully.");
  } else {
    Serial.println("[ESP32] BME280 I2C not found (Simulated fallback active).");
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
  Serial.println("[ESP32] Pan Servo attached to GPIO 26.");
  Serial.println("[ESP32] Tilt Servo attached to GPIO 27.");

  // Analog pin mode setup
  pinMode(POT_TEMP_PIN, INPUT);
  pinMode(POT_PRESS_PIN, INPUT);
  pinMode(POT_WIND_PIN, INPUT);
  pinMode(POT_VIB_PIN, INPUT);
}

void loop() {
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

  // Vibration level map
  if (raw_vib < 1365) {
    sim_vibration = "LOW";
  } else if (raw_vib < 2730) {
    sim_vibration = "MEDIUM";
  } else {
    sim_vibration = "HIGH";
  }

  // Read IMU Data
  sensors_event_t a, g, temp_mpu;
  if (mpuOK) {
    mpu.getEvent(&a, &g, &temp_mpu);
  } else {
    a.acceleration.x = 0.01; a.acceleration.y = 0.02; a.acceleration.z = 9.81;
    g.gyro.x = 0.0; g.gyro.y = 0.0; g.gyro.z = 0.0;
  }

  // Read Serial Commands (Pan/Tilt control from Python)
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

  // Emit Human-Readable Telemetry every 1 second
  if (millis() - lastTelemetryTime > 1000) {
    lastTelemetryTime = millis();

    Serial.println("----------------------------------------------");
    Serial.println("HAADS WOKWI HARDWARE SIMULATION");
    Serial.print("Temperature: "); Serial.print(sim_temperature, 1); Serial.println(" C");
    Serial.print("Pressure: "); Serial.print(sim_pressure, 1); Serial.println(" hPa");
    Serial.print("Wind: "); Serial.print(sim_wind_speed, 1); Serial.println(" km/h");
    Serial.print("Vibration: "); Serial.println(sim_vibration);
    Serial.print("IMU: "); Serial.println(mpuOK ? "OK" : "SIMULATED");
    Serial.print("BME280: "); Serial.println(bmeOK ? "OK" : "SIMULATED");
    Serial.print("Pan: "); Serial.println(pan_angle);
    Serial.print("Tilt: "); Serial.println(tilt_angle);
  }

  delay(100);
}
