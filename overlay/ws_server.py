"""
Pure Python RFC 6455 WebSocket Server
Zero external dependencies. Runs on standard Python 3 socket + hashlib + base64 + struct.
"""

import base64
import hashlib
import json
import socket
import struct
import threading
import time

WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


class PureWebSocketServer:
    def __init__(self, host="127.0.0.1", port=48888, on_message=None, on_connect=None, on_disconnect=None):
        self.host = host
        self.port = port
        self.on_message = on_message
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.clients = set()
        self.lock = threading.Lock()
        self.running = False
        self.server_socket = None

    def start(self):
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"[WebSocket] Server listening on ws://{self.host}:{self.port}")

        thread = threading.Thread(target=self._accept_loop, daemon=True)
        thread.start()

    def stop(self):
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass

    def _accept_loop(self):
        while self.running:
            try:
                client_sock, addr = self.server_socket.accept()
                threading.Thread(target=self._handle_client, args=(client_sock, addr), daemon=True).start()
            except Exception:
                break

    def _handle_client(self, client_sock, addr):
        # 1. Handshake
        try:
            req = client_sock.recv(4096).decode("utf-8", errors="ignore")
            if not req:
                client_sock.close()
                return

            headers = {}
            lines = req.split("\r\n")
            for line in lines[1:]:
                if ": " in line:
                    k, v = line.split(": ", 1)
                    headers[k.lower()] = v.strip()

            sec_key = headers.get("sec-websocket-key")
            if not sec_key:
                client_sock.close()
                return

            accept_val = base64.b64encode(hashlib.sha1((sec_key + WS_GUID).encode("utf-8")).digest()).decode("utf-8")
            response = (
                "HTTP/1.1 101 Switching Protocols\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Accept: {accept_val}\r\n\r\n"
            )
            client_sock.sendall(response.encode("utf-8"))

            with self.lock:
                self.clients.add(client_sock)
            print(f"[WebSocket] Client connected: {addr}")

            if self.on_connect:
                self.on_connect(client_sock)

            # 2. Read frames loop
            while self.running:
                data = self._read_frame(client_sock)
                if data is None:
                    break
                if data and self.on_message:
                    try:
                        parsed = json.loads(data)
                        self.on_message(parsed, client_sock)
                    except Exception as err:
                        print(f"[WebSocket] JSON parse error: {err}")

        except Exception as e:
            # Client disconnected
            pass
        finally:
            with self.lock:
                self.clients.discard(client_sock)
            try:
                client_sock.close()
            except Exception:
                pass
            print(f"[WebSocket] Client disconnected: {addr}")
            if self.on_disconnect:
                self.on_disconnect(client_sock)

    def _read_frame(self, sock):
        try:
            header = sock.recv(2)
            if len(header) < 2:
                return None
            b1, b2 = header[0], header[1]
            opcode = b1 & 0x0F
            is_masked = (b2 & 0x80) != 0
            payload_len = b2 & 0x7F

            # Connection close opcode = 0x8, ping = 0x9, pong = 0xA
            if opcode == 0x8:
                return None
            if opcode == 0x9: # ping
                # send pong
                self._send_raw_frame(sock, b"", opcode=0xA)
                return ""

            if payload_len == 126:
                ext = sock.recv(2)
                payload_len = struct.unpack("!H", ext)[0]
            elif payload_len == 127:
                ext = sock.recv(8)
                payload_len = struct.unpack("!Q", ext)[0]

            mask_key = sock.recv(4) if is_masked else None

            # Read full payload
            chunks = []
            bytes_read = 0
            while bytes_read < payload_len:
                chunk = sock.recv(min(4096, payload_len - bytes_read))
                if not chunk:
                    return None
                chunks.append(chunk)
                bytes_read += len(chunk)
            payload = b"".join(chunks)

            if is_masked and mask_key:
                unmasked = bytearray(payload_len)
                for i in range(payload_len):
                    unmasked[i] = payload[i] ^ mask_key[i % 4]
                payload = bytes(unmasked)

            return payload.decode("utf-8", errors="ignore")
        except Exception:
            return None

    def broadcast(self, data):
        if isinstance(data, dict):
            text = json.dumps(data)
        else:
            text = str(data)
        frame = self._encode_frame(text)
        with self.lock:
            dead = set()
            for client in self.clients:
                try:
                    client.sendall(frame)
                except Exception:
                    dead.add(client)
            self.clients -= dead

    def _encode_frame(self, text, opcode=0x1):
        payload = text.encode("utf-8")
        length = len(payload)
        b1 = 0x80 | (opcode & 0x0F) # FIN + text
        if length <= 125:
            header = bytes([b1, length])
        elif length <= 65535:
            header = bytes([b1, 126]) + struct.pack("!H", length)
        else:
            header = bytes([b1, 127]) + struct.pack("!Q", length)
        return header + payload

    def _send_raw_frame(self, sock, payload, opcode=0x1):
        try:
            length = len(payload)
            b1 = 0x80 | (opcode & 0x0F)
            header = bytes([b1, length])
            sock.sendall(header + payload)
        except Exception:
            pass


if __name__ == "__main__":
    def on_msg(data, sock):
        print("Received:", data)

    server = PureWebSocketServer(port=48888, on_message=on_msg)
    server.start()
    print("Testing server for 2 seconds...")
    time.sleep(2)
    server.stop()
    print("Server stopped.")
