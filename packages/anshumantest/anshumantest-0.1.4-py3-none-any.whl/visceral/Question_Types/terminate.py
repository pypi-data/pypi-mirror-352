import json

def terminate_question(openai_model, prompt):
        schema = """
        {
            "ask_logic": "", # Capture any "ask_if" logic that specifies when a question should be asked.
            "questionLabel": "string",  # Capture the label exactly as it appears, even is there's any text till we start the options, should be captured as it is. we dont want to lose any text at all, not even a single dot or bracket.
            "question": "string",  # Full question text with any logic in `{ logic: None }` format . YOU ARE NOT SUPPOSED TO DELETE ANYTHING COPY IT AS IT IS. 
            type="terminate"
        }
        """

        parsed_text = openai_model.client_open_ai.chat.completions.create(
            model="gpt-4o",
            temperature=0.0000000001,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information. The most important thing is that we should not delete even a single dot. You are dealing with transition question type"},
                {"role": "user", "content": f"""
                 
                
                You are a detailed survey question parser. Your task is to analyze survey questions and capture EVERY piece of text while structuring them into a specific JSON format. Follow these guidelines:

                CORE PRINCIPLES:
                1. Never delete or modify any text. WE SHOULD NOT LOSE EVEN A SINGLE DOT. we cannot delete any text at any cost.
                2. Preserve the exact structure and formatting
                3. DONOT EVEN DELETE A SINGLE BRACKET.

                PARSING RULES:

                1. Question Label:
                - Extract the exact identifier at the start (e.g., "Q1.", "5Kn.", etc.)
                - Keep it exactly as written

                2. Question Text:
                - Include everything from the start of the question to just before the options start (if they exist). anything and everything, even if it doent make sense will be a part of the question text.
                - Even random or unrelated text must be part of the question.
                - For any logic/instructions in parentheses or brackets, wrap them in `{{"text": None}}` format
                - Example: "What is your name? " becomes:
                "What is your name? "
                Schema would be: {schema}

                

                Important : Capture any ask if logic in the ask_logic variable. By 'ask if' logic, I mean any statement that determines when a question should be asked. Capture it as it is. 
                Important:  No need to capture ask if ogic in the question text.
                
                SPECIAL INSTRUCTIONS:
                
                
   
                - Keep all original spacing and formatting
                - Never remove any text, even if it seems redundant, we should be capturing each and every detail. we should not delete even a single dot.
                - Capture ALL parenthetical or bracketed instructions in dictionary format.

                the text should be captured as it is, we should not change even a single dot.
                
                CORE PRINCIPLES and MOST IMPORTANT:

                Never delete or modify any text: Every part of the input must be accounted for. Missing even one word is a critical error.
                Preserve structure and format: The output must follow the specified JSON schema exactly.
                please add "type":"terminate" to the json
                The most important thing is that we should not lose any text!!
                Most important: Dont get stuck, if by any chance you're confused give me whatever you understand. just dont delete anything and dont be stuck
                Parse the following survey question according to these rules:  {prompt}
                """
                }
            ]
        )

        content = parsed_text.choices[0].message.content
        result = json.loads(content)
        return result



# def single_text_logic(self, input_json,user_logic):
    

#     parsed_text = self.client_open_ai.chat.completions.create(
#         model="gpt-4o",
#         temperature=0.0000000001,
#         response_format={ "type": "json_object" },
#         messages=[
#             {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information."},
#             {"role": "user", "content": f"""
            



#             You will be receving a json which has single_text question , your task is to understand any logics if they exist and put it in the bucket of logics we currently support.
#             we currently just support termination and skip logics on single_text questions.
                
            
#             be sure to smartly understand what the user is trying to mean with that option. There can be multiple ways to say all these logics.
#             Important : Apart from that: Ill be sharing with you the users way of writing a logic for the survey. So you should be smart enough to understand what the user is trying to say and then make our json.
#             Important : The users way of writing the logic is : {user_logic} make sure to only use the words as logics which are explicitly mentioned
#             please pay special attention while assigning logics. 

#             For complete and disqualify -> we will use "THANK AND END" in our final json that we produce and for skip we use "SKIP TO [qstnLabel]" . 

#             In the question if you observe any logic associated with it. please add another field saying text_logic and for the key,value pair. For terminating the key should be Terminating and the value should be conditon but the condition will only be " [logical operator] [value]" and for skip conditions the key would be [ SKIP TO [qstnLabel] value would be " [logical operator] [value] " . 
#             The logical operator that you use should be like QuestionLabel ==, >=, <=, != , or whatever the option logic says. every opertor should have questionLabel in front of it. give me the exact logic that you get. you dont have to change any logic. make it both for Terminating or SKIP questions. Important: give me the exact logic but with questionLabel (pick it up from json) in front of every operator. keep the operators in capital like "OR"."AND". also by questionLabel : I mean the questionLabel of the question. and not "questionLabel".
                
#             Be sure to understand how a user writes the logic. 
#             Use you general understanding and the user_logic way of writing the logic. 
#             Also, if the logic is not in english. please understand it properly
        
#             Very Important: You are not supposed to add any new options on your own, just deal with whatever you have.
             
#             Most Important: No data should be deletd, not even a single dot.
#             Please pay special attention to the instructions for logics and make sure you mark it correctly, double check it. 
#             Important: Donot even delete a single bracket.
#             Most Important: No data should be deletd, not even a single dot.
#             The json is :{input_json}      


                    
#             please give me the correct json. 
#             """
#             }
#         ]
#     )

#     content = parsed_text.choices[0].message.content
#     result = json.loads(content)
#     return result

