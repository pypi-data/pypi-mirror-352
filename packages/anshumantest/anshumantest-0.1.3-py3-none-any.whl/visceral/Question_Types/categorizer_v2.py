import json

def categorizer_for_questions_v2(openai_model, prompt):
        

        parsed_text = openai_model.client_open_ai.chat.completions.create(
            model="gpt-4o",
            temperature=0.0000000001,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "you are a specialised agent which can categorize a given question into a type."},
                {"role": "user", "content": f"""
                
                The categories that we support are:
                single-select
                multi-select
                single-text
                multi-text
                grid
                number
                currency
                year
                percentage
                percent-sum
                transition
                notes
                nps
                hidden_variable
                maxdiff
                contact-form
                ranking
                multi-percentage
                van-westendorp
                zipcode
                ai-chat
            
                
                
                Guidelines:
                
                Determine the question type based on the provided options.
                Net Promoter Score (NPS): If the question is a "Net Promoter Score" question, mark its type as nps.
                Numbers: Questions like "How old are you?" should be classified as number.
                
                Message vs Notes:
                transition: Text intended to be shown to the user, such as introductions or filler questions.
                Notes: Programmer notes intended for creating the survey.
                    
                Any hidden variable question will be type variable
                 
                Any question which has options should be routed accordingly, make sure to be smart enough to decide. 
                 
                Be smart to understand the grid type questions, any question which has rows/columns or scales/options will be a grid type questions. 
                
                
                If the question type is not in the supported categories, tag it as unknown.
                
                    
                Output Format:
                Provide the response as a JSON object with a single key-value pair:

                Key: "type"
                Value: The identified type.
                Example Output:

                    {{
                    "type": "single_select"
                    }}
                    
                    The question text is : {prompt}

                """
                }
            ]
        )

        content = parsed_text.choices[0].message.content
        result = json.loads(content)
        return result


