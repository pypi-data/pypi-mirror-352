import json
from utils import retry_on_json_error

@retry_on_json_error
def contact_form_question(openai_model, prompt):
        schema = """
        {
            "ask_logic": "", # Capture any "ask_if" logic that specifies when a question should be asked.
            "questionLabel": "string",  # Capture the label exactly as it appears.
            "question": "string",  # Capture the main question text that we will be showing to the user taking the survey, donot capture unnecessary stuff that we wont be showing to the user.
            "type": "contact_form",
            "contact_form": []
        }
        """

        parsed_text = openai_model.client_open_ai.chat.completions.create(
            model="gpt-4o",
            temperature=0.0000000001,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are processing survey questions and will receive raw question text. Your task is to structure the question into a JSON format. "},
                {"role": "user", "content": f"""
                
                You are a survey question parser. Your task is to extract structured information from survey questions and return a valid JSON output following the schema below: 

                Schema:
                ```json
                {schema}
                ```
          
                
                PARSING RULES
                1. Question Label:  
                - Extract the exact identifier at the start (e.g., "Q1.", "5Kn.", etc.).  
                - Keep it exactly as written, with original spacing and punctuation.  

                2. Question Text:  
                - The question_text in sync_json should be used in the question field of the json. 

                3. Contact Form Fields:  
                - If the type is "contact_form", extract requested contact details into `contact_form` as a list of specific labels:  
                  ["First Name", "Last Name", "Phone", "Email"]  
                - Standardize variations into the correct labels:  
                  - "email address" → "Email"  
                  - "ph.No." → "Phone"  
                  - "surname" → "Last Name"  
                  - Any mention of a name split into "First Name" and "Last Name" accordingly.  

                4. 'Ask If' Logic:  
                - Capture any logic that determines when a question should be asked inside `"ask_logic"`.  
                - If no such logic exists, return `"ask_logic": ""`.  

                Examples
                Example 1:
                Input:
                ```
                (Ask if Qn=03) 
                QM. Demo Question for contact form? (Disqualify if name=="XYZ") 
                Email id
                ```

                Output:
                ```json
                {{
                    "ask_logic": "Ask if Qn=03",
                    "questionLabel": "QM",
                    "question": "Demo Question for contact form?",
                    "type": "contact_form",
                    "contact_form": ["Email"]
                }}
                ```

                Example 2:
                Input:
                ```
                QM. Demo Question? Skip if name=='XYZ' 
                ```

                Output:
                ```json
                {{
                    "ask_logic": "",
                    "questionLabel": "QM",
                    "question": "Demo Question?",
                    "type": "contact_form",
                    "contact_form": []
                }}
                ```

                IMPORTANT:  
                - Return valid JSON that follows the schema exactly.  
                - Always use the exact contact form labels listed.  
                Now, parse the following question according to these rules:  
                ```{prompt}```
                """
                }
            ]
        )
       
        content = parsed_text.choices[0].message.content
        result = json.loads(content)
        return result



# def contact_form_logic(self, input_json,user_logic):
    

#     parsed_text = self.client_open_ai.chat.completions.create(
#         model="gpt-4o",
#         temperature=0.0000000001,
#         response_format={ "type": "json_object" },
#         messages=[
#             {"role": "system", "content": "You are a precise survey question parser that captures every detail without losing any information."},
#             {"role": "user", "content": f"""
            
#             You will be receving a json which has contact_form question , your task is to understand any logics if they exist and put it in the bucket of logics we currently support. 
#             We currently support :
#             1. Termination logics (it can be written in any way) , you should be smart enough to understand if that word/sentence means termination
#             2. Skip logics (it can be written in any way) , you should be smart enough to understand if that word/sentence means skip.
#             3. User defined logics : The user might have different way of writing any logics and we've captured that.
                
#             Important : The users way of writing the logic is : {user_logic} make sure to only use the words as logics which are explicitly mentioned
#             please pay special attention while assigning logics. 

#             You will primarily see logics captured in `{{}}`. you goal is to understand if that logic falls in the above 3 categories of logics we support for the contact_form. 
#             If there's no logic that we support. (rememeber there can be mutliple ways of writing any logic, we have to be smart enough to understand the bigger picture.).But if we dont support that logic or there is no logic, just return the json as it is. without making any changes.

#             But if you see that there's any logic that we support 1. Termination, 2. Skip 3. User defined logics.  then we should follow the below steps.


#             In the question if you observe any logic that we support. Then please add another field saying contact_form_logic and the key value pair will be the following. 
#             For terminating the key should be "Terminating" and the value should be conditon but the condition will only be " [logical operator] [value]" 
#             For skip conditions the key would be "SKIP TO [questionLabel of the question]" value would be " [logical operator] [value] " 
#             important: The logical operator that you use should be like QuestionLabel ==, >=, <=, != , or whatever the option logic says. every opertor should have questionLabel in front of it. give me the exact logic that you get. you dont have to change any logic. make it both for Terminating or SKIP questions. follow the convention of writing "==, >=, <=, != " even if the user has just one "=" we should eb using "=="
#             Important: Provide the exact logic, but include the questionLabel (retrieved from the JSON) before every operator. Ensure the operators are in uppercase, like OR and AND. By questionLabel, I mean the actual value of the questionLabel field from the JSON, not the literal term questionLabel.
#             We also turn the None to True if its the logic we support and we've added a field for it in our json, like we did in the below example. 
            

#             example: you got this:

#             {{
#                     "questionLabel": "QM",
#                     "question": "Demo Question? `{{"(Disqualify if name=="XYZ")": None}}` \n random text",
#                     "contact_form" : ["Email"],
#                     "ask_logic"="Ask if Qn=03",
#                     "type":"contact_form"
#                 }}

#             your output will look something like this:

            

#             {{
#                     "questionLabel": "QM",
#                     "question": "Demo Question? `{{"(Disqualify if name=="XYZ")": True}}` \n random text",
#                     "contact_form" : ["Email"],
#                     "ask_logic"="Ask if Qn=03",
#                     "contact_form_logic": {{"Terminating":"QM=="XYZ"}},
#                     "type":"contact_form"
#             }}
            

#             example of a logic we dont understand.
#             {{
#                     "questionLabel": "QM",
#                     "question": "Demo Question? `{{"Some logic I dont know": None}}` \n random text",
#                     "type":"contact_form",
#                     "ask_logic":"Ask if Q3==0",
                 
#             }}
#             we will return it as it :
#             {{
#                     "questionLabel": "QM",
#                     "question": "Demo Question? `{{"Some logic I dont know": None}}` \n random text",
#                     "type":"contact_form",
#                     "ask_logic":"Ask if Q3==0",
                 
#             }}

#             Please pay special attention to the instructions for logics and make sure you mark it correctly, double check it. 
#             Most Important: No data should be deletd, not even a single dot or a bracket.
#             The json is :{input_json}      


                    
#             please give me the correct json. 
#             """
#             }
#         ]
#     )

#     content = parsed_text.choices[0].message.content
#     result = json.loads(content)
#     return result

