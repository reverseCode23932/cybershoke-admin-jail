from a2s import info, players
from windows_toasts import Toast, WindowsToaster
import json

toaster = WindowsToaster('Cybershoke Jail Admins Monitor py')

json_file = "admins.json"

ADMINS_DATA = json.load(open(json_file, "r", encoding="utf-8"))

SERVER_IPS = {"1":"46.174.52.88:27021",
              "2":"45.136.205.44:28029",
              "3":"45.136.205.44:28020",
            }

try:
    for ip in SERVER_IPS:
        address = (SERVER_IPS[ip].split(":")[0], int(SERVER_IPS[ip].split(":")[1]))
        info_data = info(address)#type: ignore
        players_data = players(address) #type: ignore

        admin_names = {a["name"] for a in ADMINS_DATA["admins"]}

        found = False
        for p in players_data:
            if p.name in admin_names:
                found = True
                newToast = Toast()
                newToast.text_fields = [
                    f"Admin {p.name} is online!",
                    f"Server: {info_data.server_name}"
                ]
                toaster.show_toast(newToast)

        if not found:
            print(f"на сервере {ip} нету админов онлайн")

except Exception as e:
    print(f"ошибка: {e}")