import socket
import threading

HOST = '192.168.4.44'  # Aceita conexões externas
PORT = 5000

clients = []

def handle_client(conn, addr):
    print(f"[+] Novo cliente: {addr}")
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            # Repassa áudio para os outros
            for c in clients:
                if c != conn:
                    c.sendall(data)
        except:
            break
    print(f"[-] Cliente desconectado: {addr}")
    clients.remove(conn)
    conn.close()

def main():
    print(f"Servidor de voz escutando em {HOST}:{PORT}")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    while True:
        conn, addr = server.accept()
        clients.append(conn)
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
