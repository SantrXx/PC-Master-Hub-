import customtkinter as ctk
import psutil
import platform
import subprocess
import threading
import time
import math
import os
from datetime import datetime

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

CPU_DB = {
    "Intel Core i3-10100F": {"score": 4100, "cores": 4, "threads": 8, "freq": "3.6–4.3 ГГц", "l3": "6 МБ", "tdp": 65, "tier": "Начальный игровой"},
    "AMD Ryzen 5 2600": {"score": 4400, "cores": 6, "threads": 12, "freq": "3.4–3.9 ГГц", "l3": "16 МБ", "tdp": 65, "tier": "Начальный игровой"},
    "AMD Ryzen 5 3600": {"score": 6100, "cores": 6, "threads": 12, "freq": "3.6–4.2 ГГц", "l3": "32 МБ", "tdp": 65, "tier": "Бюджетный стандарт"},
    "Intel Core i5-10400F": {"score": 5950, "cores": 6, "threads": 12, "freq": "2.9–4.3 ГГц", "l3": "12 МБ", "tdp": 65, "tier": "Бюджетный стандарт"},
    "Intel Core i5-11400F": {"score": 6800, "cores": 6, "threads": 12, "freq": "2.6–4.4 ГГц", "l3": "12 МБ", "tdp": 65, "tier": "Средний базовый"},
    "Intel Core i3-12100F": {"score": 6500, "cores": 4, "threads": 8, "freq": "3.3–4.3 ГГц", "l3": "12 МБ", "tdp": 58, "tier": "Бюджетный хит"},
    "AMD Ryzen 5 5500": {"score": 6700, "cores": 6, "threads": 12, "freq": "3.6–4.2 ГГц", "l3": "16 МБ", "tdp": 65, "tier": "Средний базовый"},
    "Intel Core i5-12400F": {"score": 8100, "cores": 6, "threads": 12, "freq": "2.5–4.4 ГГц", "l3": "18 МБ", "tdp": 65, "tier": "Народный игровой"},
    "AMD Ryzen 5 5600": {"score": 8200, "cores": 6, "threads": 12, "freq": "3.5–4.4 ГГц", "l3": "32 МБ", "tdp": 65, "tier": "Народный игровой"},
    "AMD Ryzen 5 5600X": {"score": 8450, "cores": 6, "threads": 12, "freq": "3.7–4.6 ГГц", "l3": "32 МБ", "tdp": 65, "tier": "Оптимальный игровой"},
    "AMD Ryzen 7 5700X": {"score": 9600, "cores": 8, "threads": 16, "freq": "3.4–4.6 ГГц", "l3": "32 МБ", "tdp": 65, "tier": "Оптимальный многозадачный"},
    "Intel Core i5-13400F": {"score": 9800, "cores": 10, "threads": 16, "freq": "2.5–4.6 ГГц", "l3": "20 МБ", "tdp": 65, "tier": "Оптимальный универсал"},
    "AMD Ryzen 7 5700X3D": {"score": 11400, "cores": 8, "threads": 16, "freq": "3.0–4.1 ГГц", "l3": "96 МБ (3D V-Cache)", "tdp": 105, "tier": "Топ для сокета AM4"},
    "AMD Ryzen 5 7500F": {"score": 10800, "cores": 6, "threads": 12, "freq": "3.7–5.0 ГГц", "l3": "32 МБ", "tdp": 65, "tier": "Лучший вход в AM5"},
    "AMD Ryzen 5 7600X": {"score": 11300, "cores": 6, "threads": 12, "freq": "4.7–5.3 ГГц", "l3": "32 МБ", "tdp": 105, "tier": "Высокий игровой"},
    "Intel Core i5-13600K": {"score": 12800, "cores": 14, "threads": 20, "freq": "3.5–5.1 ГГц", "l3": "24 МБ", "tdp": 125, "tier": "Предтоповый универсал"},
    "Intel Core i5-14600K": {"score": 13300, "cores": 14, "threads": 20, "freq": "3.5–5.3 ГГц", "l3": "24 МБ", "tdp": 125, "tier": "Предтоповый универсал"},
    "AMD Ryzen 7 7700X": {"score": 12900, "cores": 8, "threads": 16, "freq": "4.5–5.4 ГГц", "l3": "32 МБ", "tdp": 105, "tier": "Предтоповый игровой"},
    "Intel Core i7-13700K": {"score": 14600, "cores": 16, "threads": 24, "freq": "3.4–5.4 ГГц", "l3": "30 МБ", "tdp": 125, "tier": "Тяжелая рабочая станция"},
    "Intel Core i7-14700K": {"score": 15400, "cores": 20, "threads": 28, "freq": "3.4–5.6 ГГц", "l3": "33 МБ", "tdp": 125, "tier": "Предфлагман"},
    "AMD Ryzen 7 7800X3D": {"score": 15800, "cores": 8, "threads": 16, "freq": "4.2–5.0 ГГц", "l3": "96 МБ (3D V-Cache)", "tdp": 120, "tier": "Игровой эталон"},
    "Intel Core i9-14900K": {"score": 16900, "cores": 24, "threads": 32, "freq": "3.2–6.0 ГГц", "l3": "36 МБ", "tdp": 253, "tier": "Экстремальный"},
    "AMD Ryzen 9 7950X3D": {"score": 17400, "cores": 16, "threads": 32, "freq": "4.2–5.7 ГГц", "l3": "128 МБ (3D V-Cache)", "tdp": 120, "tier": "Ультимативный гибрид"},
    "AMD Ryzen 7 9800X3D": {"score": 18200, "cores": 8, "threads": 16, "freq": "4.7–5.2 ГГц", "l3": "96 МБ (2nd 3D V-Cache)", "tdp": 120, "tier": "Абсолютный игровой король"},
}

GPU_DB = {
    "Встроенная графика (iGPU Vega / UHD)": {"score": 1150, "vram": 2, "vram_type": "Системная ОЗУ", "bus": "64–128 бит", "tdp": 15, "tier": "Офисный / Киберспорт"},
    "AMD Radeon RX 580 8GB": {"score": 3400, "vram": 8, "vram_type": "GDDR5", "bus": "256 бит", "tdp": 185, "tier": "Бюджетная классика"},
    "NVIDIA GTX 1050 Ti": {"score": 2650, "vram": 4, "vram_type": "GDDR5", "bus": "128 бит", "tdp": 75, "tier": "Начальный"},
    "NVIDIA GTX 1060 6GB": {"score": 3700, "vram": 6, "vram_type": "GDDR5", "bus": "192 бит", "tdp": 120, "tier": "Начальный Full HD"},
    "NVIDIA GTX 1650": {"score": 3600, "vram": 4, "vram_type": "GDDR6", "bus": "128 бит", "tdp": 75, "tier": "Бюджетный"},
    "NVIDIA GTX 1660 Super": {"score": 5400, "vram": 6, "vram_type": "GDDR6", "bus": "192 бит", "tdp": 125, "tier": "Базовый Full HD"},
    "NVIDIA RTX 2060 Super": {"score": 6900, "vram": 8, "vram_type": "GDDR6", "bus": "256 бит", "tdp": 175, "tier": "Средний базовый"},
    "NVIDIA RTX 3050 8GB": {"score": 6000, "vram": 8, "vram_type": "GDDR6", "bus": "128 бит", "tdp": 130, "tier": "Базовый с DLSS"},
    "AMD Radeon RX 6600": {"score": 7600, "vram": 8, "vram_type": "GDDR6", "bus": "128 бит", "tdp": 132, "tier": "Лучший бюджетный Full HD"},
    "Intel Arc A750": {"score": 8100, "vram": 8, "vram_type": "GDDR6", "bus": "256 бит", "tdp": 225, "tier": "Средний Full HD"},
    "NVIDIA RTX 3060 12GB": {"score": 8400, "vram": 12, "vram_type": "GDDR6", "bus": "192 бит", "tdp": 170, "tier": "Народный хит Full HD"},
    "AMD Radeon RX 6650 XT": {"score": 9100, "vram": 8, "vram_type": "GDDR6", "bus": "128 бит", "tdp": 176, "tier": "Уверенный Full HD"},
    "NVIDIA RTX 3060 Ti": {"score": 10300, "vram": 8, "vram_type": "GDDR6", "bus": "256 бит", "tdp": 200, "tier": "Мощный Full HD / Начальный 2K"},
    "NVIDIA RTX 4060": {"score": 10100, "vram": 8, "vram_type": "GDDR6", "bus": "128 бит", "tdp": 115, "tier": "Современный стандарт Full HD"},
    "AMD Radeon RX 7600": {"score": 9600, "vram": 8, "vram_type": "GDDR6", "bus": "128 бит", "tdp": 165, "tier": "Современный Full HD"},
    "AMD Radeon RX 6700 XT": {"score": 11200, "vram": 12, "vram_type": "GDDR6", "bus": "192 бит", "tdp": 230, "tier": "Оптимальный для 2K"},
    "NVIDIA RTX 3070": {"score": 11600, "vram": 8, "vram_type": "GDDR6", "bus": "256 бит", "tdp": 220, "tier": "Высокий Full HD / 2K"},
    "NVIDIA RTX 4060 Ti 16GB": {"score": 12400, "vram": 16, "vram_type": "GDDR6", "bus": "128 бит", "tdp": 165, "tier": "Игры + ИИ / Рабочие задачи"},
    "AMD Radeon RX 7700 XT": {"score": 13400, "vram": 12, "vram_type": "GDDR6", "bus": "192 бит", "tdp": 245, "tier": "Уверенный 2K Ультра"},
    "AMD Radeon RX 7800 XT": {"score": 15200, "vram": 16, "vram_type": "GDDR6", "bus": "256 бит", "tdp": 263, "tier": "Хит для 2K гейминга"},
    "NVIDIA RTX 4070 Super": {"score": 16100, "vram": 12, "vram_type": "GDDR6X", "bus": "192 бит", "tdp": 220, "tier": "Золотой стандарт 2K / RT"},
    "NVIDIA RTX 4070 Ti Super": {"score": 18200, "vram": 16, "vram_type": "GDDR6X", "bus": "256 бит", "tdp": 285, "tier": "Предфлагман (2K / 4K)"},
    "AMD Radeon RX 7900 XT": {"score": 18600, "vram": 20, "vram_type": "GDDR6", "bus": "320 бит", "tdp": 315, "tier": "Мощный 4K гейминг"},
    "NVIDIA RTX 4080 Super": {"score": 20500, "vram": 16, "vram_type": "GDDR6X", "bus": "256 бит", "tdp": 320, "tier": "Топовый 4K Ultra"},
    "AMD Radeon RX 7900 XTX": {"score": 20800, "vram": 24, "vram_type": "GDDR6", "bus": "384 бит", "tdp": 355, "tier": "Флагман Radeon 4K"},
    "NVIDIA RTX 4090": {"score": 25500, "vram": 24, "vram_type": "GDDR6X", "bus": "384 бит", "tdp": 450, "tier": "Экстремальный 4K / 8K"},
}

RAM_VARIATIONS = {
    "8 ГБ DDR4 (2666 МГц, Одноканал)": {"gb": 8, "mult": 0.85, "desc": "Минимум для офиса; в тяжелых играх будут фризы"},
    "16 ГБ DDR4 (3200 МГц, Двухканал 2x8)": {"gb": 16, "mult": 1.00, "desc": "Базовый игровой стандарт для большинства задач"},
    "32 ГБ DDR4 (3600 МГц, Двухканал 2x16)": {"gb": 32, "mult": 1.05, "desc": "Отличный запас для игр, DAW (звука) и монтажа"},
    "16 ГБ DDR5 (5200 МГц, Двухканал 2x8)": {"gb": 16, "mult": 1.04, "desc": "Начальный уровень современной памяти DDR5"},
    "32 ГБ DDR5 (6000 МГц CL30, Двухканал 2x16)": {"gb": 32, "mult": 1.12, "desc": "Идеальный скоростной стандарт для современных ПК"},
    "64 ГБ DDR5 (6400 МГц, Двухканал 2x32)": {"gb": 64, "mult": 1.15, "desc": "Профессиональная станция с огромным запасом"},
}

STORAGE_VARIATIONS = {
    "Жесткий диск HDD (7200 RPM, ~150 МБ/с)": {"speed": "Медленно (~150 МБ/с)", "bonus": -0.05, "desc": "Долгие загрузки ОС и подгрузки текстур в играх"},
    "SATA III SSD 2.5\" (~550 МБ/с)": {"speed": "Хорошо (~550 МБ/с)", "bonus": 0.0, "desc": "В 4 раза быстрее HDD, комфортная работа Windows"},
    "NVMe M.2 PCIe 3.0 SSD (~3500 МБ/с)": {"speed": "Быстро (~3500 МБ/с)", "bonus": 0.02, "desc": "Отличная отзывчивость системы и быстрые загрузки"},
    "NVMe M.2 PCIe 4.0 SSD (~7000 МБ/с)": {"speed": "Сверхбыстро (~7000 МБ/с)", "bonus": 0.04, "desc": "Мгновенная загрузка уровней (DirectStorage)"},
    "NVMe M.2 PCIe 5.0 SSD (~12000 МБ/с)": {"speed": "Экстремально (~12000 МБ/с)", "bonus": 0.05, "desc": "Максимальная пропускная способность для тяжелых файлов"},
}

GAMES_DB = [
    {"name": "CS2 / Valorant / Dota 2", "cpu_req": 3500, "gpu_req": 2650, "ram_req": 8},
    {"name": "GTA V / Ведьмак 3 / War Thunder", "cpu_req": 4200, "gpu_req": 3600, "ram_req": 8},
    {"name": "Forza Horizon 5 / Apex Legends", "cpu_req": 6000, "gpu_req": 6500, "ram_req": 16},
    {"name": "Red Dead Redemption 2 / Rust", "cpu_req": 7500, "gpu_req": 8200, "ram_req": 16},
    {"name": "Cyberpunk 2077 / Baldur's Gate 3", "cpu_req": 8400, "gpu_req": 10100, "ram_req": 16},
    {"name": "Alan Wake 2 / S.T.A.L.K.E.R. 2 (Ultra)", "cpu_req": 11300, "gpu_req": 15200, "ram_req": 32},
]

PROTECTED_PROCESSES = {
    "system", "system idle process", "registry", "smss.exe", "csrss.exe", "wininit.exe",
    "services.exe", "lsass.exe", "svchost.exe", "fontdrvhost.exe", "winlogon.exe",
    "dwm.exe", "explorer.exe", "taskhostw.exe", "sihost.exe", "ctfmon.exe",
    "conhost.exe", "dllhost.exe", "runtimebroker.exe", "searchindexer.exe",
    "securityhealthservice.exe", "msmpeng.exe", "audiodg.exe", "spoolsv.exe",
    "python.exe", "pythonw.exe", "pc_master_hub.exe", "pc_master_hub_pro.exe",
    "wmiprvse.exe", "dashost.exe", "lsaiso.exe", "memory compression"
}

LIGHT_JUNK_KEYWORDS = [
    "update", "updater", "helper", "crashpad", "telemetry", "cortana", "onedrive",
    "skype", "yourphone", "phoneexperiencehost", "widget", "widgets", "gamebar"
]
MEDIUM_BLOAT_KEYWORDS = LIGHT_JUNK_KEYWORDS + [
    "steam", "epicgameslauncher", "battle.net", "riotclient", "discord", "telegram",
    "spotify", "yandexmusic", "viber", "whatsapp", "teams", "zoom", "overwolf"
]


class HardwareScanner:
    @staticmethod
    def _run_wmic(command):
        if platform.system() != "Windows":
            return []
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            out = subprocess.check_output(
                command, shell=True, stderr=subprocess.DEVNULL, startupinfo=startupinfo
            ).decode("cp866", errors="ignore")
            lines = [line.strip() for line in out.splitlines() if line.strip()]
            return lines[1:] if len(lines) > 1 else []
        except Exception:
            return []

    @staticmethod
    def get_detailed_hardware():
        cpu_lines = HardwareScanner._run_wmic("wmic cpu get Name")
        cpu_name = cpu_lines[0] if cpu_lines else (platform.processor() or "Неизвестный процессор")

        gpu_lines = HardwareScanner._run_wmic("wmic path win32_VideoController get Name")
        gpu_name = " / ".join(gpu_lines) if gpu_lines else "Стандартный графический адаптер"

        mb_lines = HardwareScanner._run_wmic("wmic baseboard get Manufacturer,Product")
        mb_info = mb_lines[0] if mb_lines else "Стандартная системная плата"
        bios_lines = HardwareScanner._run_wmic("wmic bios get SMBIOSBIOSVersion")
        bios_ver = f" (BIOS: {bios_lines[0]})" if bios_lines else ""

        ram_sticks = HardwareScanner._run_wmic("wmic memorychip get Capacity,Speed,Manufacturer")
        ram_details = []
        for stick in ram_sticks:
            parts = stick.split()
            if parts and parts[0].isdigit():
                gb = round(int(parts[0]) / (1024**3), 1)
                rest = " ".join(parts[1:])
                ram_details.append(f"{gb} ГБ ({rest} МГц)")
        ram_modules_str = f"{len(ram_details)} шт.: " + ", ".join(ram_details) if ram_details else "Автоопределение"

        disks_phys = HardwareScanner._run_wmic("wmic diskdrive get Model,Size")
        disk_models_str = "\n   • ".join(disks_phys) if disks_phys else "Стандартный дисковый накопитель"

        monitors = HardwareScanner._run_wmic("wmic desktopmonitor get Name")
        monitors_str = ", ".join(set(monitors)) if monitors else "Универсальный монитор PnP"

        audio_devs = HardwareScanner._run_wmic("wmic sounddev get Name")
        audio_str = ", ".join(set(audio_devs)) if audio_devs else "Стандартное аудиоустройство"

        keyboards = HardwareScanner._run_wmic("wmic path Win32_Keyboard get Description")
        kb_str = ", ".join(set(keyboards)) if keyboards else "HID-клавиатура"

        mice = HardwareScanner._run_wmic("wmic path Win32_PointingDevice get Name")
        mouse_str = ", ".join(set(mice)) if mice else "HID-совместимая мышь"

        cores_phys = psutil.cpu_count(logical=False) or 4
        cores_log = psutil.cpu_count(logical=True) or 8
        freq = psutil.cpu_freq()
        max_freq = round(freq.max, 0) if freq and freq.max else 3200
        ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 1)

        matched_cpu = "Intel Core i5-12400F"
        est_cpu_score = int((cores_phys * 950) + (cores_log * 230))
        for c_key, c_val in CPU_DB.items():
            short_c = c_key.replace("Intel Core ", "").replace("AMD Ryzen ", "")
            if short_c.lower() in cpu_name.lower():
                matched_cpu = c_key
                est_cpu_score = c_val["score"]
                break

        matched_gpu = "NVIDIA GTX 1650"
        for g_key in GPU_DB:
            short_g = g_key.replace("NVIDIA ", "").replace("AMD Radeon ", "")
            if short_g.lower() in gpu_name.lower():
                matched_gpu = g_key
                break

        est_tdp = CPU_DB[matched_cpu]["tdp"] + GPU_DB[matched_gpu]["tdp"] + 65
        rec_psu = int(math.ceil((est_tdp * 1.35) / 50.0) * 50)
        battery = psutil.sensors_battery()
        if battery:
            psu_info = f"Аккумулятор ноутбука (Заряд: {battery.percent}%)"
        else:
            psu_info = f"Стандартный ATX БП | Расчетное пиковое потребление ПК: ~{est_tdp} Вт (Рекомендуемый БП: от {rec_psu} Вт)"

        return {
            "os": f"{platform.system()} {platform.release()} ({platform.machine()})",
            "cpu_name": cpu_name,
            "gpu_name": gpu_name,
            "mb_info": mb_info + bios_ver,
            "ram_modules_str": ram_modules_str,
            "disk_models_str": disk_models_str,
            "psu_info": psu_info,
            "monitors_str": monitors_str,
            "audio_str": audio_str,
            "kb_str": kb_str,
            "mouse_str": mouse_str,
            "cores_phys": cores_phys,
            "cores_log": cores_log,
            "max_freq": max_freq,
            "ram_gb": ram_gb,
            "est_cpu_score": est_cpu_score,
            "matched_cpu": matched_cpu,
            "matched_gpu": matched_gpu,
        }


class PCMasterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PC Master Hub v2.0 PRO — Мониторинг, Очистка ОЗУ, Анализ и Сборка")
        self.geometry("1200x780")
        self.minsize(1020, 680)

        self.hw_info = HardwareScanner.get_detailed_hardware()
        self.monitoring_active = True
        self.manual_proc_checkboxes = []

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_pages()
        self.show_page("monitor")

        self.monitor_thread = threading.Thread(target=self._live_monitor_loop, daemon=True)
        self.monitor_thread.start()

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=245, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="⚡ PC MASTER PRO", font=ctk.CTkFont(size=21, weight="bold")).pack(pady=(22, 5), padx=15)
        ctk.CTkLabel(self.sidebar, text="Версия 2.0 • Полный контроль", font=ctk.CTkFont(size=12), text_color="gray60").pack(pady=(0, 18), padx=15)

        nav_items = [
            ("🖥  Мой ПК и Устройства", "monitor"),
            ("🧹  Очистка ОЗУ (RAM Boost)", "ram_cleaner"),
            ("🎯  Анализ и Потенциал", "analyzer"),
            ("⚖️  Сравнение железа", "compare"),
            ("🛠  Конфигуратор ПК", "builder"),
            ("🔥  Стресс-тест (Бенчмарк)", "benchmark"),
            ("🛡  Здоровье ПК и Отчет", "health"),
        ]

        self.nav_buttons = {}
        for text, page_key in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                anchor="w",
                height=40,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray25"),
                command=lambda k=page_key: self.show_page(k),
            )
            btn.pack(fill="x", padx=12, pady=4)
            self.nav_buttons[page_key] = btn

        footer = ctk.CTkLabel(
            self.sidebar,
            text=f"ОС: {self.hw_info['os']}\nЯдер: {self.hw_info['cores_phys']} ({self.hw_info['cores_log']} потоков)\nОЗУ: {self.hw_info['ram_gb']} ГБ",
            font=ctk.CTkFont(size=12),
            text_color="gray60",
            justify="left",
        )
        footer.pack(side="bottom", pady=18, padx=15, anchor="w")

    def _build_pages(self):
        self.pages = {}
        for key in ["monitor", "ram_cleaner", "analyzer", "compare", "builder", "benchmark", "health"]:
            frame = ctk.CTkScrollableFrame(self, corner_radius=10)
            frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
            self.pages[key] = frame

        self._init_monitor_page(self.pages["monitor"])
        self._init_ram_cleaner_page(self.pages["ram_cleaner"])
        self._init_analyzer_page(self.pages["analyzer"])
        self._init_compare_page(self.pages["compare"])
        self._init_builder_page(self.pages["builder"])
        self._init_benchmark_page(self.pages["benchmark"])
        self._init_health_page(self.pages["health"])

    def show_page(self, page_key):
        for k, frame in self.pages.items():
            if k == page_key:
                frame.tkraise()
                frame.grid()
            else:
                frame.grid_remove()

        for k, btn in self.nav_buttons.items():
            btn.configure(fg_color=("gray75", "#1f538d") if k == page_key else "transparent")

    def _init_monitor_page(self, parent):
        ctk.CTkLabel(parent, text="Полная сводка о комплектующих, датчиках и периферии", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(5, 12))

        live_card = ctk.CTkFrame(parent)
        live_card.pack(fill="x", pady=6)
        ctk.CTkLabel(live_card, text="📊 Живая телеметрия системы:", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(10, 6))

        self.cpu_load_lbl = ctk.CTkLabel(live_card, text="Загрузка процессора (CPU): 0%", font=ctk.CTkFont(size=14))
        self.cpu_load_lbl.pack(anchor="w", padx=15)
        self.cpu_bar = ctk.CTkProgressBar(live_card, height=13)
        self.cpu_bar.pack(fill="x", padx=15, pady=(3, 10))
        self.cpu_bar.set(0)

        self.ram_load_lbl = ctk.CTkLabel(live_card, text="Оперативная память (RAM): 0%", font=ctk.CTkFont(size=14))
        self.ram_load_lbl.pack(anchor="w", padx=15)
        self.ram_bar = ctk.CTkProgressBar(live_card, height=13)
        self.ram_bar.pack(fill="x", padx=15, pady=(3, 12))
        self.ram_bar.set(0)

        specs_card = ctk.CTkFrame(parent)
        specs_card.pack(fill="x", pady=6)
        ctk.CTkLabel(specs_card, text="🧩 Внутренние комплектующие системного блока:", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(10, 6))

        specs_text = (
            f"🔹 Процессор (CPU): {self.hw_info['cpu_name']} ({self.hw_info['cores_phys']} ядер / {self.hw_info['cores_log']} потоков, до {self.hw_info['max_freq']} МГц)\n"
            f"🔹 Видеокарта (GPU): {self.hw_info['gpu_name']}\n"
            f"🔹 Материнская плата: {self.hw_info['mb_info']}\n"
            f"🔹 Оперативная память: Всего {self.hw_info['ram_gb']} ГБ | Слоты и планки: {self.hw_info['ram_modules_str']}\n"
            f"🔹 Блок питания / Питание: {self.hw_info['psu_info']}\n"
            f"🔹 Физические накопители (SSD/HDD):\n   • {self.hw_info['disk_models_str']}"
        )
        ctk.CTkLabel(specs_card, text=specs_text, font=ctk.CTkFont(size=14), justify="left", wraplength=860).pack(anchor="w", padx=15, pady=(0, 12))

        periph_card = ctk.CTkFrame(parent)
        periph_card.pack(fill="x", pady=6)
        ctk.CTkLabel(periph_card, text="🎧 Подключенные устройства и периферия:", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(10, 6))

        periph_text = (
            f"🖥 Монитор(ы): {self.hw_info['monitors_str']}\n"
            f"🎙 Аудиоустройства (Звуковые карты / Микрофоны / Динамики): {self.hw_info['audio_str']}\n"
            f"⌨️ Клавиатура: {self.hw_info['kb_str']}\n"
            f"🖱 Мышь и ввод: {self.hw_info['mouse_str']}"
        )
        ctk.CTkLabel(periph_card, text=periph_text, font=ctk.CTkFont(size=14), justify="left", wraplength=860).pack(anchor="w", padx=15, pady=(0, 12))

        disk_card = ctk.CTkFrame(parent)
        disk_card.pack(fill="x", pady=6)
        ctk.CTkLabel(disk_card, text="💿 Логические тома и свободное место:", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(10, 6))

        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                total_gb = round(usage.total / (1024 ** 3), 1)
                used_gb = round(usage.used / (1024 ** 3), 1)
                free_gb = round(usage.free / (1024 ** 3), 1)
                pct = usage.percent

                row = ctk.CTkFrame(disk_card, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=3)
                ctk.CTkLabel(
                    row,
                    text=f"Том {part.device} ({part.fstype}) — Занято: {used_gb} ГБ из {total_gb} ГБ (Свободно: {free_gb} ГБ | {pct}%)",
                    font=ctk.CTkFont(size=13),
                ).pack(anchor="w")
                bar = ctk.CTkProgressBar(row, height=9)
                bar.pack(fill="x", pady=2)
                bar.set(pct / 100.0)
            except Exception:
                continue

    def _live_monitor_loop(self):
        while self.monitoring_active:
            try:
                cpu_pct = psutil.cpu_percent(interval=0.8)
                ram = psutil.virtual_memory()
                ram_used = round(ram.used / (1024 ** 3), 2)
                ram_free = round(ram.available / (1024 ** 3), 2)

                self.cpu_load_lbl.configure(text=f"Загрузка процессора (CPU): {cpu_pct}%")
                self.cpu_bar.set(cpu_pct / 100.0)

                ram_text = f"Оперативная память (RAM): Занято {ram_used} ГБ из {self.hw_info['ram_gb']} ГБ (Свободно: {ram_free} ГБ | {ram.percent}%)"
                self.ram_load_lbl.configure(text=ram_text)
                self.ram_bar.set(ram.percent / 100.0)

                if hasattr(self, "cleaner_ram_lbl"):
                    self.cleaner_ram_lbl.configure(text=f"Текущее состояние ОЗУ: Занято {ram_used} ГБ ({ram.percent}%) — Доступно: {ram_free} ГБ")
            except Exception:
                pass
            time.sleep(0.5)

    def _init_ram_cleaner_page(self, parent):
        ctk.CTkLabel(parent, text="Интеллектуальная и ручная очистка оперативной памяти", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(5, 8))

        self.cleaner_ram_lbl = ctk.CTkLabel(parent, text="Текущее состояние ОЗУ: Сканирование...", font=ctk.CTkFont(size=15, weight="bold"), text_color="#4da6ff")
        self.cleaner_ram_lbl.pack(anchor="w", pady=(0, 10))

        auto_card = ctk.CTkFrame(parent)
        auto_card.pack(fill="x", pady=6)
        ctk.CTkLabel(auto_card, text="🤖 РЕЖИМ 1: Автоматический подбор программ (с предварительным подтверждением)", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(12, 6))

        ctk.CTkLabel(
            auto_card,
            text="Выбери степень очистки. Программа просканирует процессы, покажет тебе точный список кандидатов на закрытие и спросит разрешение:",
            font=ctk.CTkFont(size=13),
            text_color="gray75",
        ).pack(anchor="w", padx=15, pady=(0, 8))

        ctrl_row = ctk.CTkFrame(auto_card, fg_color="transparent")
        ctrl_row.pack(fill="x", padx=15, pady=(0, 12))

        self.clean_level_menu = ctk.CTkOptionMenu(
            ctrl_row,
            values=[
                "1. Лёгкая (Только фоновые апдейтеры и мелкий кэш)",
                "2. Средняя (Фоновые клиенты, мессенджеры и лаунчеры)",
                "3. Максимальная (Все несистемные программы для игр и тяжелых задач)",
            ],
            width=480,
        )
        self.clean_level_menu.set("2. Средняя (Фоновые клиенты, мессенджеры и лаунчеры)")
        self.clean_level_menu.pack(side="left", padx=(0, 15))

        ctk.CTkButton(
            ctrl_row,
            text="🔍 Найти процессы и проверить список",
            height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._preview_auto_ram_clean,
        ).pack(side="left")

        manual_card = ctk.CTkFrame(parent)
        manual_card.pack(fill="x", pady=10)

        head_row = ctk.CTkFrame(manual_card, fg_color="transparent")
        head_row.pack(fill="x", padx=15, pady=(12, 6))

        ctk.CTkLabel(head_row, text="⚙️ РЕЖИМ 2: Механический (ручной) выбор программ для закрытия", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        ctk.CTkButton(head_row, text="🔄 Обновить список процессов", width=210, command=self._refresh_manual_process_list).pack(side="right", padx=5)

        ctk.CTkLabel(
            manual_card,
            text="Отметь галочками программы, которые хочешь закрыть вручную (системные процессы Windows скрыты для безопасности):",
            font=ctk.CTkFont(size=13),
            text_color="gray75",
        ).pack(anchor="w", padx=15, pady=(0, 6))

        self.proc_list_frame = ctk.CTkScrollableFrame(manual_card, height=250)
        self.proc_list_frame.pack(fill="x", padx=15, pady=6)

        act_row = ctk.CTkFrame(manual_card, fg_color="transparent")
        act_row.pack(fill="x", padx=15, pady=(6, 12))

        ctk.CTkButton(
            act_row,
            text="❌ Закрыть выбранные программы (с подтверждением)",
            fg_color="#c93b2b",
            hover_color="#9e2a1d",
            height=38,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._confirm_manual_close,
        ).pack(side="left")

        self.clean_status_lbl = ctk.CTkLabel(act_row, text="", font=ctk.CTkFont(size=13, weight="bold"))
        self.clean_status_lbl.pack(side="left", padx=20)

        self._refresh_manual_process_list()

    def _get_safe_user_processes(self):
        procs = []
        current_pid = os.getpid()
        for p in psutil.process_iter(["pid", "name", "memory_info"]):
            try:
                info = p.info
                pid = info["pid"]
                name = info["name"] or ""
                if not name or pid == current_pid or pid <= 4:
                    continue
                if name.lower() in PROTECTED_PROCESSES:
                    continue
                mem_mb = round(info["memory_info"].rss / (1024 * 1024), 1)
                if mem_mb >= 12.0:
                    procs.append({"pid": pid, "name": name, "mem_mb": mem_mb})
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        procs.sort(key=lambda x: x["mem_mb"], reverse=True)
        return procs

    def _refresh_manual_process_list(self):
        for w in self.proc_list_frame.winfo_children():
            w.destroy()
        self.manual_proc_checkboxes.clear()

        procs = self._get_safe_user_processes()
        if not procs:
            ctk.CTkLabel(self.proc_list_frame, text="Нет доступных сторонних процессов для отображения.").pack(pady=10)
            return

        for p in procs[:60]:
            var = ctk.BooleanVar(value=False)
            cb_text = f"{p['name']}  (PID: {p['pid']})  —  Занимает: {p['mem_mb']} МБ ОЗУ"
            cb = ctk.CTkCheckBox(self.proc_list_frame, text=cb_text, variable=var, font=ctk.CTkFont(size=13))
            cb.pack(anchor="w", padx=10, pady=4)
            self.manual_proc_checkboxes.append((var, p))

    def _preview_auto_ram_clean(self):
        level_str = self.clean_level_menu.get()
        all_procs = self._get_safe_user_processes()
        candidates = []

        if level_str.startswith("1."):
            for p in all_procs:
                n_low = p["name"].lower()
                if any(k in n_low for k in LIGHT_JUNK_KEYWORDS) or (p["mem_mb"] > 45 and "helper" in n_low):
                    candidates.append(p)
        elif level_str.startswith("2."):
            for p in all_procs:
                n_low = p["name"].lower()
                if any(k in n_low for k in MEDIUM_BLOAT_KEYWORDS) or p["mem_mb"] > 140:
                    candidates.append(p)
        else:
            for p in all_procs:
                if p["mem_mb"] >= 35.0:
                    candidates.append(p)

        self._open_confirmation_dialog(candidates, mode_title=f"Авто-очистка: {level_str}")

    def _confirm_manual_close(self):
        selected = [p for var, p in self.manual_proc_checkboxes if var.get()]
        self._open_confirmation_dialog(selected, mode_title="Ручной выбор процессов")

    def _open_confirmation_dialog(self, proc_list, mode_title):
        dialog = ctk.CTkToplevel(self)
        dialog.title("⚠️ Подтверждение закрытия программ")
        dialog.geometry("620x460")
        dialog.attributes("-topmost", True)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"Подтверждение: {mode_title}", font=ctk.CTkFont(size=17, weight="bold")).pack(anchor="w", padx=20, pady=(15, 5))

        if not proc_list:
            ctk.CTkLabel(
                dialog,
                text="✅ Не найдено ни одного лишнего процесса для выбранного режима (или ничего не отмечено галочками).\nТвоя оперативная память уже в чистоте!",
                font=ctk.CTkFont(size=14),
                justify="left",
                wraplength=560,
            ).pack(padx=20, pady=30)
            ctk.CTkButton(dialog, text="Понятно", command=dialog.destroy).pack(pady=10)
            return

        total_mb = round(sum(p["mem_mb"] for p in proc_list), 1)
        ctk.CTkLabel(
            dialog,
            text=f"Следующие программы ({len(proc_list)} шт.) будут закрыты.\nОжидаемое освобождение памяти: ~{total_mb} МБ ({round(total_mb/1024, 2)} ГБ).\nУбедись, что в них сохранены важные данные:",
            font=ctk.CTkFont(size=13),
            justify="left",
            text_color="gray80",
        ).pack(anchor="w", padx=20, pady=(0, 10))

        box = ctk.CTkTextbox(dialog, height=230, font=ctk.CTkFont(size=13))
        box.pack(fill="both", expand=True, padx=20, pady=5)
        lines = [f"• {p['name']} (PID: {p['pid']}) — {p['mem_mb']} МБ" for p in proc_list]
        box.insert("1.0", "\n".join(lines))
        box.configure(state="disabled")

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=15)

        def execute_termination():
            closed_count = 0
            freed_mb = 0.0
            for p in proc_list:
                try:
                    proc_obj = psutil.Process(p["pid"])
                    proc_obj.terminate()
                    closed_count += 1
                    freed_mb += p["mem_mb"]
                except Exception:
                    continue
            dialog.destroy()
            self.clean_status_lbl.configure(
                text=f"✅ Закрыто процессов: {closed_count} | Освобождено: ~{round(freed_mb, 1)} МБ", text_color="#2ecc71"
            )
            self._refresh_manual_process_list()

        ctk.CTkButton(
            btn_row,
            text="✅ Подтвердить и закрыть программы",
            fg_color="#27ae60",
            hover_color="#1e8449",
            height=38,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=execute_termination,
        ).pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            btn_row,
            text="Отмена (Ничего не закрывать)",
            fg_color="gray40",
            hover_color="gray30",
            height=38,
            command=dialog.destroy,
        ).pack(side="left")

    def _init_analyzer_page(self, parent):
        ctk.CTkLabel(parent, text="Анализатор потенциала ПК и рекомендации по апгрейду", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(5, 10))

        top_frame = ctk.CTkFrame(parent)
        top_frame.pack(fill="x", pady=6)

        ctk.CTkLabel(
            top_frame,
            text="Программа автоматически определила твои параметры (при необходимости уточни модель из расширенной базы для точной калибровки):",
            font=ctk.CTkFont(size=13),
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=(10, 6))

        ctk.CTkLabel(top_frame, text="Процессор:", font=ctk.CTkFont(size=13, weight="bold")).grid(row=1, column=0, padx=(15, 5), pady=8, sticky="w")
        self.user_cpu_selector = ctk.CTkOptionMenu(top_frame, values=list(CPU_DB.keys()), width=230, command=lambda _: self._update_analysis())
        self.user_cpu_selector.set(self.hw_info["matched_cpu"])
        self.user_cpu_selector.grid(row=1, column=1, padx=5, pady=8, sticky="w")

        ctk.CTkLabel(top_frame, text="Видеокарта:", font=ctk.CTkFont(size=13, weight="bold")).grid(row=1, column=2, padx=(15, 5), pady=8, sticky="w")
        self.user_gpu_selector = ctk.CTkOptionMenu(top_frame, values=list(GPU_DB.keys()), width=250, command=lambda _: self._update_analysis())
        self.user_gpu_selector.set(self.hw_info["matched_gpu"])
        self.user_gpu_selector.grid(row=1, column=3, padx=5, pady=8, sticky="w")

        ctk.CTkLabel(top_frame, text="Тип ОЗУ:", font=ctk.CTkFont(size=13, weight="bold")).grid(row=2, column=0, padx=(15, 5), pady=(0, 12), sticky="w")
        self.user_ram_selector = ctk.CTkOptionMenu(top_frame, values=list(RAM_VARIATIONS.keys()), width=340, command=lambda _: self._update_analysis())
        default_ram_key = "32 ГБ DDR5 (6000 МГц CL30, Двухканал 2x16)" if self.hw_info["ram_gb"] > 20 else ("16 ГБ DDR4 (3200 МГц, Двухканал 2x8)" if self.hw_info["ram_gb"] > 10 else "8 ГБ DDR4 (2666 МГц, Одноканал)")
        self.user_ram_selector.set(default_ram_key)
        self.user_ram_selector.grid(row=2, column=1, columnspan=3, padx=5, pady=(0, 12), sticky="w")

        self.verdict_box = ctk.CTkTextbox(parent, height=185, font=ctk.CTkFont(size=14))
        self.verdict_box.pack(fill="x", pady=8)

        ctk.CTkLabel(parent, text="🎮 Прогноз производительности в популярных играх (Full HD 1080p):", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(8, 5))

        self.games_container = ctk.CTkFrame(parent)
        self.games_container.pack(fill="x", pady=5)

        self._update_analysis()

    def _update_analysis(self):
        cpu_name = self.user_cpu_selector.get()
        gpu_name = self.user_gpu_selector.get()
        ram_key = self.user_ram_selector.get()

        c_info = CPU_DB[cpu_name]
        g_info = GPU_DB[gpu_name]
        r_info = RAM_VARIATIONS[ram_key]

        cpu_score = c_info["score"]
        gpu_score = g_info["score"]
        ram_gb = r_info["gb"]

        bottleneck_notes = []
        if cpu_score < gpu_score * 0.62:
            bottleneck_notes.append(f"⚠️ Эффект Bottleneck (Упор в ЦП): процессор {cpu_name} ограничивает потенциал видеокарты {gpu_name}. Рекомендуется апгрейд процессора.")
        elif gpu_score < cpu_score * 0.60:
            bottleneck_notes.append(f"⚠️ Упор в видеокарту: твой процессор ({cpu_name}) намного мощнее видеокарты ({gpu_name}). Установка более мощной GPU даст огромный прирост FPS.")
        else:
            bottleneck_notes.append("✅ Отличный баланс между процессором и видеокартой — компоненты работают в полной синергии!")

        if ram_gb < 16:
            bottleneck_notes.append("⚠️ Обязательный апгрейд ОЗУ: 8 ГБ недостаточно для современных игр и многозадачности. Рекомендуется 16 или 32 ГБ двумя планками.")
        elif "Одноканал" in ram_key:
            bottleneck_notes.append("⚠️ Память в одноканальном режиме теряет до 15–20% FPS. Добавь вторую планку для двухканала!")
        else:
            bottleneck_notes.append(f"👍 Конфигурация памяти ({ram_key}): {r_info['desc']}.")

        total_power = int((cpu_score * 0.38 + gpu_score * 0.62) * r_info["mult"])
        if total_power > 14000:
            purpose = "Ультимативный гейминг в 2K/4K на Ультра, тяжелый монтаж, 3D-моделирование, компиляция больших проектов и работа с ИИ."
        elif total_power > 8000:
            purpose = "Уверенный гейминг в Full HD / 2K на высоких и ультра настройках, запись и сведение музыки (FL Studio / DAW), стриминг и кодинг."
        elif total_power > 4200:
            purpose = "Киберспортивные игры (CS2, Dota 2, War Thunder, GTA V), создание музыки, учеба и повседневная разработка."
        else:
            purpose = "Учеба, веб-серфинг, программирование, офисные задачи и нетребовательные классические игры."

        verdict_text = (
            f"📊 Индекс ЦП ({cpu_name}): {cpu_score} pts | Индекс ГП ({gpu_name}, {g_info['vram']} ГБ {g_info['vram_type']}): {gpu_score} pts\n"
            f"🏆 Итоговый рейтинг производительности конфигурации: {total_power} баллов\n\n"
            f"🎯 Для чего этот ПК подходит лучше всего:\n   • {purpose}\n\n"
            f"🔧 Рекомендации по улучшению до идеальной сборки:\n   • " + "\n   • ".join(bottleneck_notes)
        )

        self.verdict_box.configure(state="normal")
        self.verdict_box.delete("1.0", "end")
        self.verdict_box.insert("1.0", verdict_text)
        self.verdict_box.configure(state="disabled")

        for widget in self.games_container.winfo_children():
            widget.destroy()

        for game in GAMES_DB:
            cpu_ratio = cpu_score / game["cpu_req"]
            gpu_ratio = gpu_score / game["gpu_req"]
            ram_factor = r_info["mult"] * (0.72 if ram_gb < game["ram_req"] else 1.0)

            effective_ratio = min(cpu_ratio, gpu_ratio) * ram_factor
            est_fps = int(60 * effective_ratio)

            if est_fps >= 100:
                status = f"🟢 Ультра настройки (~{est_fps}+ FPS)"
            elif est_fps >= 60:
                status = f"🟢 Высокие настройки (~{est_fps} FPS)"
            elif est_fps >= 40:
                status = f"🟡 Средние настройки (~{est_fps} FPS)"
            elif est_fps >= 25:
                status = f"🟠 Низкие настройки (~{est_fps} FPS)"
            else:
                status = f"🔴 Не потянет комфортно (<{max(10, est_fps)} FPS)"

            row = ctk.CTkFrame(self.games_container)
            row.pack(fill="x", padx=10, pady=3)
            ctk.CTkLabel(row, text=game["name"], font=ctk.CTkFont(size=14, weight="bold"), width=310, anchor="w").pack(side="left", padx=12, pady=7)
            ctk.CTkLabel(row, text=f"Реком. ОЗУ: {game['ram_req']} ГБ", text_color="gray70", width=130).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=status, font=ctk.CTkFont(size=14)).pack(side="right", padx=15)

    def _init_compare_page(self, parent):
        ctk.CTkLabel(parent, text="Точное сравнение процессоров, видеокарт, ОЗУ и накопителей", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(5, 12))

        cpu_frame = ctk.CTkFrame(parent)
        cpu_frame.pack(fill="x", pady=8)
        ctk.CTkLabel(cpu_frame, text="⚔️ Сравнение процессоров (CPU):", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(10, 6))

        sel_row = ctk.CTkFrame(cpu_frame, fg_color="transparent")
        sel_row.pack(fill="x", padx=15, pady=4)

        self.comp_cpu1 = ctk.CTkOptionMenu(sel_row, values=list(CPU_DB.keys()), width=270, command=lambda _: self._run_comparison())
        self.comp_cpu1.set("Intel Core i5-12400F")
        self.comp_cpu1.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(sel_row, text="VS", font=ctk.CTkFont(size=15, weight="bold")).pack(side="left", padx=8)

        self.comp_cpu2 = ctk.CTkOptionMenu(sel_row, values=list(CPU_DB.keys()), width=270, command=lambda _: self._run_comparison())
        self.comp_cpu2.set("AMD Ryzen 7 7800X3D")
        self.comp_cpu2.pack(side="left", padx=12)

        self.cpu_comp_res = ctk.CTkLabel(cpu_frame, text="", font=ctk.CTkFont(size=14), justify="left")
        self.cpu_comp_res.pack(anchor="w", padx=15, pady=(6, 12))

        gpu_frame = ctk.CTkFrame(parent)
        gpu_frame.pack(fill="x", pady=8)
        ctk.CTkLabel(gpu_frame, text="⚔️ Сравнение видеокарт (GPU):", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(10, 6))

        sel_gpu_row = ctk.CTkFrame(gpu_frame, fg_color="transparent")
        sel_gpu_row.pack(fill="x", padx=15, pady=4)

        self.comp_gpu1 = ctk.CTkOptionMenu(sel_gpu_row, values=list(GPU_DB.keys()), width=270, command=lambda _: self._run_comparison())
        self.comp_gpu1.set("NVIDIA RTX 3060 12GB")
        self.comp_gpu1.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(sel_gpu_row, text="VS", font=ctk.CTkFont(size=15, weight="bold")).pack(side="left", padx=8)

        self.comp_gpu2 = ctk.CTkOptionMenu(sel_gpu_row, values=list(GPU_DB.keys()), width=270, command=lambda _: self._run_comparison())
        self.comp_gpu2.set("NVIDIA RTX 4070 Super")
        self.comp_gpu2.pack(side="left", padx=12)

        self.gpu_comp_res = ctk.CTkLabel(gpu_frame, text="", font=ctk.CTkFont(size=14), justify="left")
        self.gpu_comp_res.pack(anchor="w", padx=15, pady=(6, 12))

        mem_frame = ctk.CTkFrame(parent)
        mem_frame.pack(fill="x", pady=8)
        ctk.CTkLabel(mem_frame, text="⚔️ Сравнение конфигураций ОЗУ и типов накопителей:", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(10, 6))

        mem_row = ctk.CTkFrame(mem_frame, fg_color="transparent")
        mem_row.pack(fill="x", padx=15, pady=4)

        self.comp_ram1 = ctk.CTkOptionMenu(mem_row, values=list(RAM_VARIATIONS.keys()), width=350, command=lambda _: self._run_comparison())
        self.comp_ram1.set("16 ГБ DDR4 (3200 МГц, Двухканал 2x8)")
        self.comp_ram1.pack(side="left", padx=(0, 10))

        self.comp_ram2 = ctk.CTkOptionMenu(mem_row, values=list(RAM_VARIATIONS.keys()), width=350, command=lambda _: self._run_comparison())
        self.comp_ram2.set("32 ГБ DDR5 (6000 МГц CL30, Двухканал 2x16)")
        self.comp_ram2.pack(side="left", padx=10)

        self.ram_comp_res = ctk.CTkLabel(mem_frame, text="", font=ctk.CTkFont(size=14), justify="left")
        self.ram_comp_res.pack(anchor="w", padx=15, pady=(6, 12))

        self._run_comparison()

    def _run_comparison(self):
        c1, c2 = self.comp_cpu1.get(), self.comp_cpu2.get()
        d1, d2 = CPU_DB[c1], CPU_DB[c2]
        diff_cpu = round(((d2["score"] - d1["score"]) / d1["score"]) * 100, 1)
        winner_cpu = c2 if d2["score"] >= d1["score"] else c1

        cpu_txt = (
            f"• {c1}: {d1['score']} pts | {d1['cores']} ядер / {d1['threads']} потоков | Частота: {d1['freq']} | Кэш L3: {d1['l3']} | TDP: {d1['tdp']} Вт ({d1['tier']})\n"
            f"• {c2}: {d2['score']} pts | {d2['cores']} ядер / {d2['threads']} потоков | Частота: {d2['freq']} | Кэш L3: {d2['l3']} | TDP: {d2['tdp']} Вт ({d2['tier']})\n"
            f"👉 Вердикт: {winner_cpu} производительнее на {abs(diff_cpu)}%"
        )
        self.cpu_comp_res.configure(text=cpu_txt)

        g1, g2 = self.comp_gpu1.get(), self.comp_gpu2.get()
        gd1, gd2 = GPU_DB[g1], GPU_DB[g2]
        diff_gpu = round(((gd2["score"] - gd1["score"]) / gd1["score"]) * 100, 1)
        winner_gpu = g2 if gd2["score"] >= gd1["score"] else g1

        gpu_txt = (
            f"• {g1}: {gd1['score']} pts | Память: {gd1['vram']} ГБ {gd1['vram_type']} ({gd1['bus']}) | Потребление: {gd1['tdp']} Вт | Класс: {gd1['tier']}\n"
            f"• {g2}: {gd2['score']} pts | Память: {gd2['vram']} ГБ {gd2['vram_type']} ({gd2['bus']}) | Потребление: {gd2['tdp']} Вт | Класс: {gd2['tier']}\n"
            f"👉 Вердикт: {winner_gpu} мощнее в играх и рендеринге на {abs(diff_gpu)}%"
        )
        self.gpu_comp_res.configure(text=gpu_txt)

        r1, r2 = self.comp_ram1.get(), self.comp_ram2.get()
        rd1, rd2 = RAM_VARIATIONS[r1], RAM_VARIATIONS[r2]
        diff_ram = round((rd2["mult"] - rd1["mult"]) * 100, 1)
        ram_txt = (
            f"• {r1} — {rd1['desc']}\n"
            f"• {r2} — {rd2['desc']}\n"
            f"👉 Разница в пропускной способности и минимальном FPS (1% Low): до {abs(diff_ram)}% в пользу более скоростного комплекта."
        )
        self.ram_comp_res.configure(text=ram_txt)

    def _init_builder_page(self, parent):
        ctk.CTkLabel(parent, text="Конфигуратор и проверка совместимости сборки ПК", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(5, 12))

        form = ctk.CTkFrame(parent)
        form.pack(fill="x", pady=6)

        ctk.CTkLabel(form, text="Процессор (CPU):", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        self.bld_cpu = ctk.CTkOptionMenu(form, values=list(CPU_DB.keys()), width=360, command=lambda _: self._calc_build())
        self.bld_cpu.set("AMD Ryzen 5 7500F")
        self.bld_cpu.grid(row=0, column=1, padx=15, pady=10)

        ctk.CTkLabel(form, text="Видеокарта (GPU):", font=ctk.CTkFont(size=14, weight="bold")).grid(row=1, column=0, padx=15, pady=10, sticky="w")
        self.bld_gpu = ctk.CTkOptionMenu(form, values=list(GPU_DB.keys()), width=360, command=lambda _: self._calc_build())
        self.bld_gpu.set("NVIDIA RTX 4070 Super")
        self.bld_gpu.grid(row=1, column=1, padx=15, pady=10)

        ctk.CTkLabel(form, text="Конфигурация ОЗУ:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=2, column=0, padx=15, pady=10, sticky="w")
        self.bld_ram = ctk.CTkOptionMenu(form, values=list(RAM_VARIATIONS.keys()), width=360, command=lambda _: self._calc_build())
        self.bld_ram.set("32 ГБ DDR5 (6000 МГц CL30, Двухканал 2x16)")
        self.bld_ram.grid(row=2, column=1, padx=15, pady=10)

        ctk.CTkLabel(form, text="Основной накопитель:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=3, column=0, padx=15, pady=10, sticky="w")
        self.bld_ssd = ctk.CTkOptionMenu(form, values=list(STORAGE_VARIATIONS.keys()), width=360, command=lambda _: self._calc_build())
        self.bld_ssd.set("NVMe M.2 PCIe 4.0 SSD (~7000 МБ/с)")
        self.bld_ssd.grid(row=3, column=1, padx=15, pady=10)

        self.build_summary_box = ctk.CTkTextbox(parent, height=260, font=ctk.CTkFont(size=14))
        self.build_summary_box.pack(fill="x", pady=10)

        self._calc_build()

    def _calc_build(self):
        c_name = self.bld_cpu.get()
        g_name = self.bld_gpu.get()
        ram_str = self.bld_ram.get()
        ssd_str = self.bld_ssd.get()

        c_data = CPU_DB[c_name]
        g_data = GPU_DB[g_name]
        r_data = RAM_VARIATIONS[ram_str]
        s_data = STORAGE_VARIATIONS[ssd_str]

        est_tdp = c_data["tdp"] + g_data["tdp"] + 75
        rec_psu = int(math.ceil((est_tdp * 1.35) / 50.0) * 50)

        ratio = c_data["score"] / max(1, g_data["score"])
        if ratio < 0.55:
            balance_msg = "⚠️ Дисбаланс (Слабый ЦП): процессор не сможет полностью нагрузить эту видеокарту. Выбери процессор классом выше."
        elif ratio > 1.65:
            balance_msg = "⚠️ Дисбаланс (Слабая видеокарта): процессор избыточен для такой видеокарты. Для игрового ПК лучше перераспределить бюджет в пользу GPU."
        else:
            balance_msg = "✅ Идеальный баланс между процессором и видеокартой! Компоненты раскрывают друг друга на 100%."

        ddr5_only_cpus = ["7500F", "7600X", "7700X", "7800X3D", "7950X3D", "9800X3D"]
        ddr4_only_cpus = ["10100F", "10400F", "11400F", "2600", "3600", "5500", "5600", "5600X", "5700X", "5700X3D"]
        mem_compat_msg = "✅ Выбранный тип оперативной памяти отлично подходит к процессору."
        if any(tag in c_name for tag in ddr5_only_cpus) and "DDR4" in ram_str:
            mem_compat_msg = "❗ ВНИМАНИЕ ПО СОВМЕСТИМОСТИ: Процессоры AMD Ryzen 7000/9000 (AM5) работают ТОЛЬКО с памятью DDR5! Выбери DDR5 в списке."
        elif any(tag in c_name for tag in ddr4_only_cpus) and "DDR5" in ram_str:
            mem_compat_msg = "❗ ВНИМАНИЕ ПО СОВМЕСТИМОСТИ: Выбранный процессор (AM4 / LGA1200) поддерживает только память DDR4! Переключи ОЗУ на DDR4."

        build_score = int((c_data["score"] * 0.38 + g_data["score"] * 0.62) * (r_data["mult"] + s_data["bonus"]))

        summary = (
            f"🛠 ПАСПОРТ ВЫБРАННОЙ СБОРКИ (Общий индекс мощности: {build_score} PTS):\n"
            f"   • Процессор: {c_name} ({c_data['cores']} ядер / {c_data['threads']} потоков, {c_data['freq']}, L3: {c_data['l3']})\n"
            f"   • Видеокарта: {g_name} ({g_data['vram']} ГБ {g_data['vram_type']}, шина {g_data['bus']})\n"
            f"   • ОЗУ: {ram_str}\n"
            f"   • Накопитель: {ssd_str} — {s_data['desc']}\n\n"
            f"⚡ РАСЧЕТ ПИТАНИЯ (БЛОК ПИТАНИЯ):\n"
            f"   • Пиковое энергопотребление системы: ~{est_tdp} Вт\n"
            f"   • Рекомендуемый Блок Питания (с запасом 35%): от {rec_psu} Вт (Сертификат 80+ Bronze / Gold)\n\n"
            f"🔍 ПРОВЕРКА СОВМЕСТИМОСТИ И БАЛАНСА:\n"
            f"   • {balance_msg}\n"
            f"   • {mem_compat_msg}"
        )

        self.build_summary_box.configure(state="normal")
        self.build_summary_box.delete("1.0", "end")
        self.build_summary_box.insert("1.0", summary)
        self.build_summary_box.configure(state="disabled")

    def _init_benchmark_page(self, parent):
        ctk.CTkLabel(parent, text="Синтетический стресс-тест процессора и ОЗУ", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(5, 10))

        ctk.CTkLabel(
            parent,
            text="Проверяет реальную скорость вычислений с плавающей запятой (FPU), тригонометрии и пропускной способности ОЗУ твоего ПК.",
            font=ctk.CTkFont(size=14),
            text_color="gray75",
        ).pack(anchor="w", pady=(0, 15))

        self.bench_btn = ctk.CTkButton(
            parent,
            text="🚀 Запустить стресс-тест ПК (5 секунд)",
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._start_benchmark,
        )
        self.bench_btn.pack(anchor="w", pady=10)

        self.bench_progress = ctk.CTkProgressBar(parent, height=16)
        self.bench_progress.pack(fill="x", pady=10)
        self.bench_progress.set(0)

        self.bench_result_box = ctk.CTkTextbox(parent, height=230, font=ctk.CTkFont(size=14))
        self.bench_result_box.pack(fill="x", pady=10)
        self.bench_result_box.insert("1.0", "Нажми кнопку выше, чтобы начать тестирование производительности твоего ПК...")
        self.bench_result_box.configure(state="disabled")

    def _start_benchmark(self):
        self.bench_btn.configure(state="disabled", text="⏳ Идет стресс-тест... Нагружаем ядра и ОЗУ")
        self.bench_progress.set(0.1)
        threading.Thread(target=self._run_benchmark_worker, daemon=True).start()

    def _run_benchmark_worker(self):
        start_cpu = time.perf_counter()
        ops = 0
        while time.perf_counter() - start_cpu < 2.5:
            for i in range(1, 20000):
                _ = math.sqrt(i) * math.sin(i) + math.cos(i)
            ops += 20000
            elapsed = time.perf_counter() - start_cpu
            self.bench_progress.set(min(0.5, (elapsed / 5.0)))

        cpu_points = int(ops / 1200)

        start_ram = time.perf_counter()
        ram_cycles = 0
        while time.perf_counter() - start_ram < 2.5:
            arr = [i % 256 for i in range(250000)]
            arr.reverse()
            ram_cycles += 1
            elapsed = 2.5 + (time.perf_counter() - start_ram)
            self.bench_progress.set(min(1.0, (elapsed / 5.0)))

        ram_points = int(ram_cycles * 85)
        total_bench = cpu_points + ram_points

        res_text = (
            f"✅ СТРЕСС-ТЕСТ УСПЕШНО ЗАВЕРШЕН!\n\n"
            f"🔹 Выполнено математических операций ЦП: {ops:,}\n"
            f"🔹 Баллы процессора (CPU Score): {cpu_points} pts\n"
            f"🔹 Баллы оперативной памяти (RAM Score): {ram_points} pts\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏆 ИТОГОВЫЙ РЕЙТИНГ СИСТЕМЫ: {total_bench} PTS\n\n"
            f"Сравнение с эталонами:\n"
            f"   • Офисный ноутбук: ~2 500 pts\n"
            f"   • Средний игровой ПК: ~6 500 pts\n"
            f"   • Мощная рабочая станция: ~11 000+ pts"
        )

        self.bench_result_box.configure(state="normal")
        self.bench_result_box.delete("1.0", "end")
        self.bench_result_box.insert("1.0", res_text)
        self.bench_result_box.configure(state="disabled")
        self.bench_btn.configure(state="normal", text="🚀 Запустить стресс-тест повторно")

    def _init_health_page(self, parent):
        ctk.CTkLabel(parent, text="Центр Здоровья ПК: Очистка кэша, Сетевой пинг и Экспорт отчета", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(5, 12))

        temp_card = ctk.CTkFrame(parent)
        temp_card.pack(fill="x", pady=6)
        ctk.CTkLabel(temp_card, text="🗑 Очистка временных файлов и системного кэша (%TEMP%):", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(10, 4))
        ctk.CTkLabel(
            temp_card,
            text="Безопасно удаляет накопившийся временный мусор из папки Temp, освобождая место на SSD/HDD без вреда для личных файлов.",
            font=ctk.CTkFont(size=13),
            text_color="gray75",
        ).pack(anchor="w", padx=15, pady=(0, 8))

        t_row = ctk.CTkFrame(temp_card, fg_color="transparent")
        t_row.pack(fill="x", padx=15, pady=(0, 12))
        ctk.CTkButton(t_row, text="🧹 Очистить системный кэш Temp", command=self._clean_temp_folder).pack(side="left")
        self.temp_status_lbl = ctk.CTkLabel(t_row, text="", font=ctk.CTkFont(size=13, weight="bold"))
        self.temp_status_lbl.pack(side="left", padx=15)

        net_card = ctk.CTkFrame(parent)
        net_card.pack(fill="x", pady=6)
        ctk.CTkLabel(net_card, text="🌐 Тест стабильности интернета и игрового пинга (Ping Test):", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(10, 4))
        ctk.CTkLabel(
            net_card,
            text="Проверяет скорость отклика твоей сети до глобальных узлов (Cloudflare 1.1.1.1, Google DNS 8.8.8.8) для оценки комфорта в онлайн-играх.",
            font=ctk.CTkFont(size=13),
            text_color="gray75",
        ).pack(anchor="w", padx=15, pady=(0, 8))

        n_row = ctk.CTkFrame(net_card, fg_color="transparent")
        n_row.pack(fill="x", padx=15, pady=(0, 12))
        self.ping_btn = ctk.CTkButton(n_row, text="📡 Проверить пинг и задержку сети", command=self._run_ping_test)
        self.ping_btn.pack(side="left")
        self.ping_status_lbl = ctk.CTkLabel(n_row, text="", font=ctk.CTkFont(size=13, weight="bold"))
        self.ping_status_lbl.pack(side="left", padx=15)

        exp_card = ctk.CTkFrame(parent)
        exp_card.pack(fill="x", pady=6)
        ctk.CTkLabel(exp_card, text="📄 Сохранение полного технического паспорта ПК в файл:", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(10, 4))
        ctk.CTkLabel(
            exp_card,
            text="Создает подробный файл PC_Report.txt со всеми характеристиками твоего ПК, материнской платой, дисками и периферией.",
            font=ctk.CTkFont(size=13),
            text_color="gray75",
        ).pack(anchor="w", padx=15, pady=(0, 8))

        e_row = ctk.CTkFrame(exp_card, fg_color="transparent")
        e_row.pack(fill="x", padx=15, pady=(0, 12))
        ctk.CTkButton(
            e_row, text="💾 Сохранить отчет (PC_Report.txt)", fg_color="#27ae60", hover_color="#1e8449", command=self._export_pc_report
        ).pack(side="left")
        self.exp_status_lbl = ctk.CTkLabel(e_row, text="", font=ctk.CTkFont(size=13, weight="bold"))
        self.exp_status_lbl.pack(side="left", padx=15)

    def _clean_temp_folder(self):
        temp_dir = os.environ.get("TEMP")
        if not temp_dir or not os.path.exists(temp_dir):
            self.temp_status_lbl.configure(text="Папка TEMP не найдена", text_color="orange")
            return

        removed_files = 0
        freed_bytes = 0
        for root_dir, dirs, files in os.walk(temp_dir):
            for f in files:
                fp = os.path.join(root_dir, f)
                try:
                    sz = os.path.getsize(fp)
                    os.remove(fp)
                    removed_files += 1
                    freed_bytes += sz
                except Exception:
                    continue

        freed_mb = round(freed_bytes / (1024 * 1024), 1)
        self.temp_status_lbl.configure(
            text=f"✅ Удалено временных файлов: {removed_files} шт. | Освобождено: {freed_mb} МБ", text_color="#2ecc71"
        )

    def _run_ping_test(self):
        self.ping_btn.configure(state="disabled", text="⏳ Измеряем пинг...")
        threading.Thread(target=self._ping_worker, daemon=True).start()

    def _ping_worker(self):
        targets = [("Cloudflare (1.1.1.1)", "1.1.1.1"), ("Google DNS (8.8.8.8)", "8.8.8.8")]
        results = []
        for label, host in targets:
            t0 = time.perf_counter()
            try:
                param = "-n" if platform.system() == "Windows" else "-c"
                startupinfo = None
                if platform.system() == "Windows":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.check_output(
                    f"ping {param} 1 -w 1500 {host}", shell=True, stderr=subprocess.DEVNULL, startupinfo=startupinfo
                )
                ms = int((time.perf_counter() - t0) * 1000)
                results.append(f"{label}: ~{ms} мс")
            except Exception:
                results.append(f"{label}: Недоступен")

        self.ping_status_lbl.configure(text=" | ".join(results), text_color="#4da6ff")
        self.ping_btn.configure(state="normal", text="📡 Проверить пинг и задержку сети")

    def _export_pc_report(self):
        filename = f"PC_Report_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.txt"
        report_content = (
            "====================================================================\n"
            "               ТЕХНИЧЕСКИЙ ПАСПОРТ ПК (PC MASTER HUB v2.0)          \n"
            "====================================================================\n"
            f"Дата создания отчета: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
            f"Операционная система: {self.hw_info['os']}\n\n"
            "--- ОСНОВНЫЕ КОМПЛЕКТУЮЩИЕ ---\n"
            f"Процессор (CPU): {self.hw_info['cpu_name']} ({self.hw_info['cores_phys']} ядер / {self.hw_info['cores_log']} потоков)\n"
            f"Видеокарта (GPU): {self.hw_info['gpu_name']}\n"
            f"Материнская плата: {self.hw_info['mb_info']}\n"
            f"Оперативная память: {self.hw_info['ram_gb']} ГБ ({self.hw_info['ram_modules_str']})\n"
            f"Питание / БП: {self.hw_info['psu_info']}\n"
            f"Накопители:\n   • {self.hw_info['disk_models_str']}\n\n"
            "--- ПОДКЛЮЧЕННЫЕ УСТРОЙСТВА И ПЕРИФЕРИЯ ---\n"
            f"Мониторы: {self.hw_info['monitors_str']}\n"
            f"Аудиоустройства: {self.hw_info['audio_str']}\n"
            f"Клавиатура: {self.hw_info['kb_str']}\n"
            f"Мышь: {self.hw_info['mouse_str']}\n"
            "====================================================================\n"
        )
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report_content)
            self.exp_status_lbl.configure(text=f"✅ Сохранено в файл: {filename}", text_color="#2ecc71")
        except Exception as e:
            self.exp_status_lbl.configure(text=f"Ошибка сохранения: {e}", text_color="red")


if __name__ == "__main__":
    app = PCMasterApp()
    app.mainloop()