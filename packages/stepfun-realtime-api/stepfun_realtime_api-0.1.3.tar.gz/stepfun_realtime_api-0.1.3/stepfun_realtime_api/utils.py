def calculate_volume(audio_buffer):
    """计算音频音量"""
    if not audio_buffer or len(audio_buffer) == 0:
        return 0
    
    # 获取样本总数 (假设16位音频 - 每样本2字节)
    sample_count = len(audio_buffer) // 2
    
    # 计算平方和
    sum_squares = 0
    for i in range(sample_count):
        # 读取16位样本 (小端序)
        sample = int.from_bytes(audio_buffer[i*2:i*2+2], byteorder='little', signed=True)
        sum_squares += sample * sample
    
    if sample_count == 0:
        return 0
    
    # 计算RMS (均方根)
    rms = (sum_squares / sample_count) ** 0.5
    
    # 归一化到0-1之间 (16位音频的值在-32768到32767之间)
    normalized_rms = rms / 32768
    
    return normalized_rms