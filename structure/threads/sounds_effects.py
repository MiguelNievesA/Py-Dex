from PyQt5.QtCore import QThread, pyqtSignal
import pyaudio
import wave
import numpy as np


#####################################
#    Clase de Pista de sonido       #
#####################################

from PyQt5.QtCore import QThread, pyqtSignal
import pyaudio
import wave
import time
import numpy as np

class SoundTrack(QThread):
    finished = pyqtSignal(bool)
    def __init__(self, file_path:str, loop=False):
        super().__init__()

        self.file_path = file_path
        self.is_playing = False
        self.is_fading_out = False
        self.chunk_size = 1024
        self.stream = None
        self.loop = loop

    def run(self):
        if self.is_playing:
            return

        self.is_playing = True
        p = pyaudio.PyAudio()

        try:
            wave_file = wave.open(self.file_path, "rb")
            self.stream = p.open(
                format=p.get_format_from_width(wave_file.getsampwidth()),
                channels=wave_file.getnchannels(),
                rate=wave_file.getframerate(),
                output=True
            )

            while self.is_playing:
                wave_file.rewind()
                data = wave_file.readframes(self.chunk_size)

                while data and self.is_playing:
                    if self.is_fading_out:
                        num_samples = len(data) // wave_file.getsampwidth()
                        fade_factor = np.linspace(1.0, 0.0, num=num_samples, endpoint=False)
                        audio_data = np.frombuffer(data, dtype=np.int16).copy()  # Crear una copia mutable

                        if len(fade_factor) > 0:
                            audio_data[:len(fade_factor)] = (audio_data[:len(fade_factor)] * fade_factor).astype(np.int16)

                        data = audio_data.tobytes()

                    self.stream.write(data)
                    data = wave_file.readframes(self.chunk_size)

                if not self.loop:
                    break

        finally:
            self.stream.stop_stream()
            self.stream.close()
            p.terminate()
            wave_file.close()

            self.finished.emit(True)

        self.is_playing = False

    def stop_sountrack(self):

        if not self.is_playing:
            return
        
        self.is_playing = False

        self.wait()  # Esperar a que el hilo termine

