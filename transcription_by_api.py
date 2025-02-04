from dotenv import load_dotenv
import os, json
from openai import OpenAI
from pathlib import Path
from openai.types.audio import (
    TranscriptionSegment,
)

load_dotenv()  # take environment variables from .env.

client: TranscriptionSegment = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)

transcription: TranscriptionSegment = client.audio.transcriptions.create(
    model="whisper-1",
    file=Path("D:\\audio\\M_0014_11y7m_1.wav"),
    language="en",
    response_format="verbose_json",
    timestamp_granularities="segment",
)

transcription_data = transcription.to_dict()


with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(transcription_data, f, ensure_ascii=False, indent=4)

with open('./data/scripts.txt', 'w', encoding='utf-8') as f:
    for line_segment in transcription_data["segments"]:
        start = line_segment["start"]
        end = line_segment["end"]
        segment_text = line_segment["text"]
        f.write(f"[{start} --> {end}] {segment_text} \n")