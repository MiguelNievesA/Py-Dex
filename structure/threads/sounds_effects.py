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

    def __init__(self, file_path:str, loop=False):
        super().__init__()

        self.file_path = file_path
        self.paused = False
        self.current_frame = 0
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
                wave_file.setpos(self.current_frame)
                data = wave_file.readframes(self.chunk_size)

                while data and self.is_playing:

                    if self.paused:
                        time.sleep(0.05)
                        continue

                    self.stream.write(data)
                    self.current_frame = wave_file.tell()
                    data = wave_file.readframes(self.chunk_size)

                if not self.loop:
                    break

        finally:
            self.stream.stop_stream()
            self.stream.close()
            p.terminate()
            wave_file.close()

        self.is_playing = False

    def stop_sountrack(self):

        if not self.is_playing:
            return
        
        self.is_playing = False
        self.paused = False
        self.current_frame = 0
        self.wait()

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False
