import os
from pydub import AudioSegment



#print(os.environ.get("PATH"))

audio = AudioSegment.from_wav("./audio/audio.wav")

# PyDub handles time in milliseconds
ten_minutes = 10 * 60 * 1000
var = 0

while len(audio) > 0:
    print(len(audio))
    audio_segment = audio[:ten_minutes]
    audio = audio[ten_minutes:]
    audio_segment.export(f"./audio/audio_{var}.mp3", format="mp3")
    var += 1