import asyncio
import logging
import json
import os
import time
from typing import Any, Optional

from websockets import connect as ws_connect
from websockets.client import WebSocketClientProtocol
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK, InvalidStatus
from neosphere.client_api import Message, NeosphereClient
from neosphere.contacts_handler import NeosphereAgentContactsClient
from neosphere.media_handler import NeosphereMediaClient
logger = logging.getLogger('neosphere').getChild(__name__)
import traceback

NEOSPHERE_DNS_NAME = "n10s.net"
class NeosphereAgent:
    """
    A client agent for the Neosphere network that manages WebSocket connections,
    message handling, and callback triggering for both human and AI messages.
    
    This class abstracts the logic required to:
    - Connect and authorize with the Neosphere server.
    - Process incoming messages and dispatch them via provided callbacks.
    - Handle reconnections and error states gracefully.
    
    Parameters:
        agent_share_id: Unique identifier for the agent.
        connection_code: Authentication code for establishing connection.
        client_name: The display name for the client.
        group_message_receiver: Callback to process group messages from human users.
        query_receiver: Callback to process queries from other AI agents.
        contacts: Initial contacts to use for message handling.
        **context: Additional context passed to callbacks.
    """
    app: Any
    ws: WebSocketClientProtocol

    def __init__(self, 
                 agent_share_id, 
                 connection_code, 
                 client_name, 
                 group_message_receiver, 
                 query_receiver,
                 contacts=[],
                 **context) -> None:
        self.agent_share_id = agent_share_id
        self.connection_code = connection_code
        self.client_name = client_name
        self.human_group_msg_callback = group_message_receiver
        self.ai_query_msg_callback = query_receiver
        self.reconnection_token = None
        self.context_to_forward = context
        self.http_url = None
        # query tracker is any simple key value structure the client will use to keep a track of queries sent and their responses received.
        # this allows the client to provide a blocking wait for a query response.
        self.query_tracker = {}
        self.neosphere_client = NeosphereClient(query_index=self.query_tracker, name=agent_share_id)
        self.recieved_pull_the_plug = False
        self.initial_contacts = contacts


    async def set_websocket(self, ws: WebSocketClientProtocol):
        self.ws = ws

    async def refresh_send_loop(self):
        """Sends a None message to the internal queue to trigger an iteration in the ws_send_loop."""
        await self.neosphere_client.send(None)
    
    async def wait_for_outgoing_message(self):
        return await self.neosphere_client.get()

    async def before_connect(self):
        pass

    async def attempt_reconnect(self):
        pass

    async def on_connect(self):
        pass
    
    async def on_authorize(self, ignore_token=False):
        if self.reconnection_token and not ignore_token:
            logger.info("Restarting agent connection with connection token")
            await self.neosphere_client.send_token_to_reconnect(self.reconnection_token, self.agent_share_id)
        else:
            logger.info("Authorizing agent connection with connection code")
            await self.neosphere_client.send_token_request(self.connection_code, self.agent_share_id, self.client_name)
    
    async def before_disconnect(self):
        logger.info('before_disconnect')

    async def on_disconnect(self):
        logger.info('on_disconnect')
    
    def set_http_requests_address(self, http_url: str):
        self.http_url = http_url
    
    def get_self_info(self):
        self_con = None
        if self.neosphere_client.contacts:
            self_con = self.neosphere_client.contacts.get_or_add_self_contact()
        if not self_con:
            return {
                'authorized': True if self.reconnection_token else False,
            }
        self_con['authorized'] = True if self.reconnection_token else False
        return self_con
    
    async def on_message(self, message: str):
        msg = Message.from_json(message)
        logger.debug(f"Received processed message: {msg.to_dict()}")
        try:
            if msg.is_pull_the_plug():
                logger.info("Received pull the plug signal. Closing connection.")
                self.recieved_pull_the_plug = True
                await self.refresh_send_loop()
            if msg.token:
                self.reconnection_token = msg.token
                self.neosphere_client.register_media_handler(NeosphereMediaClient(self.reconnection_token, "/tmp/neosphere_media", self.http_url))
                self.neosphere_client.register_contacts_handler(NeosphereAgentContactsClient(self.reconnection_token, self.initial_contacts, self.http_url, self.agent_share_id))
                # initialize contacts
                # Contacts().initial_public_contacts(public_contacts)
                logger.info(f"Received a connection token. Registered media handler and fetched ({self.neosphere_client.contacts.get_contact_count()}) contacts.")
            if msg.is_err:
                logger.error(f"Received error message.")
            if msg.group_id:
                if not msg.is_err:
                    logger.info('Message is group message')
                    await self.human_group_msg_callback(msg, self.neosphere_client, **self.context_to_forward)
                else:
                    logger.error(f"(Group={msg.group_id}) Error from: {msg.from_id}. Error: {msg.text}")
            elif msg.query_id:
                if msg.is_err:
                    if msg.from_id == "sys":
                        logger.error(f"Message is a Neosphere system error on query ID: {msg.query_id} - {msg.text}. Will not record this response as it is a system error, will let the query caller timeout.")
                    else:
                        logger.error(f"Message is an error on query ID: {msg.query_id}")
                        await self.neosphere_client._record_query_response_recvd(msg.query_id, msg)
                elif msg.is_resp:
                    logger.info('Message is a query resp')
                    await self.neosphere_client._record_query_response_recvd(msg.query_id, msg)
                else:
                    logger.info('Message is a query from another agent')
                    await self.ai_query_msg_callback(msg, self.neosphere_client, **self.context_to_forward)
        except Exception as e:
            logger.exception(f"Error while processing message: {e}")
            return


class NeosphereAgentRunner(object):
    """
    Manages the lifecycle of a NeosphereAgent's WebSocket connection.
    
    This class handles:
    - Establishing and cleaning up Neosphere connections.
    - Authorizing the agent after connecting.
    - Running separate asynchronous loops for sending and receiving messages.
    - Retrying connection attempts up to a defined maximum.
    
    Parameters:
        agent: An instance of NeosphereAgent to run.
        url: Optional URL for the Neosphere server.
    """
    
    hostname: str
    agent: NeosphereAgent
    ws: WebSocketClientProtocol

    # states
    _is_connected: bool
    _authorize_called: bool
    _listening: bool
    _auth_with_conn_code: bool
    _retry_count: int
    _err_state: bool
    MAX_RETRIES = 50

    def __init__(self, agent: NeosphereAgent, server_hostname: str = None, dump_connection_status_path: str = None) -> None:
        self.agent = agent
        self.hostname = server_hostname or NEOSPHERE_DNS_NAME
        self.agent.set_http_requests_address(self._get_url(ws=False))
        self._authorize_called = False
        self._listening = False
        self._is_connected = False
        self._auth_with_conn_code = True
        self._retry_count = 0
        self._err_state = False
        self.recv_active = []
        self.send_active = []
        self.GAP_BETWEEN_RETRIES_SEC = 2
        self.dump_connection_status_path = dump_connection_status_path
        self._status_task = None
        self._should_stop = False

    def slowdown_retries(self):
        self.GAP_BETWEEN_RETRIES_SEC = 10
    def reset_retry_speed(self):
        self.GAP_BETWEEN_RETRIES_SEC = 2
    
    def _get_url(self, ws=True):
            if self.hostname.startswith("localhost"):
                if ws:
                    proto = "ws://"
                else:
                    proto = "http://"
            else:
                if ws:
                    proto = "wss://"
                else:
                    proto = "https://"
            return f"{proto}{self.hostname}/"

    def _clean_state(self):
        self._is_connected = False
        self._listening = False
        self._err_state = False

    async def connect(self):
        self._clean_state()
        await self.agent.before_connect()
        try:
            self.ws = await ws_connect(self._get_url()+"stream/ai")
        except ConnectionRefusedError as e:
            logger.error(f'Connection refused: {e}')
            return
        except asyncio.TimeoutError as e:
            logger.error(f'Timeout when connecting: {e}')
            return
        except OSError as e:
            logger.error(f'OS error: {e}')
            self.slowdown_retries()
            return
        except InvalidStatus as e:
            logger.error(f'Invalid status: {e}')
            self.slowdown_retries()
            return
        await self.agent.set_websocket(self.ws)
        await self.agent.on_connect()
        self.reset_retry_speed()
        self._is_connected = True
    
    async def authorize(self):
        if not self._is_connected:
            logger.error("Cannot authorize as not connected")
            return
        await self.agent.on_authorize(ignore_token=self._auth_with_conn_code)
        # this only gets set from the recv_loop, reset it once it's used
        self._auth_with_conn_code = False
        self._authorize_called = True

    async def disconnect(self):
        self._is_connected = False
        await self.agent.before_disconnect()
        await self.ws.close()
        await self.agent.on_disconnect()

    async def send(self, message: str) -> Any:
        await self.ws.send(message)

    async def ws_recv_message(self) -> Optional[str]:
        try:
            return await asyncio.wait_for(self.ws.recv(), 1)

        except asyncio.TimeoutError:
            return None

    async def ws_recv_loop(self):
        while self._is_connected:
            try:
                if not self._listening:
                    self._listening = True 
                message = await self.ws.recv()
            except ConnectionClosedError as e:
                logger.error(f'Recieve loop closed with error: {e.reason}, code: {e.code}')
                if e.code == 4010:
                    # this will cause the agent to reauthorize with the connection code
                    # useful when code is pinned, auth will still fail if code also expired on the app
                    self._auth_with_conn_code = True
                self._err_state = True
                # sending None triggers an iteration in the send loop
                await self.agent.refresh_send_loop()
                break
            except ConnectionClosedOK as e:
                logger.info(f'Recieve loop closed without error: {e}')
                # this will prevent retrying to open the connection.
                self._retry_count = self.MAX_RETRIES + 1
                self._is_connected = False
                # sending None triggers an iteration in the send loop
                await self.agent.refresh_send_loop()
                break
            if message is None:
                continue

            # call on_message async function as a task and keep moving
            # await self.reciever.on_message(message)
            task = asyncio.create_task(self.agent.on_message(message))
            self.recv_active.append(task)
        logger.info(f"Recieve loop ending. Will wait for all incoming messages ({len(self.recv_active)}) to finish.")
        if len(self.recv_active) > 0:
            await asyncio.gather(*self.recv_active)
        logger.info(f"Recieve loop ended.")

    async def ws_send_loop(self):
        while self._is_connected:
            if not self._listening:
                # sleep till listening is enabled
                await asyncio.sleep(0.2)
                continue
            if self._err_state:
                logger.debug("Send loop closed as error state is set")
                break
            if self.agent.recieved_pull_the_plug:
                logger.warning("Send loop closed as we recieved the 'Pull the Plug' signal")
                break
            # then listen to the message queue
            message = await self.agent.wait_for_outgoing_message()
            if message is None:
                continue
            # logger.debug(f"Sending message: {message['cmd']}")
            logger.debug(f"Sending message: {message}")
            task = asyncio.create_task(self.ws.send(json.dumps(message)))
            self.send_active.append(task)
        logger.info(f"Send loop ending. Will wait for all outgoing messages ({len(self.send_active)}) to finish.")
        if len(self.send_active) > 0:
            await asyncio.gather(*self.send_active)
        logger.info(f"Send loop ended.")
    
    async def dump_connection_status(self):
        logger.info(f"Starting connection status dump loop")
        def dump_connection_status():
            self_info = self.agent.get_self_info()
            dump = {
                'connected': self._is_connected,
                'listening': self._listening,
                'err_state': self._err_state,
            }
            # merge dump and self_info
            dump.update(self_info)
            dump['ts'] = time.time()
            # logger.info(f"Connection status: {dump}")
            dir_path = os.path.dirname(self.dump_connection_status_path)
            if dir_path: # Ensure directory exists only if a path is provided
                os.makedirs(dir_path, exist_ok=True)
            with open(self.dump_connection_status_path, 'w') as f:
                json.dump(dump, f, indent=2)
        while not self._should_stop and self.dump_connection_status_path:
            try:
                dump_connection_status()
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                logger.info("Connection Status dump task cancelled after one last dump...")
                dump_connection_status()
                break
            except Exception as e:
                logger.error(f"Error in status dump: {e}")
                if self._should_stop:
                    break
                await asyncio.sleep(1)

    async def run(self):
        # Start the status dump loop independently if path is provided
        if self.dump_connection_status_path:
            self._status_task = asyncio.create_task(self.dump_connection_status())

        try:
            while self._retry_count <= self.MAX_RETRIES:
                await self.connect()
                await self.authorize()
                # Only gather the send and receive loops
                await asyncio.gather(self.ws_recv_loop(), self.ws_send_loop())
                # wait for the above coroutines to finish - indicates end
                logger.info("Receiver and Sender loops ended.")
                if self._retry_count >= self.MAX_RETRIES:
                    logger.error("Max retries reached. Exiting.")
                    break
                else:
                    logger.error(f"Retrying ({self._retry_count}/{self.MAX_RETRIES}) connection in {self.GAP_BETWEEN_RETRIES_SEC} seconds.")
                    await asyncio.sleep(self.GAP_BETWEEN_RETRIES_SEC)
                self._retry_count = self._retry_count + 1
        finally:
            # Signal all tasks to stop
            self._should_stop = True
            # Cancel the status dump task if it was started
            if self._status_task and not self._status_task.done():
                logger.info("Cancelling status dump task")
                self._status_task.cancel()
                try:
                    await self._status_task
                except asyncio.CancelledError:
                    logger.info("Connection Status dump task cancelled")
                    pass
                except Exception as e:
                    logger.error(f"Error in status dump: {e}")
            logger.info("Exiting Neosphere Agent Runner")

    def asyncio_run(self):
        try:
            asyncio.run(self.run())
        except KeyboardInterrupt:
            logger.info('Correct exit')
        except Exception as e:
            logger.error(f"Error in asyncio_run: {e}")
            raise
        finally:
            # Ensure all tasks are cancelled
            self._should_stop = True
            loop = asyncio.get_event_loop()
            if loop.is_running():
                for task in asyncio.all_tasks(loop):
                    if not task.done():
                        task.cancel()
