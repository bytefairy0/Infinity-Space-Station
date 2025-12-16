import socket
import threading
from .smart_room import SmartRoom

local_host = "127.0.0.1"
port = 5000

class RoomNode:
    def __init__(self, room: SmartRoom, host=local_host, port=port):
        self.room = room
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = False

    def connect(self):
        self.sock.connect((self.host, self.port))
        self.running = True
        threading.Thread(target=self.listen_loop, daemon=True).start()
        
    def send_status(self):
        msg = f"STATUS|{self.room.room_id}|{self.room.temperature:.2f}|{int(self.room.occupied)}"
        self.sock.sendall(msg.encode())

    def listen_loop(self):
        while self.running:
            try:
                data = self.sock.recv(1024)
                if not data:
                    break
                self.handle_command(data.decode().strip())
            except:
                break

    def handle_command(self, command: str):
        print(f"[{self.room.room_id}]got: {command}")
        parts = command.split(":")
        if parts[0] == "SET_TARGET_TEMP" and len(parts) == 3:
            if parts[1] == self.room.room_id:
                self.room.target_temperature = float(parts[2])


class StationServer:
    def __init__(self, host=local_host, port=port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clients = []
        self.running = False

    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.running = True
        threading.Thread(target=self.listen_loop, daemon=True).start()

    def accept_loop(self):
        while self.running:
            client, addr = self.server.accept()
            self.clients.append((client, addr))
            print("Client connected:", addr)
            threading.Thread(target=self.client_loop, args=(client,), daemon=True).start()

    def client_handler(self, client):
        while self.running:
            try:
                data = client.recv(1024).decode()
                if not data:
                    break
                print("Received:", data)
            except:
                break

    def broadcast(self, message: str):
        for client, addr in self.clients:
            try:
                client.sendall(message.encode())
            except:
                pass