import threading
import socket

host = '127.0.0.1'
port = 60000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen()

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        try:
            client.send(message)
        except:
            clients.remove(client)


def kick_user(name):
    if name in nicknames and name != 'admin':
        i = nicknames.index(name)
        client_to_kick = clients[i]
        client_to_kick.send("You were kicked by admin!".encode('utf-8'))
        client_to_kick.close()
        clients.pop(i)
        nicknames.pop(i)
        broadcast(f"{name} was kicked!".encode('utf-8'))

def handle(client):
    while True:
        try:
            msg = client.recv(1024).decode('utf-8')
            if msg.startswith('KICK '):
                if nicknames[clients.index(client)] == 'admin':
                    kick_user(msg[5:].strip())
                else:
                    client.send("Command refused!".encode('utf-8'))
            elif msg.startswith('BAN '):
                if nicknames[clients.index(client)] == 'admin':
                    name = msg[4:].strip()
                    kick_user(name)
                    with open('bans.txt', 'a') as f:
                        f.write(name + '\n')
                else:
                    client.send("Command refused!".encode('utf-8'))
            else:
                broadcast(msg.encode('utf-8'))
        except:
            if client in clients:
                i = clients.index(client)
                nickname = nicknames[i]
                clients.pop(i)
                nicknames.pop(i)
                broadcast(f"{nickname} left the chat".encode('utf-8'))
            client.close()
            break

def receive():
    while True:
        client, addr = server.accept()
        print("Connected:", addr)

        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')

        try:
            with open('bans.txt', 'r') as f:
                bans = f.read().splitlines()
        except FileNotFoundError:
            bans = []

        if nickname in bans:
            client.send("BAN".encode('utf-8'))
            client.close()
            continue

        if nickname == 'admin':
            client.send("PASS".encode('utf-8'))
            password = client.recv(1024).decode('utf-8')
            if password != 'adminpass':
                client.send("REFUSE".encode('utf-8'))
                client.close()
                continue

        clients.append(client)
        nicknames.append(nickname)
        broadcast(f"{nickname} joined the chat!".encode('utf-8'))

        threading.Thread(target=handle, args=(client,), daemon=True).start()

print("Server is listening...")
receive()
