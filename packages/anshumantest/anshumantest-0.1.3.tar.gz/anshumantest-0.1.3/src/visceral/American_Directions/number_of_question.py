import json
from utils import retry_on_json_error

@retry_on_json_error
def identify_number_of_questions(openai_model, prompt):
    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a specialized agent that identifies the number of questions in the input."},
            {"role": "user", "content": f"""
                Given the following input text, identify the number of distinct questions.  
                A question is typically prefixed with a **question label** such as (QMk, Qk. etc.). the label can be anything be smart to identify the number of question.
                Exercise your judgment to understand the number of questions in the input text. You are dealing with survey questions.   
                Your task is to accurately count and return the total number of questions.  
                

                Return the result as a JSON object in the following format:  
                {{
                    "number_of_questions": int
                }}

                Input text:  {prompt}
            """}
        ]
    )
    
    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result
