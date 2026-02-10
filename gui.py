import tkinter as tk
from tkinter import ttk
from a2s import info, players
import json
import threading

# --- CONFIGURATION ---
JSON_FILE = "admins.json"
SERVER_IPS = {
    "Server 1": "46.174.52.88:27021",
    "Server 2": "45.136.205.44:28029",
    "Server 3": "45.136.205.44:28020",
    "Server 5": "91.103.255.22:28045",
}

# Load admin data once at startup
try:
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        ADMINS_DATA = json.load(f)
    ADMIN_NAMES = {a["name"] for a in ADMINS_DATA["admins"]}
except FileNotFoundError:
    print(f"Error: {JSON_FILE} not found. Please create it.")
    ADMIN_NAMES = set() # Continue with an empty set if file is missing
except json.JSONDecodeError:
    print(f"Error: Could not decode {JSON_FILE}. Please check its format.")
    ADMIN_NAMES = set()

# --- APPLICATION LOGIC ---
def check_servers_thread():
    """Runs the server check in a separate thread to avoid freezing the UI."""
    root.after(0, lambda: update_ui_state("checking"))
    
    server_list.delete(0, tk.END)
    admin_table.delete(*admin_table.get_children())

    for server_name, ip_string in SERVER_IPS.items():
        host, port_str = ip_string.split(":")
        address = (host, int(port_str))
        
        try:
            server_info = info(address) #type: ignore
            players_data = players(address) #type: ignore
            
            found_admins = []
            for p in players_data:
                if p.name in ADMIN_NAMES:
                    found_admins.append(p.name)
            
            if found_admins:
                status_dot = "✅"
                for admin_name in found_admins:
                    admin_table.insert("", tk.END, values=(admin_name, server_info.server_name))
            else:
                status_dot = "❌"
            
            server_list.insert(tk.END, f"{status_dot} {server_info.server_name}")

        except Exception:
            server_list.insert(tk.END, f"⚠️ {server_name} (оффлайн)")
            
    root.after(0, lambda: update_ui_state("ready"))

def update_ui_state(state):
    """Updates UI elements based on the current state."""
    if state == "checking":
        status_bar.config(text="Статус: Проверка серверов...")
        start_button.config(state="disabled", text="Проверка...")
    elif state == "ready":
        status_bar.config(text="Статус: Готово")
        start_button.config(state="normal", text="Старт")

# --- UI SETUP ---
def create_ui():
    """Creates and arranges all UI widgets."""
    # Main Paned Window
    paned_window = ttk.PanedWindow(root, orient="horizontal")
    paned_window.pack(fill="both", expand=True, padx=10, pady=5)

    # Left Frame (Servers)
    left_frame = ttk.Frame(paned_window)
    paned_window.add(left_frame, weight=1)

    ttk.Label(left_frame, text="Сервера", font=("Arial", 12, "bold")).pack(anchor="w", padx=5, pady=2)
    server_list = tk.Listbox(left_frame, font=("Arial", 10))
    server_list.pack(fill="both", expand=True, padx=5, pady=5)

    # Right Frame (Admins)
    right_frame = ttk.Frame(paned_window)
    paned_window.add(right_frame, weight=2)

    ttk.Label(right_frame, text="Админы онлайн", font=("Arial", 12, "bold")).pack(anchor="w", padx=5, pady=2)
    
    columns = ("Админ", "Сервер")
    admin_table = ttk.Treeview(right_frame, columns=columns, show="headings")
    admin_table.heading("Админ", text="Ник админа")
    admin_table.heading("Сервер", text="Сервер")
    admin_table.column("Админ", width=150, anchor="w")
    admin_table.column("Сервер", width=200, anchor="w")
    
    # Scrollbar for the admin table
    scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=admin_table.yview)
    admin_table.configure(yscrollcommand=scrollbar.set)
    
    admin_table.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
    scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)

    # Bottom Frame (Button and Status)
    bottom_frame = ttk.Frame(root)
    bottom_frame.pack(fill="x", padx=10, pady=5)

    start_button = ttk.Button(bottom_frame, text="Старт", command=start_check)
    start_button.pack(fill="x")

    status_bar = ttk.Label(bottom_frame, text="Статус: Готово", relief="sunken", anchor="w")
    status_bar.pack(fill="x", pady=(5, 0))
    
    return server_list, admin_table, start_button, status_bar

def start_check():
    """Initiates the server check in a new thread."""
    thread = threading.Thread(target=check_servers_thread, daemon=True)
    thread.start()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Cybershoke Jail Admins Monitor")
    root.geometry("700x400")
    root.resizable(True, True)

    server_list, admin_table, start_button, status_bar = create_ui()
    
    root.mainloop()
