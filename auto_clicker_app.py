import json
import random
import time
from tkinter import Tk, Label, Button, Entry, StringVar, BooleanVar, Checkbutton, Toplevel, Frame
from tkinter import ttk
from tkinter.ttk import Notebook, OptionMenu, Progressbar
from ttkbootstrap import Style
import pygame
import pyautogui
import keyboard
from tkinter import messagebox 

pygame.mixer.init()

class AutoClickerApp:
    def __init__(self, root):

        self.root = root
        self.style = Style(theme='cyborg')
        root.title("Auto Clicker")
        root.geometry("600x450")

        self.avg_delay = 0.0
        self.stop_thread = None
        self.stats_text = StringVar()
        self.stats_text.set("Session Stats:")
        self.auto_clicking = False
        self.initial_clicks = 0
        self.control_frame = ttk.Frame(self.root)
        self.control_frame.pack(side="bottom", fill="x")

        self.start_button = ttk.Button(self.control_frame, text="Start", command=self.start_clicking)
        self.start_button.pack(side="left", padx=10, pady=5)
        self.style.configure('TButton', background='green')

        self.stop_button = ttk.Button(self.control_frame, text="Stop", command=self.stop_clicking)
        self.stop_button.pack(side="right", padx=10, pady=5)
        self.style.configure('TButton', background='red')

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=1, fill="both", pady=20)

        self.settings_frame = ttk.Frame(self.notebook)
        self.advanced_settings_frame = ttk.Frame(self.notebook)

        self.sound_shortcuts_frame = ttk.Frame(self.notebook)

        self.style.configure('TFrame', background='gray9')
        self.session_profile_frame = ttk.Frame(self.notebook)

        # add noteboook tabs
        self.notebook.add(self.settings_frame, text='Settings')
        self.notebook.add(self.advanced_settings_frame, text='Advanced Settings')
        self.notebook.add(self.sound_shortcuts_frame, text='Sound & Shortcuts')
        self.notebook.add(self.session_profile_frame, text='Session & Profile')

        self.key_bindings = {
        'start_clicking': 'F6',
        'stop_clicking': 'F7',
        'set_location': 'F8',
        'clear_location': 'F9'
    }
        self.setup_settings_tab()
        self.setup_advanced_settings_tab()
        self.setup_sound_shortcuts_tab()
        self.setup_session_profile_tab()
        self.apply_key_bindings()
        self.setup_randomized_clicking()
        self.initialize_session_stats()
        self.initialize_session_stats()

    def setup_settings_tab(self):
        self.label = Label(self.settings_frame, text="Auto Clicker", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.duration_label = Label(self.settings_frame, text="Duration (seconds):")
        self.duration_label.pack(pady=5)

        self.duration_entry = Entry(self.settings_frame)
        self.duration_entry.pack(pady=5)
        self.progress = Progressbar(self.settings_frame, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=20)

        if hasattr(self, 'default_duration'):
            self.duration_entry.insert(0, self.default_duration)
        else:
            self.duration_entry.insert(0, "0")

        self.delay_label = Label(self.settings_frame, text="Delay (seconds):")
        self.delay_label.pack(pady=5)

        self.delay_entry = Entry(self.settings_frame)
        self.delay_entry.pack(pady=5)

        if hasattr(self, 'default_delay'):
            self.delay_entry.insert(0, self.default_delay)
        else:
            self.delay_entry.insert(0, "0")

    def setup_advanced_settings_tab(self):
        self.click_type_var = StringVar(self.root)
        self.click_type_var.set("left")

        self.click_type_label = Label(self.advanced_settings_frame, text="Click Type:")
        self.click_type_label.pack(pady=5)

        self.click_type_menu = OptionMenu(self.advanced_settings_frame, self.click_type_var, "Left", "Left", "Right", "Middle", "Double")
        self.click_type_menu.pack(pady=5)

    def setup_sound_shortcuts_tab(self):
        self.sound_notif_var = BooleanVar()
        self.sound_notif_check = Checkbutton(self.sound_shortcuts_frame, text="Enable Sound Notifications", variable=self.sound_notif_var)
        self.sound_notif_check.pack(pady=5)

        self.customize_button = Button(self.sound_shortcuts_frame, text="Customize Shortcuts", command=self.customize_shortcuts_ui)
        self.customize_button.pack(pady=5)

    def setup_session_profile_tab(self):
        self.stats_label = Label(self.session_profile_frame, textvariable=self.stats_text)
        self.stats_label.pack(pady=5)

        self.profile_label = Label(self.session_profile_frame, text="Profile Name:")
        self.profile_label.pack(pady=5)

        self.profile_entry = Entry(self.session_profile_frame)
        self.profile_entry.pack(pady=5)

        self.export_button = Button(self.session_profile_frame, text="Export Profile", command=self.export_profile)
        self.export_button.pack(pady=5)

        self.import_button = Button(self.session_profile_frame, text="Import Profile", command=self.import_profile)
        self.import_button.pack(pady=5)

    def customize_shortcuts_ui(self):
        self.customize_window = Toplevel(self.root)
        self.customize_window.title('Customize Shortcuts')

        self.start_key_var = StringVar()
        self.start_key_var.set(self.key_bindings['start_clicking'])

        self.stop_key_var = StringVar()
        self.stop_key_var.set(self.key_bindings['stop_clicking'])

        Label(self.customize_window, text="Start Clicking:").grid(row=0, column=0)
        Entry(self.customize_window, textvariable=self.start_key_var).grid(row=0, column=1)

        Label(self.customize_window, text="Stop Clicking:").grid(row=1, column=0)
        Entry(self.customize_window, textvariable=self.stop_key_var).grid(row=1, column=1)

        Button(self.customize_window, text="Apply", command=self.update_key_bindings).grid(row=2, column=1)

    def update_key_bindings(self):
        self.key_bindings['start_clicking'] = self.start_key_var.get()
        self.key_bindings['stop_clicking'] = self.stop_key_var.get()
        self.apply_key_bindings()

    def apply_key_bindings(self):
        keyboard.add_hotkey(self.key_bindings['start_clicking'], self.start_clicking)
        keyboard.add_hotkey(self.key_bindings['stop_clicking'], self.stop_clicking)
        keyboard.add_hotkey(self.key_bindings['set_location'], self.set_click_location)
        keyboard.add_hotkey(self.key_bindings['clear_location'], self.clear_click_location)


    def start_clicking(self):
        try:
            self.duration = float(self.duration_entry.get())
            if self.duration < 0:
                raise ValueError('Duration cannot be negative.')
            self.delay = float(self.delay_entry.get())
            if self.delay < 0:
                raise ValueError('Delay cannot be negative.')

            self.initial_clicks = int(self.duration / self.delay)
            self.auto_clicking = True
            self.clicks_remaining = int(self.duration / self.delay)
            self.progress["maximum"] = self.duration  # Set the maximum value for the progress bar
            self.root.after(int(self.delay * 1000), self.perform_click)

            if self.sound_notif_var.get():
                pygame.mixer.Sound('start_clicking_sound.wav').play()

        except ValueError as e:
            messagebox.showerror('Error', str(e))

    def perform_click(self):
        if self.auto_clicking and self.clicks_remaining > 0:
            pyautogui.click(button=self.click_type_var.get())
            self.clicks_remaining -= 1
            elapsed_time = self.duration - (self.clicks_remaining * self.delay)
            self.progress["value"] = elapsed_time
            self.root.after(int(float(self.delay_entry.get()) * 1000), self.perform_click)

    def stop_clicking(self):
        print("Stop button pressed.")  # Debugging line
        self.auto_clicking = False
        if self.sound_notif_var.get():
            pygame.mixer.Sound('stop_clicking_sound.wav').play()
        self.update_session_stats(self.duration, self.delay)

    def auto_click_stop(self):
        self.execution_time = time.time() - self.start_time
        self.update_session_stats(self.execution_time, self.delay)
        if self.sound_notif_var.get():
            pygame.mixer.Sound('stop_clicking_sound.wav').play()

    def auto_click(self, duration, delay):
        time.sleep(5)
        end_time = time.time() + duration
        self.progress["maximum"] = duration  # Set the maximum value for the progress bar

        print(f"Debug: self.duration = {self.duration}, self.delay = {self.delay}") # Debugging line

        while self.auto_clicking and time.time() < end_time:
            print(f"Debug: self.auto_clicking = {self.auto_clicking}, time.time() = {time.time()}, end_time = {end_time}") # Debugging line

            if not self.auto_clicking:
                print("Exiting click_thread early.")
                break

            if self.click_location:
                pyautogui.click(x=self.click_location[0], y=self.click_location[1], button=self.click_type_var.get())
            else:
                pyautogui.click(button=self.click_type_var.get())
                actual_delay = random.uniform(delay * 0.8, delay * 1.3) if self.random_clicking_var.get() else delay

                if self.click_location:
                    pyautogui.click(x=self.click_location[0], y=self.click_location[1], button=self.click_type_var.get())
                else:
                    pyautogui.click(button=self.click_type_var.get())

            elapsed_time = time.time() - (end_time - duration)  # Calculate elapsed time
            self.root.after(0, self.progress.config, {"value": elapsed_time})

            total_sleep_time = 0
            sleep_increment = 0.1
            while total_sleep_time < actual_delay:
                time.sleep(sleep_increment)
                total_sleep_time += sleep_increment
                if not self.auto_clicking:
                    print("Exiting click_thread early.")
                    break

        # if auto-clicking was not stopped manually, update session stats
        if self.auto_clicking:
            self.update_session_stats(duration, delay)
            self.auto_clicking = False
            print("Auto-clicker stopped automatically.")

    def save_settings(self):
        settings = {
            'duration': self.duration_entry.get(),
            'delay': self.delay_entry.get(),
            'click_type': self.click_type_var.get()
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
            self.duration_entry.delete(0, 'end')
            self.duration_entry.insert(0, settings['duration'])

            self.delay_entry.delete(0, 'end')
            self.delay_entry.insert(0, settings['delay'])

            self.click_type_var.set(settings['click_type'])
        except FileNotFoundError:
            print("Settings file not found. Using default settings.")

    def set_click_location(self):
        print("Move your mouse to the desired click location and press F3.")

        def capture_location(e):
            x, y = pyautogui.position()
            self.click_location = (x, y)
            print(f"Click location set to {self.click_location}.")

        keyboard.on_press_key('f3', capture_location, suppress=True)

    def clear_click_location(self):
        self.click_location = None
        print("Click location cleared.")


    def initialize_session_stats(self):
        self.total_clicks = 0
        self.avg_delay = 0.0
        self.last_session_duration = 0.0
        self.click_location = None
        self.session_logs = []
        self.stats_text.set("Session Stats: Total Clicks: 0, Last Session: 0s, Avg Delay: 0.0s")

    def update_session_stats(self, duration, delay):
        actual_clicks = int(duration / delay)
        actual_duration = actual_clicks * delay

        if delay > 0:
            self.total_clicks += actual_clicks
            self.last_session_duration = actual_duration
            self.avg_delay = (self.avg_delay + delay) / 2

            stats_text = f"Total Clicks: {self.total_clicks}, Last Session: {self.last_session_duration}s, Avg Delay: {self.avg_delay:.2f}s"
            self.stats_text.set(stats_text)

    def validate_profile_name(self, profile_name):
        if not profile_name:
            print("Please enter a profile name.")
            return False
        return True
    def read_json_file(self, file_name):
        try:
            with open(f"{file_name}.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"File '{file_name}' not found.")
            return None

    def write_json_file(self, file_name, data):
        with open(f"{file_name}.json", 'w') as f:
            json.dump(data, f)

    def update_ui_from_profile(self, profile):
        self.duration_entry.delete(0, 'end')
        self.duration_entry.insert(0, profile.get('duration', ''))
        self.delay_entry.delete(0, 'end')
        self.delay_entry.insert(0, profile.get('delay', ''))
        self.click_type_var.set(profile.get('click_type', 'left'))

    def export_profile(self):
        profile_name = self.profile_entry.get()
        if not self.validate_profile_name(profile_name):
            return
        profile = {
            "duration": self.duration_entry.get(),
            "delay": self.delay_entry.get(),
            "click_type": self.click_type_var.get()
        }
        self.write_json_file(profile_name, profile)

    def import_profile(self):
        profile_name = self.profile_entry.get()
        if not self.validate_profile_name(profile_name):
            return
        profile = self.read_json_file(profile_name)
        if profile:
            self.update_ui_from_profile(profile)

    def setup_randomized_clicking(self):
        self.random_clicking_var = BooleanVar()
        self.random_clicking_check = Checkbutton(self.root, text="Enable Randomized Clicking", variable=self.random_clicking_var)
        self.random_clicking_check.pack()

if __name__ == "__main__":
    style = Style(theme='cyborg')
    root = style.master
    app = AutoClickerApp(root)
    root.mainloop()