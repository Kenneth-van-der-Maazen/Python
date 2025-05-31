import os
import socket
import threading
from requests import get
from datetime import datetime
import keyboard




def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')
    if os.name == 'nt':
        os.system('mode con: cols=100 lines=70')  # breedte = 100, hoogte = 30

killswitch_activated = threading.Event()



host_ip = get('https://api.ipify.org').content.decode('utf8')
public_host = '0.0.0.0'
local_host = '127.0.0.1'
com_port = 5002

#token = "<TEKST>"
#client_sockets = set()

clients = []
usernames = []
nodes = []
admins = []
client_user_map = {}


def killswitch_listener():
    while True:
        cmd = input()
        if cmd.strip().lower() == "q":
            clear_console()
            print("\n[!] Kill switch activated.")
            killswitch_activated.set()
            break

def broadcast(message):
    for client in clients:
        try:
            client.send(message)
            #client.send(colored_msg.encode('ascii'))
        except:
            pass

def handle(client):
    while not killswitch_activated.is_set():
        try:
            message = client.recv(1024).decode('ascii')
            if not message:
                continue

            username = client_user_map.get(client, "Unknown").strip()

            if username in admins:
                # Voeg een ★ voor de naam toe, ongeacht het originele bericht
                # Zoek bijv. ": " en zet daar ★ achter de naam
                if ": " in message:
                    parts = message.split(": ", 1)
                    if username in parts[0]:
                        parts[0] = parts[0].replace(username, f"★ {username}")
                        message = ": ".join(parts)

            broadcast(message.encode('utf-8'))

        except Exception as e:
            print(f"[!] Error: {e}")
            if client in clients:
                index = clients.index(client)
                client.close()
                clients.remove(client)
                username = usernames[index]
                broadcast(f'[i] {username} disconnected!'.encode('utf-8'))
                usernames.remove(username)
                nodes.pop(index)
                client_user_map.pop(client, None)
            break

def start_server():
    while not killswitch_activated.is_set():
        try:
            server.settimeout(1.0)
            client, address = server.accept()
        except socket.timeout:
            continue
        except:
            break            

        # client_user_map[client] = username
        
        time_now = datetime.now().strftime('%H:%M')
        date_now = datetime.now().strftime('%d-%m-%y @ %H:%M')
        
        client.send('LOGIN'.encode('ascii'))
        username = client.recv(1024).decode('ascii')
        node = client.recv(1024).decode('ascii')
        
        usernames.append(username)
        nodes.append(node)
        clients.append(client)
        client_user_map[client] = username
        
        print(f"[{date_now}] >> Incomming connection from {username} on [ {node} ]")
        broadcast(f"{username} connected!\n".encode('ascii'))
        client.send('[OKE] Succesfully connected with server!'.encode('ascii'))
        
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

def command_listener():
    while not killswitch_activated.is_set():
        cmd = input(">> ").strip()

        if cmd.lower() == "q":
            clear_console()
            print("\n[!] Kill switch activated.")
            killswitch_activated.set()
            break

        elif cmd == "/all":
            print("\n[!] Active Connections:")
            for i, (name, node) in enumerate(zip(usernames, nodes), 1):
                tag = " (admin)" if name in admins else ""
                print(f"  {i}. {name} on [{node}]{tag}")
            print()

        elif cmd.startswith("/admin "):
            parts = cmd.split(maxsplit=1)
            username = parts[1]
            if username in usernames:
                if username not in admins:
                    admins.append(username)
                    print(f"[✔] {username} is now an admin.")
                    broadcast(f"[i] {username} was granted admin rights.".encode('ascii'))
                else:
                    print(f"[!] {username} is already an admin.")
            else:
                print(f"[!] User '{username}' not found.")

        elif cmd.startswith("/unadmin "):
            parts = cmd.split(maxsplit=1)
            username = parts[1]
            if username in admins:
                admins.remove(username)
                print(f"[✔] {username} is no longer an admin.")
                broadcast(f"[i] {username} lost admin rights.".encode('ascii'))
            else:
                print(f"[!] {username} is not an admin.")

        elif cmd == "/help":
            print("\n[Commands]")
            print("  /all              - Show all active connections")
            print("  /admin <username> - Grant admin rights")
            print("  /unadmin <user>   - Revoke admin rights")
            print("  /help             - Show available commands")
            print("  q                 - Quit server (killswitch)")

        elif cmd != "":
            print(f"[!] Unknown command: '{cmd}' Type '/help' for available commands.")

if __name__ == "__main__":
    clear_console()
    try:
        # clear_console()
        print("[*] Starting server script..")
        print(f"[*] Server IP: {host_ip}")
        
        host = "0.0.0.0"
        port = 5002
        
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(5)
        
        # print(f"Server listening on {host}:{port}")
        print(f"[*] Server is currently active!\n")
        
        # Start killswitch thread
        # threading.Thread(target=killswitch_listener, daemon=True).start()
        
        # Start command listener thread
        threading.Thread(target=command_listener, daemon=True).start()
        
        start_server()
        
        # print("Waiting for incoming connections..")
    except KeyboardInterrupt:
        print("\n[!] Server manually interrupted.")
    finally:
        print("[*] Shutting down server...")
        for client in clients:
            client.close()
        server.close()

