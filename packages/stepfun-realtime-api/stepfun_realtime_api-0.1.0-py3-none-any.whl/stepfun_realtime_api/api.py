import json
import asyncio
import websockets
import os
from urllib.parse import urlparse, parse_qs, urlencode
from .event_handler import RealtimeEventHandler
from websockets.protocol import State

class RealtimeAPI(RealtimeEventHandler):
    def __init__(self, url=None, secret=None):
        super().__init__()
        self.ws: websockets.ClientConnection = None

        if not url:
            url = "wss://api.stepfun.com/v1/realtime"
        if not secret:
            raise ValueError("API secret is required.")
        self.url = url
        self.secret = secret

    def is_connected(self):
        return self.ws is not None and self.ws.state == State.OPEN
    
    async def connect(self, model="step-1o-audio"):
        if self.is_connected():
            print("Already connected to WebSocket.")
            return
        
        # 构建URL
        url_parts = urlparse(self.url)
        query_params = parse_qs(url_parts.query)
        query_params["model"] = [model]
        url = f"{url_parts.scheme}://{url_parts.netloc}{url_parts.path}?{urlencode(query_params, doseq=True)}"
        
        # 准备连接
        headers = {"authorization": f"Bearer {self.secret}"}

        # 处理代理
        proxy = os.environ.get("http_proxy")
        extra_opts = {}
        if proxy:
            import ssl
            ssl_context = ssl.create_default_context()
            if url.startswith("wss:"):
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            extra_opts["ssl"] = ssl_context
            extra_opts["proxy"] = proxy  # 注意: 在Python中使用代理需要更多配置，这里简化处理
        try:
            # self.ws = await websockets.connect(url, additional_headers=headers, **extra_opts)
            ws = await websockets.connect(url, additional_headers=headers, **extra_opts)
            self.ws = ws

            # 设置消息处理
            asyncio.create_task(self._message_handler())
        except Exception as e:
            raise Exception(f"WebSocket connection error: {e}")
    
    async def _message_handler(self):
        try:
            async for message in self.ws:
                data = json.loads(message)
                self.dispatch(f"server.{data['type']}", data)
                self.dispatch("server.*", data)
        except Exception as e:
            if self.ws:
                await self.ws.close()
            self.ws = None
            self.dispatch("error", {"error": True, "message": str(e)})
        finally:
            if self.ws:
                code = 1000
                reason = "Client disconnected"
                await self.ws.close(code, reason)
                self.ws = None
                self.dispatch("close", {"error": False, "message": f"WebSocket closed with code {code} and reason: {reason}"})
    
    async def disconnect(self):
        if not self.is_connected():
            return
        
        await self.ws.close()
        self.ws = None
    
    async def send(self, event):
        if not self.is_connected():
            raise Exception("WebSocket is not connected.")
        
        if not event.get("event_id"):
            import time
            import random
            import string
            timestamp = int(time.time() * 1000)
            random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            event["event_id"] = f"evt_{timestamp}_{random_str}"
        
        try:
            await self.ws.send(json.dumps(event))
            self.dispatch(f"client.{event['type']}", event)
            self.dispatch("client.*", event)
        except Exception as e:
            print(f"Error sending message: {e}")
            self.dispatch("error", {"error": True, "message": str(e)})