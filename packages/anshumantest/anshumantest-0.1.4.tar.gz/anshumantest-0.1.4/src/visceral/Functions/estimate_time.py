def estimate_time(complete_payload):
    counter = 0
    if hasattr(complete_payload, 'blocks'):
    
        
        for i, block in enumerate(complete_payload.blocks):
            
            if isinstance(block, dict):
                if 'questions' in block:
                    questions = block['questions']
                    # print(f"- Found questions: {len(questions)}")
                    counter += len(questions)
                else:
                    pass
            else:
                # fallback for Pydantic objects
                if hasattr(block, 'questions'):
                    questions = block.questions
                    # print(f"- Found questions: {len(questions)}")
                    counter += len(questions)
    else:
        pass
    
    time_in_minutes = (counter * 30) / 60
    # print(f"\nTotal questions counted: {counter}")
    return time_in_minutes