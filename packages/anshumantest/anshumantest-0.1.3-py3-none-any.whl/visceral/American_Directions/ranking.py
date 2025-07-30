import json
from utils import retry_on_json_error


@retry_on_json_error
def ranking_question_AMI(oepnai_model, prompt,sync_layer, general_tagged):
        schema = """
        {
            "ask_logic": "", # Capture any "ask_if" logic that specifies when a question should be asked.
            "questionLabel": "string",  # Capture the label exactly as it appears.
            "question": "string",   # Capture the main question text that we will be showing to the user taking the survey.
            "options": [  # List of options (if any) with their associated logic if any
                {"full_option_text": "None"}
            ],
            "type":"ranking"
            "keymap": "string"
        }
        """

        parsed_text = oepnai_model.client_open_ai.chat.completions.create(
            model="gpt-4o",
            temperature=0.0000000001,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are processing survey questions and will receive raw question text. Your task is to structure the question into a JSON format`"},
                {"role": "user", "content": f"""
                You are a detailed survey question parser. 

                The schema to be used is: {schema}
                Sync_json guides you on capturing question_text (which maps to question in our JSON), logics, and options. Use the provided output as a reference to ensure proper mapping. Your output must align with it, especially for question, options, and logics. sync_json is : {sync_layer}.
                
                Parsing Rules:
                
                1. Question Label:  
                - Extract the exact identifier at the start (e.g., "Q1.", "5Kn.", etc.).  
                - Keep it exactly as written.  

                2. Question Text:  
                - Capture the entire  question text. (even if it contains (Donot Ask) everything in the question text should be captured

                3. Ask If Logic:  
                - Capture any "ask if" condition that determines when a question should be asked.  
                - Store this in the `ask_logic` field.  

                4. Options:
                - Be smart enough to understand the options from the text.
                - Create a list of dictionaries where each option is a key and value as None
                - example {{"Option text": None}}
                - example {{"Option text (Skip to Q4)": None}}
                - example: {{"Option text Terminate": None}}
                Important: If options have numbers in front of them, use the order the numbers indicate:

                For 04. a 03. b 02. c 01. d, capture the order as (d, c, b, a) (descending).
                For 01. a 02. b 03. c 04. d, capture the order as (a, b, c, d) (ascending).

                Make sure to follow the order as mentioned in the input text if it has the numbering in front of it.
                
                

                5. Piping Logic

                If a question explicitly references options from a previous question, add a "piping" field. any question, which asks to fill it's options from previous question it means it is a a piping question. then please add a field piping with a dictionary where the  key is the questionLabel from which we have to fetch responses. and value could be any from these 4: [show selected, show not selected, hide selected, hide not selected].
                for example . you see something like this in a text: "Show all selected in QM. " then your json will have a field like : piping : {{"QM":"show selected" }}
                

                6. Port in response 
                
                If a question text references a previous question and requests to "pipe in" or "port in" results, follow these steps:
                Identify the referenced question.
                Example: If the prompt states:
                "Q3. Why do you like (port in response from Q2)?"
                Replace the placeholder with {{Q2}}, so the question becomes:
                "Why do you like {{Q2}}?"
                Ensure the label (e.g., Q2) matches the format of the referenced question.
                If the reference uses terms like "Recall #2" or similar, replace it with the corresponding question label in the format {{Q2}} (not {{Recall #2}}).
                Use the exact question label (e.g., Q2) as defined in the context.
                Do not include extra text or reference terms; only use the question label.

                7. Please capture the text after 'Ref' if it is given in the input text into a field called 'Ref'. For example, if the input text contains 'Ref:PHONEINTRO', then your output should include 'Ref': 'PHONEINTRO'.
            
                

                Examples:

                Input:
                ```Ask if Qn==1 \n
                QM. Demo Question (Disqualify if <1) Randomize \n random text
                1. option a 
                2. option b 
                3. option c 
                
                ```

                Output:
                {{
                    "ask_logic":"Ask if Qn==1",
                    "questionLabel": "QM",
                    "question": "Demo Question?",
                    "options": [
                        {{"option a ": None}},
                        {{"option b ": None}},
                        {{"option c ": None}}
                    ],
                    "type":"ranking",
                }}
                
        
                
             
                Important: please give me a valid json.
                Also, here are some special mentions by the user: pay special attention and include them as well: {general_tagged}.
                Parse the following survey question according to these rules: {prompt}
                """
                }
            ]
        )

        content = parsed_text.choices[0].message.content
        result = json.loads(content)
        return result


@retry_on_json_error
def ranking_logic_AMI(openai_model, input_json,user_logic, logic_tagged):
    

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information."},
            {"role": "user", "content": f"""
            
            You will be receving a json which has ranking question , your task is to understand any logics if they exist and put it in the bucket of logics we currently support. 
            We currently support :
            1. Termination logics (it can be written in any way) , you should be smart enough to understand if that word/sentence means termination
            2. Skip logics (it can be written in any way) , you should be smart enough to understand if that word/sentence means skip.
            3. User defined logics : The user might have different way of writing any logics and we've captured that.
             
            You are not supposed to make any changes in the options.
                
            Important : The users way of writing the logic is : {user_logic} make sure to only use the words as logics which are explicitly mentioned
            please pay special attention while assigning logics. 

            You will primarily see logics captured in `{{}}`. you goal is to understand if that logic falls in the above 3 categories of logics we support for the ranking. 
            If there's no logic that we support. (rememebr there can be mutliple ways of writing any logic, we have to be smart enough to understand the bigger picture.).But if we dont support that logic or there is no logic, just return the json as it is. without making any changes.

            But if you see that there's any logic that we support 1. Termination, 2. Skip 3. User defined logics.  then we should follow the below steps.


            In the question if you observe any logic that we support. Then please add another field saying multi_text_logic and the key value pair will be the following. 
            For terminating the key should be "Terminating" and the value should be conditon but the condition will only be " [logical operator] [value]" 
            For skip conditions the key would be "SKIP TO [questionLabel of the question]" value would be " [logical operator] [value] " 
            important: The logical operator that you use should be like QuestionLabel ==, >=, <=, != , or whatever the option logic says. every opertor should have questionLabel in front of it. give me the exact logic that you get. you dont have to change any logic. make it both for Terminating or SKIP questions. follow the convention of writing "==, >=, <=, != " even if the user has just one "=" we should eb using "=="
            Important: Provide the exact logic, but include the questionLabel (retrieved from the JSON) before every operator. Ensure the operators are in uppercase, like OR and AND. By questionLabel, I mean the actual value of the questionLabel field from the JSON, not the literal term questionLabel.
            We also turn the None to True if its the logic we support and we've added a field for it in our json, like we did in the below example. 
            

            example: you got this:

             {{     
                    "ask_logic":"Ask if Q3==0",
                    "questionLabel": "QM",
                    "question": "Demo Question? `{{"(Disqualify if QM=="XYZ")": None}}` \n random text",
                    "options": [
                        {{"option a ": None}},
                        {{"option b ": None}},
                        {{"option c ": None}}
                    ],
                    "extra_text":"",
                    "type":"ranking",
                    
                    
                 
            }}

            your output will look something like this:

            {{  
                    "ask_logic":"Ask if Q3==0",
                    "questionLabel": "QM",
                    "question": "Demo Question? `{{"(Disqualify if QM=="XYZ")": True}}` \n random text",
                    "type":"ranking",
                    "options": [
                                {{"option a ": None}},
                                {{"option b ": None}},
                                {{"option c ": None}}
                            ],
                    "extra_text":"",
                    "type":"ranking",
                    "ranking_logic": {{"Terminating":"QM=="XYZ"}}
            
            }}
            

            example of a logic we dont understand.
            {{
                    "ask_logic":"Ask if Q3==0",
                    "questionLabel": "QM",
                    "question": "Demo Question? `{{"Some logic I dont know": None}}` \n random text",
                    "type":"ranking",
                    "options": [
                        {{"option a ": None}},
                        {{"option b ": None}},
                        {{"option c ": None}}
                    ],
                    "extra_text":"",
                    "type":"ranking",
                 
            }}
            we will return it as it :
            {{
                    "ask_logic":"Ask if Q3==0"
                    "questionLabel": "QM",
                    "question": "Demo Question? `{{"Some logic I dont know": None}}` \n random text",
                    "type":"ranking",
                    "options": [
                        {{"option a ": None}},
                        {{"option b ": None}},
                        {{"option c ": None}}
                    ],
                    "extra_text":"",
                    "type":"ranking",
                 
            }}

            Please pay special attention to the instructions for logics and make sure you mark it correctly, double check it. 
            Most Important: No data should be deletd, not even a single dot or a bracket.
            please give me the correct json. 
            Make sure to properly tag all special instructions without missing any. These instructions are crucial and must always be categorized correctly. Here are the instructions: {logic_tagged}
            The json is :{input_json}      


                    
            
            """
            }
        ]
    )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result

