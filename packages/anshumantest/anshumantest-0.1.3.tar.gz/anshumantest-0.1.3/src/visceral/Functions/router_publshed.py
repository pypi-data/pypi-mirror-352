import json
from utils import retry_on_json_error

@retry_on_json_error
async def router_prompt_published(openai_model, question_text, previous_conversation, user_objective, question_labels, action=None, survey_link=None):
    output_schema = {
        "reply_to_user": "string",
    }

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        # stream=True,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a routing mechanism specialist that bascially helps in conversing with the user and also routing to the appropriate function based on the user's input."},
            {"role": "user", "content": f"""
            You specialise in undestanding the natural language of the user, you are text editor chatbot for Visceral, a cutting-edge AI-native platform that modernizes market research by automating survey programming, quality testing, and analytics. Visceral integrates with major panel companies, data collection platforms, and GenAI systems, enabling surveys to run 10x faster at 50% cost while maintaining high standards for market researchers. It’s an open, A-to-Z platform with drag-and-drop and API capabilities, designed for rapid adoption without disrupting existing workflows or vendors 
             We are dealing with the user's conversation and current message, your goal is to understand the users message and your conversation and then route the user to appropriate function (if we support it) based on the user's current message.
             we currently support the following categories: 
             1. Create a survey from an objective
             2. Add a new question
             3. Update an existing question from text editor (only the text editor, not from chat)
             4. Delete an existing question
             5. Add a new section
             6. Edit a question
             7. Set quotas

            
             We currently donot support the following categories:
             1. Add a new question to a particular section or in between two questions.
             2. we also do not support deleting multiple questions at once.. we can only delete one question at a time. and question with question labels.
            
            Important: the catch here is that the survey has already been published now. so we cannot do any of the actions. but we need to reply to the user accordingly. so just make sure you reply to the user accordingly. and let him know that they cannot change or do anything as the survey is published.. but please make sure to reply the user's message accordingly.
            The user can now go and share the link with the public and start collecting responses.
            Also, the user can see the results in the results section and use the Natural Language to interact with the results or generate ppt's etc.
             
             the survey is now shared on: {survey_link}

             Platform details: 
             Now that the survey is published, you can view results in the Analytics tab and use Natural Language to interact with the data or generate presentations (e.g., PowerPoints). To edit quotas, click the weighing scale icon next to the Preview button in the header. Currently, quota editing is not supported through chat. In the left pane, you’ll find three tabs: Responses, Analytics, and Questions.


             
            This all has to feel natural and the conversation should be as smooth as possible.
            
            
      
            Follow this output schema strictly:
            ```output_schema starts here```
            {json.dumps(output_schema)}
            ```output_schema ends here```
            please give me valid json
            we support markdown formatting. so please use proper markdown formatting in the response. (add bold, italics, underline, bullet points, etc) only if it makes sense. dont use any emojis in the response.
            all your responses should be a result of the conversation and the message.
           
             Inputs:
            ```previous converswation starts here```
            {previous_conversation}
            ```previous converswation ends here```
            the user's current message is: {question_text}
            
            """
            }
        ]
    )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result



