import socket
import threading
import os
import random
from datetime import datetime
from colorama import Fore, init


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

init()
colors = [Fore.RED, Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.MAGENTA, Fore.WHITE, Fore.YELLOW, 
          Fore.LIGHTBLACK_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTGREEN_EX, Fore.LIGHTYELLOW_EX,
          Fore.LIGHTCYAN_EX, Fore.LIGHTRED_EX]

client_color = random.choice(colors)

public = '0.0.0.0'
local = '127.0.0.1'
port = 5002

username = os.getlogin()
node = socket.gethostname()

def receive():
    while True:
        try:
            # ontvang berichten van server
            # wanneer 'USER' ontvangen, stuur 'username' terug
            message = client.recv(1024).decode('utf-8')
            if message == 'LOGIN':
                client.send(username.encode('ascii'))
                client.send(node.encode('ascii'))
            else:
                print(message)   #####
                #print('')
        except:
            print("[!] ERROR: Server disconnected!")
            client.close()
            break

def write():
    while True:
        time_now = datetime.now().strftime('%H:%M')
        
        #message = "[{}] {}: {}".format(date_now, username, input())
        #to_send = input()
        message = f"{client_color}[{time_now}] {username}: {input()}{Fore.RESET}"
    
        client.send(message.encode('utf-8'))

if __name__ == "__main__":
    try:
        
        #host = input("Specify host address: ")
        host = '127.0.0.1'
    except ValueError:
        print("Server set to localhost.")
    try:
        #port = int(input("Specify port number: "))
        port = 5002
    except ValueError:
        print("Port is set to default!")
        
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    
    # clear_console()
    
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()
