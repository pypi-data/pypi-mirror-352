import json
from utils import retry_on_json_error

@retry_on_json_error
def fix_post_validation(openai_model, input_text):
    template = """
{ 
"corrections": [
{"question_label" : "suggested_change"},  
{"question_label" : "suggested_change"}
]
}
    """
    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4.1",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a specialized agent responsible for extracting the question labels and the suggested changes from the input text."},
            {"role": "user", "content": f"""
You will be receiving a text, please extract the question labels and the question text from the text.
the question label is the unique identifier for the question in the survey.(like Q1, Q2, Q3, etc.) (It can be anything though)
The suggested change will be mentioned in the input text. please extract it. your task is to extract the question label and the suggested change.
please give me a valid response in a json format.
please follow this output schema strictly:
{json.dumps(template)}

The input text is : {input_text}
            """}
        ]
    )
    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result