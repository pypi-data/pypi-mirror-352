import asyncio
import json
import logging
import base64
import hmac
import hashlib
import requests
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from prometheus_client.exposition import basic_auth_handler
from centrifuge.exceptions import ClientDisconnectedError
from asgiref.sync import sync_to_async
from centrifuge import (
    CentrifugeError,
    Client,
    ClientEventHandler,
    ConnectedContext,
    ConnectingContext,
    DisconnectedContext,
    ErrorContext,
    JoinContext,
    LeaveContext,
    PublicationContext,
    SubscribedContext,
    SubscribingContext,
    SubscriptionErrorContext,
    UnsubscribedContext,
    SubscriptionEventHandler,
    ServerSubscribedContext,
    ServerSubscribingContext,
    ServerUnsubscribedContext,
    ServerPublicationContext,
    ServerJoinContext,
    ServerLeaveContext,
)
import threading
from django.conf import settings
from core.settings.base import CENTRIFUGE_URL, CENTRIFUGE_SECRET,GRAFANA_PROMETHUS
from compute_marketplace.self_host import (
    check_compute_verify,
    update_server_info,
    update_compute_gpus,
    handle_install_compute,
    handle_service_type,
    handle_cuda,
)

logger = logging.getLogger(__name__)


def promethus(job):
    def my_auth_handler(url, method, timeout, headers, data):
        username = "admin"
        password = "admin"
        return basic_auth_handler(
            url, method, timeout, headers, data, username, password
        )

    registry = CollectorRegistry()
    g = Gauge(
        "job_last_success_unixtime",
        "Last time a batch job successfully finished",
        registry=registry,
    )
    g.set_to_current_time()
    push_to_gateway(
        GRAFANA_PROMETHUS, job=job, registry=registry, handler=my_auth_handler
    )


def base64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=")


def generate_centrifuge_jwt(user, channel=""):
    """Generate JWT token."""
    hmac_secret = settings.CENTRIFUGE_SECRET
    header = {"typ": "JWT", "alg": "HS256"}
    payload = {"sub": user.__str__()}
    if channel:
        payload["channel"] = channel
    encoded_header = base64url_encode(json.dumps(header).encode("utf-8"))
    encoded_payload = base64url_encode(json.dumps(payload).encode("utf-8"))
    signature_base = encoded_header + b"." + encoded_payload
    signature = hmac.new(
        hmac_secret.encode("utf-8"), signature_base, hashlib.sha256
    ).digest()
    encoded_signature = base64url_encode(signature)
    jwt_token = encoded_header + b"." + encoded_payload + b"." + encoded_signature
    return jwt_token.decode("utf-8")


async def async_generate_token(user, channel=""):
    """Generate JWT token."""
    hmac_secret = settings.CENTRIFUGE_SECRET
    header = {"typ": "JWT", "alg": "HS256"}
    payload = {"sub": user.__str__()}
    if channel:
        payload["channel"] = channel
    encoded_header = base64url_encode(json.dumps(header).encode("utf-8"))
    encoded_payload = base64url_encode(json.dumps(payload).encode("utf-8"))
    signature_base = encoded_header + b"." + encoded_payload
    signature = hmac.new(
        hmac_secret.encode("utf-8"), signature_base, hashlib.sha256
    ).digest()
    encoded_signature = base64url_encode(signature)
    jwt_token = encoded_header + b"." + encoded_payload + b"." + encoded_signature
    return jwt_token.decode("utf-8")


async def get_client_token() -> str:
    return generate_centrifuge_jwt("11")


async def get_subscription_token(channel: str) -> str:
    return generate_centrifuge_jwt("11", channel)


def publish_message(channel, data, prefix=True, **kwargs):
    def p():
        topic = channel
        if prefix: 
            topic = settings.CENTRIFUGE_TOPIC_PREFIX + channel
        r = requests.post(
            settings.CENTRIFUGE_API + "/publish",
            headers={"X-API-Key": settings.CENTRIFUGE_API_KEY},
            data=json.dumps({"channel": topic, "data": data}),
        )

        if r.ok:
            logging.log(
                logging.INFO, "Published message to Centrifuge channel: " + channel
            )

            return True
        else:
            logging.log(
                logging.INFO,
                "Failed to publish message to Centrifuge channel: " + channel,
            )
            logging.log(logging.DEBUG, "-> Payload: " + json.dumps(data))
            return False

    if "sync" in kwargs:
        return p()
    else:
        t = threading.Thread(target=p, args=list())
        t.start()
        return t


def setup_client(user_id, channel_log, stop_event):
    token = generate_centrifuge_jwt("11")
    token2 = generate_centrifuge_jwt(user_id)
    client = Client(
        "wss://rt.aixblock.io/centrifugo/connection/websocket",
        events=ClientEventLoggerHandler(stop_event),
        get_token=get_client_token,
        use_protobuf=False,
    )

    sub = client.new_subscription(
        channel_log,
        events=SubscriptionEventLoggerHandler(
           stop_event
        ), 
    )
    sub.events.sub = sub
    sub.events.client = client
    return client, sub


class ClientEventLoggerHandler(ClientEventHandler):
    def __init__(self, stop_event):
        self.stop_event = stop_event

    async def on_connecting(self, ctx: ConnectingContext) -> None:
        logger.info("connecting: %s", ctx)

    async def on_connected(self, ctx: ConnectedContext) -> None:
        logger.info("connected: %s", ctx)

    async def on_disconnected(self, ctx: DisconnectedContext) -> None:
        logger.info("disconnected: %s", ctx)
        self.stop_event.set()

    async def on_error(self, ctx: ErrorContext) -> None:
        logger.error("client error: %s", ctx)
        self.stop_event.set()

    async def on_subscribed(self, ctx: ServerSubscribedContext) -> None:
        logger.info("subscribed server-side sub: %s", ctx)

    async def on_subscribing(self, ctx: ServerSubscribingContext) -> None:
        logger.info("subscribing server-side sub: %s", ctx)

    async def on_unsubscribed(self, ctx: ServerUnsubscribedContext) -> None:
        logger.info("unsubscribed from server-side sub: %s", ctx)

    async def on_publication(self, ctx: ServerPublicationContext) -> None:
        logger.info("publication from server-side sub: %s", ctx.pub.data)
        await handle_message(ctx.pub.data)

    async def on_join(self, ctx: ServerJoinContext) -> None:
        logger.info("join in server-side sub: %s", ctx)

    async def on_leave(self, ctx: ServerLeaveContext) -> None:
        logger.info("leave in server-side sub: %s", ctx)


async def handle_message(message):
    """Callback function to handle messages."""
    logger.info(f"Received message: {message}")


async def reconnect_client(client, max_retries=3, delay=5):
    for attempt in range(max_retries):
        try:
            await client.connect()
            logger.info("Reconnected to Centrifuge server")
            return client
        except Exception as e:
            logging.error(f"Reconnect attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(delay)
    raise RuntimeError(
        "Failed to reconnect to Centrifuge server after multiple attempts"
    )


async def publish_with_retry(sub, data, retries=3):
    for attempt in range(retries):
        try:
            await sub.publish(data=data)
            break
        except CentrifugeError as e:
            logging.error(f"Publish attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(2)
            else:
                raise


async def graceful_shutdown(client):
    try:
        await client.disconnect()
    except Exception as e:
        logging.error(f"Error during disconnection: {e}")


class SubscriptionEventLoggerHandler(SubscriptionEventHandler):

    def __init__(self,  stop_event):
        self.stop_event = stop_event

    async def on_subscribing(self, ctx: SubscribingContext) -> None:
        logging.info("subscribing: %s", ctx)

    async def on_subscribed(self, ctx: SubscribedContext) -> None:
        logging.info("subscribed: %s", ctx)

    async def on_unsubscribed(self, ctx: UnsubscribedContext) -> None:
        logging.info("unsubscribed: %s", ctx)

    async def on_publication(self, ctx: PublicationContext) -> None:
        print("publication: %s", ctx.pub.data)
        result = ctx.pub.data
        type = result.get("type")
        verify = result.get("verify") # 1: client 2: server 
        if type == "IP_ADDRESS":
            ip_address = result["data"]
            channel = self.sub.channel

            computeExisted, typeExisted = await check_compute_verify(
                ip_address=ip_address, infrastructure_id=channel
            )

            try:
                publish_message(
                    self.sub.channel,
                    {
                        "type": "COMPUTE_EXISTED",
                        "data": f"{computeExisted}",
                        "type_existed": f"{typeExisted}",
                    },
                    prefix=True,
                )

                print("Published verification result to the channel.")
            except Exception as e:
                logging.error("Error during publish: %s", e)
        if type == "SERVER_INFO" and verify == "2":
            config = result.get("data")[0]
            channel = self.sub.channel
            await update_server_info(channel, config)
            return
        if type == "GPU" and verify == 2:
            gpus = result.get('data')
            channel = self.sub.channel
            if gpus[0].get("uuid"):
                await update_compute_gpus(channel, gpus)  
            return

        if type == "DOCKER" and verify == "2":
            channel = self.sub.channel
            # run install compute self host
            await handle_install_compute(channel)
            return
        if type == "COMPUTE_TYPE" and verify == 2:
            channel = self.sub.channel
            type = result.get("data")
            await handle_service_type(channel, type)
            return
            # type (1: model-training, 2: storage, 3: labeling-tool)
        if type == "CUDA" and verify == "2":
            channel = self.sub.channel
            data = result.get("data")
            await handle_cuda(channel, data)
            return
        if type == "Fail":
            data = result.get("data")
            channel = self.sub.channel
            await handle_fail(data, channel)

    async def on_join(self, ctx: JoinContext) -> None:
        logging.info("join: %s", ctx)

    async def on_leave(self, ctx: LeaveContext) -> None:
        logging.info("leave: %s", ctx)

    async def on_error(self, ctx: SubscriptionErrorContext) -> None:
        logging.error("subscription error: %s", ctx)
        self.stop_event.set()

    async def publish_with_retry(self, data, retries=1):
        for attempt in range(retries):
            try:
                await self.sub.publish(data=data, timeout=120)
                break
            except ClientDisconnectedError as e:
                logging.error("Publish attempt %d failed due to client disconnection: %s", attempt + 1, e)
                await self.reconnect_or_retry()
            except Exception as e:
                logging.error("Publish attempt %d failed: %s", attempt + 1, e)
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    raise

    async def reconnect_or_retry(self):
        try:
            await self.client.connect()  # Reconnect the client
            print("Reconnected to Centrifuge server")
        except Exception as e:
            logging.error("Reconnection attempt failed: %s", e)


async def handle_fail(data, channel):
    from compute_marketplace.models import History_Rent_Computes
    from compute_marketplace.self_host import update_notify_install
    import threading
    try:
        # Wrap the ORM query to make it asynchronous
        history_instance = await sync_to_async(
            lambda: History_Rent_Computes.objects.filter(
                compute_marketplace__infrastructure_id=channel, deleted_at__isnull=True
            ).first()
        )()

        if history_instance:
            def thread_function():
                update_notify_install(
                    f"Error installing compute: {data}",
                    history_instance.account_id,
                    f"{data}",
                    history_instance.id,
                    "Install Compute",
                    "danger",
                )

            thread = threading.Thread(target=thread_function)
            thread.start()

           

    except Exception as e:
        logging.error("Error during publish: %s", e)


async def subscribe_to_channel(client, channel_name, stop_event):
    """Subscribe to a Centrifuge channel and handle messages."""
    sub = client.new_subscription(
        channel_name,
        events=SubscriptionEventLoggerHandler(stop_event),
    )
    await sub.subscribe()
    print(f"Subscribed to channel: {channel_name}")
    return sub


async def connect_to_server(user_id, stop_event):
    """Connect to the Centrifuge server and return the client instance."""
    client = Client(
        CENTRIFUGE_URL,
        get_token=generate_centrifuge_jwt(str(user_id)),
    )
    await client.connect()
    print("Connected to Centrifuge server")
    return client


async def send_log(sub, log_message):
    try:
        await sub.publish(data={"log": log_message})
    except CentrifugeError as e:
        print(e)
        logging.error("Error publish: %s", e)


def run_centrifuge(user_id, channel):
    stop_event = asyncio.Event()

    async def main():
        client, sub = setup_client(user_id, channel, stop_event)

        try:
            await reconnect_client(client)
            await sub.subscribe()

            # Wait for the stop_event to be set
            await stop_event.wait()
        except asyncio.CancelledError:
            logging.info("Shutting down...")
        finally:
            await graceful_shutdown(client)

    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(main())
        except Exception as e:
            print(f"Error in centrifuge run: {e}")
        finally:
            loop.stop()
            loop.close()

    run()
    # thread_start = threading.Thread(target=run)
    # thread_start.start()
    return stop_event


def stop_centrifuge(stop_event):
    stop_event.set()
