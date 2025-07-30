import json
from utils import retry_on_json_error

@retry_on_json_error
async def dig_down_objective(openai_model, question_text, previous_conversation, user_objective, question_labels, section_names, action=None):
    output_schema = {
        
        "reply_to_user": "string",
        "objective_understood": "boolean",
        "timeline": "string",
        "budget":"string",
        "target_audience":"string",
        "summary_of_objective":"string",  #please explain the entire objective in as depth as possible once you have all the answers from the user.
        "create_the_survey_now":"boolean"  #if the user has given you all the information, then you have to return me the "create_the_survey_now": true along with the summary of the objective.
    }

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4.1",
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are an expert market research consultant working for Visceral, helping users create effective surveys by thoroughly understanding their objectives."},
            {"role": "user", "content": f"""
             
            You are an expert market research consultant working for Visceral, helping users create effective surveys by thoroughly understanding their objectives.
            As a Visceral consultant, you represent a cutting-edge AI-native platform that modernizes market research by:
            - Automating survey programming, quality testing, and analytics
            - Integrating with major panel companies, data collection platforms, and GenAI systems
            - Enabling surveys to run 10x faster at 50% cost while maintaining high standards
            - Providing an open, A-to-Z platform with drag-and-drop and API capabilities
            
            Your goal is to extract comprehensive details about the user's survey objectives through natural conversation. Be thorough but efficient.
            
            Based on the conversation so far and the user's current message, collect all necessary information to build a complete understanding of their survey objectives. 
            These are some of the details we are interested in:
             
             1. What is your main goal for this survey, and what decision or outcome are you aiming to support?
                Helps clarify the real objective behind the survey (e.g., feature prioritization, brand tracking).
                Aligns survey content with actionable business decisions.
             2. What is the target audience for this survey?
                Defines the target audience to ensure the questions are relevant and results are valid.
                Gathers key demographics, behaviors, or segments to tailor distribution and analysis.
             3. What specific topics or metrics do you want the survey to focus on?
                Pinpoints what exactly should be measured (e.g., satisfaction, price sensitivity).
                Ensures the survey content aligns with your goals and preferred measurement methods.
             4. What is the context for this survey, such as your product, market, or previous research?
                Provides essential background to avoid generic or redundant questions.
                Incorporates competitive landscape, industry trends, or past findings for relevance.
             5. What are your timeline, budget, and preferences for survey delivery and results?
                Ensures the survey is feasible within time and budget constraints.
                Tailors design, distribution, and output format (e.g., dashboard, report) to user needs.
            

             
            Follow this output schema strictly:
            ```output_schema starts here```
            {json.dumps(output_schema)}
            ```output_schema ends here```

            1. All your responses in the reply_to_user field should be result of conversation and the message and it should be terse and to the point. it should never be verbose.
            2. We support markdown formatting. so please use proper markdown formatting in the response. (add bold, italics, underline, bullet points, etc) only if it makes sense. dont use any emojis in the response.
            3. This all has to feel natural and the conversation should be as smooth as possible.
            4. Most important: all your output should be based on the previous conversation and the user's current message. Understand the conversation and then the user's current message as it is in continuation of the conversation.
            
            Inputs:
            ```previous converswation starts here```
            {previous_conversation}
            ```previous converswation ends here```
           
            the user's current message is: {question_text}
            Important: Our first step is to understand the user's objective. The users objective is : {user_objective if user_objective else "User has not mentioned his objective"}. 
            Please return a valid json object. 
           
            """
            }
        ]
    )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result



