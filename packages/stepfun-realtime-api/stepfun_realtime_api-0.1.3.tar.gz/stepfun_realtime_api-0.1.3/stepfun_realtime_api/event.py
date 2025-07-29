from enum import Enum
from typing import Dict, List, Union, Any, Optional, TypedDict, Literal

# 导出的类型定义
__all__ = [
    # 枚举类型
    'ClientEventType',
    'ServerEventType', 
    'LocalEventType',
    
    # 基础类型
    'Modality',
    'AudioFormat',
    'ContentItem',
    'ContentTextItem',
    'ContentAudioItem', 
    'ContentTranscriptItem',
    'ContentPart',
    'TextPart',
    'AudioPart',
    
    # 复合类型
    'SessionType',
    'ItemType',
    'ItemTypeFormatted',
    'ServerResponseType',
    'ServerResponseTypeWithUsage',
    'ServerResponseOutputItem',
    'UsageType',
    'InputTokenDetails',
    'OutputTokenDetails',
    'CachedTokensDetails',
    
    # 服务器事件类型
    'ServerSessionCreated',
    'ServerSessionUpdated',
    'ServerConversationItemCreated',
    'ServerConversationItemDeleted',
    'ServerConversationItemTruncated',
    'ServerConversationItemInputAudioTranscriptionCompleted',
    'ServerConversationItemInputAudioTranscriptionDelta',
    'ServerConversationItemInputAudioTranscriptionFailed',
    'ServerInputAudioBufferSpeechStarted',
    'ServerInputAudioBufferSpeechStopped',
    'ServerInputAudioBufferCommitted',
    'ServerInputAudioBufferCleared',
    'ServerResponseCreated',
    'ServerResponseDone',
    'ServerResponseOutputItemAdded',
    'ServerResponseOutputItemDone',
    'ServerResponseContentPartAdded',
    'ServerResponseContentPartDone',
    'ServerResponseAudioDelta',
    'ServerResponseAudioDone',
    'ServerResponseAudioTranscriptDelta',
    'ServerResponseAudioTranscriptDone',
    'ServerResponseTextDelta',
    'ServerResponseTextDone',
    'ServerError',
    
    # 客户端事件类型
    'ClientSessionUpdate',
    'ClientInputAudioBufferAppend',
    'ClientInputAudioBufferCommit',
    'ClientInputAudioBufferClear',
    'ClientConversationItemCreate',
    'ClientConversationItemDelete',
    'ClientResponseCreate',
    'ClientResponseCancel',
    
    # 联合类型
    'ServerEvent',
    'ClientEvent',
    
    # 基础事件类
    'ClientRealtimeEvent',
    'ServerRealtimeEvent',
]

class ClientEventType(str, Enum):
    SESSION_UPDATE = "session.update"
    
    INPUT_AUDIO_BUFFER_APPEND = "input_audio_buffer.append"
    INPUT_AUDIO_BUFFER_COMMIT = "input_audio_buffer.commit"
    INPUT_AUDIO_BUFFER_CLEAR = "input_audio_buffer.clear"
    
    CONVERSATION_ITEM_CREATE = "conversation.item.create"
    CONVERSATION_ITEM_DELETE = "conversation.item.delete"
    
    RESPONSE_CREATE = "response.create"
    RESPONSE_CANCEL = "response.cancel"

class ServerEventType(str, Enum):
    ERROR = "error"
    
    SESSION_CREATED = "session.created"
    SESSION_UPDATED = "session.updated"
    
    CONVERSATION_ITEM_CREATED = "conversation.item.created"
    
    CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_DELTA = "conversation.item.input_audio_transcription.delta"
    CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED = "conversation.item.input_audio_transcription.completed"
    CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_FAILED = "conversation.item.input_audio_transcription.failed"
    
    CONVERSATION_ITEM_TRUNCATED = "conversation.item.truncated"
    CONVERSATION_ITEM_DELETED = "conversation.item.deleted"
    
    INPUT_AUDIO_BUFFER_COMMITTED = "input_audio_buffer.committed"
    INPUT_AUDIO_BUFFER_SPEECH_STARTED = "input_audio_buffer.speech_started"
    INPUT_AUDIO_BUFFER_SPEECH_STOPPED = "input_audio_buffer.speech_stopped"
    INPUT_AUDIO_BUFFER_CLEARED = "input_audio_buffer.cleared"
    
    RESPONSE_CREATED = "response.created"
    RESPONSE_DONE = "response.done"
    
    RESPONSE_OUTPUT_ITEM_ADDED = "response.output_item.added"
    RESPONSE_OUTPUT_ITEM_DONE = "response.output_item.done"
    
    RESPONSE_CONTENT_PART_ADDED = "response.content_part.added"
    RESPONSE_CONTENT_PART_DONE = "response.content_part.done"
    
    RESPONSE_TEXT_DELTA = "response.text.delta"
    RESPONSE_TEXT_DONE = "response.text.done"
    
    RESPONSE_AUDIO_TRANSCRIPT_DELTA = "response.audio_transcript.delta"
    RESPONSE_AUDIO_TRANSCRIPT_DONE = "response.audio_transcript.done"
    
    RESPONSE_AUDIO_DELTA = "response.audio.delta"
    RESPONSE_AUDIO_DONE = "response.audio.done"

# 基础类型定义 - 对应 TypeScript 的基础类型

# Modality 类型
Modality = Literal["text", "audio"]

# AudioFormat 类型
AudioFormat = Literal["pcm16"]

# 内容项类型
class ContentTextItem(TypedDict):
    """文本内容项"""
    type: Literal["text", "input_text"]
    text: str

class ContentAudioItem(TypedDict):
    """音频内容项"""
    type: Literal["audio"]
    audio: str
    transcript: str

class ContentTranscriptItem(TypedDict):
    """转写内容项"""
    type: Literal["transcript"]
    transcript: str

# 内容项联合类型
ContentItem = Union[ContentTextItem, ContentAudioItem, ContentTranscriptItem]

# Session 类型
class SessionType(TypedDict):
    """会话类型定义 - 对应 TypeScript Session"""
    id: str
    model: str
    modalities: List[Modality]
    instructions: str
    input_audio_format: AudioFormat
    output_audio_format: AudioFormat
    voice: str
    built_in_tools: List[str]  # only web_search for now
    threshold: Optional[float]
    turn_detection: Optional[Dict[str, str]]  # null | { type: "server_vad" }
    max_response_output_length: int

# ItemType 定义 - 对应 TypeScript ItemType
class ItemTypeFormatted(TypedDict):
    """项目格式化内容"""
    text: str
    audio: bytes  # 对应 TypeScript 的 Buffer
    transcript: str

class ItemType(TypedDict):
    """项目类型定义 - 对应 TypeScript ItemType"""
    id: str = ""
    role: Literal["user", "assistant", "system"] = ""
    type: Literal["message"]
    status: Literal["completed", "failed", "in_progress", "incomplete"]
    formatted: ItemTypeFormatted
    content: List[ContentItem]

# ServerResponseType 输出项定义
class ServerResponseOutputItem(TypedDict):
    """服务器响应输出项"""
    id: str
    object: str
    status: Literal["completed", "failed", "in_progress", "incomplete"]
    type: Literal["message"]
    role: Literal["user", "assistant", "system"]
    content: List[Union[ContentTextItem, ContentAudioItem]]

# 使用详情类型
class CachedTokensDetails(TypedDict):
    """缓存令牌详情"""
    text_tokens: int
    audio_tokens: int

class InputTokenDetails(TypedDict):
    """输入令牌详情"""
    cached_tokens: int
    audio_tokens: int
    text_tokens: int
    cached_tokens_details: CachedTokensDetails

class OutputTokenDetails(TypedDict):
    """输出令牌详情"""
    text_tokens: int
    audio_tokens: int

class UsageType(TypedDict):
    """使用情况类型"""
    total_tokens: int
    input_tokens: int
    output_tokens: int
    input_token_details: InputTokenDetails
    output_token_details: OutputTokenDetails

# ServerResponseType 定义
class ServerResponseType(TypedDict):
    """服务器响应类型定义 - 对应 TypeScript ServerResponseType"""
    id: str
    object: str
    status: Literal["completed", "failed", "in_progress", "incomplete"]
    output: List[ServerResponseOutputItem]

# 带使用详情的服务器响应类型
class ServerResponseTypeWithUsage(ServerResponseType):
    """带使用详情的服务器响应类型"""
    usage: UsageType

# 内容部分类型
class TextPart(TypedDict):
    """文本部分"""
    type: Literal["text"]
    text: str

class AudioPart(TypedDict):
    """音频部分"""
    type: Literal["audio"]
    audio: str
    transcript: str

# 内容部分联合类型
ContentPart = Union[TextPart, AudioPart]

class LocalEventType(str, Enum):
    CONVERSATION_UPDATED = "conversation.updated"
    CONVERSATION_ITEM_APPENDED = "conversation.item.appended"
    CONVERSATION_ITEM_COMPLETED = "conversation.item.completed"



# 定义各种事件类型
class ClientRealtimeEvent(dict):
    def __init__(self, event_type: ClientEventType, **kwargs):
        super().__init__(type=event_type, **kwargs)
        if "event_id" not in self:
            import time
            import random
            import string
            timestamp = int(time.time() * 1000)
            random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            self["event_id"] = f"evt_{timestamp}_{random_str}"

class ServerRealtimeEvent(dict):
    def __init__(self, event_type: ServerEventType, **kwargs):
        super().__init__(type=event_type, **kwargs)

# 具体的服务器事件类型定义，对应 TypeScript 的具体事件类型

class ServerSessionCreated(TypedDict):
    """服务器会话创建事件 - 对应 TypeScript ServerSessionCreated"""
    type: ServerEventType
    session: SessionType

class ServerSessionUpdated(TypedDict):
    """服务器会话更新事件 - 对应 TypeScript ServerSessionUpdated"""
    type: ServerEventType
    session: SessionType

class ServerConversationItemCreated(TypedDict):
    """对话项创建事件 - 对应 TypeScript ServerConversationItemCreated"""
    type: ServerEventType
    response_id: str
    previous_item_id: str
    item: ItemType

class ServerConversationItemDeleted(TypedDict):
    """对话项删除事件 - 对应 TypeScript ServerConversationItemDeleted"""
    type: ServerEventType
    item_id: str

class ServerConversationItemTruncated(TypedDict):
    """对话项截断事件 - 对应 TypeScript ServerConversationItemTruncated"""
    type: ServerEventType
    item_id: str

class ServerConversationItemInputAudioTranscriptionCompleted(TypedDict):
    """音频转写完成事件 - 对应 TypeScript ServerConversationItemInputAudioTranscriptionCompleted"""
    type: ServerEventType
    item_id: str
    content_index: int
    transcript: str

class ServerConversationItemInputAudioTranscriptionDelta(TypedDict):
    """音频转写增量事件 - 对应 TypeScript ServerConversationItemInputAudioTranscriptionDelta"""
    type: ServerEventType
    item_id: str
    content_index: int
    delta: str

class ServerInputAudioBufferSpeechStarted(TypedDict):
    """输入音频缓冲区语音开始事件 - 对应 TypeScript ServerInputAudioBufferSpeechStarted"""
    type: ServerEventType
    item_id: str
    audio_start_ms: int

class ServerInputAudioBufferSpeechStopped(TypedDict):
    """输入音频缓冲区语音停止事件 - 对应 TypeScript ServerInputAudioBufferSpeechStopped"""
    type: ServerEventType
    item_id: str
    audio_end_ms: int

class ServerInputAudioBufferCommitted(TypedDict):
    """输入音频缓冲区提交事件 - 对应 TypeScript ServerInputAudioBufferCommitted"""
    type: ServerEventType
    previous_item_id: str
    item_id: str

class ServerInputAudioBufferCleared(TypedDict):
    """输入音频缓冲区清除事件 - 对应 TypeScript ServerInputAudioBufferCleared"""
    type: ServerEventType

class ServerResponseCreated(TypedDict):
    """响应创建事件 - 对应 TypeScript ServerResponseCreated"""
    type: ServerEventType
    response: ServerResponseType

class ServerResponseDone(TypedDict):
    """响应完成事件 - 对应 TypeScript ServerResponseDone"""
    type: ServerEventType
    response: ServerResponseTypeWithUsage

class ServerResponseOutputItemAdded(TypedDict):
    """响应输出项添加事件 - 对应 TypeScript ServerResponseOutputItemAdded"""
    type: ServerEventType
    response_id: str
    output_index: int
    item: ItemType  # 注意：TypeScript 中使用 ServerItemType，这里简化为 ItemType

class ServerResponseOutputItemDone(TypedDict):
    """响应输出项完成事件 - 对应 TypeScript ServerResponseOutputItemDone"""
    type: ServerEventType
    response_id: str
    output_index: int
    item: ItemType  # 注意：TypeScript 中使用 ServerItemType，这里简化为 ItemType

class ServerResponseContentPartAdded(TypedDict):
    """响应内容部分添加事件 - 对应 TypeScript ServerResponseContentPartAdded"""
    type: ServerEventType
    response_id: str
    item_id: str
    content_index: int
    output_index: int
    part: ContentPart

class ServerResponseContentPartDone(TypedDict):
    """响应内容部分完成事件 - 对应 TypeScript ServerResponseContentPartDone"""
    type: ServerEventType
    response_id: str
    item_id: str
    content_index: int
    output_index: int
    part: ContentPart

class ServerResponseAudioDelta(TypedDict):
    """响应音频增量事件"""
    type: ServerEventType
    response_id: str
    item_id: str
    delta: str
    output_index: int
    content_index: int

class ServerResponseAudioDone(TypedDict):
    """响应音频完成事件"""
    type: ServerEventType
    response_id: str
    item_id: str
    audio: str
    output_index: int
    content_index: int

class ServerResponseAudioTranscriptDelta(TypedDict):
    """响应音频转写增量事件"""
    type: ServerEventType
    response_id: str
    item_id: str
    delta: str
    content_index: int

class ServerResponseAudioTranscriptDone(TypedDict):
    """响应音频转写完成事件"""
    type: ServerEventType
    response_id: str
    item_id: str
    content_index: int
    transcript: str

# 添加缺失的事件类型

class ServerResponseTextDelta(TypedDict):
    """响应文本增量事件 - 对应 TypeScript (虽然 TypeScript 中没有明确定义，但根据模式推断)"""
    type: ServerEventType
    response_id: str
    item_id: str
    delta: str
    content_index: int

class ServerResponseTextDone(TypedDict):
    """响应文本完成事件 - 对应 TypeScript (虽然 TypeScript 中没有明确定义，但根据模式推断)"""
    type: ServerEventType
    response_id: str
    item_id: str
    content_index: int
    text: str

class ServerError(TypedDict):
    """服务器错误事件"""
    type: ServerEventType
    error: Dict[str, Union[str, int]]  # 错误详情，通常包含 code, message 等字段

class ServerConversationItemInputAudioTranscriptionFailed(TypedDict):
    """音频转写失败事件"""
    type: ServerEventType
    item_id: str
    content_index: int
    error: Dict[str, Union[str, int]]

# 客户端事件类型定义 - 对应 TypeScript 的客户端事件

class ClientSessionUpdate(TypedDict):
    """客户端会话更新事件"""
    type: ClientEventType
    session: SessionType

class ClientInputAudioBufferAppend(TypedDict):
    """客户端输入音频缓冲区追加事件"""
    type: ClientEventType
    audio: str  # base64 编码的音频数据

class ClientInputAudioBufferCommit(TypedDict):
    """客户端输入音频缓冲区提交事件"""
    type: ClientEventType

class ClientInputAudioBufferClear(TypedDict):
    """客户端输入音频缓冲区清除事件"""
    type: ClientEventType

class ClientConversationItemCreate(TypedDict):
    """客户端对话项创建事件"""
    type: ClientEventType
    previous_item_id: Optional[str]
    item: ItemType

class ClientConversationItemDelete(TypedDict):
    """客户端对话项删除事件"""
    type: ClientEventType
    item_id: str

class ClientResponseCreate(TypedDict):
    """客户端响应创建事件"""
    type: ClientEventType
    response: Optional[Dict[str, Union[str, List[str]]]]  # 响应配置

class ClientResponseCancel(TypedDict):
    """客户端响应取消事件"""
    type: ClientEventType

# 联合类型定义

# 所有服务器事件的联合类型
ServerEvent = Union[
    ServerSessionCreated,
    ServerSessionUpdated,
    ServerConversationItemCreated,
    ServerConversationItemDeleted,
    ServerConversationItemTruncated,
    ServerConversationItemInputAudioTranscriptionCompleted,
    ServerConversationItemInputAudioTranscriptionDelta,
    ServerConversationItemInputAudioTranscriptionFailed,
    ServerInputAudioBufferSpeechStarted,
    ServerInputAudioBufferSpeechStopped,
    ServerInputAudioBufferCommitted,
    ServerInputAudioBufferCleared,
    ServerResponseCreated,
    ServerResponseDone,
    ServerResponseOutputItemAdded,
    ServerResponseOutputItemDone,
    ServerResponseContentPartAdded,
    ServerResponseContentPartDone,
    ServerResponseAudioDelta,
    ServerResponseAudioDone,
    ServerResponseAudioTranscriptDelta,
    ServerResponseAudioTranscriptDone,
    ServerResponseTextDelta,
    ServerResponseTextDone,
    ServerError,
]

# 所有客户端事件的联合类型
ClientEvent = Union[
    ClientSessionUpdate,
    ClientInputAudioBufferAppend,
    ClientInputAudioBufferCommit,
    ClientInputAudioBufferClear,
    ClientConversationItemCreate,
    ClientConversationItemDelete,
    ClientResponseCreate,
    ClientResponseCancel,
]