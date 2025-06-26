import socket
import threading
import pyaudio
import numpy as np
import os


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

SERVER_IP = '192.168.4.44'  # ou IP do servidor na rede local
SERVER_PORT = 5005

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK)

def receive_audio(sock):
    while True:
        try:
            data = sock.recv(CHUNK)
            stream.write(data)
        except:
            break

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))

    threading.Thread(target=receive_audio, args=(sock,), daemon=True).start()

    print("[*] Enviando e recebendo áudio...")
    try:
        while True:

            data = stream.read(CHUNK)
            # audio_np = np.frombuffer(data, dtype=np.int16)
            # volume = int(np.linalg.norm(audio_np) / len(audio_np) * 10)
            # bar = "#" * volume
            # print(f"[🎤] Volume: {bar}", end="\r")
            # os.system("cls")
            # data = stream.read(CHUNK)
            sock.sendall(data)
    except KeyboardInterrupt:
        print("Saindo...")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
