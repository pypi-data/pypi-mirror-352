def get_question_labels(payload):
    # Initialize an empty list to store the labels
    labels = []
    
    # Check if payload and blocks exist
    if not payload or 'blocks' not in payload or not isinstance(payload['blocks'], list):
        return labels
    
    # Iterate through each block
    for block in payload['blocks']:
        # Check if questions array exists in the block
        if 'questions' in block and isinstance(block['questions'], list):
            # Extract label from each question and add to the list
            for question in block['questions']:
                if 'label' in question:
                    labels.append(question['label'])
    
    return labels