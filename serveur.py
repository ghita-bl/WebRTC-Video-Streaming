import asyncio
import websockets
import json

connected_clients = {}

async def handle_client(websocket):
    client_id = None
    try:
        async for message in websocket:
            data = json.loads(message)
            msg_type = data.get("type")

            # First message must register with an ID
            if msg_type == "register":
                client_id = data["id"]
                connected_clients[client_id] = websocket
                print(f"Registered: {client_id}")
                await websocket.send(json.dumps({"type": "registered", "id": client_id}))
                continue

            # Forward message to target
            target = data.get("target")
            if target and target in connected_clients:
                await connected_clients[target].send(message)
            else:
                print(f"Target not found: {target}")

    except websockets.exceptions.ConnectionClosed:
        print(f"Disconnected: {client_id}")
    finally:
        if client_id:
            connected_clients.pop(client_id, None)

async def main():
    async with websockets.serve(handle_client, "0.0.0.0", 8765):
        print("Signaling server running on ws://0.0.0.0:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())