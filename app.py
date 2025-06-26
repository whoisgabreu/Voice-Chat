# app.py
import socket
import flet as ft
import threading
import time
from audio import start_audio_stream, receive_audio_stream, toggle_audio, set_push_to_talk

SERVER_IP = "192.168.4.44"
PORT = 5000

def main(page: ft.Page):
    page.title = "Chat de Voz e Texto"
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    username = ft.TextField(label="Seu nome", autofocus=True)
    chat_display = ft.Text()
    msg_input = ft.TextField(label="Mensagem", expand=True)
    send_btn = ft.ElevatedButton("Enviar")
    speaker_label = ft.Text("🔊 Ninguém está falando...", size=12, italic=True, color="grey")
    mode_toggle = ft.Dropdown(
        label="Modo de Fala",
        options=[
            ft.dropdown.Option("Push-to-Talk"),
            ft.dropdown.Option("Alternar Mudo/Desmutado"),
        ],
        value="Alternar Mudo/Desmutado",
    )

    mic_btn = ft.ElevatedButton("🎙️", width=80, height=40)

    # Estado
    sock = socket.socket()
    push_to_talk = False
    muted = False

    def update_mic_icon():
        if push_to_talk:
            mic_btn.text = "🎙️"
        else:
            mic_btn.text = "🔇" if muted else "🎙️"
        page.update()

    def toggle_mic(e=None):
        nonlocal muted
        if push_to_talk:
            return  # Não alterna nesse modo
        muted = not muted
        toggle_audio(not muted)
        update_mic_icon()

    def ptt_mouse_down(e):
        if push_to_talk:
            toggle_audio(True)
            update_mic_icon()

    def ptt_mouse_up(e):
        if push_to_talk:
            toggle_audio(False)
            update_mic_icon()

    def send_message(e=None):
        if msg_input.value.strip():
            msg = f"{username.value}: {msg_input.value.strip()}"
            try:
                sock.sendall(msg.encode())
                msg_input.value = ""
                page.update()
            except:
                page.snack_bar = ft.SnackBar(ft.Text("Erro ao enviar mensagem"))
                page.snack_bar.open = True
                page.update()

    def receive_messages():
        while True:
            try:
                data = sock.recv(1024)
                if not data.startswith(b'[AUDIO]') and not data.startswith(b'[AUDIO:'):
                    chat_display.value += data.decode() + "\n"
                    page.update()
            except:
                break

    def on_speaker_change(name):
        speaker_label.value = f"🔊 {name} está falando..."
        page.update()
        def clear():
            time.sleep(1.5)
            speaker_label.value = "🔊 Ninguém está falando..."
            page.update()
        threading.Thread(target=clear, daemon=True).start()

    def connect_chat(e):
        try:
            sock.connect((SERVER_IP, PORT))
            sock.sendall(f"{username.value} entrou no chat.".encode())
            threading.Thread(target=receive_messages, daemon=True).start()
            start_audio_stream(sock, username.value)
            receive_audio_stream(sock, on_speaker_change=on_speaker_change)
            page.controls.clear()
            build_chat_ui()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro: {ex}"))
            page.snack_bar.open = True
            page.update()

    def change_mode(e):
        nonlocal push_to_talk, muted
        push_to_talk = mode_toggle.value == "Push-to-Talk"
        set_push_to_talk(push_to_talk)
        muted = False if push_to_talk else True
        toggle_audio(not muted)
        update_mic_icon()

    def build_chat_ui():
        page.add(
            ft.Row([ft.Text(f"Usuário: {username.value}", size=16), mode_toggle], alignment="spaceBetween"),
            speaker_label,
            chat_display,
            ft.Row([msg_input, send_btn]),
            ft.Row([mic_btn]),
        )
        update_mic_icon()

    # Eventos
    send_btn.on_click = send_message
    msg_input.on_submit = send_message
    mic_btn.on_click = toggle_mic
    mic_btn.on_mouse_down = ptt_mouse_down
    mic_btn.on_mouse_up = ptt_mouse_up
    mode_toggle.on_change = change_mode

    # Tela inicial
    page.add(username, ft.ElevatedButton("Entrar no Chat", on_click=connect_chat))

ft.app(target=main)
