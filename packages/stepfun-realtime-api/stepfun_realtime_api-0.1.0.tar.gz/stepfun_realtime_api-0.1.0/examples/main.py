import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import pyaudio
import stepfun_realtime_api as stepfun
import os

async def main():
    # 创建客户端
    client = stepfun.RealtimeClient(
        url=os.getenv("STEP_API", "wss://api.stepfun.com/v1/realtime"),
        secret=os.getenv("STEP_SECRET", "")
    )
    
    # 连接到服务器
    await client.connect()
    print("已连接到实时API")

     # 更新会话设置
    await client.update_session(
        turn_detection={"type": "server_vad"},
        instructions="你是一个友好的AI助手。"
    )
   
    # 注册事件处理器
    def on_session_created(event):
        # 处理会话创建事件
        session = event.get("session")
        print(f"✅ 会话已创建: {session.get('id')}")
        print(f"   模型: {session.get('model')}")
        print(f"   模态: {', '.join(session.get('modalities', []))}")

    def on_audio_delta(event):
        # 处理音频数据
        print(f"<-{event.get('type')}:", len(event['delta']), "字节")

    def on_audio_transcript_delta(event: stepfun.event.ServerResponseAudioTranscriptDelta):
        # 处理音频转写
        print(f"<-{event.get('type')}:", event.get("delta"))

    def on_input_audio_transcript(event: stepfun.event.ServerConversationItemInputAudioTranscriptionCompleted):
        # 处理输入音频转写
        print(f"<-{event.get('type')}:", event.get("transcript"))

    
    client.on(stepfun.ServerEventType.SESSION_CREATED, on_session_created)
    client.on(stepfun.ServerEventType.RESPONSE_AUDIO_DELTA, on_audio_delta)
    client.on(stepfun.ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DELTA, on_audio_transcript_delta)
    client.on(stepfun.ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED, on_input_audio_transcript)
    client.on(stepfun.ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED, lambda e: print(f"语音开始: {e['item_id']} at {e['audio_start_ms']}ms"))

    # 创建麦克风输入
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=24000,
        input=True,
        frames_per_buffer=4096
    )
    
    try:
        # 发送音频数据
        print("开始录音...")
        for _ in range(10):  # 录制约5秒
            data = stream.read(4096)
            await client.append_input_audio(data)
            await asyncio.sleep(0.1)
        
        # 发送请求
        await client.create_response()
        print("等待响应...")
        
        # 等待响应完成
        await asyncio.sleep(10)
        await asyncio.sleep(10)
        await asyncio.sleep(10)
    finally:
        # 关闭资源
        stream.stop_stream()
        stream.close()
        p.terminate()
        await client.disconnect()
        print("已断开连接")

if __name__ == "__main__":
    asyncio.run(main())