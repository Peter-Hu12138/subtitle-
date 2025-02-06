from dotenv import load_dotenv
import os, json, time
from pydub import AudioSegment
from openai import OpenAI
from pathlib import Path
from openai.types.audio import Translation, TranslationVerbose, TranslationCreateResponse

DEBUG = True

filename = input("filename to save the result as:")

load_dotenv()  # take environment variables from .env.

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)
last_segment_ended_at = 0

for i in range(0, 3):
    path = f"D:\\UofT_Offline\\subtitle!\\audio\\audio_{i}.mp3"
    transcription = client.audio.translations.create(
        model="whisper-1",
        file=Path(f"D:\\UofT_Offline\\subtitle!\\audio\\audio_{i}.mp3"),
        response_format="verbose_json",
    )

    audio = AudioSegment.from_wav("./audio/audio_{i}.mp3")
    transcription_data = transcription.to_dict()
    if DEBUG:
        with open(f'./data/{filename}_data_{i}.json', 'w', encoding='utf-8') as f:
            json.dump(transcription_data, f, ensure_ascii=False, indent=4)

    with open(f'./data/{filename}.txt', 'a', encoding='utf-8') as f: # processing each chunked file
        for line_segment in transcription_data["segments"]:
            start = last_segment_ended_at + line_segment["start"]
            end = last_segment_ended_at + line_segment["end"]
            segment_text = line_segment["text"]
            f.write(f"[{start} --> {end}] {segment_text} \n")
    last_segment_ended_at += len(audio)
