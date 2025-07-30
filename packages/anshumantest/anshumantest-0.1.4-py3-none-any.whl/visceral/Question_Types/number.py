import json

def number_question(openai_model, prompt):
        schema = """
        {
            "ask_logic": "", # Capture any "ask_if" logic that specifies when a question should be asked.
            "questionLabel": "string",  # Capture the label exactly as it appears, even is there's any text till we start the options, should be captured as it is. we dont want to lose any text at all, not even a single dot or bracket.
            "question": "string",  # Full question text with any logic in `{ logic: None }` format . YOU ARE NOT SUPPOSED TO DELETE ANYTHING COPY IT AS IT IS. 
            "extra_text": "string", # Any text that does not fit into the specified categories should be captured here. The purpose of "extra_text" is to ensure no data is lost, allowing us to retain every detail from the input text, including any text or symbols that fall outside the defined structure. (if there's any logic, then make sure to wrap it in `{logic: None}`)
            type="number"
        }
        """

        parsed_text = openai_model.client_open_ai.chat.completions.create(
            model="gpt-4o",
            temperature=0.0000000001,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information. The most important thing is that we should not delete even a single dot. You are dealing with number question type"},
                {"role": "user", "content": f"""
                
                You are a detailed survey question parser. Your task is to analyze survey questions and capture EVERY piece of text while structuring them into a specific JSON format. Follow these guidelines:

                CORE PRINCIPLES:
                1. Never delete any text. WE SHOULD NOT LOSE EVEN A SINGLE DOT. we cannot delete any text at any cost.
                 
                The schema to be used is : {schema}


                PARSING RULES:

                1. Question Label:
                - Extract the exact identifier at the start (e.g., "Q1.", "5Kn.", etc.)
                - Keep it exactly as written

                2. Question Text:
                - Include everything from the start of the question to the end.
                - For any logic/instructions, wrap them in `{{"text": None}}` format
                - Example: "Number question? (Disqualify if <18) becomes:
                "Number question? `{{"(Disqualify if <18)": None}}`"


                Capture any ask if logic in the ask_logic variable. By 'ask if' logic, I mean any statement that determines when a question should be asked

                
                SPECIAL INSTRUCTIONS:
                
                - All logic must be wrapped in `{{}}` and quoted properly
                - Keep all original spacing and formatting
                - Never remove any text, even if it seems redundant, we should be capturing each and every detail. we should not delete even a single dot.
                


                Examples:

                Input:
                ```
                Ask if Q3==0 \n
                QM. Demo number Question? Disqualify if <18 \n random text
                ```

                Output:
                {{
                    "ask_logic":"Ask if Q3==0",
                    "questionLabel": "QM",
                    "question": "Demo number Question? `{{"Disqualify if <18": None}}` \n random text",
                    "extra_text":"",
                    "type":"number",
                    
                    
                 
                }}
                
                Most Important: make sure to capture logics in the `{{}}`
                Important: the text of the options will have the complete text.
            
 
                
                CORE PRINCIPLES and MOST IMPORTANT:

                Never delete any text: Every part of the input must be accounted for. Missing even one word is a critical error.
                The most important thing is that we should not lose any text!!
                Important: please give me a valid json.
                you just have to wrap the logic in `{{}}` , if you are confused about any text if it is a logic or not, then you can just keep it in the text without wwapping it in `{{}}`
                important: if there's any logic you dont understand, just keep it as a part of the question text.
                Finally, ensure that every piece of text from the input has been captured in the JSON without any loss. If any part of the text does not fit into the defined schema, it should be included in the extra_text field. The goal is to retain all input text in its entirety.
                Parse the following survey question according to these rules: 
                 
                {prompt}
                please give me a valid json
                """
                }
            ]
        )

        content = parsed_text.choices[0].message.content
        result = json.loads(content)
        return result



def number_logic(openai_model, input_json,user_logic):
    

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information."},
            {"role": "user", "content": f"""


            You will be receving a json which has number question , your task is to understand any logics if they exist and put it in the bucket of logics we currently support. 
            We currently support :
            1. Termination logics (it can be written in any way) , you should be smart enough to understand if that word/sentence means termination
            2. Skip logics (it can be written in any way) , you should be smart enough to understand if that word/sentence means skip.
            3. User defined logics : The user might have different way of writing any logics and we've captured that.
                
            Important : The users way of writing the logic is : {user_logic} make sure to only use the words as logics which are explicitly mentioned
            please pay special attention while assigning logics. 

            You will primarily see logics captured in `{{}}`. you goal is to understand if that logic falls in the above 3 categories of logics we support for number. 
            If there's no logic that we support. (rememebr there can be mutliple ways of writing any logic, we have to be smart enough to understand the bigger picture.).But if we dont support that logic or there is no logic, just return the json as it is. without making any changes.

            But if you see that there's any logic that we support 1. Termination, 2. Skip 3. User defined logics.  then we should follow the below steps.
            if you see anything related to ranges, please create a new field called {{"data_range":[min,max]}} 
            Also , make sure to turn the value of None to True in the data_range.


            In the question if you observe any logic that we support. Then please add another field saying number_logic and the key value pair will be the following. 
            For terminating the key should be "Terminating" and the value should be conditon but the condition will only be " [logical operator] [value]" 
            For skip conditions the key would be "SKIP TO [questionLabel of the question]" value would be " [logical operator] [value] " 
            important: The logical operator that you use should be like QuestionLabel ==, >=, <=, != , or whatever the option logic says. every opertor should have questionLabel in front of it. give me the exact logic that you get. you dont have to change any logic. make it both for Terminating or SKIP questions. follow the convention of writing "==, >=, <=, != " even if the user has just one "=" we should eb using "=="
            Important: Provide the exact logic, but include the questionLabel (retrieved from the JSON) before every operator. Ensure the operators are in uppercase, like OR and AND. By questionLabel, I mean the actual value of the questionLabel field from the JSON, not the literal term questionLabel.
            We also turn the None to True if its the logic we support and we've added a field for it in our json, like we did in the below example. 
            
            

            example: you got this:

             {{     
                    "ask_logic":"Ask if Q3==0",
                    "questionLabel": "QM",
                    "question": "Demo Question? `{{"(Disqualify if QM==0)": None}}` \n random text  `{{"Range 1-2": None}}` ",
                    "extra_text":"random text",
                    "type":"number",
                    
                 
            }}

            your output will look something like this:

            {{
                    
                    "ask_logic":"Ask if Q3==0",
                    "questionLabel": "QM",
                    "question": "Demo Question? `{{"(Disqualify if QM==0)": True}}` \n random text  `{{"Range 1-2": True}}`",
                    "extra_text":"random text",
                    "data_range":[1,2],
                    "type":"number",
                    "number_logic": {{"Terminating":"QM==0"}}
                

            }}
            

            example of a logic we dont understand.
            {{      
                    "ask_logic":"Ask if Q3==0",
                    "questionLabel": "QM",
                    "question": "Demo Question? `{{"Some logic I dont know": None}}` \n random text",
                    "extra_text":"",
                    "type":"number",
                    
                 
            }}
            we will return it as it :
            {{
                    "ask_logic":"Ask if Q3==0",
                    "questionLabel": "QM",
                    "question": "Demo Question? `{{"Some logic I dont know": None}}` \n random text",
                    "extra_text":"",
                    "type":"number",
                    
                 
            }}

            Please pay special attention to the instructions for logics and make sure you mark it correctly, double check it. 
            Most Important: No data should be deletd, not even a single dot or a bracket.
            The json is :{input_json}      


                    
            please give me the correct json. 
            



            
            """
            }
        ]
    )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result

