import asyncio
import json
import websockets
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer
import os 
from dotenv import load_dotenv
load_dotenv()

SIGNALING_SERVER = "ws://localhost:8765"
MY_ID = "sender"
PEER_ID = "receiver"

async def run_sender():
    pc = RTCPeerConnection()

    CAMERA = os.getenv("CAMERA_NAME", "video=USB2.0 HD UVC WebCam")
    player = MediaPlayer(CAMERA, format="dshow")

    
    pc.addTrack(player.video)

    async with websockets.connect(SIGNALING_SERVER) as ws:
        await ws.send(json.dumps({"type": "register", "id": MY_ID}))
        await ws.recv()

        @pc.on("icecandidate")
        async def on_ice_candidate(candidate):
            if candidate:
                await ws.send(json.dumps({
                    "type": "ice",
                    "target": PEER_ID,
                    "from": MY_ID,
                    "candidate": {
                        "candidate": candidate.candidate,
                        "sdpMid": candidate.sdpMid,
                        "sdpMLineIndex": candidate.sdpMLineIndex,
                    }
                }))

        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        await ws.send(json.dumps({
            "type": "offer",
            "target": PEER_ID,
            "from": MY_ID,
            "sdp": pc.localDescription.sdp,
        }))
        print("Offer sent, waiting for answer...")

        async for raw in ws:
            msg = json.loads(raw)
            if msg["type"] == "answer":
                await pc.setRemoteDescription(
                    RTCSessionDescription(sdp=msg["sdp"], type="answer")
                )
                print("Answer received, connection establishing...")
            elif msg["type"] == "ice":
                pass  # ignore browser ICE candidates on localhost

if __name__ == "__main__":
    asyncio.run(run_sender())

