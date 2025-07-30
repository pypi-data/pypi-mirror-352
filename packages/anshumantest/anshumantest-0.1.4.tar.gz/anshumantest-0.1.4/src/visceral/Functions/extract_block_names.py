def extract_block_names(complete_survey_data):
    """
    Extract block names from complete_survey_data
    
    Args:
        complete_survey_data: The complete_survey_data object
        
    Returns:
        list: List of block names
    """
    block_names = []
    
    # Check if blocks exists and is a list
    if hasattr(complete_survey_data, 'blocks') and isinstance(complete_survey_data.blocks, list):
        for block in complete_survey_data.blocks:
            # Check if block is a dictionary and has a 'name' key
            if isinstance(block, dict) and 'name' in block:
                block_names.append(block['name'])
    
    return block_names