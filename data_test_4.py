# wav相关操作
#音频水印
import struct

wav_file = open('rain.wav', 'rb')

wav_RIFF_chunk = wav_file.read(12)

RIFF, size, WAVE = struct.unpack('<4sI4s', wav_RIFF_chunk)
print(RIFF, size, WAVE)

wav_fmt_chunk_header = wav_file.read(8)

FMT, size = struct.unpack('<4sI', wav_fmt_chunk_header)

wav_fmt_chunk_data = wav_file.read(size)

extra = -1
if size == 16:
    codec, nChannels, samplerate, byterate, blockalign, bits = struct.unpack('<HHIIHH', wav_fmt_chunk_data)
else:
    codec, nChannels, samplerate, byterate, blockalign, bits, extra = struct.unpack('<HHIIHH', wav_fmt_chunk_data)
print(codec, nChannels, samplerate, byterate, blockalign, bits, extra)
