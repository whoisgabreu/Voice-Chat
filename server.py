# server.py
import socket
import threading

HOST = '192.168.4.44'
PORT = 5000
clients = []

def broadcast(data, sender):
    for client in clients:
        if client != sender:
            try:
                client.sendall(data)
            except:
                clients.remove(client)

def handle_client(conn):
    clients.append(conn)
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            broadcast(data, conn)
    except:
        pass
    finally:
        clients.remove(conn)
        conn.close()

def main():
    print("[*] Servidor ouvindo...")
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, _ = s.accept()
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

if __name__ == "__main__":
    main()
