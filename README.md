# 📹 WebRTC Video Streaming

Real-time peer-to-peer video streaming using WebRTC, Python (aiortc), and WebSockets.

## Architecture

```
Sender (Python)         Signaling Server         Receiver (Browser)
      |                  (Python/WS)                     |
      |--- register "sender" --->|                        |
      |                          |<--- register "receiver"|
      |--- SDP offer ----------->|-------> SDP offer ---->|
      |<-- SDP answer -----------|<------- SDP answer ----|
      |<-- ICE candidates -------|<------- ICE candidates-|
      |--- ICE candidates ------>|-------> ICE candidates->|
      |                          |                        |
      |============ Direct P2P video stream =============>|
```

Once the WebRTC connection is established, the signaling server is no longer involved — video flows directly peer-to-peer.

## Project Structure

```
├── server.py       # WebSocket signaling server
├── sender.py       # Python webcam capture + WebRTC sender
└── receiver.html   # Browser-based WebRTC receiver
```

## Requirements

### Python
```bash
pip install aiortc websockets opencv-python
```

### System
- **Windows**: DirectShow (built-in) — no extra install needed
- **Linux**: v4l2 — `sudo apt install v4l-utils`
- **macOS**: AVFoundation (built-in)

## Configuration

### Find your camera name (Windows)
```powershell
python -c "import subprocess; subprocess.run(['powershell', '-Command', 'Get-PnpDevice -Class Camera | Select-Object FriendlyName'])"
```

Then update `sender.py`:
```python
# Windows
player = MediaPlayer("video=YOUR CAMERA NAME", format="dshow")

# Linux
player = MediaPlayer("/dev/video0", format="v4l2")

# macOS
player = MediaPlayer("0", format="avfoundation")
```

### Set the server IP in `receiver.html`
```javascript
// Same machine
const ws = new WebSocket("ws://127.0.0.1:8765");

// Different device on same network (get IP via `ipconfig`)
const ws = new WebSocket("ws://192.168.x.x:8765");
```

## Usage

Run in this exact order:

**1. Start the signaling server**
```bash
python server.py
```

**2. Open the receiver in your browser**

Open `receiver.html` via Live Server or any HTTP server.

**3. Start the sender**
```bash
python sender.py
```

The video stream should appear in the browser within a few seconds.

## How It Works

### Signaling (server.py)
The WebSocket server acts as a temporary "phone book" — it lets the sender and receiver find each other by name and exchange connection setup messages (SDP + ICE). Once the WebRTC connection is established, it plays no further role.

### SDP (Session Description Protocol)
The sender creates an **offer** describing what it can send (codecs, resolution, etc.). The receiver replies with an **answer** confirming what it can accept. This negotiation happens through the signaling server.

### ICE (Interactive Connectivity Establishment)
Each peer discovers all the ways it can be reached (local IP, public IP, TURN relay) and shares these as **ICE candidates** through the signaling server. WebRTC then picks the best path for the direct connection.

## Troubleshooting

| Problem | Solution |
|---|---|
| `OSError: [Errno 10048]` | Port 8765 already in use. Run `netstat -ano \| findstr :8765` then `taskkill /PID <id> /F` |
| `no container format 'v4l2'` | You're on Windows. Use `format="dshow"` |
| `ValueError: no container format` | Wrong camera name. Check camera name with PowerShell command above |
| No video in browser | Check browser console (F12) for errors. Make sure order is: server → browser → sender |
| `ConnectionClosedError` | Server crashed. Check server terminal for errors. Make sure `handle_client` has no `path` parameter |

## Cross-Network Streaming

To stream between devices on different networks:

1. **Deploy the signaling server** on a public VPS (AWS, DigitalOcean, etc.)
2. **Add a STUN server** to both sender and receiver:
```python
# sender.py
pc = RTCPeerConnection(configuration={
    "iceServers": [{"urls": "stun:stun.l.google.com:19302"}]
})
```
3. **Enable ICE candidate exchange** in `sender.py` (currently disabled for localhost)
4. Optionally add a **TURN server** for strict NAT environments

## Dependencies

| Package | Purpose |
|---|---|
| `aiortc` | WebRTC implementation for Python |
| `websockets` | WebSocket signaling server |
| `opencv-python` | Webcam access |
| `av` | Video encoding/decoding (installed with aiortc) |
