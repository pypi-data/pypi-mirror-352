import base64
from typing import Dict, List, Optional, Any, Union, Callable, Literal, TypedDict, Generic, TypeVar
from .event import ServerEventType, ServerRealtimeEvent, ItemType

T = TypeVar('T', bound=str)

class ServerItemType(Generic[T]):
    """服务器项目类型，对应 TypeScript 的 ServerItemType<objectName extends string>"""
    def __init__(self, object_name: T):
        self.id: str = ""
        self.object: T = object_name
        self.type: Literal["message"] = "message"
        self.status: Literal["completed", "failed", "in_progress", "incomplete"] = "incomplete"
        self.role: Literal["user", "assistant", "system"] = "user"
        self.content: List[Union[
            Dict[Literal["type", "text"], Union[Literal["text", "input_text"], str]],
            Dict[Literal["type", "audio"], Union[Literal["audio"], bytes]],
            Dict[Literal["type", "transcript"], Union[Literal["transcript"], str]]
        ]] = []

class ResponseType:
    """响应类型，对应 TypeScript 的 ResponseType"""
    def __init__(self):
        self.id: str = ""
        self.output_ids: List[str] = []

class QueuedSpeechItem(TypedDict):
    """排队的语音项目类型"""
    audio_start_ms: int
    audio_end_ms: int
    audio: Optional[bytes]

class QueuedTranscriptItem(TypedDict):
    """排队的转写项目类型"""
    transcript: str

class EventProcessorResult(TypedDict):
    """事件处理器结果类型"""
    item: Optional[ItemType]
    delta: Any

class RealtimeConversation:
    """实时对话管理类，对应 TypeScript 的 RealtimeConversation"""
    def __init__(self):
        # 使用 Map 对应的 Dict 结构
        self.response_map: Dict[str, ResponseType] = {}
        self.response_items: List[ResponseType] = []
        self.item_map: Dict[str, ItemType] = {}
        self.items: List[ItemType] = []
        
        # 手动提交音频的时候，current_input_audio 保存该音频临时引用
        # 对应 TypeScript 的 Buffer，使用 bytes 类型
        self.current_input_audio: Optional[bytes] = None
        
        # 用户输入的音频片段的引用，使用更精确的类型定义
        self.queued_speech_items: Dict[str, QueuedSpeechItem] = {}
        self.queued_transcript_items: Dict[str, QueuedTranscriptItem] = {}
        
        # 事件处理器映射，对应 TypeScript 的 eventProcessor
        # 使用 Partial 对应的 Optional 值类型
        self.event_processor: Dict[ServerEventType, Callable[
            ['RealtimeConversation', Dict[str, Any], Any], Optional[EventProcessorResult]
        ]] = {
            ServerEventType.CONVERSATION_ITEM_CREATED: conversation_item_created,
            ServerEventType.CONVERSATION_ITEM_DELETED: conversation_item_deleted,
            ServerEventType.CONVERSATION_ITEM_TRUNCATED: conversation_item_truncated,
            
            ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED: input_audio_buffer_speech_started,
            ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED: input_audio_buffer_speech_stopped,
            
            ServerEventType.RESPONSE_CREATED: response_created,
            ServerEventType.RESPONSE_OUTPUT_ITEM_ADDED: response_output_item_added,
            ServerEventType.RESPONSE_OUTPUT_ITEM_DONE: response_output_item_done,
            
            ServerEventType.RESPONSE_CONTENT_PART_ADDED: response_content_part_added,
            ServerEventType.RESPONSE_CONTENT_PART_DONE: response_content_part_done,
            
            ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED: 
                conversation_item_input_audio_transcription_completed,
            
            ServerEventType.RESPONSE_AUDIO_DELTA: response_audio_delta,
            ServerEventType.RESPONSE_AUDIO_DONE: response_audio_done,
            
            ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DELTA: response_audio_transcript_delta,
            ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE: response_audio_transcript_done,
        }
    
    def clear(self) -> None:
        """清空对话内容"""
        self.item_map.clear()
        self.items = []
    
    def process_event(self, event: Dict[str, Any], extra: Optional[Any] = None) -> Optional[EventProcessorResult]:
        """处理事件，对应 TypeScript 的 processEvent
        
        Args:
            event: 服务器事件，对应 ServerRealtimeEvent<any>
            extra: 额外参数，可选
            
        Returns:
            处理结果，包含 item 和 delta 信息，或 None
        """
        processor = self.event_processor.get(event["type"])
        if not processor:
            # 对应 TypeScript 中的注释警告
            # console.warn(`No processor found for event type: ${event.type}`)
            return None
        
        result = processor(self, event, extra)
        return result
    
    def set_current_input_audio(self, audio: bytes) -> None:
        """设置当前输入音频，对应 TypeScript 的 setCurrentInputAudio
        
        Args:
            audio: 音频数据 (对应 TypeScript 的 Buffer)
        """
        self.current_input_audio = audio

# 事件处理函数实现，精确对应 TypeScript 版本

def conversation_item_created(
    conv: RealtimeConversation, 
    event: Dict[str, Any], 
    extra: Optional[Any] = None
) -> Optional[EventProcessorResult]:
    """对应 TypeScript 的 conversationItemCreated 函数"""
    print(event)
    if event.get("item", {}).get("id") not in conv.item_map:
        # 创建新的 ItemType，对应 TypeScript 的 item: ItemType 初始化
        item = ItemType()
        item["id"] = event["item"]["id"]
        item["status"] = event["item"]["status"]
        item["type"] = event["item"]["type"]
        item["role"] = event["item"]["role"]
        item["content"] = event["item"]["content"]
        # 对应 TypeScript: formatted: { text: "", audio: Buffer.alloc(0), transcript: "" }
        item["formatted"] = {
            "text": "", 
            "audio": b"",  # 使用 bytes 对应 Buffer.alloc(0)
            "transcript": ""
        }
        
        # 处理内容，对应 TypeScript 的 for (const content of event.item.content) 循环
        for content in event["item"]["content"]:
            if content["type"] in ["text", "input_text"]:
                item["formatted"]["text"] += content.get("text", "")
        # 如果已经有转写文本，直接使用
        if event["item"]["id"] in conv.queued_transcript_items:
            item["formatted"]["transcript"] = conv.queued_transcript_items[event["item"]["id"]]["transcript"]
            del conv.queued_transcript_items[event["item"]["id"]]

        # 对应 TypeScript 的条件判断逻辑
        if item["type"] == "message":
            if item["role"] == "user":
                item["status"] = "completed"
                if conv.current_input_audio:
                    item["formatted"]["audio"] = conv.current_input_audio
                    conv.current_input_audio = None
                elif event["item"]["id"] in conv.queued_speech_items:
                    if conv.queued_speech_items[event["item"]["id"]].get("audio"):
                        item["formatted"]["audio"] = conv.queued_speech_items[event["item"]["id"]]["audio"]
            else:
                item["status"] = "in_progress"

        conv.item_map[event["item"]["id"]] = item
        conv.items.append(item)
    
    # 对应 TypeScript: return null
    return None

def input_audio_buffer_speech_started(
    conv: RealtimeConversation, 
    event: Dict[str, Any], 
    extra: Optional[Any] = None
) -> Optional[EventProcessorResult]:
    """对应 TypeScript 的 inputAudioBufferSpeechStarted 函数"""
    item_id = event["item_id"]
    conv.queued_speech_items[item_id] = {
        "audio_start_ms": event["audio_start_ms"],
        "audio_end_ms": 0,
        "audio": None
    }
    # 对应 TypeScript: return { item: null, delta: null }
    return {"item": None, "delta": None}

def input_audio_buffer_speech_stopped(
    conv: RealtimeConversation, 
    event: Dict[str, Any], 
    input_buffer: Optional[bytes]
) -> Optional[EventProcessorResult]:
    """对应 TypeScript 的 inputAudioBufferSpeechStopped 函数
    
    Args:
        conv: 对话实例
        event: 事件数据
        input_buffer: 输入缓冲区 (对应 TypeScript 的 Buffer 参数)
    """
    item_id = event["item_id"]
    if item_id not in conv.queued_speech_items:
        conv.queued_speech_items[item_id] = {
            "audio_start_ms": event["audio_end_ms"],
            "audio_end_ms": 0,
            "audio": None
        }
    
    conv.queued_speech_items[item_id]["audio_end_ms"] = event["audio_end_ms"]
    
    if input_buffer:
        item = conv.queued_speech_items[item_id]
        # 对应 TypeScript: Math.floor((item.audio_start_ms * 24_000) / 1000)
        start_index = int((item["audio_start_ms"] * 24_000) / 1000)
        end_index = int((item["audio_end_ms"] * 24_000) / 1000)
        # 对应 TypeScript: inputBuffer.subarray(startIndex, endIndex)
        item["audio"] = input_buffer[start_index:end_index]
    
    # 对应 TypeScript: return null
    return None

def response_created(
    conv: RealtimeConversation, 
    event: Dict[str, Any], 
    extra: Optional[Any] = None
) -> Optional[EventProcessorResult]:
    """对应 TypeScript 的 responseCreated 函数"""
    if event["response"]["id"] not in conv.response_map:
        # 对应 TypeScript: const resp = { id: event.response.id, output_ids: [] }
        resp = ResponseType()
        resp.id = event["response"]["id"]
        resp.output_ids = []
        conv.response_map[resp.id] = resp
        conv.response_items.append(resp)
    
    return None

def response_output_item_added(
    conv: RealtimeConversation, 
    event: Dict[str, Any], 
    extra: Optional[Any] = None
) -> Optional[EventProcessorResult]:
    """对应 TypeScript 的 responseOutputItemAdded 函数"""
    response = conv.response_map.get(event["response_id"])
    if response:
        response.output_ids.append(event["item"]["id"])
    
    return None

def response_output_item_done(
    conv: RealtimeConversation, 
    event: Dict[str, Any], 
    extra: Optional[Any] = None
) -> Optional[EventProcessorResult]:
    """对应 TypeScript 的 responseOutputItemDone 函数"""
    item = conv.item_map.get(event["item"]["id"])
    if item:
        item["status"] = event["item"]["status"]
        # 对应 TypeScript: return { item, delta: null }
        return {"item": item, "delta": None}
    
    return None

def response_content_part_added(
    conv: RealtimeConversation, 
    event: Dict[str, Any], 
    extra: Optional[Any] = None
) -> Optional[EventProcessorResult]:
    """对应 TypeScript 的 responseContentPartAdded 函数"""
    item = conv.item_map.get(event["item_id"])
    if item:
        item["content"].append(event["part"])
    
    return None

def response_content_part_done(
    conv: RealtimeConversation, 
    event: Dict[str, Any], 
    extra: Optional[Any] = None
) -> Optional[EventProcessorResult]:
    """对应 TypeScript 的 responseContentPartDone 函数"""
    # 对应 TypeScript 注释: 不需要处理，part 实际上没有 done 标志
    return None

def conversation_item_input_audio_transcription_completed(
    conv: RealtimeConversation, 
    event: Dict[str, Any], 
    extra: Optional[Any] = None
) -> Optional[EventProcessorResult]:
    """对应 TypeScript 的 conversationItemInputAudioTranscriptionCompleted 函数"""
    item = conv.item_map.get(event["item_id"])
    if not item:
        conv.queued_transcript_items[event["item_id"]] = {"transcript": event["transcript"]}
        return {"item": None, "delta": None}
    else:
        # 对应 TypeScript: (item.content[event.content_index] as { transcript: string }).transcript
        item.content[event["content_index"]]["transcript"] = event["transcript"]
        item.formatted["transcript"] = event["transcript"]
        return {"item": item, "delta": {"transcript": event["transcript"]}}

def response_audio_delta(
    conv: RealtimeConversation, 
    event: Dict[str, Any], 
    extra: Optional[Any] = None
) -> Optional[EventProcessorResult]:
    """对应 TypeScript 的 responseAudioDelta 函数"""
    item = conv.item_map.get(event["item_id"])
    if item:
        # 对应 TypeScript: const deltaBuffer = Buffer.from(event.delta, "base64")
        delta_buffer = base64.b64decode(event["delta"])
        # 对应 TypeScript: Buffer.concat([item.formatted.audio, Buffer.from(deltaBuffer)])
        item["formatted"]["audio"] = item["formatted"]["audio"] + delta_buffer
        return {"item": item, "delta": event["delta"]}
    else:
        return {"item": None, "delta": None}

def response_audio_done(
    conv: RealtimeConversation, 
    event: Dict[str, Any], 
    extra: Optional[Any] = None
) -> Optional[EventProcessorResult]:
    """对应 TypeScript 的 responseAudioDone 函数"""
    item = conv.item_map.get(event["item_id"])
    if item:
        # 对应 TypeScript: Buffer.from(event.audio, "base64")
        item.formatted["audio"] = base64.b64decode(event["audio"])
        return {"item": item, "delta": None}
    else:
        return {"item": None, "delta": None}

def response_audio_transcript_delta(
    conv: RealtimeConversation, 
    event: Dict[str, Any], 
    extra: Optional[Any] = None
) -> Optional[EventProcessorResult]:
    """对应 TypeScript 的 responseAudioTranscriptDelta 函数"""
    item = conv.item_map.get(event["item_id"])
    if item:
        # 对应 TypeScript: (item.content[event.content_index] as { transcript: string }).transcript += event.delta
        item["content"][event["content_index"]]["transcript"] += event["delta"]
        item["formatted"]["transcript"] += event["delta"]
        return {"item": item, "delta": {"transcript": event["delta"]}}
    else:
        return {"item": None, "delta": None}

def response_audio_transcript_done(
    conv: RealtimeConversation, 
    event: Dict[str, Any], 
    extra: Optional[Any] = None
) -> Optional[EventProcessorResult]:
    """对应 TypeScript 的 responseAudioTranscriptDone 函数"""
    item = conv.item_map.get(event["item_id"])
    if item:
        # 对应 TypeScript: (item.content[event.content_index] as { transcript: string }).transcript = event.transcript
        item["content"][event["content_index"]]["transcript"] = event["transcript"]
        item["formatted"]["transcript"] = event["transcript"]
        return {"item": item, "delta": None}
    else:
        return {"item": None, "delta": None}

def conversation_item_deleted(
    conv: RealtimeConversation, 
    event: Dict[str, Any], 
    extra: Optional[Any] = None
) -> Optional[EventProcessorResult]:
    """对应 TypeScript 的 conversationItemDeleted 函数"""
    item = conv.item_map.get(event["item_id"])
    if item:
        # 对应 TypeScript: conv.items = conv.items.filter((i) => i.id !== item.id)
        conv.items = [i for i in conv.items if i.id != item.id]
        del conv.item_map[item.id]
        return {"item": item, "delta": None}
    
    return {"item": None, "delta": None}

def conversation_item_truncated(
    conv: RealtimeConversation, 
    event: Dict[str, Any], 
    extra: Optional[Any] = None
) -> Optional[EventProcessorResult]:
    """对应 TypeScript 的 conversationItemTruncated 函数"""
    item = conv.item_map.get(event["item_id"])
    if item:
        item.formatted["transcript"] = ""
        # 对应 TypeScript 注释: item.formatted.audio = new ArrayBuffer(0);
        # 在 Python 中相当于重置为空 bytes
        # item.formatted["audio"] = b""
    
    return None