def find_question_text_by_label(json_payload, input_label):
    """
    Finds the question text for a given label in the JSON payload.
    
    Args:
        json_payload: The JSON payload containing blocks and questions
        input_label: The label to search for (e.g., "Q5" or "Q5.")
        
    Returns:
        str: The question text if found, None otherwise
    """
    # Normalize the input label by removing trailing periods
    normalized_input_label = input_label.rstrip('.')
    
    # Check if we have blocks with questions
    if hasattr(json_payload, "blocks"):
        blocks = json_payload.blocks
    elif isinstance(json_payload, dict) and "blocks" in json_payload:
        blocks = json_payload["blocks"]
    else:
        return None  # No blocks found
    
    # Search through all questions in all blocks
    for block in blocks:
        if "questions" in block:
            for question in block["questions"]:
                if "label" in question and question["label"]:
                    # Normalize the question label as well
                    question_label = question["label"].rstrip('.')
                    
                    # Compare the normalized labels
                    if question_label == normalized_input_label:
                        # Return the question text if found
                        if "text" in question:
                            return question["text"]
                        elif "question" in question:
                            return question["question"]
    
    # If we get here, the label wasn't found
    return None