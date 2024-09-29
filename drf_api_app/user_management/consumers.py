import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from datetime import datetime
from django.db.models import OuterRef, Subquery
import asyncio

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MachineDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        logger.info("WebSocket connection accepted.")
        await self.send_initial_data()

        # Start a task to periodically send updates
        self.update_task = asyncio.create_task(self.periodic_update())

    async def disconnect(self, close_code):
        logger.info("WebSocket connection closed.")
        #if hasattr(self, 'update_task'):
            #self.update_task.cancel()  # Cancel the update task when disconnected

    async def receive(self, text_data):
        logger.info(f"Received data: {text_data}")  # Log the received data
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        if message_type == 'authenticate':
            token = text_data_json['token']
            user = await self.get_user_from_token(token)
            if user:
                self.user = user
                logger.info("User authenticated.")
                await self.send_initial_data()
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Invalid token'
                }))
                logger.warning("Invalid token provided.")
        else:
            await self.handle_data_requests(message_type)

    async def handle_data_requests(self, message_type):
        if hasattr(self, 'user'):
            if message_type == 'get_machine_data':
                await self.send_machine_data()
            elif message_type == 'get_tool_data':
                await self.send_tool_data()
            elif message_type == 'get_axis_data':
                await self.send_axis_data()
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Unknown message type'
                }))
                logger.warning("Unknown message type received.")
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Not authenticated'
            }))
            logger.warning("Not authenticated user tried to send data.")

    @database_sync_to_async
    def get_user_from_token(self, token):
        from oauth2_provider.models import AccessToken
        try:
            return AccessToken.objects.get(token=token).user
        except Exception:
            return None

    @database_sync_to_async
    def get_latest_machine_data(self):
        from .models import Machine
        return list(Machine.objects.all().values())

    @database_sync_to_async
    def get_latest_tool_data(self):
        from .models import Tool
        return list(Tool.objects.filter(
            update_timestamp=Subquery(
                Tool.objects.filter(machine_id=OuterRef('machine_id'))
                .order_by('-update_timestamp')
                .values('update_timestamp')[:1]
            )
        ).values())[:-1]

    @database_sync_to_async
    def get_latest_axis_data(self):
        from .models import AxisData
        return list(AxisData.objects.filter(
            update_timestamp=Subquery(
                AxisData.objects.filter(axis_id=OuterRef('axis_id'))
                .order_by('-update_timestamp')
                .values('update_timestamp')[:1]
            )
        ).values())[:-1]

    async def send_machine_data(self):
        machine_data = await self.get_latest_machine_data()
        await self.send(text_data=json.dumps({
            'type': 'machine_data',
            'data': machine_data
        }))

    async def send_tool_data(self):
        tool_data = await self.get_latest_tool_data()
        serialized_data = self.serialize_data(tool_data)
        await self.send(text_data=json.dumps({
            'type': 'tool_data',
            'data': serialized_data
        }))

    async def send_axis_data(self):
        axis_data = await self.get_latest_axis_data()
        serialized_data = self.serialize_data(axis_data)
        await self.send(text_data=json.dumps({
            'type': 'axis_data',
            'data': serialized_data
        }))

    async def send_initial_data(self):
        await self.send_machine_data()
        await self.send_tool_data()
        await self.send_axis_data()

    async def periodic_update(self):
        while True:
            await self.send_machine_data()
            await self.send_tool_data()
            await self.send_axis_data()
            await asyncio.sleep(1)  # Adjust the frequency of updates as needed

    def serialize_data(self, data):
        if isinstance(data, list):
            return [self.serialize_data(item) for item in data]
        elif isinstance(data, dict):
            return {key: self.serialize_data(value) for key, value in data.items()}
        elif isinstance(data, datetime):
            return data.isoformat()  # Convert datetime to ISO 8601 string
        return data
