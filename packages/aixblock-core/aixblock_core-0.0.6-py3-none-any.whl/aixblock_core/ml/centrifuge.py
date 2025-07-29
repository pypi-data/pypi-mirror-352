import asyncio
import websockets
import json
import random

class Subscription:
    def __init__(self, channel):
        self.channel = channel

class CentrifugeProvider:
    def __init__(self):
        self.subscriptions = []
        self.on_message_callbacks = {}

    def subscribe(self, channel):
        subscription = Subscription(channel)
        self.subscriptions.append(subscription)
        return subscription

    def unsubscribe(self, subscription):
        self.subscriptions.remove(subscription)

    def publish(self, channel, data):
        # Implement publishing logic here
        pass

    def on_message(self, channel, callback):
        if channel in self.on_message_callbacks:
            self.on_message_callbacks[channel].append(callback)
        else:
            self.on_message_callbacks[channel] = [callback]

        def remove_callback():
            self.on_message_callbacks[channel].remove(callback)

        return remove_callback

    def subscribe_task(self, task_id):
        return self.subscribe(f"task/{task_id}")

    def on_task_message(self, task_id, callback):
        subscription = self.subscribe_task(task_id)
        return self.on_message(f"task/{task_id}", callback)


async def connect_to_centrifuge(server):
    # token = "64214c36-5b99-45f7-8219-3ac181abd50d"
    try:
        async with websockets.connect(f"ws://{server}/connection/websocket") as websocket:
            pass
    except Exception as e:
        return e

    
        # await websocket.send(json.dumps({"token": token}))
        # async for message in websocket:
        #     message_data = json.loads(message)
        #     event_type = message_data.get("event")
        #     channel = message_data.get("channel")
        #     data = message_data.get("data")

        #     if not event_type or not channel or not data:
        #         continue

        #     if event_type == "message" and channel in centrifuge_provider.on_message_callbacks:
        #         for callback in centrifuge_provider.on_message_callbacks[channel]:
        #             callback(data)
        #     elif event_type == "connect":
        #         print("Centrifuge connected")
        #     elif event_type == "disconnect":
        #         print("Centrifuge disconnected")
        #     elif event_type == "error":
        #         print("Centrifuge error:", data)


# async def main():
#     global centrifuge_provider
#     centrifuge_provider = CentrifugeProvider()

    # try:
    #     await connect_to_centrifuge("108.181.196.144:8000")
    # except Exception as e:
    #     print(f"Failed to connect to WebSocket server: {e}")


# if __name__ == "__main__":
#     asyncio.run(main())
