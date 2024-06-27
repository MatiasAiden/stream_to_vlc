import vlc
import yt_dlp
import time
import tkinter as tk
from tkinter import ttk, PhotoImage
import os

def get_video_url(url):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_url = info_dict.get("url", None)
        return video_url

current_dir = os.path.dirname(__file__)

icon_vlc = os.path.join(current_dir, "assets", "vlc_night.png")

class VideoPlayer:
    def __init__(self, root, urls):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.urls = urls
        self.current_index = 0
        self.is_paused = False
        self.is_fullscreen = False
        self.repeat = False
        
        # Crear estilo global para el modo oscuro
        self.create_dark_theme()
        
        # Crear estilo global para el modo azul
        self.create_blue_theme()


        # Crear UI con tkinter
        self.root = root
        self.root.title("Reproductor de video - VLC Night")
        root.geometry("800x700+290+10")
        
        try:
            image_icon = PhotoImage(file=icon_vlc)
            root.iconphoto(False, image_icon)
        except tk.TclError as e:
            print(f"Error loading icon: {e}")
        
        self.frame = ttk.Frame(self.root, style='Dark.TFrame')
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.frame, bg='black')  # Establecer fondo negro directamente
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.player.set_hwnd(self.canvas.winfo_id())
        
        #fondo del reproductor
        
        self.controls_frame = ttk.Frame(self.root, style='Dark.TFrame')
        self.controls_frame.pack(fill=tk.X)
        
        self.play_button = ttk.Button(self.controls_frame, text="Play", command=self.play_pause, style='Dark.TButton')
        self.play_button.pack(side=tk.LEFT)
        
        self.stop_button = ttk.Button(self.controls_frame, text="Stop", command=self.stop, style='Dark.TButton')
        self.stop_button.pack(side=tk.LEFT)
        
        self.backward_button = ttk.Button(self.controls_frame, text="<<", command=self.backward, style='Dark.TButton')
        self.backward_button.pack(side=tk.LEFT)
        
        self.forward_button = ttk.Button(self.controls_frame, text=">>", command=self.forward, style='Dark.TButton')
        self.forward_button.pack(side=tk.LEFT)
        
        self.speed_label = ttk.Label(self.controls_frame, text="Speed:", style='Dark.TLabel')
        self.speed_label.pack(side=tk.LEFT)
        
        self.speed_var = tk.StringVar(value="1.0")
        self.speed_combo = ttk.Combobox(self.controls_frame, textvariable=self.speed_var, values=["0.25", "0.5", "1.0", "1.25", "1.5", "2.0"], state="readonly", width=3, style='Dark.TCombobox')
        self.speed_combo.pack(side=tk.LEFT)
        self.speed_combo.bind("<<ComboboxSelected>>", self.set_speed)
        
        self.time_label = ttk.Label(self.controls_frame, text="00:00 / 00:00", style='Dark.TLabel')
        self.time_label.pack(side=tk.LEFT)
        
        self.progress_frame = ttk.Frame(self.controls_frame, style='Dark.TFrame')
        self.progress_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.progress = ttk.Scale(self.progress_frame, from_=0, to=1000, orient=tk.HORIZONTAL, style='Dark.Horizontal.TScale')
        self.progress.pack(fill=tk.X, expand=True)
        self.progress.bind("<ButtonRelease-1>", self.set_position)
        
        self.progress_frame = ttk.Frame(self.controls_frame, style='Dark.TFrame')
        self.progress_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,3))
        
        self.volume_var = tk.DoubleVar(value=100)
        self.volume_scale = ttk.Scale(self.controls_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.volume_var, command=self.set_volume, style='Dark.Horizontal.TScale')
        self.volume_scale.pack(side=tk.LEFT)
        
        self.volume_label = ttk.Label(self.controls_frame, text="Volume: 100%", style='Dark.TLabel')
        self.volume_label.pack(side=tk.LEFT)
        
        self.fullscreen_button = ttk.Button(self.controls_frame, text="Fullscreen", command=self.toggle_fullscreen, style='Dark.TButton')
        self.fullscreen_button.pack(side=tk.LEFT)

        self.repeat_button = ttk.Button(self.controls_frame, text="Repeat Off", command=self.toggle_repeat, style='Dark.TButton')
        self.repeat_button.pack(side=tk.LEFT)
        
        self.add_button = ttk.Button(self.controls_frame, text="Add Video", command=self.add_video, style='Dark.TButton')
        self.add_button.pack(side=tk.LEFT)

        self.root.bind("<space>", lambda event: self.play_pause())
        self.root.bind("<Left>", lambda event: self.backward())
        self.root.bind("<Right>", lambda event: self.forward())
        self.root.bind("<period>", lambda event: self.increase_speed())
        self.root.bind("<comma>", lambda event: self.decrease_speed())
        self.root.bind("<Escape>", lambda event: self.exit_fullscreen())  # Permitir salir de pantalla completa con 'Escape'
        self.canvas.bind("<Double-1>", lambda event: self.toggle_fullscreen())
        
        self.canvas.bind("<Motion>", self.show_controls)
        self.controls_visible = True
        self.controls_frame.bind("<Motion>", self.show_controls)
        
        self.update_time()
        self.play_video()


#    def create_blue_theme(self):
#        """Crea un tema azul personalizado utilizando ttk.Style()."""
#        style = ttk.Style()
#        style.configure("BW.TLabel", foreground="blue", background="#0077FF")
    def create_dark_theme(self):
        """Crea un tema oscuro personalizado utilizando ttk.Style()."""
        style = ttk.Style()

        # Establecer colores para el modo oscuro
        dark_bg = "#333333"
        dark_fg = "white"
        light_bg = "#555555"
        light_fg = "black"

        # Configurar el estilo para diferentes componentes
        style.configure('Dark.TFrame', background=dark_bg)
        style.configure('Dark.TButton', background=dark_bg, foreground=dark_fg, borderwidth=0)
        style.map('Dark.TButton', background=[('active', 'blue')])
        style.configure('Dark.TLabel', background=dark_bg, foreground=dark_fg)
        style.configure('Dark.TCombobox', background=dark_bg, foreground=dark_fg)
        style.map('Dark.TCombobox', background=[('active', light_bg)])
        style.configure('Dark.Horizontal.TScale', background=dark_bg, troughcolor=light_bg)
        style.map('Dark.Horizontal.TScale', background=[('active', light_bg)])

    def play_video(self):
        if self.current_index < len(self.urls):
            video_url = get_video_url(self.urls[self.current_index])
            if video_url:
                media = self.instance.media_new(video_url)
                self.player.set_media(media)
                self.player.play()
                self.root.after(1000, self.check_end)
    
    def check_end(self):
        if not self.player.is_playing():
            if self.repeat:
                self.play_video()
            else:
                self.current_index += 1
                if self.current_index < len(self.urls):
                    self.play_video()
        else:
            self.root.after(1000, self.check_end)

    def play_pause(self):
        if self.player.is_playing():
            self.player.pause()
            self.play_button.config(text="Resume")
            self.is_paused = True
        else:
            self.player.play()
            self.play_button.config(text="Pause")
            self.is_paused = False
            
    def stop(self):
        self.player.stop()
        self.play_button.config(text="Play")
        
    def backward(self):
        time = self.player.get_time()
        self.player.set_time(max(0, time - 10000))  # Retroceder 10 segundos
        
    def forward(self):
        time = self.player.get_time()
        self.player.set_time(min(self.player.get_length(), time + 10000))  # Adelantar 10 segundos
        
    def set_speed(self, event):
        speed = float(self.speed_var.get())
        self.player.set_rate(speed)
        
    def set_volume(self, val):
        volume = int(self.volume_var.get())
        self.player.audio_set_volume(volume)
        self.volume_label.config(text=f"Volume: {volume}%")
        
    def increase_speed(self):
        current_speed = float(self.speed_var.get())
        speeds = [0.25, 0.5, 1.0, 1.25, 1.5, 2.0]
        if current_speed < 2.0:
            new_speed = speeds[speeds.index(current_speed) + 1]
            self.speed_var.set(str(new_speed))
            self.player.set_rate(new_speed)
        
    def decrease_speed(self):
        current_speed = float(self.speed_var.get())
        speeds = [0.25, 0.5, 1.0, 1.25, 1.5, 2.0]
        if current_speed > 0.25:
            new_speed = speeds[speeds.index(current_speed) - 1]
            self.speed_var.set(str(new_speed))
            self.player.set_rate(new_speed)
            
    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.player.set_fullscreen(self.is_fullscreen)
        self.show_controls()
        
    def exit_fullscreen(self):
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.player.set_fullscreen(False)
        
    def show_controls(self, event=None):
        if self.is_fullscreen:
            self.controls_frame.pack_forget() if self.controls_visible else self.controls_frame.pack(fill=tk.X)
            self.controls_visible = not self.controls_visible

    def toggle_repeat(self):
        self.repeat = not self.repeat
        self.repeat_button.config(text="Repeat On" if self.repeat else "Repeat Off")
    
    def add_video(self):
        url = input("URL: ")
        if url:
            self.urls.append(url.strip())
    
    def update_time(self):
        if self.player.is_playing():
            total_time = self.player.get_length() // 1000
            current_time = self.player.get_time() // 1000
            self.time_label.config(text=f"{current_time // 60:02}:{current_time % 60:02} / {total_time // 60:02}:{total_time % 60:02}")
            self.progress.config(to=total_time, value=current_time)
        self.root.after(1000, self.update_time)
    
    def set_position(self, event):
        total_time = self.player.get_length() // 1000
        new_time = int(self.progress.get() * 1000)
        self.player.set_time(new_time)

if __name__ == "__main__":
    urls = []
    print("Introduce las URLs de los videos que quieres reproducir, una por una. Cuando hayas terminado, escribe 'fin':")
    while True:
        url = input("URL: ")
        if url.lower() == 'fin':
            break
        urls.append(url.strip())

    if urls:
        root = tk.Tk()
        player = VideoPlayer(root, urls)
        root.mainloop()
    else:
        print("No se han proporcionado URLs para reproducir.")
