# Presentation Slides Outline - Project Flowise

This document contains the slide-by-slide text content for the PowerPoint presentation.

---

### Slide 1: Title Slide
*   **Main Title:** Flowise
*   **Subtitle:** Real-Time IoT & Machine Learning Water Leak Detection System
*   **Context:** Technical Funding Proposal for Physical Pipeline Test-Bed
*   **Team Members:** 
    *   Sara Khan (NUML-F22-31354)
    *   Batool Tariq (NUML-F22-16916)
    *   BSCS 8-A (Morning)
*   **Supervisor:** Ms. Qurat-ul-Ain Raja
*   **Institution:** Department of Computer Science, National University of Modern Languages (NUML), Islamabad

---

### Slide 2: Problem Statement & Project Objectives
*   **Heading:** Problem Statement & Project Objectives
*   **Key Points:**
    *   **The National Crisis:** Pakistan is rapidly approaching absolute water scarcity, yet urban distribution networks waste **30% to 40%** of municipal water due to delayed, manual leak detection.
    *   **The Flowise Solution:** An automated IoT and machine learning system that detects leakages and triggers notifications within seconds.
    *   **Our Objectives:**
        *   *Telemetry Node:* Build a sensor module for high-frequency hydraulic data acquisition.
        *   *Cloud Pipeline:* Sync live pressure and flow rates with a centralized database.
        *   *Machine Learning:* Train and deploy a classifier with temporal noise filters.
        *   *Alert App:* Deliver real-time telemetry charting and push notifications.
        *   *Physical Validation:* Verify system latency and accuracy on a physical pipeline rig.

---

### Slide 3: System Architecture
*   **Heading:** End-to-End System Architecture
*   **Architecture Flow:**
    *   **1. Sensing (Edge):** An intelligent controller reads pipe pressure and flow rates from physical sensor nodes.
    *   **2. Database (Telemetry):** Periodic telemetry packets are written securely to a cloud database.
    *   **3. Inference (Cloud):** A cloud service reads telemetry, computes rolling window trends, and runs the Machine Learning model.
    *   **4. Noise Filter:** A temporal voting filter stabilizes predictions and filters out sensor noise.
    *   **5. Alert (Mobile):** A mobile dashboard displays live updates and instant leak alerts.

---

### Slide 4: System Integration & Software
*   **Heading:** Full-System Integration & Software
*   **Key Points:**
    *   **Physical Testbed (Hardware):** Closed-loop pressurized PVC pipeline rig with flow sensors, pressure transmitters, and rechargeable battery power management to capture real-world data.
    *   **Leak Classifier (Machine Learning):** Real-time analysis of flow differences and pressure changes using an intelligent model, stabilized by a voting filter to prevent false alarms.
    *   **User Dashboard (Mobile Application):** Live telemetry visualization, secure user login, daily consumption logging, and instant push notification alerts when leakages occur.

---

### Slide 5: Hardware Components & Cost Breakdown
*   **Heading:** Prototype Development Budget
*   **Key Points:**
    *   **Total Cost:** **30,000 PKR** overall prototype development cost.
    *   **Requested Funding:** **25,050 PKR** technical grant request.
    *   **Financial Burden:** 15,000 PKR per student (unfeasible for a two-student group).
*   **Itemized Cost Breakdown Table:**
    *   *Pipeline Infrastructure & Base:* **9,980 PKR**
    *   *Sensing Module (Flow & Pressure):* **7,900 PKR**
    *   *IoT & Processing Unit (Microcontroller, Power Management, Battery Pack):* **2,120 PKR**
    *   *Signal Conditioning & Voltage Regulators (Amplifier, Regulators):* **1,250 PKR**
    *   *Circuitry & Auxiliary Hardware:* **1,516 PKR**
    *   *Fluid Dynamics Hardware (Pump, Adapter):* **760 PKR**
    *   *Logistics (Shipping & Taxes):* **1,524 PKR**
    *   *Total Grant Request:* **25,050 PKR**

---

### Slide 6: Expected Deliverables & Social Impact
*   **Heading:** Deliverables & Social Impact
*   **Key Points:**
    *   **Validated Physical Testbed:** A fully operational closed-loop pipeline testbed for system testing, validation, and academic research.
    *   **Multi-Scale Leak Detection:** Accurate classification of pipeline leakage events, ranging from small pinhole cracks to major pipe bursts.
    *   **Water Quality Protection:** Preserving water hygiene by preventing external contaminant seepage through rapid detection and prompt maintenance.
    *   **Water Resource Preservation:** A scalable framework designed to mitigate urban distribution system losses by 30-40%.
    *   **Low Latency Alerts:** End-to-end detection, analysis, and notification completed in under 10 seconds.
    *   **Digital Audit Trail:** Secure, long-term historical database logging of pressure and flow telemetry for predictive analysis.

---

### Slide 7: Future Scalability & Commercialization
*   **Heading:** Scalability and Commercialization Potential
*   **Key Points:**
    *   **Multi-Node Leak Localization:** Expanding the system to a sensor mesh network. By analyzing pressure differential curves and flow differences across nodes, the system can localize the exact leak coordinates within a larger network.
    *   **Automated Flow Isolation (Smart Valves):** Integrating motorized control valves that can automatically or remotely shut off flow via the mobile app to isolate sections immediately during a pipe burst.
    *   **Consumer Telemetry Dashboard:** Deploying household-specific dashboards that allow consumers to monitor live usage trends, promoting self-awareness and encouraging water conservation.
    *   **Municipal Enterprise Dashboards:** Centralized platforms for municipal water utility operators to monitor city mains, automate leak alerts, and audit water distribution metrics.
    *   **Smart Residential Integration:** Implementation in smart housing societies to reduce water waste and automate billing audits.
    *   **Edge Intelligence:** Quantize the machine learning model to run directly on the edge controller. This enables localized inference, reducing cloud reliance, latency, and database operating costs.

---

### Slide 8: Conclusion & Final Appeal
*   **Heading:** Flowise: Smarter Water Management for Pakistan
*   **Key Points:**
    *   Flowise bridges the gap between IoT hardware, cloud databases, and Machine Learning to resolve a critical national crisis.
    *   We have successfully built a fully functioning software architecture and a verified hardware prototype.
    *   A technical grant of **25,050 PKR** will offset student expenses, enabling us to deliver a complete, validated physical test-bed.
    *   *We look forward to your favorable consideration and guidance.*
    *   **Thank you.**
