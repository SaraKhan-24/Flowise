# LETTER OF SUPPORT AND JUSTIFICATION

**Date:** May 24, 2026  
**To:**  
Dr. Muhammad Noman Malik  
Dean, Faculty of Engineering and Computing  
National University of Modern Languages (NUML), Sector H-9, Islamabad  

**Through:**  
Head of Department (HoD), Department of Computer Science  
National University of Modern Languages (NUML), Islamabad  

**Subject: Request for Technical Funding Allocation – Project "Flowise"**  

---

**Respected Sir,**

We are writing to formally request a technical grant of **25,050 PKR** for our Final Year Project (FYP) titled **"Flowise: Solution for Detecting and Preventing Water Leaks in Pakistan's Urban Infrastructure,"** supervised by **Ms. Qurat-ul-Ain Raja**.

### 1. Significance of the Project
Pakistan is rapidly approaching absolute water scarcity, a crisis compounded by the severe inefficiencies in our municipal water distribution systems. Urban centers like Islamabad and Karachi lose an estimated **30% to 40% of their treated water** to undetected pipe leakages before it reaches consumers. The current leak detection methodology in Pakistan is highly manual, retrospective, and reactive. Leaks are typically reported only after visual surface flooding occurs, leading to days of wasted clean water, road damage, and contamination of drinking water lines by sewage infiltration.

Project **Flowise** addresses this critical national priority by introducing an automated, real-time IoT and Machine Learning (ML) solution. By immediately identifying leaks at the onset, municipal authorities can dramatically reduce Non-Revenue Water (NRW), conserve precious water reserves, and minimize infrastructure damage.

### 2. Innovation Potential
Flowise implements a high-fidelity, closed-loop IoT-to-Cloud architecture:
*   **Edge Telemetry (IoT Node):** An ESP32 microcontroller intercepts high-frequency pulse frequencies from Hall-effect flow sensors (YF-S201) and reads high-precision analog signals from pressure transmitters (HK1100C) installed along a pressurized pipe segment.
*   **Cloud Inference Pipeline:** Data is pushed atomically to a Firebase Realtime Database. A cloud-hosted Python server running an XGBoost classifier analyzes the structured hydraulic features (flow rate differences, rolling averages, pressure trend slope) 24/7 to predict leakage events.
*   **Temporal Noise Filtering:** The cloud pipeline applies a majority-vote filter on consecutive ML predictions to filter out transient pressure spikes and sensor noise, ensuring stable notifications.
*   **Instant Alerts (Flutter Mobile App):** A cross-platform mobile dashboard displays live flow and pressure charts. If a leak is predicted, the application triggers push notifications and visual warnings instantly, enabling rapid response under 10 seconds.

Unlike expensive acoustic leak detectors or rigid rule-based threshold systems, Flowise combines flow divergence and pressure trend monitoring in a lightweight machine learning engine that adapts to physical pipeline behaviors.

### 3. Current Progress Achieved
We have successfully developed the end-to-end software and data frameworks:
*   **Model Training:** The XGBoost model was initially trained on **87 synthetic hydraulic scenarios** representing a baseline, standard operations, and leak events. This base model achieved an accuracy of **95.35%** and a recall of **95.26%** on the synthetic validation set.
*   **Mobile & Cloud Pipeline:** The Flutter mobile application and Hugging Face cloud-hosted inference service are fully functional. Telemetry streams continuously from Firebase.
*   **Hardware Prototype Construction:** We designed and built a localized pressurized PVC pipeline prototype (~1.6-meter loop, 20mm diameter) equipped with a 12V DC pump and manual ball valves to simulate leaks and record physical data.
*   **Hardware Fine-Tuning:** To handle real-world sensor drift and environmental noise, we gathered data from **28 hardware test scenarios** and fine-tuned the XGBoost model (using a lower learning rate of 0.005). The fine-tuned model achieved **83.96% accuracy** and a crucial **90.99% recall** on physical hardware tests, validating the feasibility of our approach.

### 4. Requirement for Departmental Funding
As a two-student group (Sara Khan and Batool Tariq), the financial overhead of this physical implementation has been exceptionally high. The total development and component costs for constructing the physical pipeline testbed and the electronic controller system amounted to **30,000 PKR**. This averages to a self-funded burden of **15,000 PKR per student**, which exceeds our financial capacity as undergraduate students.

To offset the specialized high-precision components required to generate the real-world dataset and validate our ML models, we are requesting a technical grant of **25,050 PKR**. This grant will cover the core physical pipeline components, sensing transmitters, circuitry, power subsystem, and logistics, reducing our out-of-pocket expenses to a manageable level.

The finalized budget for the physical prototype development is itemized below:

| # | Component Category | Specific Items Included | Cost (PKR) |
|---|--------------------|-------------------------|------------|
| 1 | **Pipeline Infrastructure & Base** | Custom 5mm Acrylic Mounting Base (27" x 30.5") and Pipe Network (Pipes, Valves, Connectors) | **9,980** |
| 2 | **Sensing Module** | HK1100C Pressure Sensors and YF-S201 Flow Sensors | **7,900** |
| 3 | **IoT & Processing** | ESP32 Microcontroller, 18650 Li-ion Batteries, 2s BMS, and Charging Module | **2,120** |
| 4 | **Regulators & Signal Processing** | ADS1115 Amplifier and Voltage Regulators (AMS1117, LM2596) | **1,250** |
| 5 | **Circuitry & Auxiliary Hardware** | Breadboards, Jumper Wire Sets, Toggle Switches, and Resistors | **1,516** |
| 6 | **Fluid Dynamics Hardware** | 12V DC Water Pump, 24W Power Adapter, and Terminal Connectors | **760** |
| 7 | **Logistics** | Cumulative Shipping Charges and Taxes | **1,524** |
|   | **Total Requested Funding** | | **25,050 PKR** |

### 5. Expected Outcomes and Impact
With this funding, Project Flowise delivers:
1.  **Validated Physical Testbed:** A fully operational multi-sensor physical pipeline testbed capable of simulating leaks at various positions and flow rates, acting as a resource for future IoT research.
2.  **Conserved Municipal Water:** A demonstrated technology that enables leak detection and response within 10 seconds of occurrence, replacing traditional inspections that take days.
3.  **Open Dataset:** A clean, labeled dataset of physical water flow and pressure telemetry under leak conditions, which can be shared with the department.
4.  **Academic Publications:** The results from this end-to-end physical validation are intended to be submitted to a peer-reviewed computing conference.

We hope for your favorable consideration regarding this financial support to ensure the technical objectives of our project are successfully completed.

Respectfully yours,

**The Flowise Project Team:**  
*Sara Khan* (NUML-F22-31354)  
*Batool Tariq* (NUML-F22-16916)  
BSCS 8-A (Morning)  
Department of Computer Science  
Faculty of Engineering and Computing  
National University of Modern Languages, Islamabad  

---

**Endorsement by Supervisor:**  
*"I have reviewed the progress of the Flowise project team. The physical prototype is critical to completing the model training and validating the accuracy of the leak detection engine. I strongly endorse their request for funding of 25,050 PKR."*  

___________________________  
**Ms. Qurat-ul-Ain Raja**  
Supervisor, Department of Computer Science  
National University of Modern Languages, Islamabad  
