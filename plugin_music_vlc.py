# Плагин управления музыкой через VLC player
# author: Danil Chaparov
# необходимо установить: pip install python-vlc

import os
import vlc
from pathlib import Path
from vacore import VACore

modname = os.path.basename(__file__)[:-3] # calculating modname

class MusicPlayer:
    def __init__(self, music_folder: str = "music"):
        self.music_folder = Path(music_folder)
        self.instance = vlc.Instance('--no-xlib --quiet')
        self.player = self.instance.media_player_new()
        self.playlist: list = []
        self.current_track_index: int = -1
        self.is_playing: bool = False
        self.volume: int = 50
        self.player.audio_set_volume(self.volume)
        
        # Создаем папку для музыки если её нет
        self.music_folder.mkdir(exist_ok=True)
        
        self._load_playlist()
    
    def _load_playlist(self):
        """Загружает список музыкальных файлов из папки"""
        supported_formats = {'.mp3', '.wav', '.ogg', '.flac', '.m4a', '.wma'}
        self.playlist = []
        
        if self.music_folder.exists() and self.music_folder.is_dir():
            for file in self.music_folder.iterdir():
                if file.suffix.lower() in supported_formats and file.is_file():
                    self.playlist.append(str(file.absolute()))
        
        print(f"Загружено {len(self.playlist)} треков в плейлист")
    
    def play(self, track_index: int = None) -> bool:
        """Воспроизведение трека"""
        if not self.playlist:
            return False
        
        if track_index is None:
            if self.current_track_index == -1:
                track_index = 0
            else:
                track_index = self.current_track_index
        else:
            if track_index < 0 or track_index >= len(self.playlist):
                #print(f"Неверный индекс трека: {track_index}")
                return False
        
        try:
            media = self.instance.media_new(self.playlist[track_index])
            self.player.set_media(media)
            self.player.play()
            self.current_track_index = track_index
            self.is_playing = True
            
            #print(f"Воспроизведение: {Path(self.playlist[track_index]).name}")
            return True
        except Exception as e:
            #print(f"Ошибка воспроизведения: {e}")
            return False
    
    def pause(self) -> bool:
        """Пауза/возобновление воспроизведения"""
        if self.player.get_media():
            self.player.pause()
            self.is_playing = not self.is_playing
            #print("Пауза" if not self.is_playing else "Возобновление")
            return True
        return False
    
    def stop(self) -> bool:
        """Остановка воспроизведения"""
        if self.player.get_media():
            self.player.stop()
            self.is_playing = False
            #print("Воспроизведение остановлено")
            return True
        return False
    
    def next_track(self) -> bool:
        """Следующий трек"""
        if not self.playlist:
            return False
        
        next_index = (self.current_track_index + 1) % len(self.playlist)
        self.stop()
        return self.play(next_index)
    
    def previous_track(self) -> bool:
        """Предыдущий трек"""
        if not self.playlist:
            return False
        
        prev_index = (self.current_track_index - 1) % len(self.playlist)
        self.stop()
        return self.play(prev_index)
    
    def set_volume(self, volume: int) -> bool:
        """Установка громкости (0-100)"""
        if 0 <= volume <= 100:
            self.volume = volume
            self.player.audio_set_volume(volume)
            #print(f"Громкость установлена на {volume}%")
            return True
        return False
    
    def volume_up(self, step: int = 10) -> bool:
        """Увеличить громкость"""
        new_volume = min(100, self.volume + step)
        return self.set_volume(new_volume)
    
    def volume_down(self, step: int = 10) -> bool:
        """Уменьшить громкость"""
        new_volume = max(0, self.volume - step)
        return self.set_volume(new_volume)
    
    def get_current_track(self) -> str:
        """Получить название текущего трека"""
        if self.current_track_index >= 0 and self.current_track_index < len(self.playlist):
            return Path(self.playlist[self.current_track_index]).name
        return ""

# функция на старте
def start(core: VACore):
    manifest = {
        "name": "Музыкальный плеер VLC",
        "version": "1.0",
        "require_online": False,
        "description": "Управление локальной музыкой через VLC player. "
                       "Воспроизведение, пауза, переключение треков, регулировка громкости.",
        "url": "https://github.com/protos17/irene-plugins/plugin_music_vlc",

        "options_label": {
            "music_folder": "Папка с музыкой (относительно папки программы)",
            "default_volume": "Громкость по умолчанию (0-100)"
        },

        "default_options": {
            "music_folder": "music",
            "default_volume": "50"
        },

        "commands": {
            "включи музыку|запусти музыку|включи плеер": start_music,
            "пауза|останови музыку|стоп музыка|выключи музыку|выключи": pause_music,
            "следующий трек|next track|next|вперед": next_track,
            "предыдущий трек|previous track|previous|назад": previous_track,
            "громче|увеличь громкость|volume up": volume_up,
            "тише|уменьши громкость|volume down": volume_down,
            "статус музыки|что играет": music_status,
        }
    }
    return manifest

def start_with_options(core: VACore, manifest: dict):
    pass

def init_music_player(core: VACore):
    """Инициализация музыкального плеера"""
    options = core.plugin_options(modname)
    
    if not hasattr(core, 'music_player'):
        music_folder = options["music_folder"]
        core.music_player = MusicPlayer(music_folder)
        
        # Устанавливаем громкость по умолчанию
        try:
            default_volume = int(options["default_volume"])
            core.music_player.set_volume(default_volume)
        except ValueError:
            core.music_player.set_volume(50)
        
        #print("Музыкальный плеер инициализирован")

def start_music(core: VACore, phrase: str):
    """Запуск музыки"""
    init_music_player(core)
    
    success = core.music_player.play()
    if success:
        track_name = core.music_player.get_current_track()
        core.play_voice_assistant_speech(f"Включаю {track_name}")
    else:
        core.play_voice_assistant_speech("Не удалось воспроизвести музыку. Проверьте папку с музыкой.")

def pause_music(core: VACore, phrase: str):
    """Пауза/возобновление музыки"""
    if not hasattr(core, 'music_player'):
        core.play_voice_assistant_speech("Музыкальный плеер не инициализирован")
        return
    
    success = core.music_player.pause()
    if success:
        status = "паузу" if not core.music_player.is_playing else "воспроизведение"
        core.play_voice_assistant_speech(f"Ставлю на {status}")

def next_track(core: VACore, phrase: str):
    """Следующий трек"""
    if not hasattr(core, 'music_player'):
        core.play_voice_assistant_speech("Музыкальный плеер не инициализирован")
        return
    
    success = core.music_player.next_track()
    if success:
        track_name = core.music_player.get_current_track()
        core.play_voice_assistant_speech(f"Следующий трек: {track_name}")
    else:
        core.play_voice_assistant_speech("Не удалось переключить трек")

def previous_track(core: VACore, phrase: str):
    """Предыдущий трек"""
    if not hasattr(core, 'music_player'):
        core.play_voice_assistant_speech("Музыкальный плеер не инициализирован")
        return
    
    success = core.music_player.previous_track()
    if success:
        track_name = core.music_player.get_current_track()
        core.play_voice_assistant_speech(f"Предыдущий трек: {track_name}")
    else:
        core.play_voice_assistant_speech("Не удалось переключить трек")

def volume_up(core: VACore, phrase: str):
    """Увеличение громкости"""
    if not hasattr(core, 'music_player'):
        core.play_voice_assistant_speech("Музыкальный плеер не инициализирован")
        return
    
    success = core.music_player.volume_up()
    if success:
        core.play_voice_assistant_speech(f"Громкость увеличена до {core.music_player.volume}%")

def volume_down(core: VACore, phrase: str):
    """Уменьшение громкости"""
    if not hasattr(core, 'music_player'):
        core.play_voice_assistant_speech("Музыкальный плеер не инициализирован")
        return
    
    success = core.music_player.volume_down()
    if success:
        core.play_voice_assistant_speech(f"Громкость уменьшена до {core.music_player.volume}%")

def music_status(core: VACore, phrase: str):
    """Статус воспроизведения"""
    if not hasattr(core, 'music_player'):
        core.play_voice_assistant_speech("Музыкальный плеер не инициализирован")
        return
    
    if core.music_player.is_playing:
        track_name = core.music_player.get_current_track()
        core.play_voice_assistant_speech(f"Сейчас играет: {track_name}, громкость: {core.music_player.volume}%")
    else:
        core.play_voice_assistant_speech("Музыка не играет")