import json
from utils import retry_on_json_error

@retry_on_json_error
def initiate_survey(openai_model, prompt):
        
    output_schema = { "questions_to_add": [
        {
        "response": "string",
        "question_text": "string" # (markdown formatted)
        },
        {
        "response": "string",
        "question_text": "string" # (markdown formatted)
        }, 
    
    ]}
    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
                {"role": "system", "content": "You are a helpful assistant that can add questions to a survey."},
                {"role": "user", "content": f"""
You are a helpful text editor chatbot for Visceral, a cutting-edge AI-native platform that modernizes market research by automating survey programming, quality testing, and analytics. Visceral integrates with major panel companies, data collection platforms, and GenAI systems, enabling surveys to run 10x faster at 50% cost while maintaining high standards for market researchers. It’s an open, A-to-Z platform with drag-and-drop and API capabilities, designed for rapid adoption without disrupting existing workflows or vendors.
Your role is to assist users in adding a screener section to a survey. please give me an introductory line 
please give me a valid response in a json format.
the user's message is: {prompt}
follow this output schema strictly:
{json.dumps(output_schema)}


                """
                }
            ]
        )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result


