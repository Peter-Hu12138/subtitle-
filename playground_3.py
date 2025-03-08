from dotenv import load_dotenv
import os, json
from openai import OpenAI
from pathlib import Path
from openai.types.audio import Translation, TranslationVerbose, TranslationCreateResponse
from utils.formatting import seconds_to_str_in_srt
from translation import translate
import subprocess, shutil

def extract_audio(filename: str):
    """
    Normalize into an audio.mp3 audio file
    """
    command = f"ffmpeg -i ./input/{filename} -ab 160k -ac 2 -ar 44100 -vn ./audio/{filename}/audio.mp3"
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
    chunk the audio file at temp folder ./audio/filename/audio.mp3 into pieces, named as output_#.mp3
    returns the number of pieces
    """
    cmd = ['ffmpeg', '-i', f'./audio/{filename}/audio.mp3', '-c', 'copy', '-map','0', '-segment_time', '00:15:00', '-f', 'segment', "-reset_timestamps", "1",  f'./audio/{filename}/output_%03d.mp3']
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise ValueError(f"Could not chunk the audio file error output:{result.stderr} output:{result.stdout}")
    filename_list = next(os.walk(f"./audio/{filename}"), (None, None, []))[2]
    filename_list.remove("audio.mp3")
    filename_list.sort()
    if os.path.getsize(f"./audio/{filename}/{filename_list[-1]}") < 1024 * 6:
        # if the last segment is too small
        filename_list.pop()
    len_list = []
    for name in filename_list:
        len_list.append(get_audio_length(filename, name))
    return filename_list, len_list


DEBUG = True
IF_FUSE = True
FUSE_TYPE = 2 # whether to integrate the subtitle file into the video file
FUSE_DICT = {1: "hardcode", 2: "track"}
TRANSLATION = "NONE"
TRANSLATION_LIST = {'af': 'Afrikaans', 'ar': 'Arabic', 'az': 'Azerbaijani', 'be': 'Belarusian', 'bg': 'Bulgarian', 'bs': 'Bosnian', 
                    'ca': 'Catalan; Valencian', 'cs': 'Czech', 'cu': 'Church Slavic; Old Slavonic; Church Slavonic; Old Bulgarian; Old Church Slavonic', 
                    'cy': 'Welsh', 'da': 'Danish', 'de': 'German', 'el': 'Greek, Modern (1453-)', 'en': 'English', 'es': 'Spanish; Castilian', 'et': 'Estonian', 
                    'fa': 'Persian', 'fi': 'Finnish', 'fr': 'French', 'gl': 'Galician', 'he': 'Hebrew', 'hi': 'Hindi', 'hr': 'Croatian', 'hu': 'Hungarian', 
                    'hy': 'Armenian', 'id': 'Indonesian', 'is': 'Icelandic', 'it': 'Italian', 'ja': 'Japanese', 'kk': 'Kazakh', 'kn': 'Kannada', 'ko': 'Korean', 
                    'lt': 'Lithuanian', 'lv': 'Latvian', 'mi': 'Maori', 'mk': 'Macedonian', 'ml': 'Malayalam', 'mr': 'Marathi', 'ms': 'Malay', 
                    'nb': 'Bokmål, Norwegian; Norwegian Bokmål', 'ne': 'Nepali', 'nl': 'Dutch; Flemish', 'nn': 'Norwegian Nynorsk; Nynorsk, Norwegian', 
                    'no': 'Norwegian', 'pi': 'Pali', 'pl': 'Polish', 'pt': 'Portuguese', 'ro': 'Romanian; Moldavian; Moldovan', 'ru': 'Russian', 'sk': 'Slovak', 
                    'sl': 'Slovenian', 'sr': 'Serbian', 'sv': 'Swedish', 'sw': 'Swahili', 'ta': 'Tamil', 'th': 'Thai', 'tl': 'Tagalog', 'tr': 'Turkish', 'uk': 'Ukrainian',
                    'ur': 'Urdu', 'vi': 'Vietnamese', 'zh': 'Chinese'}
ORIGINAL_LANGUAGE = "ja"

load_dotenv()  # take environment variables from .env.

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)


if not os.path.isdir("./data"): # make sure output folder exists
   os.makedirs("./data")

filename = input("file to operate to save the result as:")

if not os.path.isdir(f"./output/{filename}/"): # make sure output folder exists
   os.makedirs(f"./output/{filename}/")

if not os.path.isfile(f"./input/{filename}"):
    raise FileNotFoundError("There is no such file in input folder, please double check")

if not os.path.isdir(f"./audio/{filename}"): # create a temp folder for processing
   os.makedirs(f"./audio/{filename}")


path = f"./input/{filename}"
try:
    # TODO, clear previously generated file
    extract_audio(filename)

    original_audio_len = get_audio_length(filename, "audio.mp3")
    if original_audio_len / 60 > 20: # TODO: set the threshold to a reasonable value
        filename_list, len_list = chunk_audio(filename) 
        # TODO: design decision: we might use return value of returned json file to know the duration
    else:
        filename_list, len_list = ["audio.mp3"], [original_audio_len]
    prompt = ""
    if TRANSLATION == "NONE" or TRANSLATION == "en":
        # no translation or translation into eng
        # use whisper only
        last_segment_ended_at = 0
        index = 1
        
        for i in range(len(filename_list)):
            # do not process that is too short for openai whisper
            if len_list[i] < 0.1:
                continue
            path = f"./audio/{filename}/{filename_list[i]}"
            if TRANSLATION == "NONE":    
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=Path(path),
                    timestamp_granularities="segment",
                    response_format="srt",
                    prompt=prompt,
                )
            else:
                transcription = client.audio.translations.create(
                    model="whisper-1",
                    file=Path(path),
                    response_format="srt",
                )

            # transcription_data = transcription.to_dict()

            if DEBUG:
                with open(f'./data/{filename}_data_{i}.srt', 'w', encoding='utf-8') as f:
                    f.write(transcription)

            
            last_segment_ended_at += len_list[i]
    
    else:
        # translate into non-eng, use grok
        last_segment_ended_at = 0
        index = 1
        
        for i in range(len(filename_list)):
            # do not process that is too short for openai whisper
            if len_list[i] < 0.1:
                continue
            path = f"./audio/{filename}/{filename_list[i]}"
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                language=ORIGINAL_LANGUAGE,
                file=Path(path),
                prompt=prompt,
                timestamp_granularities="segment",
                response_format="verbose_json",
            )
            transcription_data = transcription.to_dict()
            prompt = transcription_data["text"].split()
            

            if DEBUG:
                with open(f'./data/{filename}_data_{i}.json', 'w', encoding='utf-8') as f:
                    json.dump(transcription_data, f, ensure_ascii=False, indent=4)

            # translation with AI
            
            segments = transcription_data["segments"]

            with open(f'./output/{filename}/{filename}.srt', 'a', encoding='utf-8') as f: # processing each chunked file
                while len(segments) > 0:
                    lines = segments[:10]
                    segments = segments[10:]
                    for line in lines:
                        if line["text"].strip() == "":
                            with open(f'./error.log', 'a', encoding='utf-8') as f:
                                f.write(f"{line}")
                    if ORIGINAL_LANGUAGE != "NONE":
                        translated_lines = translate("\n".join([line["text"].strip() for line in lines]), TRANSLATION_LIST[TRANSLATION], TRANSLATION_LIST[ORIGINAL_LANGUAGE])
                    else:
                        translated_lines = translate("\n".join([line["text"].strip() for line in lines]), TRANSLATION_LIST[TRANSLATION])
                    translated_lines = translated_lines.splitlines() # read as a list of lines
                    assert len(lines) == len(translated_lines)
                    for j in range(len(lines)):
                        line_segment = lines[j]
                        start = last_segment_ended_at + line_segment["start"]
                        end = last_segment_ended_at + line_segment["end"]
                        segment_text = translated_lines[j].strip()
                        start = seconds_to_str_in_srt(start)
                        end = seconds_to_str_in_srt(end)
                        f.write(f"{index} \n{start} --> {end} \n{segment_text}\n\n")
                        index += 1
                    
            last_segment_ended_at += len_list[i]
        
    

    if IF_FUSE:
        # integrate subtitle file TODO
        if FUSE_DICT[FUSE_TYPE] == "hardcode":
            subprocess.run(f"ffmpeg -i ./input/{filename} -vf subtitles=./output/{filename}/{filename}.srt ./output/{filename}/{filename}", shell=True)
        else:
        # to hardcode the subtitle, use "ffmpeg -i ./input/sample_video.mp4 -vf subtitles=./output/sample_video.mp4.srt ./mysubtitledmovie.mp4"
        # to put the subtitle in a track, use f"ffmpeg -i ./input/{filename} -i ./output/{filename}/{filename}.srt -c copy -c:s mov_text ./output/{filename}/{filename}""
            subprocess.run(f"ffmpeg -i ./input/{filename} -i ./output/{filename}/{filename}.srt -c copy -c:s mov_text ./output/{filename}/{filename}", shell=True)

    # TODO translation
finally:
    # clean the temp files
    if os.path.isdir(f"./audio/{filename}"):
        shutil.rmtree(f"./audio/{filename}")

    pass
    # TODO, use local model
    # TODO, a GUI