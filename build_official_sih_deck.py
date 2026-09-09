"""
HAADS SIH 26050 - Official SIH 2026 Template Deck Builder
Strictly preserves the original official SIH 2026 PowerPoint template (SIH2026-IDEA-Presentation-Format.pptx).
Modifies text and elements within the original template layout, keeping fonts, header titles, team badges, and pointers intact.
Outputs:
- FINAL_SIH_26050_OFFICIAL_TEMPLATE.pptx
- FINAL_SIH_26050_OFFICIAL_TEMPLATE.pdf
"""

import sys
import os
import shutil
import pptx
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor


def populate_official_template(template_path, output_pptx_path):
    prs = pptx.Presentation(template_path)

    # 1. Update Team Name Ovals on Slides 2 to 6
    team_name = "HAADS SIH 26050"
    
    for idx, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            if shape.has_text_frame:
                if "Your Team Name" in shape.text:
                    shape.text_frame.text = team_name
                    # Format text
                    for p in shape.text_frame.paragraphs:
                        p.font.size = Pt(11)
                        p.font.bold = True
                        p.alignment = PP_ALIGN.CENTER
                elif "@SIH Idea submission- Template" in shape.text:
                    shape.text_frame.text = "🇮🇳 SIH 2026 | PS 26050 — HAADS SIH 26050"
                    for p in shape.text_frame.paragraphs:
                        p.font.size = Pt(9)
                        p.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 1: TITLE PAGE
    # =========================================================================
    slide1 = prs.slides[0]
    for shape in slide1.shapes:
        if shape.name == "TextBox 9":
            tf = shape.text_frame
            tf.word_wrap = True
            tf.clear()
            
            p = tf.paragraphs[0]
            p.text = "PROBLEM STATEMENT METADATA:"
            p.font.size = Pt(12)
            p.font.bold = True
            p.font.color.rgb = RGBColor(0, 51, 153)
            
            items = [
                ("Problem Statement ID", "26050"),
                ("Problem Statement Title", "High Altitude Performance Optimization and Robust Design of Anti-Drone System"),
                ("Project Solution Title", "HIGH-ALTITUDE RUGGEDIZED ANTI-DRONE DETECTION & PRECISION TRACKING SYSTEM WITH AI-BASED ENVIRONMENTAL COMPENSATION"),
                ("Theme", "Robotics and Drones / Defence & Security"),
                ("PS Category", "Software / Hardware Integration (Hybrid)"),
                ("Team ID", "SIH2026-PS26050-TEAM"),
                ("Team Name", "HAADS SIH 26050")
            ]
            for key, val in items:
                p = tf.add_paragraph()
                p.text = f"{key} — {val}"
                p.font.size = Pt(11)
                p.font.bold = (key in ["Problem Statement ID", "Team Name", "Project Solution Title"])
                if key == "Project Solution Title":
                    p.font.color.rgb = RGBColor(19, 136, 8)
                else:
                    p.font.color.rgb = RGBColor(30, 41, 59)

    # =========================================================================
    # SLIDE 2: IDEA TITLE
    # =========================================================================
    slide2 = prs.slides[1]
    for shape in slide2.shapes:
        if shape.name == "TextBox 8":
            tf = shape.text_frame
            tf.word_wrap = True
            tf.clear()

            def add_sec_header(title, color_rgb):
                p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
                p.text = title
                p.font.size = Pt(13)
                p.font.bold = True
                p.font.color.rgb = color_rgb

            def add_bullet(text, level=0, bold=False):
                p = tf.add_paragraph()
                p.text = text
                p.font.size = Pt(10)
                p.font.bold = bold
                p.font.color.rgb = RGBColor(30, 41, 59)
                p.level = level

            add_sec_header("PROBLEM (HIGH-ALTITUDE OPERATIONAL STRESS):", RGBColor(180, 83, 9))
            add_bullet("• Extreme cold (-30°C) affects motor pulse response, lubricant viscosity, and mechanical cable stiffness.")
            add_bullet("• Low atmospheric pressure (500 hPa) changes air density and dynamic aerodynamic behaviour.")
            add_bullet("• High wind gusts (60 km/h) cause severe aerodynamic drag (2.55 N) and target-pointing drift.")
            add_bullet("• Mountain glare and atmospheric haze reduce visual sensor reliability.")
            add_bullet("• Uncompensated environmental variation causes tracking instability and target acquisition loss.")

            add_sec_header("\nPROPOSED SOLUTION (INTEGRATED HARDWARE + AI EDGE VISION):", RGBColor(19, 136, 8))
            add_bullet("• Real-time YOLO26n-based visual object detection (sub-40ms edge inference).")
            add_bullet("• SORT-based persistent target tracking maintaining track IDs with center locking (320, 240).")
            add_bullet("• BME280 environmental monitoring (Temperature + Atmospheric Pressure + Humidity).")
            add_bullet("• MPU6050 6-axis IMU for tilt, motion, and structural vibration monitoring.")
            add_bullet("• Anemometer wind-speed sensor for real-time aerodynamic drag compensation.")
            add_bullet("• Environment-aware compensation engine scaling servo pulse signals (Stiffness factor x1.5).")
            add_bullet("• ESP32 DevKit V1 telemetry communication through HiveMQ MQTT broker.")
            add_bullet("• 2-axis Pan-Tilt servo mechanism for physical target-centred tracking.")
            add_bullet("• Piezo buzzer local alert indication (GPIO 25 @ 2000Hz tone).")

            add_sec_header("\nINNOVATION & INTEGRATED CHAIN:", RGBColor(0, 51, 153))
            add_bullet("Environment sensing + AI edge detection + persistent tracking + dynamic compensation + pan-tilt servo control in one unified system.")
            add_bullet("📌 INTEGRATED FLOW: SENSORS (BME280/MPU6050/Wind) ➔ AI DETECTION (YOLO26n) ➔ TARGET TRACKING (SORT) ➔ COMPENSATION ENGINE ➔ PAN-TILT SERVO CONTROL ➔ TARGET LOCK", bold=True)

    # =========================================================================
    # SLIDE 3: TECHNICAL APPROACH (PHYSICAL HARDWARE & SOFTWARE)
    # =========================================================================
    slide3 = prs.slides[2]
    for shape in slide3.shapes:
        if shape.name == "TextBox 8":
            tf = shape.text_frame
            tf.word_wrap = True
            tf.clear()

            def add_sec_header(title, color_rgb):
                p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
                p.text = title
                p.font.size = Pt(12)
                p.font.bold = True
                p.font.color.rgb = color_rgb

            def add_bullet(text, level=0, bold=False):
                p = tf.add_paragraph()
                p.text = text
                p.font.size = Pt(9.5)
                p.font.bold = bold
                p.font.color.rgb = RGBColor(30, 41, 59)
                p.level = level

            add_sec_header("1. REAL PHYSICAL HARDWARE COMPONENTS (PROTOTYPE BOM):", RGBColor(0, 51, 153))
            add_bullet("• ESP32 DevKit V1: Main 32-bit dual-core microcontroller, sensor acquisition, PWM servo control, MQTT Wi-Fi telemetry.")
            add_bullet("• BME280 Sensor Module: Ingests ambient Temperature, Atmospheric Pressure, and Relative Humidity.")
            add_bullet("• MPU6050 IMU Module: Measures 3-axis acceleration, tilt/orientation angles, and structural vibration.")
            add_bullet("• Anemometer / Wind Speed Sensor: Real wind-speed measurement used for aerodynamic drag force compensation.")
            add_bullet("• SG90 / MG90S Servo Motors: 2 precision servo motors (One for PAN azimuth, One for TILT elevation).")
            add_bullet("• 2-Axis Pan-Tilt Camera Bracket: Mechanical gimbal mounting structure holding and moving the camera payload.")
            add_bullet("• USB Webcam: Real camera visual input for physical target detection and tracking.")
            add_bullet("• Piezo Buzzer: Local audible alert output indicating target lock and system events (GPIO 25).")
            add_bullet("• 10kΩ Potentiometers: Manual testing and threshold calibration inputs.")
            add_bullet("• 5V Regulated Power Supply & Power Bus: Provides clean DC power for servos and microcontroller peripherals.")
            add_bullet("• Breadboard & Jumper Wires: Circuit wiring and inter-module signal connections.")

            add_sec_header("\n2. COMPUTING & AI EDGE PLATFORM (LAPTOP / SYSTEM):", RGBColor(19, 136, 8))
            add_bullet("• Laptop / Computer: Runs Python 3.12, OpenCV 4.x, YOLO26n Edge AI model, SORT Tracker, and Streamlit Dashboard.")

            add_sec_header("\n3. COMMUNICATION ARCHITECTURE:", RGBColor(180, 83, 9))
            add_bullet("• ESP32 DevKit ──[Wi-Fi / HiveMQ MQTT Broker]──> Python Hardware Interface ──> Streamlit Dashboard")

            add_sec_header("\n4. SIMULATION VALIDATION LINK (WOKWI):", RGBColor(100, 100, 100))
            add_bullet("• WOKWI SIMULATION: Virtual ESP32 platform used for hardware-in-the-loop validation before physical wiring.")

            add_sec_header("\n5. END-TO-END SYSTEM DATA FLOWS:", RGBColor(0, 51, 153))
            add_bullet("• MAIN VISION FLOW: USB WEBCAM ➔ OpenCV ➔ YOLO26n ➔ SORT TRACKER ➔ CENTROID LOCK ➔ COMPENSATION ➔ ESP32 ➔ PAN/TILT SERVOS", bold=True)
            add_bullet("• ENVIRONMENT FLOW: BME280 + MPU6050 + ANEMOMETER ➔ ESP32 ➔ MQTT TELEMETRY ➔ LAPTOP ➔ DYNAMIC COMPENSATION ENGINE", bold=True)

    # =========================================================================
    # SLIDE 4: FEASIBILITY AND VIABILITY
    # =========================================================================
    slide4 = prs.slides[3]
    for shape in slide4.shapes:
        if shape.name == "TextBox 8":
            tf = shape.text_frame
            tf.word_wrap = True
            tf.clear()

            def add_sec_header(title, color_rgb):
                p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
                p.text = title
                p.font.size = Pt(12)
                p.font.bold = True
                p.font.color.rgb = color_rgb

            def add_bullet(text, level=0, bold=False):
                p = tf.add_paragraph()
                p.text = text
                p.font.size = Pt(9.5)
                p.font.bold = bold
                p.font.color.rgb = RGBColor(30, 41, 59)
                p.level = level

            add_sec_header("TECHNICAL FEASIBILITY:", RGBColor(19, 136, 8))
            add_bullet("• ESP32 DevKit provides highly reliable, low-cost embedded control for sensor sampling and servo PWM generation.")
            add_bullet("• BME280, MPU6050, and anemometer supply accurate environmental telemetry for dynamic software compensation.")
            add_bullet("• 2-axis servo pan-tilt mechanism enables clear physical target tracking demonstration.")
            add_bullet("• Laptop CPU/GPU handles real-time YOLO26n Edge AI vision and SORT tracking during the prototype phase.")
            add_bullet("• Wokwi simulation enables safe virtual hardware testing before physical assembly.")
            add_bullet("• Modular system design supports seamless transition to standalone embedded edge hardware (e.g. Jetson Orin).")

            add_sec_header("\nOPERATIONAL CHALLENGES:", RGBColor(180, 83, 9))
            add_bullet("• Extreme cold (-30°C) increasing cable resistance, lubricant viscosity, and motor torque demand.")
            add_bullet("• Low atmospheric pressure (500 hPa) altering air density and thermal dissipation efficiency.")
            add_bullet("• High wind disturbance (60 km/h) inducing aerodynamic drag force (2.55 N) and pointing drift.")
            add_bullet("• Mechanical vibration and chatter caused by high-altitude winds.")
            add_bullet("• Sensor drift and visual glare under intense high-altitude sunlight.")
            add_bullet("• Servo positioning backlash and potential MQTT communication network latency.")

            add_sec_header("\nMITIGATION STRATEGIES:", RGBColor(0, 51, 153))
            add_bullet("• Temperature-aware pulse compensation multiplying servo drive gain (Stiffness factor x1.5).")
            add_bullet("• Wind-speed based aerodynamic drag calculation and automatic pan/tilt angular offset correction.")
            add_bullet("• IMU-based vibration monitoring and adaptive stabilization filtering.")
            add_bullet("• Sensor validation and noise rejection algorithms.")
            add_bullet("• SORT persistent object tracking preserving target Track IDs through momentary camera glare drops.")
            add_bullet("• Servo position feedback control and MQTT heartbeat liveness monitoring.")
            add_bullet("• Truthful 9-subsystem health monitor providing complete operator visibility.")

    # =========================================================================
    # SLIDE 5: IMPACT AND BENEFITS
    # =========================================================================
    slide5 = prs.slides[4]
    for shape in slide5.shapes:
        if shape.name == "TextBox 8":
            tf = shape.text_frame
            tf.word_wrap = True
            tf.clear()

            def add_sec_header(title, color_rgb):
                p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
                p.text = title
                p.font.size = Pt(12)
                p.font.bold = True
                p.font.color.rgb = color_rgb

            def add_bullet(text, level=0, bold=False):
                p = tf.add_paragraph()
                p.text = text
                p.font.size = Pt(9.5)
                p.font.bold = bold
                p.font.color.rgb = RGBColor(30, 41, 59)
                p.level = level

            add_sec_header("TARGET APPLICATIONS & USER DOMAINS:", RGBColor(0, 51, 153))
            add_bullet("• High-altitude security installations and remote defense outposts (Himalayan border sectors).")
            add_bullet("• Mountainous border surveillance and perimeter monitoring corridors.")
            add_bullet("• Critical national infrastructure protection (power plants, communication relays, airbases).")
            add_bullet("• Defense R&D laboratories and prototyping testbeds.")
            add_bullet("• Non-kinetic anti-drone detection, tracking, and authorized response research.")

            add_sec_header("\nSYSTEM BENEFITS:", RGBColor(19, 136, 8))
            add_bullet("• Environment-aware tracking resilient against severe atmospheric and thermal stress.")
            add_bullet("• Improved pointing stability and reduced target acquisition loss under strong wind gusts.")
            add_bullet("• Real-time environmental monitoring (Temperature, Pressure, Wind Speed, Vibration).")
            add_bullet("• Real-time operator visibility into complete system health via 9-subsystem health matrix.")
            add_bullet("• Modular hardware architecture allowing straightforward component upgrades and maintenance.")
            add_bullet("• Low-cost simulation-first development model combining Wokwi ESP32 and open-source AI tools.")
            add_bullet("• Scalable edge-AI architecture designed for easy future transition to rugged field deployment.")

            add_sec_header("\nSCALABILITY ROADMAP:", RGBColor(180, 83, 9))
            add_bullet("• CURRENT PROTOTYPE: Laptop + USB Webcam + Wokwi ESP32 Simulation & MQTT Telemetry Link.")
            add_bullet("• PHYSICAL PROTOTYPE: ESP32 + BME280 + MPU6050 + Anemometer + USB Webcam + 2-Axis Servos + Buzzer + 5V Supply.")
            add_bullet("• FUTURE FIELD DEPLOYMENT: Embedded Edge AI (Jetson Orin) + Ruggedized IP67 Enclosure + High-Altitude Field Operations.")

    # =========================================================================
    # SLIDE 6: RESEARCH AND REFERENCES
    # =========================================================================
    slide6 = prs.slides[5]
    for shape in slide6.shapes:
        if shape.name == "TextBox 8":
            tf = shape.text_frame
            tf.word_wrap = True
            tf.clear()

            def add_sec_header(title, color_rgb):
                p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
                p.text = title
                p.font.size = Pt(12)
                p.font.bold = True
                p.font.color.rgb = color_rgb

            def add_bullet(text, level=0, bold=False):
                p = tf.add_paragraph()
                p.text = text
                p.font.size = Pt(9.5)
                p.font.bold = bold
                p.font.color.rgb = RGBColor(30, 41, 59)
                p.level = level

            add_sec_header("GENUINE TECHNICAL & RESEARCH REFERENCES:", RGBColor(0, 51, 153))
            add_bullet("• [1] YOLO / Ultralytics Documentation: Real-time object detection models and edge vision deployment benchmarks.")
            add_bullet("• [2] SORT Tracking Algorithm (Bewley et al.): Simple Online and Realtime Tracking for persistent target centroid locking.")
            add_bullet("• [3] ESP32 Microcontroller Documentation (Espressif Systems): ESP32 dual-core architecture, PWM, and Wi-Fi stack.")
            add_bullet("• [4] Bosch BME280 Sensor Datasheet: Environmental sensing principles for barometric pressure, temperature & humidity.")
            add_bullet("• [5] MPU6050 IMU Datasheet (InvenSense): 6-axis motion tracking, accelerometer, and gyroscope processing.")
            add_bullet("• [6] Anemometer Measurement Principles: Principles of wind-speed measurement and aerodynamic drag calculation.")
            add_bullet("• [7] Wokwi Simulator Documentation: Virtual microcontroller hardware simulation platform for ESP32 and IoT modules.")
            add_bullet("• [8] MQTT Protocol Specification (OASIS Standard): Lightweight publish/subscribe messaging transport for IoT telemetry.")
            add_bullet("• [9] MIL-STD-810H Military Standard: Environmental engineering considerations and laboratory tests for high altitude & extreme cold.")

    # Remove Slide 7 (Important Instructions Slide)
    # To delete slide 7 in python-pptx:
    rId = prs.slides._sldIdLst[6].rId
    prs.part.drop_rel(rId)
    del prs.slides._sldIdLst[6]

    # Save presentation
    prs.save(output_pptx_path)
    print(f"Successfully generated official template deck at: {output_pptx_path}")


if __name__ == "__main__":
    src_tmpl = r"SIH2026_template_working.pptx"
    out_dir = r"C:\Users\mitta\OneDrive\SIH PROTOTYPE\HAADS_SIH_26050"
    out_pptx = os.path.join(out_dir, "FINAL_SIH_26050_OFFICIAL_TEMPLATE.pptx")
    populate_official_template(src_tmpl, out_pptx)
