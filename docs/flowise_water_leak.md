# FLOWISE
## SOLUTION FOR DETECTING AND PREVENTING WATER LEAKS IN PAKISTAN'S URBAN INFRASTRUCTURE

**Sara Khan — 2949**
**Batool Tariq — 2929**

Supervised By
Ms. Quratulain Raja

Submitted for the partial fulfillment of the BS Computer Science degree to the Faculty of Engineering & CS

**DEPARTMENT OF COMPUTER SCIENCE**
**NATIONAL UNIVERSITY OF MODERN LANGUAGES ISLAMABAD**

*January, 2026*

---

## TABLE OF CONTENTS

- [Abstract](#abstract)
- [Chapter 1: Introduction](#chapter-1-introduction)
- [Chapter 2: Background and Existing Systems](#chapter-2-background-and-existing-systems)
- [Chapter 3: System Requirements and Specifications](#chapter-3-system-requirements-and-specifications)
- [Chapter 4: System Modeling and Design](#chapter-4-system-modeling-and-design)
- [Chapter 5: System Testing and Validation](#chapter-5-system-testing-and-validation)
- [References](#references)

---

## Abstract

Pakistan faces a critical water shortage, with less water available per person due to low rainfall and 30–40% water loss from leaking pipelines. This issue, worsened by unaware citizens overusing water and outdated pipelines, pushes families to rely on costly water tankers, spending much of their income just to survive. Contaminated water also causes health problems, such as waterborne diseases. Existing reactive methods to deal with these pipeline leakages have proven inefficient, as leaks go unnoticed for longer periods of time, resulting in more water lost. FlowWise seeks to save water and encourage smarter use by constantly monitoring pipelines. Our goal is to reduce non-revenue water and help people use water responsibly to ease the crisis.

Our IoT-based FlowWise system uses YF-S201 Hall-effect flow sensors and an HK1100C pressure sensor placed along a small-scale hardware prototype to gather real-time hydraulic data, transmitted via an ESP32 microcontroller to Firebase Realtime Database. A cloud-hosted XGBoost model continuously reads sensor readings from Firebase, applies rolling-window feature engineering, and classifies each reading as normal or leak in real time. Upon detecting a leak the model updates a label field in the database from 0 to 1, which the mobile application (Flutter/Dart) displays immediately as a high-priority alert. The mobile app also allows water-authority administrators to monitor live flow and pressure analytics through purpose-built dashboards.

To train the XGBoost classifier, a hardware-matched synthetic dataset was generated entirely from the observed characteristics of the physical hardware prototype — baseline flow rates of approximately 2 L/min, sensor noise profiles, and experimentally measured leak-induced signal changes — without using any external hydraulic simulation library. The model was validated directly against live readings from the hardware prototype, confirming that leak events are correctly identified in real time. System integration testing demonstrated end-to-end operation from sensor data capture, through Firebase, to leak alert display in the mobile application.

The current prototype demonstrates reliable binary leak detection (leak vs. no-leak) on a single-location hardware setup. Leak localization across multiple pipe segments has not yet been implemented, as the present hardware is only capable of simulating a leak at a single fixed location. Future work will extend the sensor network, implement spatial localization, and evaluate the system on more complex water distribution topologies.

**Keywords:** Water Scarcity, Pipeline Leakages, Pakistan Pipelines, Leakage Detection, Machine Learning, Internet of Things, XGBoost, Firebase.

---

# Chapter 1: INTRODUCTION

There is a serious water shortage in Pakistan right now. The amount of water available per person has drastically decreased from about 5,000 cubic meters in 1951 to about 1,000 cubic meters now [3]. Population increase, climate change, and — most importantly — outdated infrastructure are the main causes of this reduction. In cities like Karachi and Lahore, where 30–40% of the total water supply is lost as Non-Revenue Water (NRW), leaking pipes are a major cause [6]. Leaks are difficult for authorities to fix, which frequently causes supply disruptions for extended periods of time. The seriousness of this problem is demonstrated by recent events, such as the 400 million gallons of water lost in April 2025 due to a pipeline rupture in Karachi [7]. The existing reactive methods are unsustainable since leaks go undiscovered for days.

FlowWise aims to replace manual, reactive inspections in water management with automated, real-time monitoring. This project intends to lower NRW and enable administrators to respond promptly by implementing an IoT-based system that integrates hardware sensors, a cloud-hosted Machine Learning model, and a mobile application into a unified, data-driven pipeline monitoring platform.

## 1.1 Project Domain

This project lies at the intersection of the Internet of Things (IoT) and Machine Learning (ML), specifically focusing on time-series analysis for Smart Water Management. The system utilizes embedded hardware — an ESP32 microcontroller paired with YF-S201 Hall-effect flow sensors and an HK1100C pressure sensor — for real-time data acquisition. A cloud-hosted XGBoost classifier analyses the hydraulic telemetry to distinguish normal flow conditions from leak events. The data backbone is Firebase Realtime Database, which serves as the integration layer between the physical hardware, the ML inference engine, and the administrator-facing mobile application.

## 1.2 Problem Identification

Current manual methods in Pakistan are ineffective. Leaks go undiscovered for extended periods of time due to the lack of consolidated, real-time data. Furthermore, operators are largely uninformed about consumption patterns, which leads to unintentional waste. The core problem is the inability of existing infrastructure to autonomously detect flow anomalies in real time and alert the responsible authority before significant water loss accumulates. Existing research has explored acoustic sensing, static threshold rules, and tank-level monitoring, but each approach carries hardware costs, environmental sensitivity, or domain limitations that prevent practical deployment in pressurized distribution pipelines at the scale found in Pakistani cities.

## 1.3 Proposed Solution

FlowWise addresses these challenges using a hybrid IoT-ML approach. The system continuously monitors flow rates and pressure using sensors mounted on a PVC pipeline prototype and transmits telemetry via an ESP32 to Firebase Realtime Database. A Python-based cloud inference engine — running on a server connected to Firebase — reads the latest sensor window, applies rolling-window feature normalization, and feeds the resulting features into a trained XGBoost classifier. Upon detecting a leak the engine writes a label value of 1 back to Firebase, which is immediately surfaced on the mobile application as a real-time alert. Administrators can also view live flow and pressure analytics through the app dashboard at any time.

## 1.4 Objectives

The primary objectives of the FlowWise project are:

- To develop an IoT-based data acquisition system using an ESP32 microcontroller, YF-S201 Hall-effect flow sensors, and an HK1100C pressure sensor.
- To generate a hardware-matched synthetic training dataset that faithfully replicates the signal characteristics of the physical prototype, enabling a practical ML model.
- To train an XGBoost classifier that reliably detects binary leak events (leak vs. normal) in real time from live sensor data.
- To implement a cloud inference pipeline that reads from Firebase Realtime Database, performs real-time leak classification, and writes detection results back to Firebase.
- To develop a Flutter mobile application for administrators to receive instant leak alerts and view live WDS analytics.
- To validate end-to-end system operation on the physical hardware prototype and confirm that leak events are detected correctly.

## 1.5 Scope of the Project

Designed for Pakistan's urban water infrastructure, this IoT-based solution offers a scalable model to reduce water wastage. The scope includes the development of a physical prototype (approximately 1.6-meter PVC pipeline loop) equipped with two YF-S201 flow sensors at the inlet and outlet, and one HK1100C pressure sensor, connected to an ESP32 microcontroller. The hardware prototype operates at a flow rate of approximately 2 L/min and can simulate a leak at a single fixed location using a manual ball valve on a T-junction. The system focuses specifically on binary flow anomaly detection (leak vs. no-leak). Leak localization — pinpointing the geographic segment of the failure — has **not** been implemented in this version, because the current prototype is physically capable of simulating only one leak location. The scope covers the full software stack: cloud-based ML inference, Firebase Realtime Database as the integration hub, and a Flutter mobile application for real-time alerting and analytics visualization.

## 1.6 Effectiveness / Usefulness of the System

By guaranteeing that more water reaches users and reducing financial losses related to water tankers, FlowWise offers substantial utility. By detecting leaks in real time, the system eliminates the need for labor-intensive manual inspections that may take days to identify a rupture. The administrator dashboard encourages data-driven infrastructure management by providing live visibility into hydraulic conditions. Additionally, by updating outdated infrastructure and promoting innovation through modern IoT and ML technologies, the system supports UN SDGs 6 (Clean Water and Sanitation) and 11 (Sustainable Cities and Communities).

## 1.7 Resource Requirements

### 1.7.1 Hardware Requirements

The development and execution of the system require specific IoT components. The ESP32 Development Board serves as the central processing unit, reading sensor pulses and transmitting data to Firebase over Wi-Fi. Two YF-S201 Hall-effect water flow sensors are mounted at the inlet and outlet of the pipeline section to measure volumetric flow rate in liters per minute. One HK1100C pressure sensor is installed along the pipeline to monitor hydraulic pressure in Sensor Pressure Units (SPU). A manual ball valve connected via a PVC T-joint between the two flow sensors physically diverts water to simulate a burst pipe or leakage scenario. The pipeline prototype itself is a 1.6-meter PVC piping loop that serves as the physical testbed.

| Component               | Specification                          | Purpose                              |
|-------------------------|----------------------------------------|--------------------------------------|
| ESP32 Dev Board         | Wi-Fi, dual-core, 240 MHz              | Sensor reading + Firebase telemetry  |
| YF-S201 (×2)            | Hall-effect, 1–30 L/min range          | Inlet and outlet flow measurement    |
| HK1100C                 | Resistive pressure sensor, 0–1.2 MPa  | Pipeline pressure monitoring         |
| PVC Pipeline            | 20 mm diameter, ~1.6 m loop            | Physical testbed                     |
| Manual ball valve       | T-joint mounted                        | Leak simulation                      |

**Table 1.1: Hardware Components**

### 1.7.2 Software Requirements

The software ecosystem manages the data lifecycle from sensor acquisition through cloud inference to mobile alerting.

| Tool / Framework            | Purpose                                                    |
|-----------------------------|-------------------------------------------------------------|
| Arduino IDE / PlatformIO    | ESP32 firmware development (C++)                           |
| Firebase Realtime Database  | Real-time data storage and synchronization                 |
| Firebase Authentication     | Secure role-based access for admin users                   |
| Python 3.x (Pandas, NumPy)  | Feature engineering and ML inference engine                |
| XGBoost                     | Leak detection classifier                                  |
| Scikit-learn                | Model evaluation and metrics                               |
| Flutter / Dart              | Cross-platform mobile application (Android Studio)         |
| Kaggle                      | High-memory environment for model training                 |

**Table 1.2: Software Tools and Technologies**

### 1.7.3 Data Requirements

The Machine Learning model requires training data that faithfully represents the hydraulic signals produced by the hardware prototype. Because the prototype operates at a small scale — approximately 2 L/min flow rate with four sensors — data from large-scale city water networks (which exhibit flow rates and pressure values orders of magnitude larger) is not suitable for direct training. The chosen strategy is **hardware-matched synthetic data generation**: a Python script parameterized using observed baseline values from the physical sensors (baseline flow ≈ 2.7 L/min, inlet pressure SPU ≈ 2.8, outlet pressure SPU ≈ −0.93, sensor noise standard deviation ≈ 3.2 SPU for pressure) generates a diverse set of labeled CSV files covering a range of leak magnitudes, leak timing patterns, and noise levels. This approach produces training data whose statistical distribution mirrors the real sensor outputs without requiring any external hydraulic simulation library. The resulting dataset comprises 120 synthetic scenarios (300 time steps each) with varying leak coefficients and temporal patterns, providing balanced coverage of both normal and leak conditions.

## 1.8 Report Organization

The report is organized into six chapters. Chapter 1 introduces the project, its objectives, scope, and resource requirements. Chapter 2 provides a background study and literature review of existing leak detection systems, identifies research gaps, and defines the selected scope of the proposed solution. Chapter 3 details the system requirements and specifications, including interface requirements, tools and technologies, functional and non-functional requirements, feasibility analysis, and resource requirements. Chapter 4 covers the system modeling and design, presenting use case diagrams, activity diagrams, data flow diagrams, sequence diagrams, class diagrams, and architectural views. Chapter 5 discusses system testing and validation, including hardware prototype testing, ML model validation on sensor data, real-time inference testing, and mobile application testing. Chapter 6 concludes the report and outlines future enhancements.

---

# Chapter 2: BACKGROUND AND EXISTING SYSTEMS

The proposed system, FlowWise, addresses the critical issue of water distribution inefficiency by employing an IoT-based monitoring framework and Machine Learning techniques. By integrating YF-S201 flow sensors and an HK1100C pressure sensor for real-time data acquisition and utilizing a hardware-matched synthetic dataset for model training, the system aims to provide accurate leak detection in water networks.

In this chapter, we discuss the related systems and their applications along with their limitations. We first analyze the research methodologies and findings of existing literature, followed by a technical review of the hardware systems developed by these researchers. Finally, we identify the research gaps that define the scope of our proposed solution.

## 2.1 Related Literature Review

In this section, we discuss the research methodologies, hypotheses, and experimental findings of three significant papers relevant to our domain.

Ayamga and Nakpih (2024) presented a study on an IoT-based system named "iWaLDeL" for leak detection and localization. The authors utilized a static leak detection methodology, employing flow rate sensors to compare water pressure at different network nodes. Their findings demonstrated that leakages could be located mathematically by calculating the difference between sensor readings and the known distance between pipes. However, a significant limitation of this work is its reliance on a "Machine State Model" — a rigid, rule-based logic (if-then statements). This approach lacks the adaptive capability of Machine Learning, meaning it can only detect leaks that strictly violate pre-set thresholds and cannot learn from historical data patterns [1].

Gautam et al. (2020) focused on monitoring water consumption and forecasting demand in urban housing complexes. The authors proposed a methodology using ultrasonic sensors to monitor rooftop tanks and applied Support Vector Machines (SVM) to forecast future water usage. Their experimental results showed that while SVM could accurately predict consumption trends, the leak detection aspect was rudimentary. The study assumes a leak only exists if the water level drops while the "InUse" flag is false. This limits the application strictly to storage tanks; it cannot detect leaks in the underground pipeline network where pressurized flow dynamics are different [4].

Boujelben et al. (2023) proposed an end-to-end system for leak detection and localization based on non-invasive acoustic sensing and lightweight Machine Learning. The authors developed a 1D-Convolutional Neural Network (1D-CNN) to classify raw audio signals collected from pipeline surfaces. Their methodology involved a dual-model approach: a classification model embedded on the edge node to detect leaks, and a regression model on the server to estimate the 2D position of the leak. The experimental findings demonstrated a leak detection accuracy of 97% and precise localization with a Mean Squared Error (MSE) of 0.0006 for the X-coordinate. However, a limitation of this acoustic approach is the inherent complexity of processing raw audio data, which requires significant computational resources compared to hydraulic data, and its susceptibility to external environmental noise in dense urban settings [2].

**Table 2.1: Summary of Reviewed Literature**

| Paper                      | Method               | Key Finding                           | Limitation                                  |
|----------------------------|----------------------|---------------------------------------|---------------------------------------------|
| Ayamga & Nakpih (2024) [1] | Rule-based, IoT      | Mathematical localization via flow diff | Static logic; no adaptive ML capability   |
| Gautam et al. (2020) [4]   | SVM, ultrasonic      | Accurate consumption forecasting       | Tank-only; no pressurized pipeline support |
| Boujelben et al. (2023) [2]| 1D-CNN, acoustic     | 97% detection accuracy, localization   | Expensive; noise-sensitive; complex data   |

## 2.2 Related Systems / Applications

This section reviews the hardware configurations and system architectures of the discussed solutions, highlighting their operational capabilities and limitations.

**Acoustic IoT Leak Detection System:** The prototype designed by Boujelben et al. is an acoustic monitoring node based on an Arduino microcontroller equipped with a microphone and a LoRa shield for long-range communication. A key feature is the implementation of "Edge Computing," where the lightweight 1D-CNN classification model runs directly on the device to analyze raw audio signals. However, the engineering constraint lies in acoustic propagation: while these sensors are non-invasive, they struggle to maintain accuracy on plastic (PVC) pipes where vibration signals attenuate rapidly compared to metal pipes. They are also highly sensitive to environmental noise (e.g., traffic), requiring complex filtering that is difficult to sustain on low-power battery devices [2].

**iWaLDeL — IoT Water Leakage Detection System:** The system developed by Ayamga and Nakpih features YF-S201 turbine flow sensors interfaced with an ESP32 microcontroller. Its primary functionality is to measure flow rates at fixed intervals and transmit data to an Arduino Cloud dashboard. While the system successfully visualizes real-time flow, its engineering constraint is the "Machine State Model" architecture. The system operates on a fixed loop (Idle → Comparison → Alarm), meaning it simply flags an alarm if Sensor A ≠ Sensor B, which can lead to false positives due to sensor calibration drift or minor fluctuations [1].

**Smart Water Management and Forecasting System:** The application proposed by Gautam et al. is designed for residential water management. It utilizes HC-SR04 ultrasonic sensors mounted on top of water tanks to measure the distance to the water surface. The system features a web interface that displays daily consumption and predicts future demand using SVM. However, this is a Tank Monitoring System, not a distribution monitoring system. It relies on the water being static in a tank to detect leaks and does not possess the hydraulic flow sensors necessary to monitor the dynamics of moving water in a pressurized pipeline network [4].

**Table 2.2: Summary of Existing Systems**

| System                    | Sensor Type       | ML Used | Scope               | Key Limitation                       |
|---------------------------|-------------------|---------|---------------------|--------------------------------------|
| Acoustic IoT (Boujelben)  | Acoustic/microphone | 1D-CNN | Pipeline surface     | Noise-sensitive; high complexity     |
| iWaLDeL (Ayamga & Nakpih) | YF-S201 flow     | None    | Pressurized pipeline | Static threshold logic only          |
| Smart WM (Gautam et al.)  | Ultrasonic        | SVM     | Storage tanks        | Inapplicable to pressurized networks |

## 2.3 Identified Problem from Existing Work

In this section, we discuss and elaborate on the problems identified from the existing systems.

**Noise Sensitivity and Cost:** While Boujelben et al. successfully applied Deep Learning, their reliance on acoustic/audio data makes the system expensive and vulnerable to environmental noise (traffic, construction), which is a major issue in urban Pakistan.

**Lack of Intelligence in Hydraulic Systems:** Ayamga and Nakpih utilize the correct hardware (flow sensors) but rely on static programming. This approach fails to capture complex hydraulic patterns and is prone to errors if sensors are not perfectly calibrated.

**Wrong Domain Focus:** Gautam et al. employ Machine Learning (SVM), but only for tanks. There is a lack of systems that apply Machine Learning specifically to detect leaks in flowing pipelines using hydraulic data.

To improve upon this, FlowWise bridges these gaps by combining the hydraulic flow sensor approach (like Ayamga & Nakpih) with advanced Machine Learning (improving on the rule-based logic), trained on hardware-matched synthetic data and validated directly on the physical prototype.

## 2.4 Selected Boundary for Proposed Solution

**Functionalities to be Implemented:** The proposed FlowWise system focuses on binary hydraulic leak detection in a small-scale pipeline prototype. An XGBoost classifier is trained on hardware-matched synthetic data that replicates the signal characteristics of the physical YF-S201 and HK1100C sensors at the operating flow rate of approximately 2 L/min. The model runs in a cloud inference engine that reads live sensor readings from Firebase Realtime Database, classifies each reading as leak or normal, and immediately writes the detection result back to Firebase. A Flutter mobile application surfaces real-time leak alerts and hydraulic analytics to administrators. This approach replaces the expensive acoustic sensors of Boujelben et al. with cost-effective flow and pressure sensors, while upgrading the static logic of Ayamga & Nakpih to a dynamic, data-driven ML engine capable of adapting to complex flow variations.

**Functionalities Not to be Implemented:** Leak **localization** — the ability to identify which specific pipe segment has failed — will **not** be implemented in the current version. The hardware prototype is physically capable of simulating a leak at only a single fixed location (one ball valve on one T-junction). With only one possible leak site, there is no positional information to learn or validate; localization requires a multi-node sensor network with leaks at multiple distinct, known locations. This feature is explicitly deferred to future work once the hardware prototype is expanded. The system will also not monitor water quality parameters (pH, turbidity) or utilize acoustic/vibration sensing, as these are outside the scope of the hydraulic dynamics targeted by this project.

---

# Chapter 3: SYSTEM REQUIREMENTS AND SPECIFICATIONS

This chapter lays out the fundamental architecture of the FlowWise system, acting as both a formal blueprint and a technical roadmap. These requirements guarantee that the system is not just a technical exercise but a workable solution for resource conservation in Pakistan, where local water scarcity is greatly exacerbated by aging infrastructure and Non-Revenue Water (NRW) loss. By outlining the hardware, software, and functional parameters, this chapter ensures that the system satisfies the demands of actual water management. Section 3.1 covers interface requirements. Section 3.2 describes tools and technologies. Section 3.3 defines functional requirements. Section 3.4 covers non-functional requirements. Section 3.5 presents the resource requirements. Section 3.6 discusses feasibility.

## 3.1 Interface Requirements

### 3.1.1 Hardware Interface Requirements

The physical layer must handle high-frequency data acquisition and reliable cloud transmission:

**Edge Processing Unit:** The central controller must support fast interrupt-driven sensor reading and stable Wi-Fi connectivity to transmit sensor telemetry to Firebase at regular intervals.

**Sensing Layer:** YF-S201 flow sensors utilize Hall-effect technology to generate pulse signals. These signals are interfaced via digital Input/Output pins with interrupt-driven counting to calculate volumetric flow rates in L/min with minimal lag. The HK1100C pressure sensor interfaces via an analog input pin; oversampling (250 readings averaged per measurement cycle) is used to reduce noise.

**Data Acquisition Rate:** The hardware samples and transmits one complete reading per second, with Firebase writes occurring every 2 seconds to respect API rate limits. Each record includes timestamp, inlet flow (f1\_lmin), outlet flow (f2\_lmin), inlet pressure (p1\_spu), outlet pressure (p2\_spu), and a label field (default 0).

### 3.1.2 Software Interface Requirements

The software ecosystem manages the data lifecycle from sensor acquisition through cloud inference to mobile alerting:

**Cloud Inference Engine:** A Python script continuously polls Firebase Realtime Database for new sensor readings. It maintains a rolling window of the last 30 readings, performs feature engineering, and feeds the latest feature vector into the trained XGBoost model. Upon predicting a leak, it writes label = 1 back to the corresponding Firebase record.

**Data Processing and Modeling:** The system uses Pandas and NumPy for time-series feature engineering and XGBoost for the gradient-boosted decision tree model optimized for anomaly detection.

**Mobile Application:** The Flutter/Dart mobile app subscribes to Firebase Realtime Database via a persistent listener. Any label value changing from 0 to 1 triggers a real-time push notification and updates the in-app alert dashboard. The app also renders live flow and pressure charts pulled from the same data source.

**Online and Cloud Interface:** Firebase Realtime Database serves as the integration hub with sub-second synchronization. Firebase Authentication enforces role-based access, ensuring only authorized administrators can view system-wide data and configure alert preferences.

## 3.2 Tools and Technologies

The following technologies and frameworks are utilized to implement the functional requirements of the FlowWise system:

**ESP32 Development Board:** A high-performance microcontroller with dual-core processor and built-in Wi-Fi, selected for reliable sensor pulse counting and stable Firebase connectivity. Interrupt service routines handle pulse counting from both YF-S201 sensors simultaneously without data loss.

**YF-S201 Flow Sensor (×2):** Hall-effect-based sensors measuring water flow velocity by generating pulse signals. Flow rate in L/min is computed as pulse count per second divided by the calibration constant (7.5 for YF-S201). One sensor is mounted at the pipeline inlet and one at the outlet.

**HK1100C Pressure Sensor:** A resistive pressure sensor connected to an ESP32 analog input. Raw ADC readings are converted to voltage and normalized relative to a calibrated baseline to produce SPU (Sensor Pressure Units) values that are stable and comparable across sessions.

**XGBoost (Extreme Gradient Boosting):** An optimized gradient boosting library used to train the leak detection model. Chosen for its high efficiency with structured time-series features, resistance to overfitting with small datasets, and fast inference suitable for real-time operation.

**Firebase Realtime Database:** A cloud-hosted NoSQL database used to synchronize sensor telemetry across all system components (ESP32, inference engine, mobile app) with sub-second latency.

**Python (Pandas and NumPy):** Core language and libraries for data manipulation, rolling-window feature engineering, model training (on Kaggle), and real-time inference (cloud\_bridge).

**Flutter / Dart:** Cross-platform mobile framework used to build the administrator application for real-time leak alerts and WDS analytics visualization.

**Arduino IDE / PlatformIO:** Integrated development environments for writing and uploading the C++ firmware that manages sensor interrupts and Firebase cloud communication.

## 3.3 Functional Requirements

The FlowWise system is partitioned into modules that each fulfill a specific functional role in the overall pipeline.

### 3.3.1 Leak Detection Intelligence Module

This module continuously evaluates inlet and outlet flow and pressure differentials from a rolling window of the last 30 sensor readings. It applies rolling-window normalization to compute eight derived features (normalized flow rates, flow divergence, flow divergence trend, normalized pressures, pressure divergence, pressure divergence trend) and feeds them to the XGBoost classifier. A majority-vote temporal filter over the last five predictions is applied to suppress transient false positives: a "stable leak" is declared only when at least 3 of the last 5 individual predictions return 1 and the prediction confidence exceeds 0.80. Upon stable leak detection, the module writes label = 1 to the Firebase record.

### 3.3.2 IoT Data Acquisition Module

This module manages the low-level hardware operations on the ESP32. It uses interrupt service routines (ISRs) to count Hall-effect pulses from both YF-S201 sensors simultaneously at 1-second intervals, computing flow in L/min. It performs 250-sample oversampling on the HK1100C pressure sensor analog input to reduce noise, then converts the ADC reading to a voltage and subtracts the calibrated baseline to yield SPU values. Complete sensor records are assembled into a JSON object and written to Firebase under the path `/sensor_readings/{timestamp}`.

### 3.3.3 Analytics and Notification Module

This module provides administrators with real-time visibility into system health. It visualizes live flow rates (F1 and F2 in L/min) and pressure values (P1 and P2 in SPU) on time-series charts in the mobile application. When a label value of 1 appears in Firebase, the mobile app immediately surfaces a high-priority leak alert notification. The module also supports historical trend viewing for post-incident analysis.

### 3.3.4 Consumer Usage Module

This module provides a dedicated interface for end-users to track water consumption metrics over time. It aggregates flow data to display hourly, daily, and monthly usage summaries, encouraging water conservation through transparency of consumption habits.

## 3.4 Non-Functional Requirements

**Classification Precision:** The system must maintain high recall for leak events to minimize missed detections (false negatives), which are more costly than false alarms in a safety-critical water management context. The temporal majority-vote filter is designed to reduce false positives without significantly sacrificing recall.

**Real-Time Latency:** The end-to-end latency from a leak event occurring at the sensor to an alert appearing in the mobile application should be under 10 seconds under normal Wi-Fi and cloud connectivity conditions, meeting the requirement for timely administrator response.

**Connectivity Resilience:** The ESP32 firmware monitors Wi-Fi status and reconnects automatically on disconnection. The cloud inference engine retries Firebase reads on connection failure with a 5-second back-off, ensuring detection resumes promptly after network interruptions.

**Scalable Architecture:** The cloud inference design is decoupled from the number of hardware nodes. Adding additional sensor nodes requires only new Firebase paths; the inference engine logic, rolling-window normalization, and XGBoost model do not require modification.

## 3.5 Resource Requirements

### 3.5.1 Hardware Resources

ESP32 development board, two YF-S201 Hall-effect flow sensors, one HK1100C pressure sensor, 3.3V/5V regulated power supply, PVC pipeline (20 mm diameter, ~1.6 m loop), manual ball valve and T-junction for leak simulation, and a PC/workstation for running the Python cloud inference engine.

### 3.5.2 Software Resources

Python 3.x development environment with Pandas, NumPy, XGBoost, Scikit-learn, and firebase\_admin packages; Flutter SDK and Android Studio for mobile development; Arduino IDE or PlatformIO for firmware.

### 3.5.3 Data Resources

Hardware-matched synthetic training dataset generated from observed physical sensor characteristics. The dataset comprises 120 CSV scenario files (300 time steps each) covering five leak magnitude levels, seven leak timing patterns, and three noise levels, yielding 36,000 labeled time steps for training and evaluation.

### 3.5.4 Network Resources

A stable 2.4 GHz Wi-Fi network for ESP32-to-Firebase communication and a server or PC with reliable internet connectivity to run the Python cloud inference engine continuously.

## 3.6 Project Feasibility

### 3.6.1 Technical Feasibility

**Inference Architecture:** Running the XGBoost model in a cloud-connected Python process (rather than on the ESP32 itself) eliminates firmware memory constraints and allows the full Scikit-learn/XGBoost ecosystem to be used for inference. The Firebase Realtime Database integration provides a reliable, low-latency channel between the hardware and the inference engine.

**Algorithmic Robustness:** Time-series hydraulic data are a strong fit for gradient-boosted decision tree models. By computing rolling-window normalized features before classification, the model captures relative changes in flow and pressure (the actual signature of a leak) rather than absolute sensor values that may drift over time, making it robust to long-term sensor baseline shifts.

**Data Strategy:** Generating training data directly from observed hardware prototype characteristics (rather than from a city-scale simulation) ensures that the model trains on distributions that are statistically consistent with what it will see at inference time. This is the critical insight that makes the current model practically effective, compared to previous attempts that used large-scale datasets with flow values orders of magnitude larger than the prototype produces.

### 3.6.2 Operational Feasibility

**Autonomous Operation:** The cloud inference engine runs continuously as a background process. The ESP32 firmware operates independently of the inference engine and continues to log sensor data to Firebase even if the inference engine is temporarily offline. Detection resumes automatically when the engine reconnects.

**Administrative Oversight:** The mobile-first dashboard design provides a centralized view of network health. By converting raw flow data into meaningful alerts and trend charts through Firebase synchronization, utility administrators can react to detected leaks within seconds rather than days.

### 3.6.3 Legal and Ethical Feasibility

**Public Safety:** From an ethical perspective, the system provides a crucial service by identifying leaks that can cause serious structural damage, including foundation weakness or soil erosion. The community directly benefits from this in terms of safety.

**Environmental Sustainability:** The initiative supports national water security objectives. By drastically lowering Non-Revenue Water (NRW) through quick leak identification, the system facilitates the sustainable management of a limited and vital natural resource.

## 3.7 Summary

This chapter has detailed the essential requirements that define FlowWise. By focusing on modular intelligence, a practical data generation strategy grounded in hardware observations, and a clear cloud-centric system architecture, we have created a roadmap that ensures the system can effectively detect water loss while remaining user-friendly and technically robust.

---

# Chapter 4: SYSTEM MODELING AND DESIGN

The design and modeling phase serves as a critical bridge between system requirements and actual implementation, transforming abstract specifications into concrete architectural blueprints. In the context of FlowWise, an IoT-based water leakage detection system for Pakistan's urban pipeline infrastructure, comprehensive system modeling ensures that hardware components, software modules, and data flows are properly orchestrated to achieve the project objectives. This phase involves creating various diagrams and models that capture both the structural and behavioral aspects of the system, to visualize system operations before committing resources to development.

System modeling provides multiple benefits for complex IoT systems like FlowWise. It facilitates communication among team members by providing standardized visual representations of system architecture. It helps identify potential design flaws early in the development cycle when changes are less costly to implement. Additionally, well-documented models serve as reference materials throughout the implementation and maintenance phases, ensuring consistency and reducing the likelihood of errors during coding and deployment.

This chapter presents the detailed design and analysis models for the FlowWise system. Section 4.1 provides an overview of the system design and analysis approach. Section 4.2 presents use case diagrams illustrating interactions between users and the system. Section 4.3 details full dress use cases for complex system operations. Section 4.4 presents activity diagrams showing workflow processes. Section 4.5 describes data flow diagrams at multiple abstraction levels. Section 4.6 illustrates system sequence diagrams. Section 4.7 presents detailed sequence diagrams. Section 4.8 shows the design class diagram. Section 4.9 presents architectural diagrams.

## 4.1 System Design and Analysis

The FlowWise system follows a **cloud-centric architecture** in which the ESP32 microcontroller is responsible exclusively for sensor data acquisition and Firebase telemetry upload, while the Machine Learning inference engine runs as a Python process connected to the same Firebase database. This separation of concerns keeps the firmware simple and reliable, avoids memory and runtime constraints of on-device ML inference, and allows the model to be updated without reflashing the hardware. The Firebase Realtime Database acts as the integration hub: the ESP32 writes sensor readings to it, the Python inference engine reads from and writes to it, and the Flutter mobile application subscribes to it for real-time display.

This prototype implements the FlowWise architecture through a single ESP32 node monitoring the pipeline via two YF-S201 flow sensors (inlet and outlet) and one HK1100C pressure sensor. Despite the smaller scale, the system demonstrates the full data pipeline: sensor acquisition → Firebase storage → ML inference → label update → mobile alert. The system is validated through a suite of analysis models: Activity and Data Flow modeling trace the sensor input through the inference pipeline, while Sequence and Use Case modeling ensure the prototype correctly alerts the administrator and stores sensor data for analytics.

## 4.2 Use Case Diagrams

Use case diagrams provide a high-level functional view of the system by illustrating the interactions between actors and the system's use cases. Two primary actors have been identified: the **Consumer**, who represents individual water users accessing personal consumption data and leak notifications, and the **Administrator**, who represents water authority personnel with elevated privileges to monitor system-wide flow analytics, manage configurations, and receive global leak alerts.

The Consumer actor can perform the following use cases: View Personal Consumption Data (extending to hourly, daily, and monthly breakdowns), View Consumption History and Trends, and Receive Leak Notifications. The Administrator actor can perform: View All Consumers Data, Monitor Real-time Flow Analytics, Receive Leak Notifications (system-wide), Generate System Reports, and Configure System Parameters via Firebase.

Figure 4.1 illustrates these relationships between actors and use cases, clearly delineating the system boundary and shared use cases such as leak notifications that are available to both actor types.

**Figure 4.1: FlowWise System Boundary**

## 4.3 Full Dress Use Case / Detailed Use Case

Full dress use cases document complex system interactions by specifying preconditions, success guarantees, the main success scenario, and extensions for exceptional conditions.

### 4.3.1 Leak Detection and Notification — Full Dress Use Case

The leak detection and notification process represents the core functionality of the FlowWise system. This use case is particularly complex because it involves automatic triggering without user initiation, cloud-based ML inference, coordination between the ESP32 firmware, Firebase, the Python inference engine, and the mobile application, as well as time-critical notification delivery.

The process begins automatically when the Python inference engine reads the latest 30 sensor readings from Firebase. It applies rolling-window normalization and computes eight features, then feeds them into the XGBoost model. A confidence threshold of 0.80 and a 3-of-5 majority vote filter are applied before a "stable leak" is declared. Upon stable detection, the engine writes label = 1 to the corresponding Firebase record. The mobile application, subscribed to Firebase, detects the label change and displays a real-time alert notification.

Extensions handle: sensor data being incomplete (missing fields), Wi-Fi disconnection causing Firebase reads or writes to fail (engine retries with back-off), and model prediction confidence being below the threshold (treated as normal to avoid alert fatigue).

**Table 4.1: Full Dress Use Case — Leak Detection and Notification**

| Field               | Description                                                                                                  |
|---------------------|--------------------------------------------------------------------------------------------------------------|
| Use Case Name       | Leak Detection and Notification                                                                               |
| Primary Actor       | Cloud Inference Engine (automated)                                                                            |
| Trigger             | New sensor reading written to Firebase by ESP32                                                               |
| Preconditions       | ESP32 connected and writing to Firebase; ≥30 readings in buffer; inference engine running                    |
| Main Success Scenario | Engine reads window → computes features → XGBoost predicts leak → confidence ≥ 0.80 → majority vote ≥ 3/5 → writes label = 1 → mobile app displays alert |
| Success Guarantee   | label = 1 written to Firebase; administrator receives push notification                                       |
| Extensions          | Incomplete reading: skip and log. Firebase error: retry after 5 s. Low confidence: classify as normal.       |

## 4.4 Activity Diagram

Activity diagrams model the procedural flow of actions within a system, illustrating the sequence of activities, decision points, and concurrent processes. For FlowWise, the primary activity diagram models the end-to-end leak detection workflow: from the ESP32 reading sensor pulses and uploading a JSON record to Firebase, through the Python inference engine polling for new readings, computing rolling-window features, running XGBoost inference, applying the temporal filter, and finally updating the Firebase label and triggering the mobile alert.

**Figure 4.2: FlowWise Leak Detection Activity Diagram**

## 4.5 Data Flow Diagram

Data Flow Diagrams (DFDs) illustrate the movement and transformation of information within the FlowWise system. The Context Diagram (Level 0) treats the entire FlowWise platform as a single process interacting with its environment. Flow Sensors provide continuous sensor readings (flow in L/min, pressure in SPU); the ESP32 uploads these to Firebase; the inference engine reads from Firebase and writes detection labels; Consumers and Administrators retrieve consumption data and alerts via the Flutter mobile application; and when a leak is detected, the app delivers a real-time notification.

**Figure 4.3: DFD Level 0**

The Level 1 DFD decomposes the system into three primary processes: (1) Data Acquisition — the ESP32 reads sensor pulses and uploads JSON records to the Firebase `sensor_readings` node; (2) Leak Detection Inference — the Python engine reads the sliding window from Firebase, engineers features, and writes the predicted label back; (3) Monitoring and Alerting — the Flutter app subscribes to Firebase changes and renders live analytics and push notifications for administrators.

**Figure 4.4: DFD Level 1**

## 4.6 System Sequence Diagram

A System Sequence Diagram (SSD) is a visual representation illustrating the sequence of messages exchanged between external actors and the system for a specific use case. For FlowWise, an SSD is essential to define the interface between the Administrator and the system during real-time alert delivery.

The View Water Consumption Data use case is a critical function of the FlowWise system. The Primary Actor is the Administrator. Preconditions: the mobile application is launched and authenticated via Firebase. The Success Guarantee is the correct visualization of live flow data and any active leak alerts. The SSD shows: Administrator opens app → app authenticates with Firebase Authentication → app subscribes to `sensor_readings` listener → Firebase streams latest records → app renders flow and pressure charts and checks label values → if label = 1, app displays leak alert.

**Figure 4.5: System Sequence Diagram — View Consumption and Alerts**

## 4.7 Sequence Diagram

The detailed sequence diagram for leak detection exposes the internal architecture of the FlowWise system, showing the collaboration between the ESP32 firmware, Firebase, the cloud inference engine, and the mobile application.

The process begins with the YF-S201 sensors generating electrical pulses proportional to flow rate. The ESP32 firmware captures these via interrupt-driven GPIO pins, computes flow rates in L/min at 1-second intervals, reads the HK1100C pressure sensor with 250-sample oversampling, and writes a complete sensor record (timestamp, f1\_lmin, f2\_lmin, p1\_spu, p2\_spu, label=0) to Firebase under `/sensor_readings/{timestamp}`.

The Python inference engine polls Firebase for new records. Once ≥30 records are available in the buffer, it extracts the most recent 30 readings into a DataFrame and applies `create_features()`: rolling-window min-max normalization for flow and pressure, flow divergence, pressure divergence, and their rolling means. The latest row of features is fed into the loaded XGBoost model's `predict()` and `predict_proba()` methods. The raw prediction and confidence are added to a 5-element prediction history buffer. A stable leak is declared when ≥3 of the last 5 predictions return 1 and confidence ≥ 0.80. On stable detection, the engine calls `db.reference(f'sensor_readings/{timestamp}/label').set(1)`.

The Flutter mobile app, subscribed to the Firebase listener, detects the label update and immediately renders a "LEAK DETECTED" alert notification. The administrator receives this notification and can tap through to view the associated sensor readings and timeline.

**Figure 4.6: Detailed Sequence Diagram — Leak Detection**

## 4.8 Design Class Diagram

The design class diagram represents the static structure of the software system, showing classes, their attributes, methods, and relationships. The FlowWise class diagram encompasses classes across multiple architectural layers.

**Layer 1: Hardware Interface Layer** — `FlowSensor` (pin, calibrationConstant, pulseCount; readPulses(), getFlowLPM()), `PressureSensor` (pin, baselineVoltage, gainSPU; readRaw(), getSPU()), `ESP32Controller` (deviceId, wifiSSID; connectWiFi(), calibrateBaseline(), publishReading()).

**Layer 2: Cloud Storage Layer** — `FirebaseDatabase` (databaseURL, credential; writeSensorReading(), readWindow(), updateLabel()), `SensorRecord` (timestamp, f1_lmin, f2_lmin, p1_spu, p2_spu, label).

**Layer 3: ML Inference Layer** — `FeatureEngineer` (windowSize; createFeatures(df)), `LeakDetector` (model, windowSize, confidenceThreshold, majorityThreshold; predict(features), isStableLeak(history)), `PredictionBuffer` (size, history; add(pred), getStable()).

**Layer 4: Application Layer** — `MobileApp` (userId; subscribeToAlerts(), renderAnalytics(), displayLeakAlert()), `NotificationService` (firebaseToken; sendPushNotification()).

**Figure 4.7: Class Diagram — FlowWise**

## 4.9 Architectural Diagrams

Architecture serves as a blueprint for the FlowWise system, providing a necessary abstraction to manage complexity and establish clear communication mechanisms among hardware, cloud, and mobile components. The system follows a distributed, cloud-centric architecture.

### 4.9.1 Component Level Design

The component-level design represents the modular parts of FlowWise and their interdependencies. Three primary subsystems are defined:

**Hardware Subsystem (ESP32 + Sensors):** Handles sensor pulse counting, analog pressure oversampling, calibration, and JSON telemetry upload to Firebase. Communicates outward via the Firebase REST API over Wi-Fi.

**Cloud Analytics Subsystem (Python Inference Engine):** Polls Firebase for new sensor records, maintains a sliding window, performs feature engineering, runs XGBoost inference, applies the temporal filter, and writes back prediction labels. Communicates with Firebase using the `firebase_admin` Python SDK.

**Mobile Application Subsystem (Flutter App):** Subscribes to Firebase in real time, renders live flow and pressure charts, surfaces leak alerts, and manages administrator authentication and session state.

**Figure 4.8: Component Level Design**

### 4.9.2 Deployment Diagram

The deployment diagram shows the physical nodes and their communication links. The ESP32 microcontroller (embedded node) communicates with Firebase Realtime Database (Google Cloud) over HTTPS/Wi-Fi. The Python inference engine (a PC or cloud server) also communicates with Firebase over HTTPS. The Flutter mobile application (Android device) communicates with Firebase over HTTPS/cellular or Wi-Fi. Firebase serves as the central data exchange point between all three nodes.

**Figure 4.9: Deployment Diagram**

---

# Chapter 5: SYSTEM TESTING AND VALIDATION

This chapter describes the testing and validation activities conducted to verify that the FlowWise system meets its functional and non-functional requirements. Specifically, it provides evidence that the hardware prototype correctly acquires and transmits sensor data, that the Machine Learning model accurately detects leaks in data produced by the physical sensors, and that the end-to-end system pipeline (hardware → Firebase → inference engine → mobile app) operates correctly in real time. Section 5.1 covers hardware prototype testing. Section 5.2 covers ML model training and evaluation. Section 5.3 covers real-time inference and integration testing. Section 5.4 covers mobile application testing. Section 5.5 covers non-functional requirements evaluation.

## 5.1 Hardware Prototype Testing

### 5.1.1 Purpose and Approach

Hardware testing validates that the ESP32 firmware correctly reads both YF-S201 flow sensors and the HK1100C pressure sensor, and that the published Firebase records match the expected physical state of the pipeline. A black-box testing approach was adopted: the tester controls the physical pipeline state (pump on/off, ball valve open/closed to simulate a leak) and observes the Firebase records to confirm they reflect the correct readings.

### 5.1.2 Sensor Calibration Verification

Before data collection the ESP32 baseline calibration procedure was executed. With the pump off, the firmware averages 250 ADC samples from each pressure sensor input to establish `baseP1` and `baseP2`. Following calibration:

- With the pump running and no leak (ball valve closed), typical observed values are: F1 ≈ 2.7 L/min, F2 ≈ 2.7 L/min, P1_SPU ≈ 2.80, P2_SPU ≈ −0.93. The near-equal inlet and outlet flows confirm no diversion.
- With the leak valve opened (simulated leak), typical observed values are: F1 ≈ 3.0 L/min (slight increase due to pressure release), F2 ≈ 2.4 L/min (reduced downstream flow), P1_SPU ≈ 1.2, P2_SPU ≈ −2.9. The inlet-outlet flow divergence (approximately 0.6 L/min) and pressure drops confirm a physical diversion of water.

These measurements match the signal deltas used in the synthetic data generation script, validating the hardware-simulation alignment.

### 5.1.3 Firebase Upload Verification

Firebase records were inspected during a 5-minute continuous run:

- Data appeared in the `sensor_readings` node within 2 seconds of each measurement cycle.
- All required fields (timestamp, f1\_lmin, f2\_lmin, p1\_spu, p2\_spu, label) were present in every record.
- No missing records were observed during stable Wi-Fi connectivity.
- On deliberate Wi-Fi disconnection and reconnection, the firmware automatically reconnected and resumed uploads within 10 seconds.

**Table 5.1: Hardware Prototype Test Cases**

| Test Case | Condition                          | Expected F1 | Expected F2 | Expected P1_SPU | Result |
|-----------|------------------------------------|-------------|-------------|-----------------|--------|
| TC-H1     | Pump ON, no leak                   | ~2.7 L/min  | ~2.7 L/min  | ~2.8            | PASS   |
| TC-H2     | Pump ON, leak valve open           | ~3.0 L/min  | ~2.4 L/min  | ~1.2            | PASS   |
| TC-H3     | Pump OFF                           | 0 L/min     | 0 L/min     | ~0              | PASS   |
| TC-H4     | Wi-Fi disconnect then reconnect    | —           | —           | —               | PASS   |
| TC-H5     | Firebase record completeness (30 records) | All fields present | — | — | PASS |

## 5.2 ML Model Training and Evaluation

### 5.2.1 Dataset Overview

The training dataset was generated using `datasetgen.ipynb`. The generator was parameterized with baseline values extracted directly from the hardware prototype sensor readings: base flow ≈ 2.7 L/min, inlet pressure SPU ≈ 2.8, outlet pressure SPU ≈ −0.93. Leak-induced signal deltas (F1 +0.28, F2 −0.32, P1 −1.60, P2 −2.00, scaled by leak severity) were derived from experimental observations on the physical prototype with the ball valve open.

The dataset comprises 120 CSV scenario files. Each file contains 300 time steps at 1-second resolution. Five leak magnitude levels (no-leak, very small, small, medium, large), seven leak timing patterns (early short/long, mid short/long, late long, sudden full, spike), and three noise levels (low, medium, high) are represented. The total dataset has 36,000 labeled rows, with approximately 60% no-leak and 40% leak labels.

### 5.2.2 Feature Engineering

The training pipeline in `hardwaretraining.ipynb` applies rolling-window normalization (window = 30 seconds) to eight features:

| Feature            | Description                                               |
|--------------------|-----------------------------------------------------------|
| Flow\_1\_LPM\_Norm  | Min-max normalized inlet flow over 30-s window           |
| Flow\_2\_LPM\_Norm  | Min-max normalized outlet flow over 30-s window          |
| Flow\_Div\_Norm     | Normalized inlet-outlet flow divergence                  |
| Flow\_Div\_Trend    | 30-s rolling mean of flow divergence                     |
| Pres\_1\_SPU\_Norm  | Min-max normalized inlet pressure over 30-s window       |
| Pres\_2\_SPU\_Norm  | Min-max normalized outlet pressure over 30-s window      |
| Pres\_Div\_Norm     | Normalized pressure divergence (P2 − P1)                 |
| Pres\_Div\_Trend    | 30-s rolling mean of pressure divergence                 |

**Table 5.2: Engineered Features Used for Model Training**

Rolling normalization is used instead of global (per-file) normalization because it operates on a fixed lookback window of data already available at inference time, making it directly applicable in real-time operation without knowledge of future data.

### 5.2.3 Model Training Configuration

The XGBoost classifier was trained with the following configuration:

| Parameter           | Value                             |
|---------------------|-----------------------------------|
| n\_estimators        | 150                               |
| max\_depth           | 5                                 |
| learning\_rate       | 0.1                               |
| subsample           | 0.8                               |
| colsample\_bytree    | 0.8                               |
| scale\_pos\_weight   | Computed from class imbalance ratio |
| eval\_metric         | logloss                           |
| tree\_method         | hist                              |

**Table 5.3: XGBoost Training Configuration**

The dataset was split by complete scenarios (not by individual rows) to prevent data leakage: 80 scenarios for training, 24 for validation, 16 for testing. Splitting by scenario ensures the model's generalization is assessed on complete, unseen hydraulic sequences rather than individual rows from the same time series.

### 5.2.4 Evaluation Results

The model was evaluated on the held-out test set of 16 unseen scenarios.

| Metric        | Value   |
|---------------|---------|
| Accuracy      | 96.8%   |
| Precision     | 95.2%   |
| Recall        | 97.4%   |
| F1 Score      | 96.3%   |
| ROC-AUC       | 0.991   |

**Table 5.4: XGBoost Model Evaluation on Test Set**

The high recall (97.4%) confirms that the model reliably catches leak events with very few misses, which is the primary safety-critical requirement. The high precision (95.2%) confirms that false alarms are infrequent. The ROC-AUC of 0.991 demonstrates strong discriminative power across all classification thresholds.

## 5.3 Real-Time Inference and Integration Testing

### 5.3.1 Purpose and Approach

Integration testing validates the complete end-to-end pipeline: ESP32 sensor readings → Firebase upload → Python inference engine reads → features computed → XGBoost prediction → label updated in Firebase → mobile app displays alert. This testing was carried out using the physical hardware prototype with the leak valve both closed (normal condition) and open (leak condition).

### 5.3.2 Test Procedure

1. Start the ESP32 (pump running, no leak): confirm the inference engine outputs "✅ NORMAL" for all readings.
2. Open the ball valve (simulate leak): measure the time from valve opening to the inference engine declaring a stable leak and updating the Firebase label.
3. Close the ball valve (end leak): confirm the inference engine returns to "✅ NORMAL" within the majority-vote window (≤5 seconds).
4. Confirm the mobile app reflects label changes in real time.

### 5.3.3 Results

- **Normal condition:** The inference engine produced a "NORMAL" classification for all 150 consecutive readings tested with the valve closed, with zero false positives (0% false positive rate over 150 samples).
- **Leak detection latency:** After the ball valve was opened, the inference engine declared a stable leak within 4–6 seconds (consistent with the 5-reading majority-vote buffer at 1-second sampling). This is within the < 10-second latency non-functional requirement.
- **Post-leak recovery:** After the valve was closed, the engine returned to "NORMAL" within 5 seconds, consistent with the buffer flushing.
- **Mobile app update:** The label change was reflected in the Flutter app within approximately 1 second of the Firebase write, confirming sub-second Firebase listener responsiveness.

**Table 5.5: Integration Test Results**

| Test Case | Condition              | Expected Result          | Actual Result        | Latency  | Status |
|-----------|------------------------|--------------------------|----------------------|----------|--------|
| TC-I1     | 150 readings, no leak  | 0 false positives        | 0 false positives    | —        | PASS   |
| TC-I2     | Valve open (leak)      | Stable leak declared     | Leak declared        | 4–6 s    | PASS   |
| TC-I3     | Valve closed (no leak) | Return to normal         | Normal within 5 s    | <5 s     | PASS   |
| TC-I4     | App notification       | Label change reflected   | Reflected in <1 s    | <1 s     | PASS   |

## 5.4 Mobile Application Testing

### 5.4.1 Purpose and Approach

The Flutter mobile application was tested using black-box testing to verify that each user-facing feature operates correctly. Test cases were designed for authentication, real-time data display, leak alert notification, and historical trend visualization.

### 5.4.2 Test Cases

| Test Case | Feature                      | Action                                      | Expected Result                              | Status |
|-----------|------------------------------|---------------------------------------------|----------------------------------------------|--------|
| TC-A1     | Authentication               | Login with valid admin credentials           | Access granted, dashboard displayed          | PASS   |
| TC-A2     | Authentication               | Login with invalid credentials              | Error message, access denied                 | PASS   |
| TC-A3     | Real-time flow display       | Pump running, app open                       | F1, F2 charts update every ~2 s              | PASS   |
| TC-A4     | Leak alert notification      | Leak simulated on hardware                  | Alert notification appears within 5 s        | PASS   |
| TC-A5     | Alert cleared after leak     | Valve closed, label returns to 0            | Alert notification dismissed                 | PASS   |
| TC-A6     | Historical trend             | View last 24 hours of data                  | Line chart renders with correct timestamps   | PASS   |
| TC-A7     | Consumption aggregation      | Daily usage screen                          | Correct total flow for the day displayed     | PASS   |

**Table 5.6: Mobile Application Test Cases**

## 5.5 Non-Functional Requirements Evaluation

### 5.5.1 Real-Time Latency

End-to-end latency from a physical leak event at the sensor to an alert appearing in the mobile application was measured at 4–6 seconds across five test runs, well within the ≤10 second requirement.

### 5.5.2 Accuracy and Alert Quality

Over 150 consecutive normal readings, zero false positives were recorded, confirming the temporal majority-vote filter effectively suppresses transient noise without waiting too long to declare a real leak.

### 5.5.3 Connectivity Resilience

During deliberate Wi-Fi disconnection tests the ESP32 automatically reconnected within 10 seconds and resumed uploading to Firebase. The Python inference engine's 5-second retry loop ensured detection resumed immediately upon reconnection. No permanent data loss was observed.

### 5.5.4 Usability

The mobile application was reviewed by two test users (project team members acting as proxy administrators). Both confirmed that: the home dashboard provides an immediately comprehensible view of current network status; the leak alert is prominent and clearly distinguishable; and the historical trend charts are interpretable without training.

**Table 5.7: Non-Functional Requirements Summary**

| NFR                    | Requirement               | Achieved               | Status |
|------------------------|---------------------------|------------------------|--------|
| Real-time latency      | ≤ 10 s end-to-end         | 4–6 s                  | PASS   |
| False positive rate    | Minimized                 | 0/150 normal readings  | PASS   |
| Wi-Fi resilience       | Auto-reconnect            | Reconnects within 10 s | PASS   |
| Firebase sync          | Sub-second app update     | <1 s observed          | PASS   |
| ML recall (test set)   | High (>90%)               | 97.4%                  | PASS   |

---

## References

[1] M. A. Ayamga and C. I. Nakpih, "An IoT-based water leakage detection and localization system," *Journal of Water Resources and Environmental Engineering*, vol. 17, no. 3, pp. 1–14, 2024.

[2] M. Boujelben et al., "Acoustic leak detection and 2D localization based on non-invasive acoustic sensing and lightweight deep learning," *Measurement*, vol. 218, p. 113189, 2023.

[3] I. Bhatti, "Water crisis worsens in Karachi as supply line bursts," *Dawn*, Jul. 13, 2021. [Online]. Available: https://www.dawn.com/news/1634786.

[4] J. Gautam et al., "Monitoring and forecasting water consumption and detecting leakage using an IoT system," *Water Supply*, vol. 20, no. 3, pp. 1103–1113, 2020.

[5] N. Maqbool, "Pakistan's urban water challenges and prospects," *Pakistan Institute of Development Economics (PIDE)*, Knowledge Brief No. 115, 2024. [Online]. Available: https://file.pide.org.pk/pdfpideresearch/kb-115-pakistans-urban-water-challenges-and-prospects.pdf.

[6] "Water crisis exacerbated amid delays in pipeline repairs," *The Express Tribune*, Apr. 12, 2025. [Online]. Available: https://tribune.com.pk/story/2539426/water-crisis-exacerbated-amid-delays-in-pipeline-repairs.
