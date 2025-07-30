import json
from utils import retry_on_json_error

@retry_on_json_error
def optimize_survey_instructions(openai_model, user_instructions, section_and_question_details, previous_conversation):
        
    output_schema = {         
    "optimize_instructions":"string"
    }
    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
                {"role": "system", "content": "You are an expert survey designer and you specialise in optimizing surveys based on the user's instructions."},
                {"role": "user", "content": f"""
                 
You are an expert survey designer specializing in optimizing surveys based on user instructions.
User's Instructions: {user_instructions}
Current Section and Question Details: {section_and_question_details}
Previous Conversation: {previous_conversation}

Your task is to provide a high-level plan for optimizing the survey according to the user's goals.
You may suggest adding or deleting sections, or modifying the number of questions within sections.
Keep the plan lightweight and conceptual — do not make it too detailed or exhaustive.
Ensure your response flows naturally and could be easily integrated into an ongoing conversation.


Important:
Follow this output schema exactly: {json.dumps(output_schema)}
Return your response strictly in valid JSON format.

we follow markdown format, our goal is to create a survey that can accomplish the users objective. you can get an idea about the user's objective from the previous conversation.
we need to optimize the survey based on the user's instructions making sure it matches the user's objective.
give me a valid response in a json format.

Also, please keep your response concise and to the point. no need to give each and every detail. just give me a 4-5 bullet points of how you think we can optimize the survey.
We follow markdown format.
Keep you response to the point and concise.
                """
                }
            ]
        )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result


