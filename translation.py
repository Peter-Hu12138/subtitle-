# In your terminal, first run:
# pip install openai

import os
from openai import OpenAI

XAI_API_KEY = os.getenv("XAI_API_KEY")
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)
def translate(content: str, target_language: str, original_language: str = "(please detect it yourself)") -> str:
    n = content.strip().count("\n") + 1
    print(f"translated # of lines:{n}")
    # TODO: implement a fail save system
    # basic  prompt (review after first version)
    basic_prompt = \
    f"""You are a professional translator tasked with translating text from {original_language} to {target_language}. Your translations must be contextually accurate, natural, and fluent in {target_language}. If idioms, jokes, or cultural references don’t translate directly, adapt them to sound native in {target_language} while preserving the intended meaning, even if some literal details are adjusted.

### Instructions
- Translate the following {original_language} segments into {target_language}.
- Keep the exact line structure: since INPUT HAS {n} LINE, the output MUST have {n} lines.
- Your output MUST have {n} lines.
- Your output MUST have {n} lines.
- Your output MUST have {n} lines.
- Translate all text into {target_language}, regardless of its original language.
- Use consistent wording for repeated terms across the translation.
- Double-check for grammatical accuracy and natural phrasing in {target_language}.
- Double-check for line strcture: your output MUST have {n} lines.
- Output only the translation, nothing else.
- Mark the start and end of the translation with "@@@".

### Example (from English to Spanish)
**Input (English):**
It’s raining cats and dogs.  
The early bird catches the worm.  
**Bold move**, my friend!

**Output (Spanish):**
@@@
Está lloviendo a cántaros.  
El que madruga encuentra.  
**Movida audaz**, ¡amigo mío!  
@@@
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
        temperature=0.6,
    )
    for i in range(0, 3):
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
            response = completion.choices[0].message.content.split("@@@")[1].strip()
            assert response.count("\n") == content.strip().count("\n")
            print(response)
            return response
        except AssertionError:
            print("translation line numbers dont match, retrying")
            print("content:")
            print(content)
            print("translation:")
            print(response)
            print("end")
    print("failing 3 times in a row, giving up and force adjusting line number")
    if response.count("\n") > content.strip().count("\n"):
        response = "\n".join(response.splitlines()[:n])
        print("too many line!")
    elif response.count("\n") < content.strip().count("\n"):
        response_lines = response.count("\n") + 1
        response = "\n".join(response.splitlines() + [response.splitlines()[-1] for i in range(n - response_lines)])
        print("too less line")
    print("adjust line number:")
    print("content:")
    print(content)
    print("translation:")
    print(response)
    print("end")
    assert response.count("\n") == content.strip().count("\n")
    return response