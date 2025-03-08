import json
import os
from translation import translate
from utils.formatting import seconds_to_str_in_srt

DEBUG = True
IF_FUSE = True
FUSE_TYPE = 2 # whether to integrate the subtitle file into the video file
FUSE_DICT = {1: "hardcode", 2: "track"}
TRANSLATION = "zh"
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

filename = "jap_sample_full_with_whisper_prompt.mp4"
if not os.path.isdir(f"./output/{filename}/"): # make sure output folder exists
    os.makedirs(f"./output/{filename}/")
last_segment_ended_at = 0
index = 1
for i in range(0, 11):
    with open(f"./data/{filename}_data_{i}.json", 'r', encoding="utf-8") as f:
        transcription_data = json.loads(f.read())
    print("load json file")
    segments = transcription_data["segments"]


    with open(f'./output/{filename}/{filename}_plg3.srt', 'a', encoding='utf-8') as f: # processing each chunked file
        while len(segments) > 0:
            lines = segments[:15]
            segments = segments[15:]
            print("partitioned lines")
            for line in lines:
                if line["text"].strip() == "":
                    with open(f'./error.log', 'a', encoding='utf-8') as e:
                        e.write(f"{line}\n")
            print("before translation")
            if ORIGINAL_LANGUAGE != "NONE":
                translated_lines = translate("\n".join([line["text"].strip() for line in lines]), TRANSLATION_LIST[TRANSLATION], TRANSLATION_LIST[ORIGINAL_LANGUAGE])
            else:
                translated_lines = translate("\n".join([line["text"].strip() for line in lines]), TRANSLATION_LIST[TRANSLATION])
            print("after translation")
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
    last_segment_ended_at += transcription_data["duration"]
    print("added duration", transcription_data["duration"])