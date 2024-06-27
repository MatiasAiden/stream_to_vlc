import vlc
import yt_dlp
import time
import tkinter as tk
from tkinter import ttk

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

class VideoPlayer:
    def __init__(self, root, urls):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.urls = urls
        self.current_index = 0
        self.is_paused = False
        self.is_fullscreen = False
        
        # Crear una interfaz de usuario con tkinter
        self.root = root
        self.root.title("Video Player")
        
        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.frame)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.player.set_hwnd(self.canvas.winfo_id())
        
        self.controls_frame = ttk.Frame(self.root)
        self.controls_frame.pack(fill=tk.X)
        
        self.play_button = ttk.Button(self.controls_frame, text="Play", command=self.play_pause)
        self.play_button.pack(side=tk.LEFT)
        
        self.stop_button = ttk.Button(self.controls_frame, text="Stop", command=self.stop)
        self.stop_button.pack(side=tk.LEFT)
        
        self.backward_button = ttk.Button(self.controls_frame, text="<<", command=self.backward)
        self.backward_button.pack(side=tk.LEFT)
        
        self.forward_button = ttk.Button(self.controls_frame, text=">>", command=self.forward)
        self.forward_button.pack(side=tk.LEFT)
        
        self.speed_label = ttk.Label(self.controls_frame, text="Speed:")
        self.speed_label.pack(side=tk.LEFT)
        
        self.speed_var = tk.StringVar(value="1.0")
        self.speed_combo = ttk.Combobox(self.controls_frame, textvariable=self.speed_var, values=["0.25", "0.5", "1.0", "1.25", "1.5", "2.0"], state="readonly")
        self.speed_combo.pack(side=tk.LEFT)
        self.speed_combo.bind("<<ComboboxSelected>>", self.set_speed)
        
        self.volume_var = tk.DoubleVar(value=100)
        self.volume_scale = ttk.Scale(self.controls_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.volume_var, command=self.set_volume)
        self.volume_scale.pack(side=tk.LEFT)
        
        self.volume_label = ttk.Label(self.controls_frame, text="Volume: 100%")
        self.volume_label.pack(side=tk.LEFT)
        
        self.fullscreen_button = ttk.Button(self.controls_frame, text="Fullscreen", command=self.toggle_fullscreen)
        self.fullscreen_button.pack(side=tk.LEFT)
        
        self.root.bind("<space>", lambda event: self.play_pause())
        self.root.bind("<Left>", lambda event: self.backward())
        self.root.bind("<Right>", lambda event: self.forward())
        self.root.bind("<period>", lambda event: self.increase_speed())
        self.root.bind("<comma>", lambda event: self.decrease_speed())
        self.canvas.bind("<Double-1>", lambda event: self.toggle_fullscreen())
        
        self.canvas.bind("<Motion>", self.show_controls)
        self.controls_visible = True
        self.controls_frame.bind("<Motion>", self.show_controls)
        
        self.play_video()

    def play_video(self):
        if self.current_index < len(self.urls):
            video_url = get_video_url(self.urls[self.current_index])
            if video_url:
                media = self.instance.media_new(video_url)
                self.player.set_media(media)
                self.player.play()
                self.root.after(1000, self.check_end)

    def check_end(self):
        if not self.player.is_playing() and self.current_index < len(self.urls):
            self.current_index += 1
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
        
    def show_controls(self, event=None):
        if self.is_fullscreen:
            self.controls_frame.pack_forget() if self.controls_visible else self.controls_frame.pack(fill=tk.X)
            self.controls_visible = not self.controls_visible

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
