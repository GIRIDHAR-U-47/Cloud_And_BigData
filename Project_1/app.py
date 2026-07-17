import streamlit as st
import psutil
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import platform
import socket
import time
import os

# Set page configuration
st.set_page_config(
    page_title="System Resource Monitor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# Helper & Utility Functions
# ----------------------------------------------------

def get_size(bytes_val, suffix="B"):
    """
    Scale bytes to its proper format (KB, MB, GB, etc.)
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes_val < factor:
            return f"{bytes_val:.2f} {unit}{suffix}"
        bytes_val /= factor
    return f"{bytes_val:.2f} Y{suffix}"

def get_processor_name():
    """
    Retrieve processor details across OS platforms.
    """
    try:
        if platform.system() == "Windows":
            return platform.processor() or "Unknown Processor"
        elif platform.system() == "Darwin":
            import subprocess
            return subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).strip().decode()
        elif platform.system() == "Linux":
            import subprocess
            all_info = subprocess.check_output("cat /proc/cpuinfo", shell=True).decode()
            for line in all_info.split("\n"):
                if "model name" in line:
                    return line.split(":")[1].strip()
            return platform.processor() or "Unknown Processor"
    except Exception:
        pass
    return platform.processor() or "Generic Processor"

def get_system_uptime():
    """
    Calculate and format the system uptime.
    """
    try:
        boot_time_timestamp = psutil.boot_time()
        uptime_seconds = time.time() - boot_time_timestamp
        days = int(uptime_seconds // (24 * 3600))
        uptime_seconds %= (24 * 3600)
        hours = int(uptime_seconds // 3600)
        uptime_seconds %= 3600
        minutes = int(uptime_seconds // 60)
        seconds = int(uptime_seconds % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        return " ".join(parts)
    except Exception:
        return "Unknown"

# ----------------------------------------------------
# Session State Initialization
# ----------------------------------------------------

# Historical stats
if 'history' not in st.session_state:
    st.session_state.history = {
        'timestamp': [],
        'cpu': [],
        'memory': [],
        'disk': []
    }

# Network counters for speeds
if 'prev_net_stats' not in st.session_state:
    st.session_state.prev_net_stats = None

# Metric deltas tracking
if 'prev_cpu' not in st.session_state:
    st.session_state.prev_cpu = None
if 'prev_mem' not in st.session_state:
    st.session_state.prev_mem = None
if 'prev_disk' not in st.session_state:
    st.session_state.prev_disk = None

if 'prev_upload_rate' not in st.session_state:
    st.session_state.prev_upload_rate = 0.0
if 'prev_download_rate' not in st.session_state:
    st.session_state.prev_download_rate = 0.0

# ----------------------------------------------------
# Sidebar - System Specifications & Dashboard Settings
# ----------------------------------------------------

st.sidebar.markdown("# ⚙️ Dashboard Controls")

# Settings & Theme Toggle
theme_mode = st.sidebar.selectbox("Dashboard Theme Style", ["Dark Mode", "Light Mode"])
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", min_value=1, max_value=10, value=2)
auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=True)

if st.sidebar.button("Clear History"):
    st.session_state.history = {
        'timestamp': [],
        'cpu': [],
        'memory': [],
        'disk': []
    }
    st.sidebar.success("History cleared!")

st.sidebar.markdown("---")
st.sidebar.markdown("# 💻 System Specifications")

# Retrieve general specifications safely
try:
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
except Exception:
    hostname = "Unknown Host"
    ip_address = "Unknown IP"

sys_os = f"{platform.system()} {platform.release()}"
sys_ver = platform.version()
processor = get_processor_name()
phys_cores = psutil.cpu_count(logical=False)
log_cores = psutil.cpu_count(logical=True)

# Fetch RAM and Disk info safely
try:
    total_ram = get_size(psutil.virtual_memory().total)
except Exception:
    total_ram = "Unknown"

try:
    total_disk = get_size(psutil.disk_usage('/').total)
except Exception:
    total_disk = "Unknown"

try:
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
except Exception:
    boot_time = "Unknown"

uptime_str = get_system_uptime()

# Sidebar display fields
st.sidebar.info(f"""
*   **Hostname:** {hostname}
*   **IP Address:** {ip_address}
*   **OS:** {sys_os}
*   **Processor:** {processor}
*   **Physical Cores:** {phys_cores}
*   **Logical Cores:** {log_cores}
*   **Total Memory (RAM):** {total_ram}
*   **Boot Disk Capacity:** {total_disk}
*   **Boot Time:** {boot_time}
*   **Uptime:** {uptime_str}
""")

# ----------------------------------------------------
# Vitals Computation (Main Body)
# ----------------------------------------------------

# Current CPU Percentage
cpu_usage = psutil.cpu_percent(interval=None)

# Current Memory
try:
    mem = psutil.virtual_memory()
    mem_pct = mem.percent
except Exception:
    mem_pct = 0.0
    mem = None

# Current Disk Usage
try:
    disk = psutil.disk_usage('/')
    disk_pct = disk.percent
except Exception:
    disk_pct = 0.0
    disk = None

# Current Network Data and Rates
try:
    net_io = psutil.net_io_counters()
    curr_time = time.time()
    curr_sent = net_io.bytes_sent
    curr_recv = net_io.bytes_recv
    
    if st.session_state.prev_net_stats is not None:
        prev_time, prev_sent, prev_recv = st.session_state.prev_net_stats
        time_diff = curr_time - prev_time
        if time_diff > 0:
            upload_rate = (curr_sent - prev_sent) / time_diff
            download_rate = (curr_recv - prev_recv) / time_diff
        else:
            upload_rate = 0.0
            download_rate = 0.0
    else:
        upload_rate = 0.0
        download_rate = 0.0
        
    st.session_state.prev_net_stats = (curr_time, curr_sent, curr_recv)
except Exception:
    upload_rate = 0.0
    download_rate = 0.0
    net_io = None

# Calculate Metric Deltas
cpu_delta = 0.0
if st.session_state.prev_cpu is not None:
    cpu_delta = cpu_usage - st.session_state.prev_cpu
st.session_state.prev_cpu = cpu_usage

mem_delta = 0.0
if st.session_state.prev_mem is not None and mem is not None:
    mem_delta = mem_pct - st.session_state.prev_mem
st.session_state.prev_mem = mem_pct

disk_delta = 0.0
if st.session_state.prev_disk is not None and disk is not None:
    disk_delta = disk_pct - st.session_state.prev_disk
st.session_state.prev_disk = disk_pct

upload_delta = upload_rate - st.session_state.prev_upload_rate
st.session_state.prev_upload_rate = upload_rate

download_delta = download_rate - st.session_state.prev_download_rate
st.session_state.prev_download_rate = download_rate

# Update rolling history list
current_time_str = datetime.datetime.now().strftime("%H:%M:%S")
st.session_state.history['timestamp'].append(current_time_str)
st.session_state.history['cpu'].append(cpu_usage)
st.session_state.history['memory'].append(mem_pct)
st.session_state.history['disk'].append(disk_pct)

# Max window size (keep last 30 readings ~1 min at 2s interval)
max_history_length = 30
if len(st.session_state.history['timestamp']) > max_history_length:
    for key in st.session_state.history:
        st.session_state.history[key].pop(0)

# ----------------------------------------------------
# Main UI Layout
# ----------------------------------------------------

st.title("🖥️ System Resource Monitoring Dashboard")
st.markdown("A premium real-time visualization tool analyzing CPU, memory, disk storage, and network statistics.")
st.markdown("---")

# Metrics Cards row
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    label="CPU Utilization",
    value=f"{cpu_usage:.1f}%",
    delta=f"{cpu_delta:+.1f}%",
    delta_color="inverse"
)
if mem is not None:
    col2.metric(
        label="Memory Utilization",
        value=f"{mem_pct:.1f}%",
        delta=f"{mem_delta:+.1f}%",
        delta_color="inverse"
    )
else:
    col2.metric(label="Memory Utilization", value="N/A")

if disk is not None:
    col3.metric(
        label="Disk Utilization",
        value=f"{disk_pct:.1f}%",
        delta=f"{disk_delta:+.1f}%",
        delta_color="inverse"
    )
else:
    col3.metric(label="Disk Utilization", value="N/A")

col4.metric(
    label="Upload Speed",
    value=f"{get_size(upload_rate)}/s",
    delta=f"{get_size(upload_delta)}/s" if upload_delta != 0 else None
)
col5.metric(
    label="Download Speed",
    value=f"{get_size(download_rate)}/s",
    delta=f"{get_size(download_delta)}/s" if download_delta != 0 else None
)

st.markdown("### 📊 Live Resource Allocation Vitals")
# Visual progress indicators
c_prog1, c_prog2, c_prog3 = st.columns(3)
with c_prog1:
    st.write(f"**CPU Vitals**")
    st.progress(float(cpu_usage / 100.0))
with c_prog2:
    if mem is not None:
        st.write(f"**Memory Vitals** ({get_size(mem.used)} / {total_ram})")
        st.progress(float(mem_pct / 100.0))
with c_prog3:
    if disk is not None:
        st.write(f"**Disk Vitals** ({get_size(disk.used)} / {total_disk})")
        st.progress(float(disk_pct / 100.0))

st.markdown("---")

# Visual Graphs Row
g_col1, g_col2 = st.columns(2)

# Theme-specific color parameters
if theme_mode == "Dark Mode":
    text_color = "#E0E0E0"
    label_color = "#A0A0A0"
    grid_color = "#444444"
    border_color = "#333333"
else:
    text_color = "#2E2E2E"
    label_color = "#4F4F4F"
    grid_color = "#E0E0E0"
    border_color = "#CCCCCC"

def make_chart(timestamps, data_series, title, ylabel="% Percentage"):
    """
    Renders customizable dark/light Matplotlib line plot with transparent canvas.
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # Enable transparent backgrounds to mesh with Streamlit styling
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    for label, data in data_series.items():
        if label == "CPU":
            line_color = "#00F2FE" if theme_mode == "Dark Mode" else "#008B8B"
        elif label == "Memory":
            line_color = "#4FACFE" if theme_mode == "Dark Mode" else "#1E90FF"
        elif label == "Disk":
            line_color = "#F35588" if theme_mode == "Dark Mode" else "#D32F2F"
        else:
            line_color = "#8A2BE2"

        ax.plot(timestamps, data, label=label, color=line_color, linewidth=2.5, marker='o', markersize=4)
        
    ax.set_title(title, color=text_color, fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel(ylabel, color=label_color, fontsize=9)
    ax.set_ylim(-5, 105)
    
    ax.grid(True, linestyle=":", alpha=0.5, color=grid_color)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(border_color)
    ax.spines['bottom'].set_color(border_color)
    ax.tick_params(colors=label_color, labelsize=8)
    
    if len(timestamps) > 0:
        step = max(1, len(timestamps) // 5)
        ax.set_xticks(range(0, len(timestamps), step))
        ax.set_xticklabels([timestamps[i] for i in range(0, len(timestamps), step)], rotation=30, ha='right')
        
    legend = ax.legend(facecolor='none', edgecolor='none', labelcolor=text_color, fontsize=9)
    if legend:
        legend.get_frame().set_alpha(0.0)
        
    fig.tight_layout()
    return fig

# Render Graphs
with g_col1:
    cpu_mem_data = {
        "CPU": st.session_state.history['cpu'],
        "Memory": st.session_state.history['memory']
    }
    fig1 = make_chart(st.session_state.history['timestamp'], cpu_mem_data, "CPU & Memory Utilization History")
    st.pyplot(fig1)

with g_col2:
    disk_data = {
        "Disk": st.session_state.history['disk']
    }
    fig2 = make_chart(st.session_state.history['timestamp'], disk_data, "Disk Storage Utilization History")
    st.pyplot(fig2)

st.markdown("---")

# Expandable Sections
st.markdown("### 🔍 System Breakdown Vitals")

# Section 1: Detailed CPU Core utilization
with st.expander("🧩 CPU Core Utilization Breakdowns"):
    core_percents = psutil.cpu_percent(interval=None, percpu=True)
    c_cols = st.columns(min(len(core_percents), 4))
    for idx, pct in enumerate(core_percents):
        col_slot = c_cols[idx % 4]
        with col_slot:
            st.write(f"**Core {idx}**")
            st.metric(label=f"Core {idx} Load", value=f"{pct:.1f}%")
            st.progress(float(pct / 100.0))

# Section 2: Detailed Disk Partitions
with st.expander("💾 Storage Partitions Details"):
    try:
        partitions = psutil.disk_partitions()
        partition_list = []
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partition_list.append({
                    "Mountpoint": partition.mountpoint,
                    "Device": partition.device,
                    "File System": partition.fstype,
                    "Total Size": get_size(usage.total),
                    "Used": get_size(usage.used),
                    "Free": get_size(usage.free),
                    "Percentage": f"{usage.percent}%"
                })
            except (PermissionError, FileNotFoundError):
                # Certain system mounts may reject queries or fail
                continue
        if len(partition_list) > 0:
            df_disk = pd.DataFrame(partition_list)
            st.dataframe(df_disk, use_container_width=True)
        else:
            st.info("No partition information available.")
    except Exception as e:
        st.error(f"Error gathering partition details: {e}")

# Section 3: Detailed Network Stats
with st.expander("🌐 Network Interfaces & Configurations"):
    try:
        net_addrs = psutil.net_if_addrs()
        interface_list = []
        for interface, addrs in net_addrs.items():
            ip_v4 = "N/A"
            mac_addr = "N/A"
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ip_v4 = addr.address
                elif hasattr(psutil, 'AF_LINK') and addr.family == psutil.AF_LINK:
                    mac_addr = addr.address
                elif platform.system() != "Windows" and hasattr(socket, 'AF_LINK') and addr.family == socket.AF_LINK:
                    mac_addr = addr.address
            
            interface_list.append({
                "Interface": interface,
                "IPv4 Address": ip_v4,
                "MAC Address": mac_addr
            })
            
        if len(interface_list) > 0:
            df_net = pd.DataFrame(interface_list)
            st.dataframe(df_net, use_container_width=True)
        else:
            st.info("No network interface configurations detected.")
    except Exception as e:
        st.error(f"Error gathering network details: {e}")

# ----------------------------------------------------
# Auto Refresh Execution Loop
# ----------------------------------------------------
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()
