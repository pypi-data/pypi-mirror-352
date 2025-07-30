import json
from utils import retry_on_json_error

@retry_on_json_error
def process_complex_tasks(openai_model, prompt):
        parsed_text = openai_model.client_open_ai.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            temperature=0.00000001,
            messages=[
                {"role": "system", "content": "You are an agent specializing in capturing and categorizing all text content from survey documents"},
                {"role": "user", "content": f"""
    Your task is to restructure the input text based on the following rules:

    1. Phone and Online Pattern Recognition:
    - For "Phone": Look for the pattern "Phone:" followed by text up to the next punctuation mark or keyword
    - For "Online": Look for any web address (ending in .com, .org, .net, etc.) in the text

    2. Text Transformation:
    - Each identified phone number and web address should be transformed into the format: ^returnText('phone','online')^
    - If multiple items are found:
        * Phone numbers go in the first argument
        * Web addresses go in the second argument
    - Use empty string "" if either phone or online is missing in that segment

    3. Pattern Matching Rules:
    - Phone numbers: Capture all text after "Phone:" until a punctuation mark or new keyword
    - Web addresses: Capture any text containing .com, .org, .net, etc.
    - Multiple occurrences should each get their own returnText function

    4. Preservation Rules:
    - Keep all original text, spacing, and punctuation outside of the transformations
    - Only transform the specific phone numbers and web addresses
    - Maintain the exact position of transformed elements in the text
                 
                 6. Examples:
                - Input: "Call me on Phone: 8902 or Online: bio.com. If not, Phone: 902."
                - Output: "Call me on ^returnText('8902 or','bio.com')^. If not, ^returnText('902','')^."
                - Input: "Support: [Phone: 777-888 Online: help.com]. Sales: online: 999"
                - Output: "Support: [^returnText('777-888','help.com')^]. Sales: ^returnText('','999')^"
                - Input: "Support: [Phone: 777-888 Online: help.com]. online: 999"
                - Output: "Support: [^returnText('777-888','help.com')^].^returnText('','999')^"
                
    
    very important: make sure that the 1st argument of the returnText is text after phone and the 2nd argument is the text after online
    the text that you are receiving has multiple phone/onlines so make sure to have the retunrText accoridngly. we need the break the arguments if we see any phone/online after the qst retunrText
    Please transform the input text according to these rules and return in JSON format:
    {{
        "transformed_text": "your transformed text here"
    }}

    Input text to process: {prompt}
    """}
            ],
        )
        content = parsed_text.choices[0].message.content
        blocks = json.loads(content)
        return_text=blocks.get("transformed_text","")
        print("used LLM to tranform")
        return return_text
