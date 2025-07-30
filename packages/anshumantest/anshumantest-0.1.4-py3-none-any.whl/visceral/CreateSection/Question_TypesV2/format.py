import json
import asyncio

def format_text(openai_model, prompt):
    parsed_text = openai_model.client_open_ai.chat.completions.create(
            model="gpt-4o",
            temperature=0.0000000001,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information."},
                {"role": "user", "content": f"""
                You will receive an input text that contains a lot of noise. Your task is to format it properly using Markdown while ensuring that no characters (such as dots or punctuation) are lost. However, you may adjust line breaks to improve readability.
                Remember, we cannot lose any text. It's like we are copy pasting stuff but just formatting it for proper readability.
                You are not supposed to move any text, keep it whereever it was.
                please donot add anything, you just have to format it.

                Return the output in the following JSON format:
                {{
                    "mdText": "<formatted_markdown_text>"
                }}

                Input text:  
                {prompt}
"""}
            ]
        
    )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)

    return result
