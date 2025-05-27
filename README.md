# SentryIoT - Real-time Ransomware Detection & Response for IoT Devices

SentryIoT is a smart, automated threat detection and response system tailored for low-end IoT environments. Using machine learning, it analyzes network traffic and shuts down the compromised device’s network interface if ransomware activity (specifically WannaCry) is detected. The system provides a live monitoring dashboard and a centralized GUI to control backend, frontend, and detection models.

---

## 🚀 Features

* 🔐 **Real-time Ransomware Detection** using a trained XGBoost model.
* 📊 **Live Dashboard** (React frontend + Flask backend).
* 📉 **Network Traffic Analysis** from IoT devices.
* 🔌 **Remote Interface Shutdown** on detection of WannaCry.
* 🖥️ **Unified GUI** to start/stop all modules with log visibility (Tkinter desktop app).
* 📂 **Logging** of all detection events in JSONL format.
* 💡 Works on low-spec virtual IoT environments.

---

## 🗂️ Project Structure

```
SentryIoT/
├── backend/
│   ├── dashboard_api.py
│   ├── detection_log.jsonl
├── frontend/
│   ├── ... (React App)
├── model/
│   ├── watcher.py
│   ├── network_model.py
│   ├── xgboost_model.pkl
│   ├── scaler.pkl
├── sentryiot_gui.py  # Unified control panel (Tkinter)
├── captured_data/
│   ├── *.txt  # Network traffic samples
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/SentryIoT.git
cd SentryIoT
```

### 2. Backend

```bash
cd backend
pip install flask flask-cors
python3 dashboard_api.py
```

### 3. Frontend

```bash
cd frontend
npm install
npm start
```

### 4. Model (Detection)

```bash
cd model
python3 watcher.py
```

### 5. Launch the GUI (Unified Control Panel)

```bash
python3 sentryiot_gui.py
```

---

## 💠 Dependencies

* Python 3.10+
* Flask, Flask-CORS
* scikit-learn, xgboost, pandas, numpy
* paramiko
* React (frontend)
* Tkinter (Python built-in GUI)
* `npm` (for React)

---

## 🧪 How It Works

1. **IoT device** captures packet data and sends it to `captured_data/` as `.txt`.
2. `watcher.py` triggers on new files, invokes `network_model.py` to classify.
3. If ransomware is detected:

   * Interface is shut down via SSH.
   * Status is updated in `interface_status.json`.
4. **Flask backend** serves latest detection data.
5. **React frontend** polls and visualizes updates.
6. **Tkinter GUI** controls backend/frontend/model launch and shows logs.

---

## 📈 Output Logs

* `detection_log.jsonl`: Each detection is appended here.
* `interface_status.json`: Holds current network state (`active` or `disabled`).

---

## 📸 Dashboard Preview

![Dashboard Screenshot](./assets/dashboard_preview.png) <!-- Replace with actual path -->

---

## 📝 License

This project is licensed under the MIT License.
