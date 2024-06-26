import vlc
import yt_dlp
import time

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

def play_urls(urls):
    # Inicializar VLC
    instance = vlc.Instance()
    player = instance.media_player_new()

    for url in urls:
        video_url = get_video_url(url)
        if video_url:
            media = instance.media_new(video_url)
            player.set_media(media)
            player.play()
            
            # Esperar a que el medio comience a reproducirse
            time.sleep(2)
            
            # Esperar hasta que la reproducción termine
            while player.is_playing():
                time.sleep(1)
            
            # Detener el reproductor después de cada URL
            player.stop()

if __name__ == "__main__":
    urls = []
    print("Introduce las URLs de los videos que quieres reproducir, una por una. Cuando hayas terminado, escribe 'fin':")
    while True:
        url = input("URL: ")
        if url.lower() == 'fin':
            break
        urls.append(url.strip())

    if urls:
        play_urls(urls)
    else:
        print("No se han proporcionado URLs para reproducir.")
