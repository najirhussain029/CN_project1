import socket
import threading

nickname = input("Choose a nickname: ")
if nickname == 'admin':
    password = input("Enter a password for admin: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 60000))

stop_thread = False

def receive():
    global stop_thread
    while True:
        if stop_thread:
            break
        try:
            message = client.recv(1024).decode('utf-8')

            if message == 'SWASTIK':
                client.send(nickname.encode('utf-8'))

                next_message = client.recv(1024).decode('utf-8')

                if next_message == 'PASS':
                    client.send(password.encode('utf-8'))
                    if client.recv(1024).decode('utf-8') == 'REFUSE':
                        print("❌ Wrong admin password")
                        stop_thread = True

                elif next_message == 'BAN':
                    print("❌ You are banned from this server")
                    client.close()
                    stop_thread = True
            else:
                print(message)

        except:
            print("❌ Connection error")
            client.close()
            break

def write():
    while True:
        if stop_thread:
            break

        msg = input("")
        message = f"{nickname}: {msg}"

        if msg.startswith('/'):

            if nickname == 'admin':
                if msg.startswith('/kick'):
                    client.send(f"KICK{msg[6:]}".encode('utf-8'))

                elif msg.startswith('/ban'):
                    client.send(f"BAN{msg[5:]}".encode('utf-8'))
            else:
                print("❌ Only admin can use commands")
        else:
            client.send(message.encode('utf-8'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
