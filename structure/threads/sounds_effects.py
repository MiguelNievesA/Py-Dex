from PyQt5.QtCore import QThread, pyqtSignal
import pyaudio
import wave
import time
import numpy as np

# ==================================================
# SoundTrack Thread Class
# ==================================================

class SoundTrack(QThread):
    """
    Audio playback thread for WAV files using PyAudio.
    """

    def __init__(self, file_path: str, loop=False, volume: int = 50):
        super().__init__()

        # Convert volume from percentage (0–100) to float (0.0–1.0)
        self.volume = volume / 100.0

        # Audio file path
        self.file_path = file_path

        # Playback state flags
        self.paused = False
        self.is_playing = False
        self.is_fading_out = False  # Reserved for future fade-out logic

        # Audio playback position (frame index)
        self.current_frame = 0

        # Audio stream configuration
        self.chunk_size = 1024  # Number of frames read per iteration
        self.stream = None

        # Loop control
        self.loop = loop


    # ==================================================
    # Thread Execution Logic
    # ==================================================

    def run(self):

        # Prevent multiple concurrent playbacks
        if self.is_playing:
            return

        self.is_playing = True
        p = pyaudio.PyAudio()

        try:
            # Open WAV file in read-binary mode
            wave_file = wave.open(self.file_path, "rb")

            # Create PyAudio output stream using WAV metadata
            self.stream = p.open(
                format=p.get_format_from_width(wave_file.getsampwidth()),
                channels=wave_file.getnchannels(),
                rate=wave_file.getframerate(),
                output=True
            )

            # Main playback loop
            while self.is_playing:

                # Resume playback from last stored frame
                wave_file.setpos(self.current_frame)
                data = wave_file.readframes(self.chunk_size)

                # Read and play chunks until file ends or playback stops
                while data and self.is_playing:

                    # Pause handling (non-blocking)
                    if self.paused:
                        time.sleep(0.05)
                        continue

                    # Convert raw bytes to NumPy array for processing
                    audio_data = np.frombuffer(data, dtype=np.int16)

                    # Apply volume scaling
                    audio_data = (audio_data * self.volume).astype(np.int16)

                    # Convert processed audio back to bytes
                    data = audio_data.tobytes()

                    # Write audio data to output stream
                    self.stream.write(data)

                    # Update current playback position
                    self.current_frame = wave_file.tell()

                    # Read next chunk
                    data = wave_file.readframes(self.chunk_size)

                # Exit loop if looping is disabled
                if not self.loop:
                    break

        finally:
            # Ensure proper cleanup of audio resources
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()

            p.terminate()
            wave_file.close()

        self.is_playing = False


    # ==================================================
    # Playback Control Methods
    # ==================================================

    def stop_sountrack(self):

        if not self.is_playing:
            return

        self.is_playing = False
        self.paused = False
        self.current_frame = 0

        # Wait until the thread finishes execution
        self.wait()


    def pause(self):
        self.paused = True


    def resume(self):
        self.paused = False


    def set_volume(self, volume: int):

        # Clamp value to valid range and normalize
        self.volume = max(0.0, min(volume / 100.0, 1.0))
