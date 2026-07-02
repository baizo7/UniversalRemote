import customtkinter as ctk
import threading
import time
import queue
from adb import *
import config

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class RemoteApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Universal Android Remote V2.2")
        self.geometry("400x760")
        self.resizable(False, False)
        
        # Connection Manager Thread
        self.is_running = True
        threading.Thread(target=self.connection_manager, daemon=True).start()
        
        # Live Keyboard Queue Worker
        self.type_queue = queue.Queue()
        threading.Thread(target=self.live_typing_worker, daemon=True).start()
        
        self.build_ui()
        self.bind_keys()
        
    def build_ui(self):
        # 1. Header Frame
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(10, 5), fill="x", padx=10)
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="Universal Remote", font=("Segoe UI", 24, "bold"))
        self.title_label.pack()
        
        # Device Dropdown
        self.device_var = ctk.StringVar(value=config.ACTIVE_DEVICE)
        self.device_dropdown = ctk.CTkOptionMenu(
            self.header_frame, 
            variable=self.device_var, 
            values=list(config.DEVICES.keys()), 
            command=self.change_device
        )
        self.device_dropdown.pack(pady=5)
        
        self.status_label = ctk.CTkLabel(self.header_frame, text="Connecting...", text_color="orange", font=("Segoe UI", 14))
        self.status_label.pack()

        # 2. App Launcher (Favorites)
        self.apps_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.apps_frame.pack(pady=5)
        
        ctk.CTkButton(self.apps_frame, text="YouTube", width=80, fg_color="#FF0000", hover_color="#CC0000",
                      command=lambda: launch_app(["com.google.android.youtube.tv", "com.google.android.youtube"])).grid(row=0, column=0, padx=5)
        ctk.CTkButton(self.apps_frame, text="Netflix", width=80, fg_color="#E50914", hover_color="#B81D24",
                      command=lambda: launch_app(["com.netflix.ninja", "com.netflix.mediaclient"])).grid(row=0, column=1, padx=5)
        ctk.CTkButton(self.apps_frame, text="Prime", width=80, fg_color="#00A8E1", hover_color="#0079A3",
                      command=lambda: launch_app(["com.amazon.amazonvideo.livingroom", "com.amazon.avod.thirdpartyclient"])).grid(row=0, column=2, padx=5)

        # 3. Animated D-Pad
        self.dpad_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#2A2D34")
        self.dpad_frame.pack(pady=5, padx=20, ipadx=10, ipady=10)
        
        self.btn_up = ctk.CTkButton(self.dpad_frame, text="▲", width=50, height=50, corner_radius=25,
                                    command=lambda: key(KEYS["UP"]))
        self.btn_up.grid(row=0, column=1, pady=5)
        
        self.btn_left = ctk.CTkButton(self.dpad_frame, text="◀", width=50, height=50, corner_radius=25,
                                      command=lambda: key(KEYS["LEFT"]))
        self.btn_left.grid(row=1, column=0, padx=5)
        
        self.btn_ok = ctk.CTkButton(self.dpad_frame, text="OK", width=60, height=60, corner_radius=30,
                                    fg_color="#3A3D44", hover_color="#4A4D54", font=("Segoe UI", 14, "bold"),
                                    command=lambda: key(KEYS["OK"]))
        self.btn_ok.grid(row=1, column=1)
        
        self.btn_right = ctk.CTkButton(self.dpad_frame, text="▶", width=50, height=50, corner_radius=25,
                                       command=lambda: key(KEYS["RIGHT"]))
        self.btn_right.grid(row=1, column=2, padx=5)
        
        self.btn_down = ctk.CTkButton(self.dpad_frame, text="▼", width=50, height=50, corner_radius=25,
                                      command=lambda: key(KEYS["DOWN"]))
        self.btn_down.grid(row=2, column=1, pady=5)

        # 4. Basic Controls
        self.basic_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.basic_frame.pack(pady=5)
        
        ctk.CTkButton(self.basic_frame, text="🔙 Back", width=90, command=lambda: key(KEYS["BACK"])).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(self.basic_frame, text="🏠 Home", width=90, command=lambda: key(KEYS["HOME"])).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(self.basic_frame, text="🔍 Search", width=90, command=lambda: key(KEYS["SEARCH"])).grid(row=1, column=0, padx=5, pady=5)
        ctk.CTkButton(self.basic_frame, text="⚙ Settings", width=90, command=self.open_settings).grid(row=1, column=1, padx=5, pady=5)

        # 5. Media & Volume Controls
        self.media_frame = ctk.CTkFrame(self, fg_color="#2A2D34", corner_radius=15)
        self.media_frame.pack(pady=5, padx=20, fill="x")
        
        self.vol_frame = ctk.CTkFrame(self.media_frame, fg_color="transparent")
        self.vol_frame.pack(pady=10)
        ctk.CTkButton(self.vol_frame, text="🔉 -", width=60, command=lambda: key(KEYS["VOL_DOWN"])).grid(row=0, column=0, padx=10)
        ctk.CTkButton(self.vol_frame, text="🔇 Mute", width=80, fg_color="#555", hover_color="#777", command=lambda: key(KEYS["MUTE"])).grid(row=0, column=1, padx=10)
        ctk.CTkButton(self.vol_frame, text="🔊 +", width=60, command=lambda: key(KEYS["VOL_UP"])).grid(row=0, column=2, padx=10)
        
        self.play_frame = ctk.CTkFrame(self.media_frame, fg_color="transparent")
        self.play_frame.pack(pady=(0, 10))
        ctk.CTkButton(self.play_frame, text="⏮", width=60, command=lambda: key(KEYS["PREVIOUS"])).grid(row=0, column=0, padx=10)
        ctk.CTkButton(self.play_frame, text="⏯ Play/Pause", width=120, fg_color="#1DB954", hover_color="#1ED760", command=lambda: key(KEYS["PLAY_PAUSE"])).grid(row=0, column=1, padx=10)
        ctk.CTkButton(self.play_frame, text="⏭", width=60, command=lambda: key(KEYS["NEXT"])).grid(row=0, column=2, padx=10)

        # 6. Keyboard Input
        self.kbd_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.kbd_frame.pack(pady=5, padx=20, fill="x")
        
        self.live_kbd_var = ctk.BooleanVar(value=False)
        self.live_kbd_switch = ctk.CTkSwitch(self.kbd_frame, text="Live Keybd", variable=self.live_kbd_var, font=("Segoe UI", 12))
        self.live_kbd_switch.pack(side="left", padx=(0,5))
        
        self.entry = ctk.CTkEntry(self.kbd_frame, placeholder_text="Type and press Enter...", width=130)
        self.entry.pack(side="left", expand=True, fill="x", padx=(0,5))
        self.entry.bind("<Return>", self.send_text)
        
        self.send_btn = ctk.CTkButton(self.kbd_frame, text="Send", width=40, command=self.send_text)
        self.send_btn.pack(side="right")

        # 7. Mouse / Trackpad mode
        self.trackpad = ctk.CTkFrame(self, height=70, corner_radius=10, fg_color="#1E2024")
        self.trackpad.pack(pady=5, padx=20, fill="x")
        self.trackpad.pack_propagate(False)
        
        tp_label = ctk.CTkLabel(self.trackpad, text="Mouse Mode (Swipe to Navigate)", text_color="#777")
        tp_label.place(relx=0.5, rely=0.5, anchor="center")
        
        self.trackpad.bind("<ButtonPress-1>", self.tp_press)
        self.trackpad.bind("<B1-Motion>", self.tp_drag)
        tp_label.bind("<ButtonPress-1>", self.tp_press)
        tp_label.bind("<B1-Motion>", self.tp_drag)
        
        self.tp_start_x = 0
        self.tp_start_y = 0
        self.tp_threshold = 40 # px threshold for swipe
        
    def tp_press(self, e):
        self.tp_start_x = e.x
        self.tp_start_y = e.y
        
    def tp_drag(self, e):
        dx = e.x - self.tp_start_x
        dy = e.y - self.tp_start_y
        
        if abs(dx) > self.tp_threshold:
            if dx > 0:
                key(KEYS["RIGHT"])
            else:
                key(KEYS["LEFT"])
            self.tp_start_x = e.x 
            self.tp_start_y = e.y
            
        elif abs(dy) > self.tp_threshold:
            if dy > 0:
                key(KEYS["DOWN"])
            else:
                key(KEYS["UP"])
            self.tp_start_x = e.x
            self.tp_start_y = e.y

    def bind_keys(self):
        self.bind("<Up>", lambda e: key(KEYS["UP"]))
        self.bind("<Down>", lambda e: key(KEYS["DOWN"]))
        self.bind("<Left>", lambda e: key(KEYS["LEFT"]))
        self.bind("<Right>", lambda e: key(KEYS["RIGHT"]))
        self.bind("<Escape>", lambda e: key(KEYS["BACK"]))
        
        # Handle Enter and Backspace differently if typing in the entry box
        def on_enter(e):
            if self.focus_get() != self.entry:
                if self.live_kbd_var.get():
                    self.type_queue.put(lambda: key(66)) # 66 is Enter for ADB text fields
                else:
                    key(KEYS["OK"])
                
        def on_backspace(e):
            if self.focus_get() != self.entry:
                if self.live_kbd_var.get():
                    self.type_queue.put(lambda: key(KEYS["DEL"]))
                else:
                    key(KEYS["BACK"])
                    
        def on_keypress(e):
            if self.live_kbd_var.get() and self.focus_get() != self.entry:
                if e.char and e.char.isprintable():
                    c = e.char
                    self.type_queue.put(lambda c=c: input_text(c))
                
        self.bind("<Return>", on_enter)
        self.bind("<BackSpace>", on_backspace)
        self.bind("<KeyPress>", on_keypress)

    def change_device(self, new_device_name):
        config.save_settings(config.DEVICES, new_device_name)
        disconnect()

    def open_settings(self):
        settings_win = ctk.CTkToplevel(self)
        settings_win.title("Add Device")
        settings_win.geometry("320x220")
        settings_win.attributes("-topmost", True)
        
        ctk.CTkLabel(settings_win, text="Add New Device", font=("Segoe UI", 16, "bold")).pack(pady=(20, 5))
        
        name_entry = ctk.CTkEntry(settings_win, width=220, placeholder_text="Name (e.g. Living Room TV)")
        name_entry.pack(pady=5)
        
        ip_entry = ctk.CTkEntry(settings_win, width=220, placeholder_text="IP:PORT (e.g. 192.168.1.10:5555)")
        ip_entry.pack(pady=5)
        
        def save():
            name = name_entry.get().strip()
            ip = ip_entry.get().strip()
            if name and ip:
                devices = config.DEVICES
                devices[name] = ip
                config.save_settings(devices, name)
                
                # Update dropdown menu dynamically
                self.device_dropdown.configure(values=list(config.DEVICES.keys()))
                self.device_var.set(name)
                
                disconnect() # reconnects to new
            settings_win.destroy()
            
        ctk.CTkButton(settings_win, text="Save & Connect", command=save, width=140).pack(pady=15)

    def send_text(self, event=None):
        txt = self.entry.get()
        if txt:
            input_text(txt)
            self.entry.delete(0, 'end')

    def live_typing_worker(self):
        while self.is_running:
            try:
                task = self.type_queue.get(timeout=1.0)
                task()
            except queue.Empty:
                pass

    def connection_manager(self):
        connect()
        while self.is_running:
            if is_connected():
                try:
                    self.status_label.configure(text=f"🟢 Connected to {config.ACTIVE_DEVICE}", text_color="lightgreen")
                except:
                    pass
            else:
                try:
                    self.status_label.configure(text=f"🔴 Disconnected from {config.ACTIVE_DEVICE}", text_color="red")
                except:
                    pass
                connect()
            time.sleep(4)
            
    def destroy(self):
        self.is_running = False
        super().destroy()

if __name__ == "__main__":
    app = RemoteApp()
    app.mainloop()