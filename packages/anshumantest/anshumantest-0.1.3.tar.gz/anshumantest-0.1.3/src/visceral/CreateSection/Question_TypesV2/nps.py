import json
from utils import retry_on_json_error

@retry_on_json_error
def nps_question(openai_model, prompt):
        schema = """
        {
            "ask_logic": "", # Capture any "ask_if" logic that specifies when a question should be asked.
            "questionLabel": "string",  # Capture the label exactly as it appears.
            "question": "string",  # Capture the main question text that we will be showing to the user taking the survey.
            type="nps"
        }
        """

        parsed_text = openai_model.client_open_ai.chat.completions.create(
            model="gpt-4o",
            temperature=0.0000000001,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information. The most important thing is that we should not delete even a single dot. You are dealing with nps question type"},
                {"role": "user", "content": f"""
                You are a detailed survey question parser.
                The schema to be used is : {schema}


                 You are a detailed survey question parser. 
         
                
                Parsing Rules:
                
                1. Question Label:  
                - Extract the exact identifier at the start (e.g., "Q1.", "5Kn.", etc.).  
                - Keep it exactly as written.  

                2. Question Text:  
                - The question_text in sync_json should be used in the question field of the json.   

                3. Ask If Logic:  
                - Capture any "ask if" condition that determines when a question should be asked.  
                - Store this in the `ask_logic` field.  

              
                Examples:

                Input:
                ```
                Ask if Q3==0 \n
                QM. Demo Question? Disqualify if QM=="XYZ" \n random text
                ```

                Output:
                {{
                    "ask_logic":"Ask if Q3==0",
                    "questionLabel": "QM",
                    "question": "Demo Question?",
                    "type":"nps",
                    
                 
                }}
                
               
                Important: please give me a valid json.
           
               
                Parse the following survey question according to these rules:  {prompt}
                 
               
                """
                }
            ]
        )

        content = parsed_text.choices[0].message.content
        result = json.loads(content)
        return result


@retry_on_json_error
def nps_logic(openai_model, input_json,user_logic,input_text):
    

    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information."},
            {"role": "user", "content": f"""
            

            You will receive a JSON containing a single-text question. 
            Your task is to identify and categorize any logic present, ensuring it falls within our supported logic types:

            1. Termination Logics: If the text explicitly indicates termination (e.g., disqualify, end survey etc), assign it accordingly.  
            2. Skip Logics: If the text explicitly mentions skipping to another question, classify it as "Skip" logic.  
            3. User-Defined Logics: Use the predefined logic structure provided by the user.  

            Important:  
            - The user's way of writing logic is: {user_logic}.  
            - Only use explicitly mentioned words as logic do not infer or introduce new logic.  
            - Pay close attention when identifying and assigning logic categories.  

            If there's no logic that we support. (rememebr there can be mutliple ways of writing any logic, we have to be smart enough to understand the bigger picture.).But if we dont support that logic or there is no logic, just return the json as it is. without making any changes.

            But if you see that there's any logic that we support 1. Termination, 2. Skip 3. User defined logics.  then we should follow the below steps.
            In the question if you observe any logic that we support. Then please add another field saying nps_logic and the key value pair will be the following. 
            For terminating the key should be "Terminating" and the value should be conditon but the condition will only be " [logical operator] [value]" 
            For skip conditions the key would be "SKIP TO [questionLabel of the question]" value would be " [logical operator] [value] " 
            important: The logical operator that you use should be like QuestionLabel ==, >=, <=, != , or whatever the option logic says. every opertor should have questionLabel in front of it. give me the exact logic that you get. you dont have to change any logic. make it both for Terminating or SKIP questions. follow the convention of writing "==, >=, <=, != " even if the user has just one "=" we should eb using "=="
            Important: Provide the exact logic, but include the questionLabel (retrieved from the JSON) before every operator. Ensure the operators are in uppercase, like OR and AND. By questionLabel, I mean the actual value of the questionLabel field from the JSON, not the literal term questionLabel.
           
            If no supported logic is found (remember, there can be multiple ways of writing the same logic, and we need to smartly understand the bigger picture), then do not make any changes to the JSON. If no logic is supported or there is no logic at all, simply return the JSON as it is.
            However, if any logic that we support is identified (1. Termination, 2. Skip, or 3. User-defined logics), please follow these steps:
            1. Adding Logic to the JSON:
            - If you observe any logic that we support, add a new field called `"nps_logic"` with the following format:
            
                - For Termination Logic:
                - The key should be "Terminating".
                - The value should be the condition, formatted as `"[logical operator] [value]"`.
                
                - For Skip Logic:
                - The key should be `"SKIP TO [questionLabel]"`.
                - The value should be `"[logical operator] [value]"`.
                
            2. Logical Operators:
            - The logical operator should always be written with the questionLabel in front of it, as shown in the example below.
            - Operators such as `==`, `>=`, `<=`, and `!=` must be used, even if the user provided only one `=`.
            - Ensure the operators are in uppercase (e.g., `==`, `>=`, `<=`, `!=`).
            - Do not change the logic; provide the exact logic found in the original input.

            3. Example of Logic Handling
            - The logic should be formatted as follows:



             {{
                    "questionLabel": "QM",
                    "question": "Demo Question?",
                    "type":"nps",
                    "ask_logic":"Ask if Q3==0",
                 
            }}

            raw input text had: (Disqualify if QM=="XYZ")
            your output will look something like this:

            {{
            
            "questionLabel": "QM",
            "question": "Demo Question?",
            "type":"nps",
            "nps_logic": {{"Terminating":"QM=="XYZ"}}
            "ask_logic":"Ask if Q3==0",
            
            }}
            

            example of a logic we dont understand.
            {{
                    "questionLabel": "QM",
                    "question": "Demo Question?",
                    "type":"nps",
                    "ask_logic":"Ask if Q3==0",
                 
            }}
            the input text had something that we dont understand. so we will return it as it :
            
            {{
                    "questionLabel": "QM",
                    "question": "Demo Question? `{{"Some logic I dont know": None}}` \n random text",
                    "type":"nps",
                    "ask_logic":"Ask if Q3==0",
                 
            }}

            Important: There can be multiple logics in the nps_logic field, so ensure that you add all the logics you can infer from the provided data.
            Please pay special attention to the instructions for the logics and double-check the logic marking to ensure correctness.
            Your task is to return the valid JSON after applying the logics.
      
            The input JSON is: {input_json}
            The input raw text is :{input_text} 
            
            """
            }
        ]
    )

    content = parsed_text.choices[0].message.content
    result = json.loads(content)
    return result

