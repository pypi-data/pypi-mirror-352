# Stepfun Realtime API 阶跃星辰实时语音（python）

## 简介

本项目提供了一个实时的语音交互 API，允许将基于语音的功能无缝集成到您的应用程序中。

## 安装

```bash
pip install stepfun_realtime_api
```

## 示例程序

该程序从麦克风读取音频，并发送给 stepfun realtime api，语音检测采用服务端检测（server_vad），只在命令行展示文字（有声音返回但是没有播放）。

```python
import asyncio
import pyaudio
import stepfun_realtime_api as stepfun
import os
import signal

# 全局标志用于控制程序退出
shutdown_flag = False

def signal_handler(signum, frame):
    """处理 Ctrl+C 信号"""
    global shutdown_flag
    print("\n收到退出信号，正在关闭...")
    shutdown_flag = True

async def main():
    global shutdown_flag
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)

    step_api = os.getenv("STEP_API", "wss://api.stepfun.com/v1/realtime")
    step_secret = os.getenv("STEP_SECRET", "")
    print(f"使用 StepFun API: {step_api}")
    # Mask the secret key for security - show only first 3 and last 3 characters
    masked_secret = f"{step_secret[:3]}{'*' * (len(step_secret) - 6)}{step_secret[-3:]}" if len(step_secret) >= 6 else "***"
    print(f"使用 Secret: {masked_secret}")
    
    # 创建客户端
    client = stepfun.RealtimeClient(
        url=step_api,
        secret=step_secret,
    )
    
    # 注册事件处理器
    def on_session_created(event):
        # 处理会话创建事件
        session = event.get("session")
        print("✅ 已连接到实时API")
        print(f"   会话已创建: {session.get('id')}")
        print(f"   模型: {session.get('model')}")
        print("🎤 开始语音对话，按 Ctrl+C 退出...")

    def on_audio_transcript_delta(event: stepfun.event.ServerResponseAudioTranscriptDelta):
        # 处理音频转写
        print(f"<-{event.get('type')}:", event.get("delta"))

    def on_input_audio_transcript(event: stepfun.event.ServerConversationItemInputAudioTranscriptionCompleted):
        # 处理输入音频转写
        print(f"<-{event.get('type')}:", event.get("transcript"))

    client.on(stepfun.ServerEventType.SESSION_CREATED, on_session_created)
    client.on(stepfun.ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DELTA, on_audio_transcript_delta)
    client.on(stepfun.ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED, on_input_audio_transcript)
    client.on(stepfun.ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED, lambda e: print(f"语音开始: {e['item_id']} at {e['audio_start_ms']}ms"))

    # 连接到服务器
    await client.connect()

     # 更新会话设置
    await client.update_session(
        turn_detection={"type": "server_vad"},
        instructions="你是一个友好的AI助手，能够用简介口语的方式回答问题。"
    )

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
        while not shutdown_flag:
            data = stream.read(4096, exception_on_overflow=False)
            # 持续发送音频数据
            await client.append_input_audio(data)
            # 让出控制权，避免阻塞
            await asyncio.sleep(0.01)
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 关闭资源
        print("正在关闭音频流...")
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("正在断开连接...")
        await client.disconnect()
        print("✅ 程序已安全退出")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
```