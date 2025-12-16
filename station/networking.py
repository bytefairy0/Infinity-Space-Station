import socket
import threading
from typing import Dict, Tuple, Optional
from .smart_room import SmartRoom

local_host = "127.0.0.1"
port = 5000

class RoomNode:
    def __init__(self, room: SmartRoom, host=local_host, port=port):
        self.room = room
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False

    def connect(self):
        self.sock.connect((self.host, self.port))
        self.running = True
        # identify ourselves to the server
        self._send_line(f"HELLO|{self.room.room_id}")
        threading.Thread(target=self.listen_loop, daemon=True).start()
        
    def send_status(self):
        msg = f"STATUS|{self.room.room_id}|{self.room.temperature:.2f}|{int(self.room.occupied)}"
        self._send_line(msg)

    def _send_line(self, text: str):
        try:
            self.sock.sendall((text + "\n").encode())
        except OSError:
            self.running = False

    def listen_loop(self):
        while self.running:
            try:
                data = self.sock.recv(1024)
                if not data:
                    break
                for line in data.decode().splitlines():
                    line = line.strip()
                    if line:
                        self.handle_command(line)
            except OSError:
                break
        self.running = False

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
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients: Dict[socket.socket, Tuple[str, Tuple[str, int]]] = {}
        self.room_map: Dict[str, socket.socket] = {}
        self.running = False

    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.running = True
        threading.Thread(target=self.accept_loop, daemon=True).start()

    def accept_loop(self):
        while self.running:
            try:
                client, addr = self.server.accept()
            except OSError:
                break
            print("Client connected:", addr)
            self.clients[client] = ("", addr)
            threading.Thread(target=self.client_loop, args=(client,), daemon=True).start()

    def client_loop(self, client: socket.socket):
        while self.running:
            try:
                data = client.recv(1024)
            except OSError:
                break
            if not data:
                break

            for raw_line in data.decode().splitlines():
                line = raw_line.strip()
                if not line:
                    continue
                self._handle_message(client, line)

        self._drop_client(client)

    def broadcast(self, message: str):
        for client in list(self.clients.keys()):
            try:
                client.sendall((message + "\n").encode())
            except OSError:
                self._drop_client(client)

    def set_target_temp(self, room_id: str, target_temp: float):
        """
        Send a SET_TARGET_TEMP command to a specific room if known,
        otherwise broadcast it.
        """
        command = f"SET_TARGET_TEMP:{room_id}:{target_temp}"
        client = self.room_map.get(room_id)
        if client:
            try:
                client.sendall((command + "\n").encode())
                return
            except OSError:
                self._drop_client(client)
        # fallback: broadcast
        self.broadcast(command)

    def _handle_message(self, client: socket.socket, line: str):
        if line.startswith("HELLO|"):
            room_id = line.split("|", 1)[1]
            self.clients[client] = (room_id, self.clients[client][1])
            self.room_map[room_id] = client
            print(f"Registered room {room_id}")
            return

        if line.startswith("STATUS|"):
            try:
                _, room_id, temp, occupied = line.split("|")
                self.room_map[room_id] = client
                self.clients[client] = (room_id, self.clients[client][1])
                print(f"[STATUS] {room_id}: temp={temp}, occupied={occupied}")
            except ValueError:
                print("Malformed STATUS:", line)
            return

        print("Received:", line)

    def _drop_client(self, client: socket.socket):
        room_id: Optional[str] = None
        if client in self.clients:
            room_id = self.clients[client][0]
            del self.clients[client]
        if room_id and self.room_map.get(room_id) == client:
            del self.room_map[room_id]
        try:
            client.close()
        except OSError:
            pass
