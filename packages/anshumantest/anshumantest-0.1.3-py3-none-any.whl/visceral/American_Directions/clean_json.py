import json
def clean_json_with_backticks(openai_model, prompt):
    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0.0000000001,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a JSON cleaning expert."},
            {"role": "user", "content": f"""
            You will receive a JSON string that may have formatting issues. Your task is to:
            1. Clean and format this JSON string to make it valid
            2. Return the cleaned JSON object with the same structure but properly formatted
            
            Examples:
            Input: {{"Skip to Q8 IF Q9=="Anshu"": True}}
            Output: {{"Skip to Q8 IF Q9=='Anshu'": true}}
            
            Input: {{"Disqualify IF Q9=="Anshuman"": True}}
            Output: {{"Disqualify IF Q9=='Anshuman'": true}}
            
            Important:
            - Keep the same key structure but ensure valid JSON formatting
            - Convert Python-style True/False to JSON true/false
            - Fix quote issues (convert double quotes in values to single quotes if needed)
            - The output must be a valid JSON object
            
            Here is the JSON string to clean: {prompt}
            """}
        ]
    )
    content = parsed_text.choices[0].message.content
    try:
        result = json.loads(content)
        return result
    except json.JSONDecodeError as e:
        print(f"Error parsing cleaned JSON: {e}")
        return None