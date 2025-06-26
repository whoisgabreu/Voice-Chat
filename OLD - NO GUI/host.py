# import socket
# import threading

# HOST = '31.97.27.195'  # Aceita conexões externas
# PORT = 5005

# clients = []

# def handle_client(conn, addr):
#     print(f"[+] Novo cliente: {addr}")
#     while True:
#         try:
#             data = conn.recv(1024)
#             if not data:
#                 break
#             # Repassa áudio para os outros
#             for c in clients:
#                 if c != conn:
#                     c.sendall(data)
#         except:
#             break
#     print(f"[-] Cliente desconectado: {addr}")
#     clients.remove(conn)
#     conn.close()

# def main():
#     print(f"Servidor de voz escutando em {HOST}:{PORT}")
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.bind((HOST, PORT))
#     server.listen()
#     while True:
#         conn, addr = server.accept()
#         clients.append(conn)
#         threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

# if __name__ == "__main__":
#     main()


import socket
import threading
import queue

HOST = '31.97.27.195'  # Aceita conexões externas
PORT = 5005

clients = {}  # {conn: queue.Queue()}

def client_sender(conn, msg_queue):
    """Thread de envio para um cliente específico."""
    while True:
        try:
            msg = msg_queue.get()
            if msg is None:
                break
            conn.sendall(msg)
        except:
            break

def handle_client(conn, addr):
    print(f"[+] Novo cliente: {addr}")
    msg_queue = queue.Queue()
    clients[conn] = msg_queue

    # Thread que envia mensagens para o cliente
    threading.Thread(target=client_sender, args=(conn, msg_queue), daemon=True).start()

    try:
        while True:
            data = conn.recv(2048)
            if not data:
                break
            # Envia para todos os outros clientes (via fila)
            for c, q in list(clients.items()):
                if c != conn:
                    try:
                        q.put_nowait(data)
                    except queue.Full:
                        print(f"[!] Fila cheia para {c.getpeername()}")
    except:
        pass
    finally:
        print(f"[-] Cliente desconectado: {addr}")
        clients.pop(conn, None)
        msg_queue.put(None)
        conn.close()

def main():
    print(f"[Servidor] Escutando em {HOST}:{PORT}")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
