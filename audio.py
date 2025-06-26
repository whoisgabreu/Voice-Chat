# audio.py
import pyaudio
import threading
import time

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()
send_audio_enabled = True
push_to_talk_mode = False

def toggle_audio(enabled: bool):
    global send_audio_enabled
    send_audio_enabled = enabled

def set_push_to_talk(enabled: bool):
    global push_to_talk_mode
    push_to_talk_mode = enabled

def start_audio_stream(sock, username):
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    def send_audio():
        while True:
            try:
                if send_audio_enabled or push_to_talk_mode:
                    data = stream.read(CHUNK)
                    packet = f"[AUDIO:{username}]".encode() + data
                    sock.sendall(packet)
                else:
                    time.sleep(0.05)
            except:
                break
    threading.Thread(target=send_audio, daemon=True).start()

def receive_audio_stream(sock, on_speaker_change=None):
    stream_out = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    def receive():
        while True:
            try:
                data = sock.recv(CHUNK + 100)
                if data.startswith(b'[AUDIO:'):
                    sep = data.find(b']')
                    header = data[7:sep].decode()
                    payload = data[sep+1:]
                    stream_out.write(payload)
                    if on_speaker_change:
                        on_speaker_change(header)
            except:
                break
    threading.Thread(target=receive, daemon=True).start()
