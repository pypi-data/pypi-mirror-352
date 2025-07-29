import base64
from typing import Dict, Any, Optional, Union, Callable, overload, Literal
from .api import RealtimeAPI
from .event import (
    ClientEventType, ServerEventType, LocalEventType, SessionType,
    ServerRealtimeEvent, ClientRealtimeEvent,
    # 具体的服务器事件类型
    ServerSessionCreated, ServerSessionUpdated, ServerConversationItemCreated,
    ServerConversationItemDeleted, ServerConversationItemTruncated,
    ServerConversationItemInputAudioTranscriptionCompleted,
    ServerConversationItemInputAudioTranscriptionDelta,
    ServerInputAudioBufferSpeechStarted, ServerInputAudioBufferSpeechStopped,
    ServerInputAudioBufferCommitted, ServerInputAudioBufferCleared,
    ServerResponseCreated, ServerResponseDone, ServerResponseOutputItemAdded,
    ServerResponseOutputItemDone, ServerResponseContentPartAdded,
    ServerResponseContentPartDone, ServerResponseAudioDelta,
    ServerResponseAudioDone, ServerResponseAudioTranscriptDelta,
    ServerResponseAudioTranscriptDone
)
from .conversation import RealtimeConversation, ServerItemType

class RealtimeClient:
    def __init__(self, url=None, secret=None):
        self.api = RealtimeAPI(url=url, secret=secret)
        self.conversation = RealtimeConversation()
        self.session: SessionType = {
            'id': '',
            'model': 'step-1o-audio',
            'modalities': ['text', 'audio'],
            'instructions': '',
            'input_audio_format': 'pcm16',
            'output_audio_format': 'pcm16',
            'voice': 'jingdiannvsheng',
            'built_in_tools': ['web_search'],
            'threshold': None,
            'turn_detection': {'type': 'server_vad'},
            'max_response_output_length': 4096
        }
        self.audio_buffer = bytearray()
        self.session_created = False
        
        # 注册会话创建事件处理器
        self.api.on("server." + ServerEventType.SESSION_CREATED, self._handle_session_created)
        self._register_api_handler()
    
    def _handle_session_created(self, event):
        self.session['id'] = event["session"]["id"]
        self.session_created = True
    
    def get_conversation(self):
        return self.conversation
    
    def cancel_response(self):
        self.api.send({"type": ClientEventType.RESPONSE_CANCEL})
    
    async def create_response(self):
        if not self.api.is_connected():
            raise Exception("WebSocket is not connected.")
        
        if not self.session['turn_detection'] or self.session['turn_detection'].get("type") != "server_vad":
            await self.api.send({"type": ClientEventType.INPUT_AUDIO_BUFFER_COMMIT})
            self.conversation.set_current_input_audio(self.audio_buffer)
            self.audio_buffer = bytearray()  # Reset buffer after dispatching
        
        await self.api.send({"type": ClientEventType.RESPONSE_CREATE})
    
    async def append_input_audio(self, arr):
        if not arr or len(arr) == 0:
            return
        
        buffer_arr = bytearray(arr)
        event = {
            "type": ClientEventType.INPUT_AUDIO_BUFFER_APPEND,
            "audio": base64.b64encode(buffer_arr).decode('utf-8')
        }
        await self.api.send(event)
        self.audio_buffer.extend(buffer_arr)
    
    async def send_user_message(self, contents):
        if contents:
            event = {
                "type": ClientEventType.CONVERSATION_ITEM_CREATE,
                "item": {
                    "content": contents,
                    "type": "message", 
                    "role": "user"
                }
            }
            await self.api.send(event)
        
        await self.create_response()
    
    async def delete_item(self, item_id):
        await self.api.send({
            "type": ClientEventType.CONVERSATION_ITEM_DELETE,
            "item_id": item_id
        })
    
    async def wait_for_session_created(self):
        if self.session_created:
            return self.session
        
        event = await self.api.wait_for_next("server." + ServerEventType.SESSION_CREATED)
        return event["session"]
    
    async def wait_for_next_item(self):
        event = await self.api.wait_for_next(LocalEventType.CONVERSATION_ITEM_APPENDED)
        if event:
            return event
        return None
    
    async def wait_for_next_item_done(self):
        event = await self.api.wait_for_next(LocalEventType.CONVERSATION_ITEM_COMPLETED)
        if event:
            return event
        return None
    
    async def update_session(
        self,
        id: Optional[str] = None,
        model: Optional[str] = None,
        modalities: Optional[list] = None,
        instructions: Optional[str] = None,
        input_audio_format: Optional[str] = None,
        output_audio_format: Optional[str] = None,
        voice: Optional[str] = None,
        built_in_tools: Optional[list] = None,
        threshold: Optional[float] = None,
        turn_detection: Optional[Dict] = None,
        max_response_output_length: Optional[int] = None,
        **additional_params
    ):
        """更新会话配置
        
        Args:
            id: 会话ID
            model: 模型名称 (默认: "step-1o-audio")
            modalities: 模态列表 (默认: ["text", "audio"])
            instructions: 系统指令
            input_audio_format: 输入音频格式 (默认: "pcm16")
            output_audio_format: 输出音频格式 (默认: "pcm16")
            voice: 语音 (默认: "jingdiannvsheng")
            built_in_tools: 内置工具 (默认: ["web_search"])
            turn_detection: 轮次检测配置 (默认: {"type": "server_vad"})
            max_response_output_length: 最大响应长度 (默认: 4096)
            additional_params: 其他可能的会话参数
        """
        # Build session updates dictionary from provided parameters
        session_updates = {}
        
        # Add all non-None parameters to the updates dictionary
        local_vars = locals()
        for param in ['model', 'modalities', 'instructions', 'input_audio_format',
                      'output_audio_format', 'voice', 'built_in_tools',
                      'turn_detection', 'max_response_output_length']:
            if param in local_vars and local_vars[param] is not None:
                session_updates[param] = local_vars[param]
        
        # Add any additional parameters
        session_updates.update(additional_params)
        
        if self.api.is_connected():
            await self.api.send({
                "type": ClientEventType.SESSION_UPDATE,
                "session": session_updates
            })
        
        # 更新会话设置
        for key, value in session_updates.items():
            self.session[key] = value
    
    def get_session_id(self):
        return self.session['id']
    
    async def connect(self):
        await self.api.connect(model=self.session['model'])
        await self.update_session(dict(self.session))
    
    async def disconnect(self):
        self.session_created = False
        if self.api.is_connected():
            await self.api.disconnect()
        self.conversation.clear()
    
    def _register_api_handler(self):
        def handle_event(event_type):
            self.api.on("server." + event_type, lambda e: self.conversation.process_event(e))
        
        def handle_and_dispatch(event_type):
            def handler(e):
                ret = self.conversation.process_event(e)
                if ret and ret.get("item"):
                    self.api.dispatch("conversation.updated", ret)
            self.api.on("server." + event_type, handler)
        
        # 注册事件处理器
        handle_event(ServerEventType.RESPONSE_CREATED)
        handle_event(ServerEventType.RESPONSE_OUTPUT_ITEM_ADDED)
        handle_event(ServerEventType.RESPONSE_CONTENT_PART_ADDED)
        handle_event(ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED)
        
        # 特殊处理
        self.api.on("server." + ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED, 
                    lambda event: self.conversation.process_event(event, self.audio_buffer))
        
        self.api.on("server." + ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED,
                    lambda event: self.api.dispatch("interrupted", {}))
        
        # 对话项创建事件处理
        def handle_conversation_item_created(event):
            ret = self.conversation.process_event(event)
            if ret and ret.get("item"):
                self.api.dispatch("conversation.item.appended", event)
                if ret["item"].status == "completed":
                    self.api.dispatch("conversation.item.completed", event)
        
        self.api.on("server." + ServerEventType.CONVERSATION_ITEM_CREATED, handle_conversation_item_created)
        
        # 注册其他事件处理器
        handle_and_dispatch(ServerEventType.CONVERSATION_ITEM_DELETED)
        handle_and_dispatch(ServerEventType.CONVERSATION_ITEM_TRUNCATED)
        handle_and_dispatch(ServerEventType.RESPONSE_AUDIO_DELTA)
        handle_and_dispatch(ServerEventType.RESPONSE_TEXT_DELTA)
        handle_and_dispatch(ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DELTA)
        handle_and_dispatch(ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE)
        handle_and_dispatch(ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_DELTA)
        handle_and_dispatch(ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED)
        
        # 响应输出项完成事件处理
        def handle_response_output_item_done(event):
            ret = self.conversation.process_event(event)
            if ret and ret.get("item"):
                if ret["item"]["status"] == "completed":
                    self.api.dispatch(LocalEventType.CONVERSATION_ITEM_COMPLETED, event)
        
        self.api.on("server." + ServerEventType.RESPONSE_OUTPUT_ITEM_DONE, handle_response_output_item_done)
    
    # 使用 @overload 装饰器定义方法重载，对应 TypeScript 的函数重载
    @overload
    def on(self, event: Literal["server.*"], callback: Callable[[Dict[str, Any]], None]) -> None: ...
    
    @overload  
    def on(self, event: Literal["client.*"], callback: Callable[[Dict[str, Any]], None]) -> None: ...
    
    @overload
    def on(
        self, 
        event: LocalEventType, 
        callback: Callable[[Dict[str, Any]], None]  # LocalEventType with ServerItemType item
    ) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.SESSION_CREATED], callback: Callable[[ServerSessionCreated], None]) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.SESSION_UPDATED], callback: Callable[[ServerSessionUpdated], None]) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.CONVERSATION_ITEM_CREATED], callback: Callable[[ServerConversationItemCreated], None]) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED], callback: Callable[[ServerConversationItemInputAudioTranscriptionCompleted], None]) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_DELTA], callback: Callable[[ServerConversationItemInputAudioTranscriptionDelta], None]) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED], callback: Callable[[ServerInputAudioBufferSpeechStarted], None]) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED], callback: Callable[[ServerInputAudioBufferSpeechStopped, Optional[bytes]], None]) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.INPUT_AUDIO_BUFFER_COMMITTED], callback: Callable[[ServerInputAudioBufferCommitted], None]) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.INPUT_AUDIO_BUFFER_CLEARED], callback: Callable[[ServerInputAudioBufferCleared], None]) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.CONVERSATION_ITEM_DELETED], callback: Callable[[ServerConversationItemDeleted], None]) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.CONVERSATION_ITEM_TRUNCATED], callback: Callable[[ServerConversationItemTruncated], None]) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.RESPONSE_AUDIO_DELTA], callback: Callable[[ServerResponseAudioDelta], None]) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.RESPONSE_AUDIO_DONE], callback: Callable[[ServerResponseAudioDone], None]) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.RESPONSE_CONTENT_PART_ADDED], callback: Callable[[ServerResponseContentPartAdded], None]) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.RESPONSE_CONTENT_PART_DONE], callback: Callable[[ServerResponseContentPartDone], None]) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DELTA], callback: Callable[[ServerResponseAudioTranscriptDelta], None]) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE], callback: Callable[[ServerResponseAudioTranscriptDone], None]) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.RESPONSE_OUTPUT_ITEM_ADDED], callback: Callable[[ServerResponseOutputItemAdded], None]) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.RESPONSE_OUTPUT_ITEM_DONE], callback: Callable[[ServerResponseOutputItemDone], None]) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.RESPONSE_CREATED], callback: Callable[[ServerResponseCreated], None]) -> None: ...
    
    @overload
    def on(self, event: Literal[ServerEventType.RESPONSE_DONE], callback: Callable[[ServerResponseDone], None]) -> None: ...
    
    def on(
        self,
        event: Union[
            ServerEventType, LocalEventType, ClientEventType, 
            Literal["server.*"], Literal["client.*"]
        ],
        callback: Callable[[Any, Optional[Any]], None]
    ) -> None:
        """注册事件处理器，对应 TypeScript 的 on 方法重载
        
        Args:
            event: 事件类型或通配符
            callback: 回调函数，接收事件数据和可选的额外参数
        """
        # 对应 TypeScript: if (Object.values(ServerEventType).includes(event as any))
        if isinstance(event, ServerEventType) or (isinstance(event, str) and event in [e.value for e in ServerEventType]):
            self.api.on("server." + event, callback)
            return
        
        # 对应 TypeScript: if (Object.values(ClientEventType).includes(event as any))  
        if isinstance(event, ClientEventType) or (isinstance(event, str) and event in [e.value for e in ClientEventType]):
            self.api.on("client." + event, callback)
            return
        
        # 对应 TypeScript: this.api.on(event, callback)
        self.api.on(event, callback)
    
    def off(
        self, 
        event: Union[LocalEventType, ServerEventType, ClientEventType, Literal["server.*"], Literal["client.*"]], 
        callback: Callable
    ) -> None:
        """取消注册事件处理器，对应 TypeScript 的 off 方法
        
        Args:
            event: 事件类型或通配符
            callback: 要移除的回调函数
        """
        # 对应 TypeScript: if (Object.values(ServerEventType).includes(event as any))
        if isinstance(event, ServerEventType) or (isinstance(event, str) and event in [e.value for e in ServerEventType]):
            self.api.off("server." + event, callback)
            return
        
        # 对应 TypeScript: if (Object.values(ClientEventType).includes(event as any))
        if isinstance(event, ClientEventType) or (isinstance(event, str) and event in [e.value for e in ClientEventType]):
            self.api.off("client." + event, callback)
            return
        
        # 对应 TypeScript: this.api.off(event, callback)
        self.api.off(event, callback)