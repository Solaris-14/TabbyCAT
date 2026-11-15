"""
TabbyPatrol - Standalone Test Script
Simulates a Chrome tab notification over WebSocket to test the cat walking and swatting!
"""

import json
import socket
import time

WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def test_trigger():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("127.0.0.1", 48888))
    except Exception as e:
        print(f"Error: Could not connect to Tabby Overlay on port 48888: {e}")
        print("Please ensure 'python overlay/tabby_overlay.py' or 'run_tabby.bat' is running!")
        return

    # WebSocket handshake
    handshake = (
        "GET / HTTP/1.1\r\n"
        "Host: 127.0.0.1:48888\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
        "Sec-WebSocket-Version: 13\r\n\r\n"
    )
    sock.sendall(handshake.encode("utf-8"))
    res = sock.recv(1024)

    if b"101 Switching Protocols" not in res:
        print("WebSocket handshake failed:", res)
        sock.close()
        return

    print("Connected to Tabby! Sending simulated blocked tab event (Tab #3: Reddit)...")

    # Send blocked tab payload
    payload = json.dumps({
        "type": "BLOCKED_TAB_OPENED",
        "tabId": 1337,
        "tabIndex": 3,
        "totalTabs": 7,
        "title": "r/all - Endless Scrolling Distraction",
        "url": "https://reddit.com/r/all",
        "window": {
            "left": 0,
            "top": 0,
            "width": 1920,
            "height": 1080
        }
    })

    # Encode frame (client frames must be masked)
    mask = b"\x12\x34\x56\x78"
    raw = payload.encode("utf-8")
    masked = bytearray(len(raw))
    for i in range(len(raw)):
        masked[i] = raw[i] ^ mask[i % 4]

    frame = bytes([0x81, 0x80 | len(raw)]) + mask + bytes(masked)
    sock.sendall(frame)

    print("Event sent! Watch the cute cat walk over to Tab #3, swat it, and celebrate! 🐾")
    sock.close()


if __name__ == "__main__":
    test_trigger()
