import json
from utils import retry_on_json_error

@retry_on_json_error
def quota_creator(openai_model, questions, objective, predefined_quotas, conversation_history, completes_desired="1000"):
        schema = """
        "quota":[
            {
                "name": "Total",
                "target": 1000,
                "definition": null
            },
            {
                "name": "Male",
                "target": 100,
                "definition": "Q3 == `1`"
            }
            ],
            "quota_explained": "string"
        """

        parsed_text = openai_model.client_open_ai.chat.completions.create(
            model="gpt-4o",
            temperature=0.0000000001,
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are processing survey questions and will receive raw question text. Your task is to structure the question into a JSON format"},
                {"role": "user", "content": f"""
                You are an exper in creating quotas for a survey that is about to be published, given a users objective and the questions.
                quotas drives the number of responses and the segments of the audience that will be targeted.
                follow this schema for the quota:
                {schema}
                the questions are:
                {questions}
                the objective is:
                {objective}

                you have to create 3-4 quotas based on the questions. There should always be a complete quota which will be the total number of responses. based on the user's audience he wants to target.
                then on the basis of the objective and the questions, decide smartly how to divide the quota into segments.
                example quota:
                [
            {{
                "name": "Total",
                "target": 1000,
                "definition": null
            }},
            {{
                "name": "Male",
                "target": 400,
                "definition": "Q3 == `1`"
            }},
            {{
                "name": "Female",
                "target": 600,
                "definition": "Q3 == `2`"
            }},
            {{
                "name": "Age 18-25",
                "target": 400,
                "definition": "AGE >= 18 AND AGE <= 25" #where AGE is the question label for age.
            }},
            {{
                "name": "Masters",
                "target": 300,
                "definition": "Q5 == `Masters`" #where Q5 is the question label for education.
            }}
            
            ]

            here the defintion is built using the Question label and the option label. 
            please refer the question json for the question label and the option label.
            please give me a valid json.

            Rules/ DSL:
            1. any option label should be enclosed in backticks.
            2. Use AND, OR rather than &&, ||
            3. If dealing with multiple labels you may use list : for example -> EDC IN [`1`, `2`]

            the number of completes desired is: {completes_desired}, adjust the quotas based on this number.
            
            {f"Also the user has predefined quotas, you can use them as a reference and add more to them. here are the predefined quotas: {predefined_quotas}" if predefined_quotas else ""}
            also the conversation history is:
            {conversation_history} (you can refer this to understand the user's preferences and then decide the quotas, but decide the quotas based on the questions and the objective more than the conversation history)
            also the quota_explained is a string that explains the quotas in a way that is easy to understand. (keep it short and concise) we use this in the survey to explain the quotas to the respondents.

            We support markdown formatting.
                """
                }
            ]
        )

        content = parsed_text.choices[0].message.content
        result = json.loads(content)
        return result

