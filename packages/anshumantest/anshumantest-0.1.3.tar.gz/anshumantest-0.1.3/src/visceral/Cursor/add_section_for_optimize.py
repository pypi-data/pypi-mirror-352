import json
from utils import retry_on_json_error

@retry_on_json_error
def add_section_for_optimize(openai_model, prompt, block_names, previous_conversation_for_sections):
        
    output_schema = {         
    "section_name":"string", # recommend me the name of the section we are creating, keep in mind that the name should be unique and not repeated. I am sharing with you a list of sections names that already exist in the survey.
    "number_of_questions":"integer", # the number of questions we are creating, example 10
    "details_about_section":"string" # detailed information about the section we are creating, include as many details as possible including any terminates we should focus on etc.
    }
    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
                {"role": "system", "content": "You are an expert in creating survey questions and sections. You are given a user's objective and you have to create a section of questions that can be used to accomplish the objective."},
                {"role": "user", "content": f"""
You are an expert in creating survey questions and sections. You are given a user's objective and you have to create a section of questions that can be used to accomplish the objective.You represent Visceral, a cutting-edge AI-native platform that modernizes market research by automating survey programming, quality testing, and analytics. Visceral integrates with major panel companies, data collection platforms, and GenAI systems, enabling surveys to run 10x faster at 50% cost while maintaining high standards for market researchers. It’s an open, A-to-Z platform with drag-and-drop and API capabilities, designed for rapid adoption without disrupting existing workflows or vendors.
Your role is to assist users in optimizing a survey within Visceral’s platform, you are basically rewriting the section we are creating. we are bascially optimizing the survey.
You are helping to optimize the survey based on the previous conversation and user's input.
1. Adding a new section with questions in it.
                 

Some rules to follow:
1. Keep the introduction minimal and high-level.
2. First section usually should be a screener section.
3. Organize questions into clear, thematic sections.
4. Each question should focus on one topic only (no double-barreled questions)
5. Avoid Yes/No questions unless asking about factual information (to reduce bias).
6. Use response options that are mutually exclusive and exhaustive.
7. Avoid jargon or technical terms — keep language simple and clear.
8. Randomize list options when appropriate (not for items that follow a natural sequence).
9. Avoid overusing MaxDiff, grid question- use sparingly. max of 1 max-diff and a couple of grid questions in the survey
10. When appropriate, ask about both current behavior/perceptions and future expectations.
                 
your goal is to tell how many questions you think will be best fit for the section we are creating based on the previous conversation and user's input. add it in the number_of_questions field. keep in mind that we are optimizing the survey based on the previous conversation and user's input.
The list of sections names that already exist in the survey are: {block_names}
please give me a valid response in a json format.
The deatils about the section we are creating are: {prompt}
the previous conversation is, understand what we would like to do... {previous_conversation_for_sections}
follow this output schema strictly:
{json.dumps(output_schema)}


                """
                }
            ]
        )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result


