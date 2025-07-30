def delete_question_by_label(json_payload, label_to_delete):
    """
    Deletes a question with the specified label from both the survey questions and annotated data.
    
    Args:
        json_payload: The JSON payload containing blocks and questions
        label_to_delete: The label of the question to delete (e.g., "Q5" or "Q5.")
        
    Returns:
        The modified JSON payload with the question removed
    """
    # Normalize the label by removing trailing periods
    normalized_label = label_to_delete.rstrip('.')
    question_id_to_delete = None
    
    # Check if we have blocks with questions
    if hasattr(json_payload, "blocks"):
        blocks = json_payload.blocks
    elif isinstance(json_payload, dict) and "blocks" in json_payload:
        blocks = json_payload["blocks"]
    else:
        return json_payload  # No blocks found, return unchanged
    
    # Step 1: Find and remove the question from blocks
    for block in blocks:
        if "questions" in block:
            # Find the question to delete and get its ID
            for index, question in enumerate(block["questions"]):
                if "label" in question and question["label"]:
                    question_label = question["label"].rstrip('.')
                    if question_label == normalized_label:
                        # Store the ID for annotated_data deletion
                        question_id_to_delete = question.get("id")
                        # Remove the question from the list
                        block["questions"].pop(index)
                        break
    
    # Step 2: Remove the corresponding entry from annotated_data
    if question_id_to_delete:
        if hasattr(json_payload, "annotated_data"):
            annotated_data = json_payload.annotated_data
        elif isinstance(json_payload, dict) and "annotated_data" in json_payload:
            annotated_data = json_payload["annotated_data"]
        else:
            return json_payload  # No annotated_data found
        
        # Find and remove the annotated data entry with matching ID
        for index, item in enumerate(annotated_data):
            if "id" in item and item["id"] == question_id_to_delete:
                annotated_data.pop(index)
                break
    
    return json_payload