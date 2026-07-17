# 📊 System Resource Monitoring Dashboard

A modern, interactive, and responsive real-time resource monitoring application built with Python, Streamlit, psutil, matplotlib, and pandas. 

This dashboard provides deep insights into your computer's performance, resource utilization, and system specifications in a clean, visual layout.

---

## ✨ Features

- **Real-Time Vitals Tracking**: Continuous monitoring of CPU Usage (%), Memory Usage (%), Disk Storage Usage (%), and Network Speeds (Upload & Download rates).
- **Rolling Performance History**: Maintains a sliding buffer of the last 30 readings to render dynamic Matplotlib history charts for CPU, memory, and disk.
- **Detailed System Specifications**: Shows Hostname, IP address, OS kernel version, exact CPU model, physical/logical CPU cores count, total system RAM, boot disk size, boot time, and uptime.
- **Granular Hardware Breakdowns**:
  - **CPU Core Breakdown**: Utilization percentage tracked per individual core.
  - **Storage Partition List**: Table detailing all partition mount points, file system types, absolute total/used/free space, and percent allocations.
  - **Network Configuration**: Interface connections, corresponding IPv4 and MAC addresses.
- **Theme Versatility**: Easily toggle styling between **Dark Mode** and **Light Mode** to customize visual colors and charts formatting.
- **Customizable Refresh Control**: Adjustable sliders to modify refresh interval speeds (1s to 10s) with a pause toggle and history reset command.
- **Universal Multi-Platform Support**: Fully compatible across **Windows**, **Linux**, and **macOS**.

---

## 🛠️ Prerequisites

- **Python**: Python `3.8` or newer installed.
- **Libraries**: `streamlit`, `psutil`, `matplotlib`, and `pandas`.

---

## 🚀 Installation & Execution

Follow these step-by-step instructions to run the application locally.

### 1. Set Up the Project Directory
Clone or extract this folder to your local machine and navigate into it:
```bash
cd Project_1
```

### 2. Create and Activate a Virtual Environment (Recommended)

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install all the required python packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Launch the Dashboard
Run the Streamlit server command to open the application in your browser:
```bash
streamlit run app.py
```
> The dashboard will automatically open in a new tab at [http://localhost:8501](http://localhost:8501).

---

## 📂 Codebase Architecture

- [app.py](file:///e:/Project_1/app.py): The main Python code including resource calculations, plotting logic, session state cache storage, and dashboard layout structure.
- [requirements.txt](file:///e:/Project_1/requirements.txt): List of python dependency packages required for execution.
- [README.md](file:///e:/Project_1/README.md): Instructions manual.

---

## 🛡️ License

This project is open-source and free to distribute under the MIT License.
