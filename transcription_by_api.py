from dotenv import load_dotenv
import os, json
from pydub import AudioSegment
from openai import OpenAI
from pathlib import Path
from openai.types.audio import Translation, TranslationVerbose, TranslationCreateResponse
from utils.formatting import seconds_to_str_in_srt
import subprocess

def extract_audio(filename: str):
    command = f"ffmpeg -i ./input/{filename} -ab 160k -ac 2 -ar 44100 -vn ./audio/{filename}/audio.wav"
    result: subprocess.CompletedProcess = subprocess.run(command, text=True, shell=True)
    result.check_returncode()


def get_audio_length(uploaded_filename: str, file: str):
    """
    returns audio length of filename in ./input/filename in seconds
    """
    path = f"./audio/{uploaded_filename}/{file}"
    command = f'ffprobe -i {path} -show_entries format=duration -v quiet -of csv="p=0"'
    result: subprocess.CompletedProcess =  subprocess.run(command, text=True, capture_output=True, shell=True)
    if result.returncode != 0:
        raise ValueError("fail to get audio length")
    
    if result.stdout:
        length_in_str: str = result.stdout
        return float(length_in_str.strip())
    else:
        raise ValueError("fail to get audio length")

def chunk_audio(filename: str) -> tuple[list[str], list[int]]:
    """
    chunk the audio file at temp folder ./audio/filename/audio.wav into pieces, named as output_#.wav
    returns the number of pieces
    """
    cmd = ['ffmpeg', '-i', f'./audio/{filename}/audio.wav', '-c', 'copy', '-map','0', '-segment_time', '00:01:00', '-f', 'segment', "-reset_timestamps", "1",  f'./audio/{filename}/output_%03d.wav']
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise ValueError(f"Could not chunk the audio file error output:{result.stderr} output:{result.stdout}")
    filename_list = next(os.walk(f"./audio/{filename}"), (None, None, []))[2]
    filename_list.remove("audio.wav")
    filename_list.sort()
    len_list = []
    for name in filename_list:
        len_list.append(get_audio_length(filename, name))
    return filename_list, len_list


DEBUG = True
load_dotenv()  # take environment variables from .env.

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)

if not os.path.isdir("./output"): # make sure output folder exists
   os.makedirs("./output")

if not os.path.isdir("./data"): # make sure output folder exists
   os.makedirs("./data")

filename = input("file to operate to save the result as:")

if not os.path.isfile(f"./input/{filename}"):
    raise FileNotFoundError("There is no such file in input folder, please double check")

if not os.path.isdir(f"./audio/{filename}"): # create a temp folder for processing
   os.makedirs(f"./audio/{filename}")


path = f"./input/{filename}"

if filename.endswith("mp4") or filename.endswith("avi"):
    extract_audio(filename)

original_audio_len = get_audio_length(filename, "audio.wav")
if original_audio_len / 60 > 10: # TODO: set the threshold to a reasonable value
    filename_list, len_list = chunk_audio(filename) # TODO: chunk the audio file
else:
    filename_list, len_list = ["audio.wav"], [original_audio_len]

last_segment_ended_at = 0
index = 1
for i in range(len(filename_list)):
    path = f"./audio/{filename}/{filename_list[i]}"
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=Path(path),
        timestamp_granularities="segment",
        response_format="verbose_json",
    )

    transcription_data = transcription.to_dict()

    if DEBUG:
        with open(f'./data/{filename}_data_{i}.json', 'w', encoding='utf-8') as f:
            json.dump(transcription_data, f, ensure_ascii=False, indent=4)

    with open(f'./output/{filename}.srt', 'a', encoding='utf-8') as f: # processing each chunked file
        for line_segment in transcription_data["segments"]:
            start = last_segment_ended_at + line_segment["start"]
            end = last_segment_ended_at + line_segment["end"]
            segment_text = line_segment["text"].strip()
            start = seconds_to_str_in_srt(start)
            end = seconds_to_str_in_srt(end)
            f.write(f"{index} \n{start} --> {end} \n{segment_text}\n\n")
            index += 1
    last_segment_ended_at += len_list[i]
