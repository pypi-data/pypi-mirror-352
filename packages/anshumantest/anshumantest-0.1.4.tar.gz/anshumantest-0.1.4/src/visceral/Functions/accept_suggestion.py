import json
import asyncio
from utils import retry_on_json_error

@retry_on_json_error
async def accept_suggestion(openai_model,input_question, suggestion, correction):
    
    

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        # model="o1",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You will be receiving a question_text and a suggestion which has been accepted by the user to modify the input_question. You need to return the corrected question_text"},
            {"role": "user", "content": f"""
            You will be receiving a question_text and a suggestion which has been accepted by the user to modify the input_question. You need to return the corrected question_text
            Please return the corrected question_text in the json format.
            Please return the json in the following format:
            {{
                "corrected_question_text": "corrected_question_text"
            }}
            input_question: {input_question}
            suggestion: {suggestion} 
            {"In this special case user has agreed to accept both the correction and the suggestion, so the correction is : " + correction  if correction else "" }
            


            """
            }
        ]
    ) 

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result



