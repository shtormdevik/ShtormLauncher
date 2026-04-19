import customtkinter as ctk
import minecraft_launcher_lib
import subprocess
import os
import uuid
import threading
import json

# Настройки путей на диске D
base_dir = "D:\\Mylacnher"
mine_dir = os.path.join(base_dir, "minecraft_data")
mods_dir = os.path.join(mine_dir, "mods")
config_file = os.path.join(base_dir, "config.json")

# Создаем папки при запуске
for folder in [mine_dir, mods_dir]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def save_config(username, version, ram):
    try:
        data = {"username": username, "version": version, "ram": ram}
        with open(config_file, "w") as f:
            json.dump(data, f)
    except:
        pass

def load_config():
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except:
            pass
    return {"username": "Shtorm_Player", "version": "1.21.4", "ram": 4}

conf = load_config()

class ShtormLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SHTORM LAUNCHER PRO V3.0")
        self.geometry("550x700")
        self.current_max = 0

        # Основной заголовок
        ctk.CTkLabel(self, text="SHTORM LAUNCHER PRO", font=("Arial", 28, "bold")).pack(pady=20)

        # Поле ввода ника
        self.entry = ctk.CTkEntry(self, placeholder_text="Никнейм", width=300, height=40)
        self.entry.insert(0, conf["username"])
        self.entry.pack(pady=10)

        # Выбор версии
        self.version_menu = ctk.CTkOptionMenu(self, values=["1.12.2", "1.16.5", "1.18.2", "1.20.1", "1.21.4"], width=300)
        self.version_menu.set(conf["version"])
        self.version_menu.pack(pady=10)

        # Настройка ОЗУ
        ctk.CTkLabel(self, text="Выделение ОЗУ (ГБ):", font=("Arial", 14)).pack()
        self.ram_slider = ctk.CTkSlider(self, from_=2, to=16, number_of_steps=7, command=self.update_ram_label)
        self.ram_slider.set(conf["ram"])
        self.ram_slider.pack(pady=5)
        self.ram_label = ctk.CTkLabel(self, text=f"{int(self.ram_slider.get())} ГБ")
        self.ram_label.pack()

        # Прогресс-бар
        self.label_perc = ctk.CTkLabel(self, text="0%", font=("Arial", 16, "bold"), text_color="#3498db")
        self.label_perc.pack(pady=(20, 0))
        self.progressbar = ctk.CTkProgressBar(self, width=400, height=20)
        self.progressbar.set(0)
        self.progressbar.pack(pady=10)
        
        self.status_label = ctk.CTkLabel(self, text="Готов к работе", font=("Arial", 14))
        self.status_label.pack()

        # Кнопка запуска
        self.btn = ctk.CTkButton(self, text="В БОЙ!", command=self.start_thread, fg_color="#27ae60", height=60, font=("Arial", 20, "bold"), width=300)
        self.btn.pack(pady=30)

    def update_ram_label(self, value):
        self.ram_label.configure(text=f"{int(value)} ГБ")

    def set_max(self, value):
        self.current_max = value

    def set_progress(self, value):
        if self.current_max > 0:
            prog = value / self.current_max
            self.after(0, lambda: self.progressbar.set(prog))
            self.after(0, lambda: self.label_perc.configure(text=f"{int(prog * 100)}%"))

    def start_thread(self):
        user = self.entry.get()
        ver = self.version_menu.get()
        ram = int(self.ram_slider.get())
        save_config(user, ver, ram)
        
        self.btn.configure(state="disabled", text="ЗАГРУЗКА...")
        threading.Thread(target=self.launch, daemon=True).start()

    def launch(self):
        ver = self.version_menu.get()
        user = self.entry.get()
        ram = int(self.ram_slider.get())
        
        cb = {
            "setPropertyMax": self.set_max, 
            "setProperty": self.set_progress, 
            "setStatus": lambda t: self.after(0, lambda: self.status_label.configure(text=t))
        }

        try:
            minecraft_launcher_lib.install.install_minecraft_version(ver, mine_dir, callback=cb)
            minecraft_launcher_lib.fabric.install_fabric(ver, mine_dir, callback=cb)
            
            options = {
                "username": user,
                "uuid": str(uuid.uuid4()),
                "token": "",
                "jvmArguments": [f"-Xmx{ram}G", f"-Xms{ram}G"]
            }
            
            installed = minecraft_launcher_lib.utils.get_installed_versions(mine_dir)
            fab_id = next((v['id'] for v in installed if "fabric-loader" in v['id'] and ver in v['id']), ver)
            
            command = minecraft_launcher_lib.command.get_minecraft_command(fab_id, mine_dir, options)
            subprocess.Popen(command)
            self.after(5000, lambda: self.destroy())
        except Exception as e:
            self.after(0, lambda: self.btn.configure(state="normal", text="ОШИБКА!"))
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    app = ShtormLauncher()
    app.mainloop()