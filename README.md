# 🏙️ AureaTech — Zona Residencial Simulada
# README DESACTUALIZADO, MIRAR GITHUB PARA LA ULTIMA VERSION

**AureaTech** is an academic software engineering project that simulates a **smart residential area** using an **IoT-inspired architecture**, a **Python backend**, and a **graphical interface built with Flet**.
The system allows different user roles to monitor sensors, control actuators, and inspect historical data, all persisted using **JSON files** and structured under the **Model–View–Controller (MVC)** pattern.

This project has been developed following **SCRUM methodology** as part of *Proyecto de Informática I (PII1)* in the **Bachelor’s Degree in Computer Science Engineering** at **Universidad Europea de Madrid**.

---

## 📌 Project Objectives

The main goal is to design and implement a **functional, modular, and extensible monitoring system** that:

* Simulates data acquisition from multiple sensors
* Differentiates access and views according to **user roles**
* Stores all information using **JSON persistence**
* Provides a **responsive graphical interface**
* Follows **software engineering best practices**

The system is intentionally designed to be **educational**, **portable**, and **demonstrable**, while remaining close to real IoT architectures.

---

## 👥 User Roles

The application supports **three distinct roles**, all accessed through a **single application and login system**:

| Role              | Description                                                 |
| ----------------- | ----------------------------------------------------------- |
| **Administrator** | Manages users, sensors, actuators, and system configuration |
| **Technician**    | Monitors sensor readings, logs, and system behavior         |
| **Neighbor**      | Views simplified sensor data and personal alerts            |

Each role is automatically redirected to a **different dashboard** after login.

---

## 🧠 System Architecture

The project strictly follows the **Model–View–Controller (MVC)** pattern:

```
app/
├── model/          # Domain entities (User, Sensor, Reading, Actuator, Alert, LogEntry)
├── repository/     # Interfaces + JSON-based implementations
├── service/        # Business logic and use cases
├── controller/     # UI controllers (event handling, navigation)
├── view/           # Flet UI components and views
├── infrastructure/ # JSON persistence, configuration, adapters
```

### Key Design Decisions

* **MVC** for separation of concerns and maintainability
* **Repositories + interfaces** to decouple storage from logic
* **JSON files** as a lightweight, transparent persistence layer
* **Service layer** to centralize business rules
* **Role-based navigation** enforced at controller level

---

## 🧪 Sensors & Actuators (Simulated)

The system simulates realistic behavior for common IoT devices:

### Sensors

* **DHT22** — Temperature & humidity
* **LDR** — Ambient light
* **HC-SR04** — Distance / proximity

### Actuators

* Street lighting (ON/OFF)
* Alarm indicators
* Additional simulated actuators

Sensor readings are generated **periodically**, stored with timestamps, and visualized in real time.

---

## 💾 Data Persistence

All data is stored in **JSON files**, ensuring portability and easy inspection:

```
data/
├── users.json
├── sensors.json
├── readings.json
├── actuators.json
├── alerts.json
├── logs.json
```

Features include:

* Historical records
* Log rotation / size control
* Error handling for corrupted or missing files
* Export functionality (JSON)

---

## 🖥️ User Interface

* Built with **Flet (Python)**
* Responsive layout (desktop-first)
* Corporate visual identity (**AureaTech** palette & typography)
* Dynamic dashboards with live updates
* Clear feedback (alerts, errors, confirmations)

---

## 🚀 Installation & Execution

### 1️⃣ Requirements

* **Python 3.10+**
* **pip**
* Recommended IDE: **PyCharm**

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is missing, install manually:

```bash
pip install flet
```

(Additional standard libraries are part of Python)

### 3️⃣ Run the application

From the **project root**:

```bash
flet run app.py
```

> ⚠️ Important: Run the project from the root directory so that **relative paths** work correctly.

---

## 🔐 Authentication

* Unified login & registration system
* Role-based redirection
* Password hashing
* Basic protection against repeated failed attempts
* Session handling at application level

---

## 🧪 Testing Strategy

Testing is **continuous and incremental**, covering:

* **Unit tests** (repositories, services)
* **Integration tests** (MVC flow)
* **Functional tests** (user scenarios per role)
* **Regression tests**
* **Performance simulations** (long-running sensor updates)

Tools used:

* `pytest`
* Manual UI validation
* Automated scripts for core flows

---

## 🧭 Development Methodology

* **SCRUM**
* Iterative development across **4 sprints**
* Product Backlog + Sprint Backlogs
* Daily SCRUMs
* Sprint Reviews & Retrospectives
* Full traceability via actas and documentation

---

## 👨‍💻 Team

**AureaTech – Group 1**

* Daniel de Abajo Nacarino
* Paula Gómez Lucas
* Franco Nahuel Zimmermann
* Pablo Serrano Tirado

---

## 📄 Documentation

The repository is accompanied by:

* Anteproyecto
* Sprint planning & actas
* UML class diagrams
* BPMN test flow
* Corporate identity guide
* Prototype designs (Figma)
* Test plan & validation reports

---

## 🔮 Future Improvements

Planned or optional extensions include:

* Real sensor integration (ESP32 / Arduino)
* Database backend (SQL)
* Fire detection system
* Automatic garage access with license-plate recognition
* Predictive analytics (regression models)
* Mobile deployment

---

## 📜 License

This project is developed **for academic purposes only** as part of *Proyecto de Informática I*.
Reuse for educational purposes is permitted with attribution.
