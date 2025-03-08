# In your terminal, first run:
# pip install openai

import os
from openai import OpenAI

XAI_API_KEY = os.getenv("XAI_API_KEY")
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)

original_language = "English"
target_language = "Chinese"

content = \
"""
"""

# basic  prompt (review after first version)
basic_prompt = \
f"""you are a professional translator that works for subtitle making. You translate according to the context and always try to sound as natural and native as possible in target language. If the jokes or meanings do not translate naturally into the target language, you understand it is better to sound natural even if the sacrifice in accuracy is big as long as the overall meanings align. Translate the following {original_language} segments into {target_language} while preserving the line structure perfectly, i.e. output line by line as the original lines were given. 
Be consistent with your translation and use English nouns if there are no good alternative(like names!). Do not output anything else but translation and indicate the start AND end of the of translation by \"@@@\".  TRANSLATE ALL THE SEGMENTS, DO NOT STOP IN THE MIDDLE.
"""
# advanced  prompt (review after first version)
advanced_prompt = \
f"""you are a professional translator that works for subtitle making. You translate according to the context and always try to sound as natural and native as possible in target language. If the jokes or meanings do not translate naturally into the target language, you understand it is better to sound natural even if the sacrifice in accuracy is big as long as the overall meanings align. Translate the following {original_language} segments into {target_language} while preserving the line structure perfectly, i.e. output line by line as the original lines were given. 
inditace the start AND end of the second version of translation by \"@@@\"
Be consistent with your translation and use English nouns if there are no good alternative(like names!). After first version of the translation, you compare it with the original version and think critically from a native chinese point of view what might improve the naturalness of the translation and start over the second version. TRANSLATE ALL THE SEGMENTS, DONOT STOP IN THE MIDDLE.
"""


completion = client.chat.completions.create(
    model="grok-2-latest",
    messages=[
        {
            "role": "system",
            "content": basic_prompt
        },
        {
            "role": "user",
            "content": content
        },
    ],
)
while True:
    try:
        completion = client.chat.completions.create(
            model="grok-2-latest",
            messages=[
                {
                    "role": "system",
                    "content": basic_prompt
                },
                {
                    "role": "user",
                    "content": content
                },
            ],
        )
        # assert completion.choices[0].message.content.split("@@@")[1].strip().count("\n") == content.strip().count("\n")
        print(completion.choices[0].message.content.split("@@@")[1].strip())
        lines = completion.choices[0].message.content.split("@@@")[1].strip()
        i = 0
        for line in lines.splitlines():
            print(f"{i}\n{line.strip()}\n\n")
            i+=1
        break
    except AssertionError:
        pass


"""
@@@
去打我吧。
你想做什么就做什么。
停下来。
停下来。
我一直想看到你这个样子。
停下来。
你很美。
你就像我想的一样美。
停下来。
放开我。
Akira。
你是最棒的。
我要每天都把你这样录下来。
停下来。
停下来。
@@@
"""