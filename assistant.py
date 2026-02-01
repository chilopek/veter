import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import threading
import time
import os
import platform
import webbrowser
import sys
import subprocess
import datetime
import random
import re
import json
import warnings
import asyncio
import wave
import pyaudio
from vosk import Model, KaldiRecognizer

# Отключаем все предупреждения для угрузки
warnings.filterwarnings("ignore")

print("🚀 Запуск голосового помощника ВЕТЕР...")

class LazyImports:
    """Ленивая загрузка тяжелых библиотек"""
    def __init__(self):
        self._pyautogui = None
        self._pygetwindow = None
        self._telethon = None
        self._vosk = None
        self._pyaudio = None
        
    @property
    def pyautogui(self):
        if self._pyautogui is None:
            try:
                import pyautogui
                self._pyautogui = pyautogui
                print("✅ pyautogui загружен")
            except ImportError as e:
                print(f"❌ Ошибка загрузки pyautogui: {e}")
                self._pyautogui = None
        return self._pyautogui
    
    @property
    def pygetwindow(self):
        if self._pygetwindow is None:
            try:
                import pygetwindow as gw
                self._pygetwindow = gw
                print("✅ pygetwindow загружен")
            except ImportError as e:
                print(f"❌ Ошибка загрузки pygetwindow: {e}")
                self._pygetwindow = None
        return self._pygetwindow
    
    @property
    def telethon(self):
        if self._telethon is None:
            try:
                from telethon import TelegramClient
                import asyncio
                self._telethon = {
                    'TelegramClient': TelegramClient,
                    'asyncio': asyncio
                }
                print("✅ telethon загружен")
            except ImportError as e:
                print(f"❌ Ошибка загрузки telethon: {e}")
                self._telethon = None
        return self._telethon
    
    @property
    def vosk(self):
        if self._vosk is None:
            try:
                import vosk
                self._vosk = vosk
                print("✅ vosk загружен")
            except ImportError as e:
                print(f"❌ Ошибка загрузки vosk: {e}")
                self._vosk = None
        return self._vosk
    
    @property
    def pyaudio(self):
        if self._pyaudio is None:
            try:
                import pyaudio
                self._pyaudio = pyaudio
                print("✅ pyaudio загружен")
            except ImportError as e:
                print(f"❌ Ошибка загрузки pyaudio: {e}")
                self._pyaudio = None
        return self._pyaudio

lazy = LazyImports()

class VoiceAssistantGUI:
    def __init__(self, root, assistant):
        self.root = root
        self.assistant = assistant
        self.setup_gui()
        
    def setup_gui(self):
        """Настройка графического интерфейса"""
        self.root.title("🎤 Voice Assistant - ВЕТЕР")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Стиль для кнопок
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 9))
        style.configure('TLabel', font=('Arial', 9))
        
        # Основные фреймы
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="🎤 Голосовой помощник ВЕТЕР", 
                               font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Статус бар
        self.status_var = tk.StringVar(value="⚡ Запуск...")
        status_label = ttk.Label(header_frame, textvariable=self.status_var, 
                                font=("Arial", 10), foreground="gray")
        status_label.pack(side=tk.RIGHT)
        
        # Панель с вкладками
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладки
        self.setup_main_tab()
        self.setup_telegram_tab()
        self.setup_logs_tab()
        self.setup_commands_tab()
        
        # Панель управления
        self.setup_control_panel(main_frame)
        
        # Запуск обновления интерфейса
        self.update_ui()
        
    def setup_main_tab(self):
        """Вкладка основного управления"""
        main_tab = ttk.Frame(self.notebook)
        self.notebook.add(main_tab, text="🏠 Основное")
        
        # Статус помощника
        status_frame = ttk.LabelFrame(main_tab, text="📊 Статус системы", padding="10")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Сетка для статуса
        status_grid = ttk.Frame(status_frame)
        status_grid.pack(fill=tk.X)
        
        # Информация о системе
        info_labels = [
            ("🔍 Состояние:", "status_label", "Загрузка..."),
            ("🎯 Режим:", "mode_label", "Ожидание ключевого слова"),
            ("⚙️ Рабочий режим:", "work_mode_label", "Активен"),
            ("🎤 Микрофон:", "mic_label", "Проверка..."),
            ("📱 Telegram:", "tg_label", "Не настроен"),
            ("🔊 Чувствительность:", "sensitivity_label", "0.5")
        ]
        
        for i, (text, attr, default) in enumerate(info_labels):
            ttk.Label(status_grid, text=text, font=("Arial", 9)).grid(
                row=i, column=0, sticky=tk.W, padx=(0, 5), pady=2)
            label = ttk.Label(status_grid, text=default, font=("Arial", 9, "bold"))
            label.grid(row=i, column=1, sticky=tk.W, pady=2)
            setattr(self, attr, label)
        
        # Быстрые команды
        commands_frame = ttk.LabelFrame(main_tab, text="🚀 Быстрые команды", padding="10")
        commands_frame.pack(fill=tk.X, padx=5, pady=5)
        
        quick_buttons = [
            ("📅 Время/дата", self.show_time_date),
            ("🌐 Браузер", self.open_browser),
            ("🎵 Громче", self.volume_up),
            ("🔇 Тише", self.volume_down),
            ("🔄 Калибровка", self.calibrate_mic),
            ("📸 Скриншот", self.take_screenshot),
            ("🏢 Рабочий режим", self.switch_to_work_mode),
            ("🎮 Игровой режим", self.switch_to_game_mode),
            ("❌ Закрой окно", self.close_window),
            ("🔄 Переключи окно", self.switch_window),
            ("⏰ Таймер 5 мин", self.set_timer_5min),
        ]
        
        btn_frame = ttk.Frame(commands_frame)
        btn_frame.pack()
        
        for i, (text, command) in enumerate(quick_buttons):
            btn = ttk.Button(btn_frame, text=text, command=command, width=15)
            btn.grid(row=i//4, column=i%4, padx=5, pady=5, sticky="ew")
        
        # Информация о системе
        info_frame = ttk.LabelFrame(main_tab, text="ℹ️ Информация", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        info_text = """
🤖 Голосовой помощник "ВЕТЕР" готов к работе!

📋 Основные возможности:
• Управление компьютером голосом (оффлайн)
• Открытие приложений и сайтов
• Поиск в интернете
• Управление громкостью
• Установка таймеров
• Скриншоты
• Отправка сообщений в Telegram

🎯 Просто скажите "ВЕТЕР" и вашу команду!
        """
        
        info_text_widget = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD, 
                                                   width=80, height=8, font=("Arial", 9))
        info_text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        info_text_widget.insert(tk.END, info_text)
        info_text_widget.config(state=tk.DISABLED)
        
    def setup_telegram_tab(self):
        """Вкладка Telegram"""
        telegram_tab = ttk.Frame(self.notebook)
        self.notebook.add(telegram_tab, text="📱 Telegram")
        
        # Настройки API
        api_frame = ttk.LabelFrame(telegram_tab, text="⚙️ Настройки Telegram API", padding="15")
        api_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # API ID
        ttk.Label(api_frame, text="🔑 API ID:", font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.api_id_var = tk.StringVar()
        api_id_entry = ttk.Entry(api_frame, textvariable=self.api_id_var, 
                                width=40, font=("Arial", 10))
        api_id_entry.pack(fill=tk.X, pady=(0, 10))
        
        # API Hash
        ttk.Label(api_frame, text="🔒 API Hash:", font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.api_hash_var = tk.StringVar()
        api_hash_entry = ttk.Entry(api_frame, textvariable=self.api_hash_var, 
                                  width=40, font=("Arial", 10))
        api_hash_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Номер телефона
        ttk.Label(api_frame, text="📞 Номер телефона:", font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.phone_var = tk.StringVar()
        phone_entry = ttk.Entry(api_frame, textvariable=self.phone_var, 
                               width=40, font=("Arial", 10))
        phone_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Кнопки управления Telegram
        tg_btn_frame = ttk.Frame(api_frame)
        tg_btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(tg_btn_frame, text="💾 Сохранить настройки", 
                  command=self.save_telegram_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(tg_btn_frame, text="🔗 Подключить Telegram", 
                  command=self.connect_telegram).pack(side=tk.LEFT, padx=5)
        ttk.Button(tg_btn_frame, text="🧪 Тест отправки", 
                  command=self.test_telegram_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(tg_btn_frame, text="👥 Показать контакты", 
                  command=self.show_contacts).pack(side=tk.LEFT, padx=5)
        
        # История сообщений
        history_frame = ttk.LabelFrame(telegram_tab, text="📨 История сообщений", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.telegram_logs = scrolledtext.ScrolledText(history_frame, wrap=tk.WORD, 
                                                      width=80, height=15, font=("Arial", 9))
        self.telegram_logs.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.telegram_logs.config(state=tk.DISABLED)
        
        # Загружаем сохраненные настройки
        self.load_telegram_settings()
        
    def setup_commands_tab(self):
        """Вкладка с командами"""
        commands_tab = ttk.Frame(self.notebook)
        self.notebook.add(commands_tab, text="🎯 Команды")
        
        # Голосовые команды
        voice_frame = ttk.LabelFrame(commands_tab, text="🎤 Голосовые команды", padding="10")
        voice_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        commands_text = """
🎯 Ключевое слово: 'ВЕТЕР'

📋 ОСНОВНЫЕ КОМАНДЫ:

🌐 Открытие сайтов:
• 'открой браузер' - открыть Google
• 'открой ютуб' - открыть YouTube
• 'открой вк' - открыть ВКонтакте
• 'открой яндекс' - открыть Яндекс

🖥️ Открытие приложений:
• 'открой калькулятор' - открыть калькулятор
• 'открой блокнот' - открыть блокнот
• 'открой проводник' - открыть проводник

🔊 Управление звуком:
• 'громче' - увеличить громкость
• 'тише' - уменьшить громкость
• 'выключи звук' - отключить звук
• 'включи звук' - включить звук

⏰ Время и таймеры:
• 'время' - текущее время
• 'дата' - текущая дата
• 'таймер на 5 минут' - установить таймер
• 'поставь таймер 10 минут'

🔍 Поиск:
• 'найди [запрос]' - поиск в интернете
• 'ищи [запрос]' - поиск в интернете

🖼️ Системные команды:
• 'скриншот' - сделать скриншот
• 'закрой окно' - закрыть активное окно
• 'переключи окно' - переключить окно

📱 TELEGRAM КОМАНДЫ:
• 'напиши [имя] [сообщение]' - отправить сообщение
• 'телеграм тест' - проверить подключение
• 'покажи контакты' - показать список контактов

🎮 РЕЖИМЫ РАБОТЫ:
• 'рабочий режим' - постоянное слушание
• 'игровой режим' - активация по ключевому слову
• 'какой режим' - узнать текущий режим
        """
        
        cmd_text = scrolledtext.ScrolledText(voice_frame, wrap=tk.WORD, 
                                           width=80, height=20, font=("Arial", 9))
        cmd_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        cmd_text.insert(tk.END, commands_text)
        cmd_text.config(state=tk.DISABLED)
        
    def setup_logs_tab(self):
        """Вкладка логов"""
        logs_tab = ttk.Frame(self.notebook)
        self.notebook.add(logs_tab, text="📊 Логи системы")
        
        # Текстовое поле для логов
        self.log_text = scrolledtext.ScrolledText(logs_tab, wrap=tk.WORD, 
                                                width=80, height=25, font=("Arial", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)
        
        # Кнопки управления логами
        btn_frame = ttk.Frame(logs_tab)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="🗑️ Очистить логи", 
                  command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 Сохранить логи", 
                  command=self.save_logs).pack(side=tk.LEFT, padx=5)
        
    def setup_control_panel(self, parent):
        """Панель управления"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(control_frame, text="🎤 Начать слушать", 
                  command=self.start_listening, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="⏸️ Остановить", 
                  command=self.stop_listening, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🔇 Выключить звук", 
                  command=self.assistant.stop_speech, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="❌ Выход", 
                  command=self.quit_app, width=15).pack(side=tk.RIGHT, padx=5)
        
    def update_ui(self):
        """Обновление интерфейса"""
        try:
            # Обновляем статус
            if self.assistant.is_listening:
                self.status_label.config(text="🟢 Активен", foreground="green")
                self.mode_label.config(text="Слушает команды", foreground="blue")
                self.status_var.set("🔊 Слушает...")
            else:
                self.status_label.config(text="🟡 Остановлен", foreground="orange")
                self.mode_label.config(text="Приостановлено", foreground="orange")
                self.status_var.set("⏸️ Остановлен")
            
            # Обновляем режим работы
            if self.assistant.work_mode:
                self.work_mode_label.config(text="РАБОЧИЙ", foreground="green")
            else:
                self.work_mode_label.config(text="ИГРОВОЙ", foreground="orange")
            
            # Обновляем статус микрофона
            if hasattr(self.assistant, 'audio') and self.assistant.audio:
                self.mic_label.config(text="✅ Работает", foreground="green")
            else:
                self.mic_label.config(text="❌ Не доступен", foreground="red")
            
            # Обновляем статус Telegram
            if hasattr(self.assistant, 'telegram_client') and self.assistant.telegram_client:
                if self.assistant.telegram_client.is_connected():
                    self.tg_label.config(text="✅ Подключен", foreground="green")
                else:
                    self.tg_label.config(text="🟡 Ожидает код", foreground="orange")
            else:
                self.tg_label.config(text="⚙️ Не настроен", foreground="orange")
            
            # Обновляем чувствительность
            if hasattr(self.assistant, 'recognition_threshold'):
                sensitivity = self.assistant.recognition_threshold
                self.sensitivity_label.config(text=f"{sensitivity:.2f}")
                
        except Exception as e:
            pass
        
        # Планируем следующее обновление
        self.root.after(1000, self.update_ui)
        
    def add_log(self, message):
        """Добавление сообщения в лог"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def add_telegram_log(self, message):
        """Добавление сообщения в историю Telegram"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.telegram_logs.config(state=tk.NORMAL)
        self.telegram_logs.insert(tk.END, log_message)
        self.telegram_logs.see(tk.END)
        self.telegram_logs.config(state=tk.DISABLED)
        
    def clear_logs(self):
        """Очистка логов"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def save_logs(self):
        """Сохранение логов в файл"""
        try:
            filename = f"assistant_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.log_text.get(1.0, tk.END))
            self.add_log(f"Логи сохранены в {filename}")
            messagebox.showinfo("Успех", f"Логи сохранены в файл:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить логи: {e}")
            
    def load_telegram_settings(self):
        """Загрузка настроек Telegram из файла"""
        try:
            if os.path.exists("telegram_settings.json"):
                with open("telegram_settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    self.api_id_var.set(settings.get('api_id', ''))
                    self.api_hash_var.set(settings.get('api_hash', ''))
                    self.phone_var.set(settings.get('phone', ''))
                    
                    # Передаем настройки ассистенту
                    self.assistant.telegram_api_id = settings.get('api_id')
                    self.assistant.telegram_api_hash = settings.get('api_hash')
                    self.assistant.telegram_phone = settings.get('phone')
                    
                self.add_telegram_log("✅ Настройки Telegram загружены из файла")
                self.add_log("Настройки Telegram загружены")
        except Exception as e:
            print(f"❌ Ошибка загрузки настроек Telegram: {e}")
            
    def save_telegram_settings(self):
        """Сохранение настроек Telegram в файл"""
        api_id = self.api_id_var.get().strip()
        api_hash = self.api_hash_var.get().strip()
        phone = self.phone_var.get().strip()
        
        if not api_id or not api_hash or not phone:
            messagebox.showwarning("Предупреждение", "Заполните все обязательные поля настроек Telegram")
            return
        
        try:
            # Сохраняем в файл
            settings = {
                'api_id': api_id,
                'api_hash': api_hash,
                'phone': phone
            }
            
            with open("telegram_settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            # Сохраняем в переменные ассистента
            self.assistant.telegram_api_id = api_id
            self.assistant.telegram_api_hash = api_hash
            self.assistant.telegram_phone = phone
            
            self.add_log("Настройки Telegram сохранены")
            self.add_telegram_log("✅ Настройки сохранены в telegram_settings.json")
            messagebox.showinfo("Успех", "Настройки Telegram сохранены!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
            
    def connect_telegram(self):
        """Подключение к Telegram"""
        if not hasattr(self.assistant, 'telegram_api_id') or not self.assistant.telegram_api_id:
            messagebox.showwarning("Предупреждение", "Сначала сохраните настройки Telegram")
            return
            
        try:
            self.add_telegram_log("🔗 Подключаемся к Telegram...")
            
            # Запускаем подключение в отдельном потоке
            def connect_thread():
                try:
                    success = self.assistant.init_telegram()
                    
                    if success:
                        if self.assistant.telegram_client and self.assistant.telegram_client.is_connected():
                            self.root.after(0, lambda: self.add_telegram_log("✅ Успешно подключено к Telegram"))
                        else:
                            # Требуется код подтверждения
                            self.root.after(0, self.request_telegram_code)
                    else:
                        self.root.after(0, lambda: self.add_telegram_log("❌ Ошибка подключения к Telegram"))
                        
                except Exception as e:
                    self.root.after(0, lambda: self.add_telegram_log(f"❌ Ошибка: {e}"))
            
            threading.Thread(target=connect_thread, daemon=True).start()
                
        except Exception as e:
            self.add_telegram_log(f"❌ Ошибка: {e}")
            
    def request_telegram_code(self):
        """Запрос кода подтверждения через всплывающее окно"""
        self.add_telegram_log("📱 Запрошен код подтверждения")
        self.add_telegram_log("🔐 Код отправлен в приложение Telegram")
        
        # Создаем всплывающее окно для ввода кода
        code = simpledialog.askstring(
            "Код подтверждения Telegram",
            "Код подтверждения отправлен в приложение Telegram.\n\n"
            "Введите код:",
            parent=self.root
        )
        
        if code:
            self.add_telegram_log(f"🔐 Вводим код подтверждения: {code}")
            
            # Вводим код в отдельном потоке
            def enter_code_thread():
                try:
                    success = self.assistant.enter_telegram_code(code)
                    if success:
                        self.root.after(0, lambda: self.add_telegram_log("✅ Успешная авторизация в Telegram"))
                        self.root.after(0, lambda: messagebox.showinfo("Успех", "Подключение к Telegram установлено!"))
                    else:
                        self.root.after(0, lambda: self.add_telegram_log("❌ Неверный код подтверждения"))
                        self.root.after(0, lambda: messagebox.showerror("Ошибка", "Неверный код подтверждения"))
                except Exception as e:
                    self.root.after(0, lambda: self.add_telegram_log(f"❌ Ошибка ввода кода: {e}"))
            
            threading.Thread(target=enter_code_thread, daemon=True).start()
        else:
            self.add_telegram_log("❌ Ввод кода отменен")
            
    def test_telegram_message(self):
        """Тест отправки сообщения"""
        if not hasattr(self.assistant, 'telegram_client') or not self.assistant.telegram_client:
            messagebox.showwarning("Предупреждение", "Сначала подключитесь к Telegram")
            return
            
        try:
            self.add_telegram_log("🧪 Тестируем отправку сообщения...")
            
            # Запускаем отправку в отдельном потоке
            def send_test_message():
                try:
                    success = self.assistant.send_telegram_message_sync("me", "Тестовое сообщение от голосового помощника ВЕТЕР")
                    if success:
                        self.root.after(0, lambda: self.add_telegram_log("✅ Тестовое сообщение отправлено"))
                        self.root.after(0, lambda: messagebox.showinfo("Успех", "Тестовое сообщение отправлено!"))
                    else:
                        self.root.after(0, lambda: self.add_telegram_log("❌ Ошибка отправки тестового сообщения"))
                        self.root.after(0, lambda: messagebox.showerror("Ошибка", "Не удалось отправить тестовое сообщение"))
                except Exception as e:
                    self.root.after(0, lambda: self.add_telegram_log(f"❌ Ошибка отправки: {e}"))
            
            threading.Thread(target=send_test_message, daemon=True).start()
            
        except Exception as e:
            self.add_telegram_log(f"❌ Ошибка отправки: {e}")
            messagebox.showerror("Ошибка", f"Ошибка отправки: {e}")

    def show_contacts(self):
        """Показать список контактов"""
        if not hasattr(self.assistant, 'telegram_client') or not self.assistant.telegram_client:
            messagebox.showwarning("Предупреждение", "Сначала подключитесь к Telegram")
            return
            
        try:
            self.add_telegram_log("👥 Загружаем список контактов...")
            
            def load_contacts_thread():
                try:
                    contacts = self.assistant.get_telegram_contacts()
                    if contacts:
                        contacts_text = "📋 Доступные контакты:\n\n"
                        for contact in contacts:
                            contacts_text += f"• {contact}\n"
                        
                        self.root.after(0, lambda: self.add_telegram_log(contacts_text))
                        self.root.after(0, lambda: messagebox.showinfo("Контакты Telegram", contacts_text))
                    else:
                        self.root.after(0, lambda: self.add_telegram_log("❌ Не удалось загрузить контакты"))
                except Exception as e:
                    self.root.after(0, lambda: self.add_telegram_log(f"❌ Ошибка загрузки контактов: {e}"))
            
            threading.Thread(target=load_contacts_thread, daemon=True).start()
            
        except Exception as e:
            self.add_telegram_log(f"❌ Ошибка: {e}")
            
    def switch_to_work_mode(self):
        """Переключение в рабочий режим"""
        self.assistant.switch_to_work_mode()
        self.add_log("🏢 Включен рабочий режим")
        
    def switch_to_game_mode(self):
        """Переключение в игровой режим"""
        self.assistant.switch_to_game_mode()
        self.add_log("🎮 Включен игровой режим")

    def start_listening(self):
        """Начать прослушивание"""
        self.assistant.is_listening = True
        self.add_log("🎤 Прослушивание запущено")
            
    def stop_listening(self):
        """Остановить прослушивание"""
        self.assistant.is_listening = False
        self.add_log("⏸️ Прослушивание остановлено")
            
    def show_time_date(self):
        """Показать время и дату"""
        current_time = time.strftime("%H:%M:%S")
        current_date = time.strftime("%d.%m.%Y")
        self.assistant.speak(f"Сейчас {current_time}, сегодня {current_date}")
        self.add_log(f"📅 Запрос времени: {current_time}, {current_date}")
        
    def open_browser(self):
        """Открыть браузер"""
        webbrowser.open("https://google.com")
        self.assistant.speak("Открываю браузер")
        self.add_log("🌐 Открыт браузер")
        
    def volume_up(self):
        """Увеличить громкость"""
        self.assistant.change_volume("громче")
        self.add_log("🔊 Громкость увеличена")
        
    def volume_down(self):
        """Уменьшить громкость"""
        self.assistant.change_volume("тише")
        self.add_log("🔇 Громкость уменьшена")
        
    def calibrate_mic(self):
        """Калибровка микрофона"""
        self.assistant.speak("Начинаю калибровку микрофона")
        self.add_log("🎤 Запущена калибровка микрофона")
        
    def take_screenshot(self):
        """Сделать скриншот"""
        self.assistant.take_screenshot()
        self.add_log("📸 Сделан скриншот")
        
    def close_window(self):
        """Закрыть активное окно"""
        self.assistant.close_active_window()
        self.add_log("❌ Закрыто активное окно")
        
    def switch_window(self):
        """Переключить окно"""
        self.assistant.switch_windows()
        self.add_log("🔄 Переключено окно")
        
    def set_timer_5min(self):
        """Установить таймер на 5 минут"""
        self.assistant.set_timer(300, "5 минут")
        self.add_log("⏰ Установлен таймер на 5 минут")
        
    def quit_app(self):
        """Завершение работы приложения"""
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.assistant.is_listening = False
            if hasattr(self.assistant, 'telegram_client') and self.assistant.telegram_client:
                self.assistant.telegram_client.disconnect()
            self.root.quit()
            self.root.destroy()

class TelegramManager:
    """Менеджер для работы с Telegram в отдельном потоке"""
    
    def __init__(self, assistant):
        self.assistant = assistant
        self.loop = None
        self.client = None
        self.thread = None
        self.contacts_cache = None
        self.last_contacts_update = 0
        
    def start_loop(self):
        """Запуск event loop в отдельном потоке"""
        if self.loop and self.loop.is_running():
            return
            
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            try:
                self.loop.run_forever()
            finally:
                self.loop.close()
                
        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()
        
    def stop_loop(self):
        """Остановка event loop"""
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
            
    async def _connect_telegram_async(self):
        """Асинхронное подключение к Telegram"""
        try:
            if not self.assistant.telegram_api_id or not self.assistant.telegram_api_hash or not self.assistant.telegram_phone:
                return False, "Настройки Telegram не заполнены"
            
            # Создаем клиент
            self.client = lazy.telethon['TelegramClient'](
                'assistant_session', 
                int(self.assistant.telegram_api_id), 
                self.assistant.telegram_api_hash,
                loop=self.loop
            )
            
            # Подключаемся
            await self.client.start(phone=self.assistant.telegram_phone)
            
            if self.client.is_connected():
                return True, "Успешно подключено к Telegram"
            else:
                return True, "Ожидание кода подтверждения"
                
        except Exception as e:
            return False, f"Ошибка подключения: {e}"
            
    def connect_telegram(self):
        """Синхронная обертка для подключения к Telegram"""
        if not self.loop or not self.loop.is_running():
            self.start_loop()
            
        future = asyncio.run_coroutine_threadsafe(self._connect_telegram_async(), self.loop)
        return future.result(timeout=30)
    
    async def _update_contacts_cache(self):
        """Обновление кэша контактов"""
        try:
            if not self.client or not self.client.is_connected():
                return
            
            # Обновляем кэш раз в 5 минут
            if time.time() - self.last_contacts_update < 300 and self.contacts_cache:
                return
                
            self.contacts_cache = []
            dialogs = await self.client.get_dialogs(limit=100)
            
            for dialog in dialogs:
                entity = dialog.entity
                contact_info = {
                    'entity': entity,
                    'id': entity.id,
                    'name': '',
                    'username': '',
                    'type': 'unknown'
                }
                
                if hasattr(entity, 'first_name') and entity.first_name:
                    contact_info['name'] = f"{entity.first_name} {entity.last_name or ''}".strip()
                    contact_info['type'] = 'user'
                elif hasattr(entity, 'title'):
                    contact_info['name'] = entity.title
                    contact_info['type'] = 'chat'
                
                if hasattr(entity, 'username') and entity.username:
                    contact_info['username'] = f"@{entity.username}"
                
                self.contacts_cache.append(contact_info)
            
            self.last_contacts_update = time.time()
            
        except Exception as e:
            print(f"Ошибка обновления кэша контактов: {e}")
        
    async def _send_message_async(self, contact_name, message):
        """Асинхронная отправка сообщения"""
        try:
            if not self.client or not self.client.is_connected():
                return False, "Telegram клиент не подключен"
            
            # Обновляем кэш контактов
            await self._update_contacts_cache()
            
            entity = None
            contact_info = "неизвестному контакту"
            
            # Поиск контакта с приоритетами
            candidates = []
            
            if self.contacts_cache:
                # 1. Точное совпадение по username (без @)
                for contact in self.contacts_cache:
                    if contact['username'] and contact['username'].lower() == f"@{contact_name.lower()}":
                        entity = contact['entity']
                        contact_info = contact['name'] or contact['username']
                        break
                
                # 2. Точное совпадение по имени
                if not entity:
                    for contact in self.contacts_cache:
                        if contact['name'] and contact['name'].lower() == contact_name.lower():
                            entity = contact['entity']
                            contact_info = contact['name']
                            break
                
                # 3. Частичное совпадение по имени (сбор кандидатов)
                if not entity:
                    for contact in self.contacts_cache:
                        if contact['name'] and contact_name.lower() in contact['name'].lower():
                            candidates.append(contact)
                    
                    # Если нашли несколько кандидатов, используем самого подходящего
                    if len(candidates) == 1:
                        entity = candidates[0]['entity']
                        contact_info = candidates[0]['name']
                    elif len(candidates) > 1:
                        # Ищем наиболее точное совпадение
                        best_match = None
                        best_score = 0
                        
                        for candidate in candidates:
                            score = self._calculate_match_score(contact_name.lower(), candidate['name'].lower())
                            if score > best_score:
                                best_score = score
                                best_match = candidate
                        
                        if best_match and best_score > 0.5:  # Порог совпадения
                            entity = best_match['entity']
                            contact_info = best_match['name']
                        else:
                            return False, f"Найдено несколько контактов: {', '.join([c['name'] for c in candidates[:3]])}"
            
            # 4. Поиск по ID
            if not entity and contact_name.isdigit():
                try:
                    entity = await self.client.get_entity(int(contact_name))
                    contact_info = f"ID {contact_name}"
                except:
                    pass
            
            # 5. Если не нашли, используем "me" (себя)
            if not entity:
                entity = await self.client.get_entity("me")
                contact_info = "себе"
                return False, f"Контакт '{contact_name}' не найден. Отправлено себе."
            
            # Отправляем сообщение
            await self.client.send_message(entity, message)
            return True, f"Сообщение отправлено {contact_info}"
            
        except Exception as e:
            return False, f"Ошибка отправки: {e}"
    
    def _calculate_match_score(self, search_term, contact_name):
        """Вычисляет оценку совпадения контакта"""
        if search_term == contact_name:
            return 1.0
        
        # Разбиваем на слова
        search_words = search_term.split()
        contact_words = contact_name.split()
        
        # Считаем совпадения слов
        matches = 0
        for s_word in search_words:
            for c_word in contact_words:
                if s_word in c_word or c_word in s_word:
                    matches += 1
                    break
        
        return matches / max(len(search_words), len(contact_words))
            
    def send_message(self, contact_name, message):
        """Синхронная обертка для отправки сообщения"""
        if not self.loop or not self.loop.is_running():
            return False, "Event loop не запущен"
            
        future = asyncio.run_coroutine_threadsafe(self._send_message_async(contact_name, message), self.loop)
        return future.result(timeout=30)

    async def _get_contacts_async(self):
        """Асинхронное получение списка контактов"""
        try:
            if not self.client or not self.client.is_connected():
                return []
            
            await self._update_contacts_cache()
            
            if not self.contacts_cache:
                return []
            
            contacts_list = []
            for contact in self.contacts_cache:
                if contact['name']:
                    contact_str = contact['name']
                    if contact['username']:
                        contact_str += f" ({contact['username']})"
                    contact_str += f" [ID: {contact['id']}]"
                    contacts_list.append(contact_str)
            
            return contacts_list
            
        except Exception as e:
            print(f"Ошибка получения контактов: {e}")
            return []
            
    def get_contacts(self):
        """Синхронная обертка для получения контактов"""
        if not self.loop or not self.loop.is_running():
            return []
            
        future = asyncio.run_coroutine_threadsafe(self._get_contacts_async(), self.loop)
        return future.result(timeout=30)

class UltraFastVoiceAssistant:
    def __init__(self):
        print("⚡ Инициализация голосового помощника ВЕТЕР...")
        
        # Основные настройки
        self.keyword = "ветер"
        self.is_listening = True
        self.current_process = None
        self.gui = None
        
        # Режимы работы
        self.work_mode = True  # True - рабочий режим, False - игровой режим
        self.continuous_mode = False
        self.continuous_mode_end_time = 0
        self.continuous_mode_duration = 25
        
        # Vosk распознавание
        self.model = None
        self.recognizer = None
        self.audio = None
        self.stream = None
        self.recognition_threshold = 0.5
        
        # Telegram настройки
        self.telegram_api_id = None
        self.telegram_api_hash = None
        self.telegram_phone = None
        self.telegram_client = None
        self.telegram_manager = TelegramManager(self)
        
        # Таймеры
        self.active_timers = []
        
        # Словари команд
        self._load_commands()
        
        # Запускаем инициализацию в фоне
        self._init_background()

    def _load_commands(self):
        """Загрузка всех команд"""
        # Быстрые команды
        self.quick_commands = {
            "привет": lambda: self.speak("Привет! Чем могу помочь?"),
            "время": lambda: self.speak(f"Сейчас {time.strftime('%H:%M')}"),
            "дата": lambda: self.speak(f"Сегодня {time.strftime('%d.%m.%Y')}"),
            "пока": lambda: self._exit_command(),
            "стоп": lambda: self.stop_speech(),
            "тест": lambda: self.speak("Тестирование голосового синтеза"),
            "телеграм": lambda: self.test_telegram_connection(),
            "покажи контакты": lambda: self.show_contacts_command(),
        }
        
        # Сайты
        self.websites = {
            "ютуб": "https://youtube.com",
            "youtube": "https://youtube.com",
            "гугл": "https://google.com", 
            "google": "https://google.com",
            "вк": "https://vk.com",
            "вконтакте": "https://vk.com",
            "яндекс": "https://yandex.ru",
            "yandex": "https://yandex.ru",
            "почта": "https://gmail.com",
            "gmail": "https://gmail.com",
            "github": "https://github.com",
            "гитхаб": "https://github.com",
            "новости": "https://news.google.com",
            "погода": "https://yandex.ru/pogoda",
        }
        
        # Приложения
        self.applications = {
            "блокнот": "notepad", 
            "калькулятор": "calc",
            "проводник": "explorer",
            "панель управления": "control",
            "диспетчер задач": "taskmgr",
            "командная строка": "cmd",
            "paint": "mspaint",
            "word": "winword",
            "excel": "excel",
        }

    def _init_background(self):
        """Фоновая инициализация компонентов"""
        def background_init():
            try:
                print("🔄 Фоновая инициализация компонентов...")
                
                # Инициализируем Vosk модель
                if lazy.vosk and lazy.pyaudio:
                    try:
                        # Проверяем наличие модели
                        model_path = "vosk-model-small-ru-0.22"
                        if not os.path.exists(model_path):
                            print("📥 Модель Vosk не найдена, скачиваем...")
                            self._download_vosk_model()
                        
                        self.model = Model(model_path)
                        self.recognizer = KaldiRecognizer(self.model, 16000)
                        self.audio = lazy.pyaudio.PyAudio()
                        
                        # Настраиваем аудиопоток
                        self.stream = self.audio.open(
                            format=lazy.pyaudio.paInt16,
                            channels=1,
                            rate=16000,
                            input=True,
                            frames_per_buffer=4000
                        )
                        self.stream.start_stream()
                        print("✅ Vosk распознавание инициализировано")
                        
                    except Exception as e:
                        print(f"❌ Ошибка инициализации Vosk: {e}")
                        self.model = None
                        self.recognizer = None
                
                if self.gui:
                    self.gui.add_log("✅ Все системы инициализированы")
                    
            except Exception as e:
                print(f"❌ Ошибка инициализации: {e}")
                if self.gui:
                    self.gui.add_log(f"❌ Ошибка инициализации: {e}")
        
        thread = threading.Thread(target=background_init, daemon=True)
        thread.start()

    def _download_vosk_model(self):
        """Скачивание модели Vosk"""
        try:
            import urllib.request
            import zipfile
            
            model_url = "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip"
            zip_path = "vosk-model-small-ru-0.22.zip"
            
            print("📥 Скачиваем модель Vosk...")
            urllib.request.urlretrieve(model_url, zip_path)
            
            print("📦 Распаковываем модель...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(".")
            
            os.remove(zip_path)
            print("✅ Модель Vosk успешно установлена")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки модели Vosk: {e}")

    def listen_for_speech(self):
        """Прослушивание речи с помощью Vosk"""
        if not self.recognizer or not self.stream:
            return None
            
        try:
            data = self.stream.read(4000, exception_on_overflow=False)
            
            if len(data) == 0:
                return None
                
            if self.recognizer.AcceptWaveform(data):
                result = self.recognizer.Result()
                text = json.loads(result)["text"]
                
                if text and len(text) > 0:
                    return text.lower()
            
            return None
            
        except Exception as e:
            return None

    def listen_for_keyword(self):
        """Прослушивание ключевого слова"""
        text = self.listen_for_speech()
        if text and self.keyword in text:
            return True
        return False

    def listen_for_command(self):
        """Прослушивание команды после ключевого слова"""
        if not self.recognizer or not self.stream:
            return None
            
        self.speak("Слушаю команду")
        start_time = time.time()
        command_text = ""
        
        # Слушаем 5 секунд для получения команды
        while time.time() - start_time < 5:
            text = self.listen_for_speech()
            if text:
                command_text += " " + text
                # Если получили значительную команду, возвращаем
                if len(command_text.strip().split()) >= 2:
                    return command_text.strip()
        
        return command_text.strip() if command_text else None

    def speak(self, text):
        """Произнести текст"""
        print(f"🗣️ Ассистент: {text}")
        
        if self.gui:
            self.gui.add_log(f"Ассистент: {text}")
        
        # Останавливаем предыдущую речь
        if self.current_process and self.current_process.poll() is None:
            try:
                self.current_process.terminate()
            except:
                pass
        
        # Используем системный TTS СКРЫТЫЙ
        try:
            if platform.system() == "Windows":
                self.current_process = subprocess.Popen([
                    'powershell', '-Command',
                    f'Add-Type -AssemblyName System.speech; '
                    f'$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; '
                    f'$speak.Speak("{text}")'
                ], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW)  # ← ЭТО ГЛАВНОЕ!
                
        except Exception as e:
            print(f"❌ Ошибка TTS: {e}")

    def stop_speech(self):
        """Остановить речь"""
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
        if self.gui:
            self.gui.add_log("🔇 Речь остановлена")

    # ИСПРАВЛЕННЫЕ ФУНКЦИИ ГРОМКОСТИ
    def change_volume(self, command):
        """Регулировка громкости - ПОЛНОСТЬЮ ПЕРЕПИСАННАЯ"""
        try:
            if platform.system() == "Windows":
                if "громче" in command:
                    # Способ 1: PowerShell с увеличенным количеством нажатий
                    for _ in range(10):  # Увеличиваем в 10 раз
                        subprocess.run([
                            'powershell', '-Command',
                            '(New-Object -ComObject WScript.Shell).SendKeys([char]175)'
                        ], capture_output=True, timeout=2)
                        time.sleep(0.1)  # Небольшая задержка между нажатиями
                    
                    self.speak("Громкость увеличена")
                    if self.gui:
                        self.gui.add_log("🔊 Громкость увеличена")
                        
                elif "тише" in command:
                    # Способ 1: PowerShell с увеличенным количеством нажатий
                    for _ in range(10):  # Увеличиваем в 10 раз
                        subprocess.run([
                            'powershell', '-Command',
                            '(New-Object -ComObject WScript.Shell).SendKeys([char]174)'
                        ], capture_output=True, timeout=2)
                        time.sleep(0.1)
                    
                    self.speak("Громкость уменьшена")
                    if self.gui:
                        self.gui.add_log("🔇 Громкость уменьшена")
                        
                elif "выключи звук" in command or "отключи звук" in command:
                    # Alt-код для отключения звука
                    subprocess.run([
                        'powershell', '-Command',
                        '(New-Object -ComObject WScript.Shell).SendKeys([char]173)'
                    ], capture_output=True)
                    self.speak("Звук выключен")
                    if self.gui:
                        self.gui.add_log("🔇 Звук выключен")
                        
                elif "включи звук" in command:
                    # Alt-код для включения звука (тот же код переключает)
                    subprocess.run([
                        'powershell', '-Command',
                        '(New-Object -ComObject WScript.Shell).SendKeys([char]173)'
                    ], capture_output=True)
                    self.speak("Звук включен")
                    if self.gui:
                        self.gui.add_log("🔊 Звук включен")
                        
        except Exception as e:
            self.speak("Не удалось изменить громкость")
            print(f"Ошибка управления громкостью: {e}")

    def close_active_window(self):
        """Закрыть активное окно"""
        try:
            if lazy.pyautogui:
                # Alt+F4 для закрытия активного окна
                lazy.pyautogui.hotkey('alt', 'f4')
                self.speak("Закрываю окно")
                if self.gui:
                    self.gui.add_log("❌ Закрыто активное окно")
            else:
                self.speak("Не удалось закрыть окно")
        except Exception as e:
            self.speak("Ошибка закрытия окна")
            print(f"Ошибка закрытия окна: {e}")

    def switch_windows(self):
        """Переключение между окнами"""
        try:
            if lazy.pyautogui:
                # Alt+Tab для переключения окон
                lazy.pyautogui.hotkey('alt', 'tab')
                self.speak("Переключаю окно")
                if self.gui:
                    self.gui.add_log("🔄 Переключено окно")
            else:
                self.speak("Не удалось переключить окно")
        except Exception as e:
            self.speak("Ошибка переключения окон")
            print(f"Ошибка переключения окон: {e}")

    # ИСПРАВЛЕННЫЕ ФУНКЦИИ ТАЙМЕРА
    def set_timer(self, duration_seconds, timer_name=""):
        """Установка таймера - ПОЛНОСТЬЮ ПЕРЕПИСАННАЯ"""
        try:
            # Создаем уникальный ID для таймера
            timer_id = f"timer_{len(self.active_timers)}_{time.time()}"
            
            def timer_thread():
                try:
                    print(f"⏰ Таймер {timer_id} запущен на {duration_seconds} секунд")
                    
                    # Ждем указанное время
                    time.sleep(duration_seconds)
                    
                    # Проверяем, что ассистент еще работает
                    if self.is_listening:
                        if timer_name:
                            message = f"Таймер '{timer_name}' завершился!"
                        else:
                            message = f"Таймер на {duration_seconds} секунд завершился!"
                        
                        print(f"⏰ {message}")
                        self.speak(message)
                        
                        if self.gui:
                            self.gui.add_log(f"⏰ {message}")
                    
                    # Удаляем таймер из активных
                    if timer_id in self.active_timers:
                        self.active_timers.remove(timer_id)
                        
                except Exception as e:
                    print(f"❌ Ошибка в таймере: {e}")
            
            # Добавляем таймер в список активных
            self.active_timers.append(timer_id)
            
            # Запускаем таймер в отдельном потоке
            timer = threading.Thread(target=timer_thread, daemon=True)
            timer.start()
            
            # Сообщаем пользователю
            if timer_name:
                response = f"Таймер '{timer_name}' установлен на {duration_seconds} секунд"
            else:
                response = f"Таймер установлен на {duration_seconds} секунд"
            
            self.speak(response)
            if self.gui:
                self.gui.add_log(f"⏰ {response}")
                
        except Exception as e:
            error_msg = "Ошибка установки таймера"
            self.speak(error_msg)
            print(f"❌ {error_msg}: {e}")

    def parse_timer_command(self, command):
        """Парсинг команды таймера - УЛУЧШЕННАЯ"""
        try:
            print(f"🔍 Парсим команду таймера: {command}")
            
            # Ищем все числа в команде
            numbers = re.findall(r'\d+', command)
            if not numbers:
                print("❌ Числа не найдены в команде")
                return None
                
            duration = int(numbers[0])
            print(f"🔍 Найдено число: {duration}")
            
            # Определяем единицы измерения
            if any(word in command for word in ["минут", "минуты", "минуту"]):
                duration *= 60
                print(f"🔍 Конвертировано в секунды: {duration}")
            elif any(word in command for word in ["час", "часа", "часов"]):
                duration *= 3600
                print(f"🔍 Конвертировано в секунды: {duration}")
            elif any(word in command for word in ["секунд", "секунды", "секунду"]):
                print(f"🔍 Оставлено в секундах: {duration}")
            
            # Извлекаем название таймера
            timer_name = ""
            
            # Паттерны для извлечения названия
            patterns = [
                r'таймер\s+(?:на\s+)?\d+\s*(?:\w+\s+)?(?:назови\s+)?(.+)',
                r'поставь\s+таймер\s+(?:на\s+)?\d+\s*(?:\w+\s+)?(?:назови\s+)?(.+)',
                r'назови\s+(.+)',
                r'именем\s+(.+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, command)
                if match:
                    timer_name = match.group(1).strip()
                    # Убираем лишние слова
                    timer_name = re.sub(r'(?:таймер|на|поставь|именем|назови)', '', timer_name).strip()
                    if timer_name:
                        print(f"🔍 Найдено название таймера: '{timer_name}'")
                        break
            
            return duration, timer_name
            
        except Exception as e:
            print(f"❌ Ошибка парсинга таймера: {e}")
            return None

    # Остальные функции без изменений
    def init_telegram(self):
        """Инициализация Telegram клиента"""
        try:
            success, message = self.telegram_manager.connect_telegram()
            
            if success:
                self.telegram_client = self.telegram_manager.client
                if self.telegram_client and self.telegram_client.is_connected():
                    if self.gui:
                        self.gui.add_telegram_log("✅ Успешно подключено к Telegram")
                    return True
                else:
                    if self.gui:
                        self.gui.add_telegram_log("⏳ Ожидаем код подтверждения...")
                    return True
            else:
                if self.gui:
                    self.gui.add_telegram_log(f"❌ {message}")
                return False
                
        except Exception as e:
            if "verification code" in str(e):
                if self.gui:
                    self.gui.add_telegram_log("⏳ Требуется код подтверждения")
                return True
            else:
                if self.gui:
                    self.gui.add_telegram_log(f"❌ Ошибка инициализации Telegram: {e}")
                return False

    def enter_telegram_code(self, code):
        """Ввод кода подтверждения Telegram"""
        try:
            if not self.telegram_client:
                if self.gui:
                    self.gui.add_telegram_log("❌ Telegram клиент не инициализирован")
                return False
            
            # Вводим код в event loop менеджера
            async def sign_in_async():
                await self.telegram_client.sign_in(code=code)
                return self.telegram_client.is_connected()
            
            if self.telegram_manager.loop and self.telegram_manager.loop.is_running():
                future = asyncio.run_coroutine_threadsafe(sign_in_async(), self.telegram_manager.loop)
                success = future.result(timeout=30)
                
                if success:
                    if self.gui:
                        self.gui.add_telegram_log("✅ Успешная авторизация в Telegram")
                    return True
                else:
                    if self.gui:
                        self.gui.add_telegram_log("❌ Неверный код подтверждения")
                    return False
            else:
                if self.gui:
                    self.gui.add_telegram_log("❌ Event loop не запущен")
                return False
                
        except Exception as e:
            if self.gui:
                self.gui.add_telegram_log(f"❌ Ошибка ввода кода: {e}")
            return False

    def send_telegram_message_sync(self, contact_name, message):
        """Синхронная отправка сообщения в Telegram"""
        try:
            success, result_message = self.telegram_manager.send_message(contact_name, message)
            
            if success:
                if self.gui:
                    self.gui.add_telegram_log(f"✅ {result_message}")
                return True
            else:
                if self.gui:
                    self.gui.add_telegram_log(f"❌ {result_message}")
                return False
            
        except Exception as e:
            if self.gui:
                self.gui.add_telegram_log(f"❌ Ошибка отправки сообщения: {e}")
            return False

    def get_telegram_contacts(self):
        """Получение списка контактов Telegram"""
        try:
            contacts = self.telegram_manager.get_contacts()
            return contacts
        except Exception as e:
            if self.gui:
                self.gui.add_telegram_log(f"❌ Ошибка получения контактов: {e}")
            return []

    def show_contacts_command(self):
        """Команда показа контактов"""
        if not self.telegram_client:
            self.speak("Telegram не подключен")
            return
            
        self.speak("Загружаю список контактов")
        contacts = self.get_telegram_contacts()
        
        if contacts:
            self.speak(f"Найдено {len(contacts)} контактов")
            if self.gui:
                contacts_text = "📋 Доступные контакты:\n\n"
                for contact in contacts[:10]:  # Показываем первые 10
                    contacts_text += f"• {contact}\n"
                if len(contacts) > 10:
                    contacts_text += f"\n... и еще {len(contacts) - 10} контактов"
                self.gui.add_telegram_log(contacts_text)
        else:
            self.speak("Не удалось загрузить контакты")

    def test_telegram_connection(self):
        """Тест подключения к Telegram"""
        if not self.telegram_client:
            self.speak("Telegram не настроен")
            return
        
        if self.telegram_client.is_connected():
            self.speak("Telegram подключен и работает")
            if self.gui:
                self.gui.add_log("Telegram: подключен")
        else:
            self.speak("Telegram не подключен")
            if self.gui:
                self.gui.add_log("Telegram: не подключен")

    def open_website(self, url, site_name=None):
        """Открыть сайт"""
        try:
            if site_name:
                self.speak(f"Открываю {site_name}")
            else:
                self.speak("Открываю сайт")
            webbrowser.open(url)
        except Exception as e:
            self.speak("Не удалось открыть сайт")

    def open_application(self, app_name):
        """Открыть приложение"""
        try:
            if app_name in self.applications:
                app_command = self.applications[app_name]
                self.speak(f"Открываю {app_name}")
                subprocess.Popen(app_command, shell=True)
            else:
                self.speak("Приложение не найдено")
        except Exception as e:
            self.speak("Ошибка открытия приложения")

    def switch_to_work_mode(self):
        """Переключение в рабочий режим"""
        if not self.work_mode:
            self.work_mode = True
            self.continuous_mode = True
            self.continuous_mode_end_time = time.time() + 3600
            self.speak("Включен рабочий режим")
            if self.gui:
                self.gui.add_log("🏢 РАБОЧИЙ РЕЖИМ АКТИВИРОВАН")

    def switch_to_game_mode(self):
        """Переключение в игровой режим"""
        if self.work_mode:
            self.work_mode = False
            self.continuous_mode = False
            self.speak("Включен игровой режим")
            if self.gui:
                self.gui.add_log("🎮 ИГРОВОЙ РЕЖИМ АКТИВИРОВАН")

    def take_screenshot(self):
        """Сделать скриншот"""
        try:
            if lazy.pyautogui:
                screenshot = lazy.pyautogui.screenshot()
                filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                screenshot.save(filename)
                self.speak("Скриншот сохранен")
                if self.gui:
                    self.gui.add_log(f"📸 Скриншот сохранен: {filename}")
            else:
                self.speak("Функция скриншота недоступна")
        except Exception as e:
            self.speak("Не удалось сделать скриншот")

    def process_command(self, command):
        """Обработка команды"""
        if not command:
            return False
            
        command_lower = command.lower()
        
        if self.gui:
            self.gui.add_log(f"🎯 Распознано: {command}")
        
        # Команды управления режимом
        mode_commands = {
            'рабочий режим': self.switch_to_work_mode,
            'игровой режим': self.switch_to_game_mode,
            'режим работы': self.switch_to_work_mode,
            'режим игры': self.switch_to_game_mode,
            'какой режим': lambda: self.speak(f"{'Рабочий' if self.work_mode else 'Игровой'} режим"),
            'покажи контакты': self.show_contacts_command,
        }
        
        for phrase, action in mode_commands.items():
            if phrase in command_lower:
                action()
                return True

        # Команды Telegram
        telegram_keywords = ["напиши", "отправь", "скажи", "сообщение"]
        if any(keyword in command_lower for keyword in telegram_keywords):
            clean_cmd = command_lower
            for keyword in telegram_keywords:
                clean_cmd = clean_cmd.replace(keyword, "")
            clean_cmd = clean_cmd.strip()
            
            # Ищем имя контакта и сообщение
            parts = clean_cmd.split(' ', 1)
            if len(parts) >= 2:
                contact_name = parts[0].strip()
                message = parts[1].strip()
                
                self.speak(f"Отправляю сообщение {contact_name}")
                
                if hasattr(self, 'telegram_client') and self.telegram_client:
                    success = self.send_telegram_message_sync(contact_name, message)
                    if success:
                        self.speak("Сообщение отправлено")
                    else:
                        self.speak("Ошибка отправки сообщения")
                else:
                    self.speak("Telegram не подключен")
            else:
                self.speak("Не понял кому и что отправить")
            return True

        # Быстрые команды
        for cmd, action in self.quick_commands.items():
            if cmd in command_lower:
                action()
                return True

        # Открытие сайтов
        if any(word in command_lower for word in ["открой", "запусти"]):
            for site_name, url in self.websites.items():
                if site_name in command_lower:
                    self.open_website(url, site_name)
                    return True
            
            # Открытие приложений
            for app_name in self.applications:
                if app_name in command_lower:
                    self.open_application(app_name)
                    return True
            
            self.speak("Не понял что открыть")
            return True

        # Поиск в интернете
        if "найди" in command_lower or "ищи" in command_lower:
            search_query = command_lower.replace("найди", "").replace("ищи", "").strip()
            if search_query:
                webbrowser.open(f"https://www.google.com/search?q={search_query}")
                self.speak(f"Ищу {search_query}")
            return True

        # Управление громкостью
        if any(word in command_lower for word in ["громче", "тише", "выключи звук", "включи звук"]):
            self.change_volume(command_lower)
            return True

        # Таймер
        if "таймер" in command_lower or "поставь таймер" in command_lower:
            timer_params = self.parse_timer_command(command_lower)
            if timer_params:
                duration, timer_name = timer_params
                self.set_timer(duration, timer_name)
            else:
                self.speak("Не понял параметры таймера")
            return True

        # Скриншот
        if "скриншот" in command_lower:
            self.take_screenshot()
            return True

        # Закрыть окно
        if "закрой окно" in command_lower:
            self.close_active_window()
            return True

        # Переключить окно
        if "переключи окно" in command_lower or "смени окно" in command_lower:
            self.switch_windows()
            return True

        self.speak("Я не понял команду")
        return False

    def _exit_command(self):
        """Команда выхода"""
        self.speak("До свидания!")
        self.is_listening = False
        return "exit"

    def run(self):
        """Основной цикл работы ассистента"""
        self.speak("Голосовой помощник ВЕТЕР запущен и готов к работе!")
        
        if self.gui:
            self.gui.add_log("✅ Ассистент запущен")
        
        try:
            while self.is_listening:
                try:
                    # Проверка таймаута режима слушания
                    if (self.continuous_mode and 
                        time.time() > self.continuous_mode_end_time):
                        self.continuous_mode = False
                        if not self.work_mode:
                            self.speak("Режим слушания завершён")
                            if self.gui:
                                self.gui.add_log("⏹️ Режим слушания завершён")
                    
                    # В рабочем режиме слушаем постоянно
                    if self.work_mode:
                        if self.recognizer and self.stream:
                            command = self.listen_for_speech()
                            if command:
                                self.process_command(command)
                    
                    # В игровом режиме слушаем только по ключевому слову
                    elif not self.work_mode:
                        if self.listen_for_keyword():
                            self.speak("Да, слушаю")
                            command = self.listen_for_command()
                            if command:
                                self.process_command(command)
                    
                    time.sleep(0.1)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    if "NoneType" not in str(e):  # Игнорируем ошибки таймаута
                        print(f"❌ Ошибка в цикле: {e}")
                    time.sleep(0.1)
                    
        finally:
            self.stop_speech()
            if hasattr(self, 'telegram_manager'):
                self.telegram_manager.stop_loop()
            if hasattr(self, 'telegram_client') and self.telegram_client:
                try:
                    self.telegram_client.disconnect()
                except:
                    pass
            if hasattr(self, 'stream') and self.stream:
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                except:
                    pass
            if hasattr(self, 'audio') and self.audio:
                try:
                    self.audio.terminate()
                except:
                    pass
            
            if self.gui:
                self.gui.add_log("👋 Ассистент завершил работу")

def main():
    """Основная функция запуска приложения"""
    print("Запуск голосового помощника с графическим интерфейсом")
    
    try:
        # Создаем главное окно
        root = tk.Tk()
        
        # Создаем ассистента
        assistant = UltraFastVoiceAssistant()
        
        # Создаем GUI
        gui = VoiceAssistantGUI(root, assistant)
        assistant.gui = gui
        
        # Запускаем ассистента в отдельном потоке
        assistant_thread = threading.Thread(target=assistant.run, daemon=True)
        assistant_thread.start()
        
        # Настраиваем обработку закрытия окна
        def on_closing():
            if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
                assistant.is_listening = False
                if hasattr(assistant, 'telegram_manager'):
                    assistant.telegram_manager.stop_loop()
                if hasattr(assistant, 'telegram_client') and assistant.telegram_client:
                    try:
                        assistant.telegram_client.disconnect()
                    except:
                        pass
                root.quit()
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        print("✅ Приложение успешно запущено!")
        print("🎤 Скажите 'ВЕТЕР' для активации голосового помощника")
        
        # Запускаем главный цикл GUI
        root.mainloop()
        
        print("👋 Приложение завершено")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        messagebox.showerror("Ошибка", f"Не удалось запустить приложение: {e}")

if __name__ == "__main__":
    main()