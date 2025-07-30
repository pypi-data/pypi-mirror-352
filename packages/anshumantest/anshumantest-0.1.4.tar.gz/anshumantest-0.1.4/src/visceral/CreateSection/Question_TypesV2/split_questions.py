import json
from utils import retry_on_json_error

@retry_on_json_error
def split_questions(openai_model, prompt):
    parsed_text = openai_model.client_open_ai.chat.completions.create(
        model="gpt-4o",
        temperature=0,  # No need for extreme precision
        response_format={"type": "json_object"},  
        messages=[
            {"role": "system", "content": "You are an extraction agent that must IDENTICALLY copy the input text while separating individual questions."},
            {"role": "user", "content": f"""
             
            Extract every element related to each survey question from the input text and provide a JSON object where the keys are sequential numbers (1, 2, 3, ...) and the values are the full content related to each question. Ensure that no alteration or omission of punctuation occurs, maintaining the complete integrity of the original input text.

            Most important: Not even a single dot should be lost from the input text. I should have each and eveything in the json you output

            # Output Format

            - Provide the extracted content in a JSON format with each segment assigned to a numeric key like 1, 2, 3.

            # Notes

            - Ensure the precision of content extraction, capturing the entire section related to each question.
            - Handle input that doesn't immediately make sense and separate potential questions smartly without losing any details from the original text.
            - Most important: We cannot lose even a single dot from the input text; each and every part should be entirely captured.
            - Capture each and every formatting. we cannot lose anything.
            - everything there in the input text should be there in the json, but splatted into different question.
            - each line break and eveyr formatting should be captured, even if it doesnt make sense. Whatever is there in the input text should be there in the output
             

            The Input text is : {prompt}
            """}
        ]
    )

    try:

        content = parsed_text.choices[0].message.content
        result = json.loads(content)
        return result
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error parsing response: {e}")
        return None  # Or raise an appropriate exception
