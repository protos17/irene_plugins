# Плагин управления музыкой через VLC player
# author: protos17
# необходимо установить: pip install python-vlc

import os
import vlc
import random
from pathlib import Path
from vacore import VACore

modname = os.path.basename(__file__)[:-3]

class MusicPlayer:
    def __init__(self, music_folder: str = "../Music"):
        # Получаем абсолютный путь к папке с музыкой
        base_dir = Path(os.getcwd())
        self.music_folder = (base_dir / music_folder).resolve()
        
        self.instance = vlc.Instance('--no-xlib --quiet')
        self.player = self.instance.media_player_new()
        self.playlist: list = []
        self.current_track_index: int = -1
        self.is_playing: bool = False
        self.volume: int = 50
        self.is_shuffled: bool = False
        self.player.audio_set_volume(self.volume)
        
        # Создаем папку для музыки если её нет
        self.music_folder.mkdir(exist_ok=True, parents=True)
        
        self._load_playlist()
    
    def _load_playlist(self):
        """Загружает список музыкальных файлов из папки"""
        supported_formats = {'.mp3', '.wav', '.ogg', '.flac', '.m4a', '.wma'}
        self.playlist = []
        
        if self.music_folder.exists() and self.music_folder.is_dir():
            for file in self.music_folder.iterdir():
                if file.suffix.lower() in supported_formats and file.is_file():
                    self.playlist.append(str(file.absolute()))
    
    def latin_to_cyrillic(self, text: str) -> str:
        """Преобразует латинские символы в кириллические для озвучивания"""
        # Таблица преобразования латиницы в кириллицу
        conversion_table = {
            'a': 'а', 'b': 'б', 'c': 'к', 'd': 'д', 'e': 'е', 'f': 'ф', 'g': 'г',
            'h': 'х', 'i': 'и', 'j': 'дж', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н',
            'o': 'о', 'p': 'п', 'q': 'к', 'r': 'р', 's': 'с', 't': 'т', 'u': 'у',
            'v': 'в', 'w': 'в', 'x': 'кс', 'y': 'и', 'z': 'з',
            'A': 'А', 'B': 'Б', 'C': 'К', 'D': 'Д', 'E': 'Е', 'F': 'Ф', 'G': 'Г',
            'H': 'Х', 'I': 'И', 'J': 'Дж', 'K': 'К', 'L': 'Л', 'M': 'М', 'N': 'Н',
            'O': 'О', 'P': 'П', 'Q': 'К', 'R': 'Р', 'S': 'С', 'T': 'Т', 'U': 'У',
            'V': 'В', 'W': 'В', 'X': 'Кс', 'Y': 'И', 'Z': 'З'
        }
        
        result = []
        i = 0
        while i < len(text):
            # Проверяем комбинации из двух символов
            if i + 1 < len(text):
                two_chars = text[i:i+2].lower()
                if two_chars == 'sh':
                    result.append('ш')
                    i += 2
                    continue
                elif two_chars == 'ch':
                    result.append('ч')
                    i += 2
                    continue
                elif two_chars == 'zh':
                    result.append('ж')
                    i += 2
                    continue
                elif two_chars == 'th':
                    result.append('т')
                    i += 2
                    continue
                elif two_chars == 'ph':
                    result.append('ф')
                    i += 2
                    continue
            
            # Обрабатываем одиночные символы
            char = text[i]
            if char in conversion_table:
                result.append(conversion_table[char])
            else:
                result.append(char)
            i += 1
        
        return ''.join(result)
    
    def get_readable_track_name(self, filename: str) -> str:
        """Получает читаемое название трека для озвучивания"""
        # Убираем расширение файла
        name = Path(filename).stem
        
        # Заменяем подчеркивания и дефисы на пробелы
        name = name.replace('_', ' ').replace('-', ' ')
        
        # Убираем специальные символы
        for char in ['[', ']', '(', ')', '{', '}', '<', '>', '@', '#', '$', '%', '^', '&', '*', '+', '=']:
            name = name.replace(char, ' ')
        
        # Преобразуем латинские символы в кириллицу
        name = self.latin_to_cyrillic(name)
        
        # Убираем множественные пробелы
        name = ' '.join(name.split())
        
        return name
    
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
                return False
        
        try:
            self.stop()
            media = self.instance.media_new(self.playlist[track_index])
            self.player.set_media(media)
            self.player.play()
            self.current_track_index = track_index
            self.is_playing = True
            
            track_name = Path(self.playlist[track_index]).name
            readable_name = self.get_readable_track_name(track_name)
            print(f"Воспроизведение: {track_name} -> {readable_name}")
            return True
        except Exception as e:
            print(f"Ошибка воспроизведения: {e}")
            return False
    
    def pause(self) -> bool:
        """Пауза/возобновление воспроизведения"""
        if self.player.get_media():
            self.player.pause()
            self.is_playing = not self.is_playing
            return True
        return False
    
    def stop(self) -> bool:
        """Остановка воспроизведения"""
        if self.player.get_media():
            self.player.stop()
            self.is_playing = False
            return True
        return False
    
    def shuffle_playlist(self):
        """Перемешивает плейлист"""
        random.shuffle(self.playlist)
        self.is_shuffled = True
        self.play(0)
    
    def unshuffle_playlist(self):
        """Возвращает оригинальный порядок плейлиста"""
        self._load_playlist()
        self.is_shuffled = False
        self.play(0)
    
    def next_track(self) -> bool:
        """Следующий трек"""
        if not self.playlist:
            return False
        
        next_index = (self.current_track_index + 1) % len(self.playlist)
        return self.play(next_index)
    
    def previous_track(self) -> bool:
        """Предыдущий трек"""
        if not self.playlist:
            return False
        
        prev_index = (self.current_track_index - 1) % len(self.playlist)
        return self.play(prev_index)
    
    def set_volume(self, volume: int) -> bool:
        """Установка громкости (0-100)"""
        if 0 <= volume <= 100:
            self.volume = volume
            self.player.audio_set_volume(volume)
            print(f"Громкость установлена на {volume}%")
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
    
    def get_readable_current_track(self) -> str:
        """Получить читаемое название текущего трека"""
        track_name = self.get_current_track()
        if track_name:
            return self.get_readable_track_name(track_name)
        return ""

# функция на старте
def start(core: VACore):
    manifest = {
        "name": "Музыкальный плеер VLC",
        "version": "1.3",
        "require_online": False,
        "description": "Управление локальной музыкой через VLC player. "
                       "Воспроизведение, пауза, переключение треков, регулировка громкости, перемешивание.",
        "options_label": {
            "music_folder": "Папка с музыкой (относительно папки программы, например: ../Music)",
            "default_volume": "Громкость по умолчанию (0-100)"
        },

        "default_options": {
            "music_folder": "../Music",
            "default_volume": "50"
        },

        "commands": {
            "включи музыку|запусти музыку|музыка|музыку": start_music,
            "пауза": pause_music,
            "стоп|стоп музыка|останови музыку": stop_music,
            "следующий трек|дальше": next_track,
            "предыдущий трек|назад": previous_track,
            "громче|увеличь громкость|погромче": volume_up,
            "тише|уменьши громкость|потише": volume_down,
            "статус музыки|что играет|кто поет": music_status,
            "перемешай|перемешать|случайный порядок": shuffle_music,
            "обычный порядок|верни порядок": unshuffle_music,
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
        
def start_music(core: VACore, phrase: str):
    """Запуск музыки"""
    init_music_player(core)
    
    success = core.music_player.play()
    if success:
        track_name = core.music_player.get_readable_current_track()
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

def stop_music(core: VACore, phrase: str):
    """Остановка музыки"""
    if not hasattr(core, 'music_player'):
        core.play_voice_assistant_speech("Музыкальный плеер не инициализирован")
        return
    
    success = core.music_player.stop()
    if success:
        status = "стоп"
        core.play_voice_assistant_speech(f"Ставлю на {status}")

def next_track(core: VACore, phrase: str):
    """Следующий трек"""
    if not hasattr(core, 'music_player'):
        core.play_voice_assistant_speech("Музыкальный плеер не инициализирован")
        return
    
    success = core.music_player.next_track()
    if success:
        track_name = core.music_player.get_readable_current_track()
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
        track_name = core.music_player.get_readable_current_track()
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
        track_name = core.music_player.get_readable_current_track()
        mode = "перемешанном" if core.music_player.is_shuffled else "обычном"
        core.play_voice_assistant_speech(f"Сейчас играет: {track_name}, громкость: {core.music_player.volume}%, режим: {mode}")
    else:
        core.play_voice_assistant_speech("Музыка не играет")

def shuffle_music(core: VACore, phrase: str):
    """Перемешивание плейлиста"""
    if not hasattr(core, 'music_player'):
        core.play_voice_assistant_speech("Музыкальный плеер не инициализирован")
        return
    
    success = core.music_player.shuffle_playlist()
    if success:
        core.play_voice_assistant_speech("Плейлист перемешан. Включаю первый трек.")
        core.music_player.play(0)  # Запускаем первый трек в перемешанном плейлисте
    else:
        core.play_voice_assistant_speech("Не удалось перемешать плейлист")

def unshuffle_music(core: VACore, phrase: str):
    """Возврат к обычному порядку"""
    if not hasattr(core, 'music_player'):
        core.play_voice_assistant_speech("Музыкальный плеер не инициализирован")
        return
    
    success = core.music_player.unshuffle_playlist()
    if success:
        core.play_voice_assistant_speech("Порядок плейлиста восстановлен")
    else:
        core.play_voice_assistant_speech("Не удалось восстановить порядок плейлиста")