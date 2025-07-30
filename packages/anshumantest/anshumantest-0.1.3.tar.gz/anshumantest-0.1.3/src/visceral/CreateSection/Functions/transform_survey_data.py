
from CreateSection.Functions.generate_uuid import *
from typing import Optional, Dict, List, Any
from CreateSection.Functions.process_question import *

import time


def transform_survey_data(input_data: List[Dict[str, Any]], identified_blocks: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    used_labels = set()
    output = []

    # Create a mapping of question labels to their respective blocks
    label_to_block = {}
    for block_name, labels in identified_blocks.items():
        for label in labels:
            label_to_block[label] = block_name

    # Initialize blocks with alphabetic labels, maintaining original order
    blocks = {}
    for i, (block_name, _) in enumerate(identified_blocks.items()):
        block_label = chr(65 + i)  # A, B, C, D, ...
        blocks[block_name] = {
            "id": generate_nano_id(),
            "label": block_label,
            "name": block_name,
            "config": {},
            "questions": []
        }

    # Keep track of current block while processing
    current_block = None
    
    for item in input_data:
        if isinstance(item, dict):
            processed_questions = process_question(item, used_labels)
            
            # Handle case where process_question returns a list of questions
            if isinstance(processed_questions, list):
                for processed_question in processed_questions:
                    if processed_question:
                        processed_question["raw_data"] = item.get("raw_data", {})
                        question_label = processed_question['label']
                        
                        # First try to find the block from label_to_block
                        block_name = label_to_block.get(question_label.replace('HV', ''))
                        
                        # If not found in mapping, use current block or create new one
                        if block_name is None:
                            if current_block is None:
                                block_name = list(identified_blocks.keys())[0]  # Use first block as default
                            else:
                                block_name = current_block
                        
                        current_block = block_name
                        
                        # Create block if it doesn't exist
                        if block_name not in blocks:
                            new_block_label = chr(65 + len(blocks))
                            blocks[block_name] = {
                                "id": generate_nano_id(),
                                "label": new_block_label,
                                "name": block_name,
                                "config": {},
                                "questions": []
                            }
                        
                        blocks[block_name]["questions"].append(processed_question)
            else:
                if processed_questions:
                    processed_questions["raw_data"] = item.get("raw_data", {})
                    question_label = processed_questions['label']
                    
                    # First try to find the block from label_to_block
                    block_name = label_to_block.get(question_label)
                    
                    # If not found in mapping, use current block or create new one
                    if block_name is None:
                        if current_block is None:
                            block_name = list(identified_blocks.keys())[0]  # Use first block as default
                        else:
                            block_name = current_block
                    
                    current_block = block_name
                    
                    # Create block if it doesn't exist
                    if block_name not in blocks:
                        new_block_label = chr(65 + len(blocks))
                        blocks[block_name] = {
                            "id": generate_nano_id(),
                            "label": new_block_label,
                            "name": block_name,
                            "config": {},
                            "questions": []
                        }
                    
                    blocks[block_name]["questions"].append(processed_questions)

    output = [block for block in blocks.values() if block["questions"]]
    return output


def preprocess_survey_data(input_data: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Preprocess the survey data to fit the expected input format for transform_survey_data.
    """
    preprocessed_data = []
    identified_blocks = {}

    # for block_name, questions in input_data.items():
    #     identified_blocks[block_name] = [q['questionLabel'] for q in questions]
    #     preprocessed_data.extend(questions)

    # return preprocessed_data, identified_blocks
    for block_name, questions in input_data.items():
        # Get labels, skipping any questions that cause errors
        block_labels = []
        for q in questions:
            try:
                if isinstance(q, dict) and 'questionLabel' in q:
                    block_labels.append(q['questionLabel'])
            except:
                continue
        
        identified_blocks[block_name] = block_labels
        preprocessed_data.extend(questions)

    return preprocessed_data, identified_blocks

def transform_new_survey_data(input_data: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Transform the new survey data structure into the desired output format.
    """

    # raise Exception("Simulated error in Excel transformation")
    preprocessed_data, identified_blocks = preprocess_survey_data(input_data)
    # print("completed transform_new_survey_Data")
    return transform_survey_data(preprocessed_data, identified_blocks)






def transform_with_fallback(data, is_excel=False, identified_blocks=None):
    """
    Transform the survey data with a fallback mechanism.
    """
    # Initialize fallback mechanism
    fallback_block = {
        "id": generate_nano_id(),
        "label": "Z",  # Use 'Z' as the label for the fallback block
        "name": "Fallback Block",
        "config": {},
        "questions": [{
            "id": generate_nano_id(),
            "text": "Fallback Question: Raw Data",
            "type": "text",
            "label": "FB",
            "config": {},
            "mdText": "Fallback Question: Raw Data\n\n",
            "created": int(time.time() * 1000),
            "updated": int(time.time() * 1000),
            "skips": [],
            "optout": {"text": None, "allowed": False},
            "dynamic": False,
            "options": [],
            "condition": None,
            "confidence": 1.0,
            "issue": None,
            "subtype": "single"
        }]
    }

    # Accumulate raw data in the fallback question
    if is_excel:
        for section, questions in data.items():
            for question in questions:
                raw_data = question.get("raw_data", "")
                if raw_data:
                    fallback_block["questions"][0]["text"] += f"\n\n{raw_data}"
                    fallback_block["questions"][0]["mdText"] += f"\n\n{raw_data}"
    else:
        for item in data:
            raw_data = item.get("raw_data", "")
            if raw_data:
                fallback_block["questions"][0]["text"] += f"\n\n{raw_data}"
                fallback_block["questions"][0]["mdText"] += f"\n\n{raw_data}"

    try:
        # Attempt the main transformation
        if is_excel:
            result = transform_new_survey_data(data)
        else:
            result = transform_survey_data(data, identified_blocks)
        return result
    except Exception as e:
        print(f"Main transformation failed: {str(e)}")
        print("Falling back to raw data accumulation")
        return [fallback_block]
    




# def process_new_format_data(input_data: dict) -> dict:
#     """
#     Process the new format data into blocks and questions.
#     Returns a dictionary with blocks as keys and lists of questions as values.
#     """
#     current_section = "Survey"
#     processed_data = {}
    
#     # Sort keys to ensure we process in order
#     # sorted_keys = input_data.keys()
    
#     for key in input_data.keys():
#         value = input_data[key]
        
#         # Handle section markers
#         if key.endswith('_Section'):
#             current_section = value
#             if current_section not in processed_data:
#                 processed_data[current_section] = []
#             continue
            
#         # Skip processing the key if it's a section marker
#         # if key.endswith('_Section'):
#         #     continue
            
#         # Ensure the current section exists in processed_data
#         if current_section not in processed_data:
#             processed_data[current_section] = []
            
#         # Process different types of questions
#         if key.endswith('_m'):  # Transition message
#             if isinstance(value, list) and len(value) >= 2:
#                 question_data = {
#                     "questionLabel": value[0],  # Use the provided questionLabel
#                     "question": value[1],   # Use the provided text
#                     "type": "message",
#                     "options": {},
#                     "columns": {},
#                     "rows": {},
#                     "logic": [],
#                     "Randomize": False,
#                     "raw_data": value[1]    # Store the text as raw_data
#                 }
#             else:
#                 # Fallback for old format or invalid input
#                 question_data = {
#                     "questionLabel": generate_nano_id_for_label(),
#                     "question": str(value),
#                     "type": "message",
#                     "options": {},
#                     "columns": {},
#                     "rows": {},
#                     "logic": [],
#                     "Randomize": False,
#                     "raw_data": str(value)
#                 }
#             processed_data[current_section].append(question_data)
            
            
#         elif key.endswith('_d'):  # Normal question
#             # The value is already in the correct format, just append it
#             processed_data[current_section].append(value)
            
#         else :  # Notes
#             # Create a note type question
#             note_data = {
#                 "questionLabel": generate_nano_id_for_label(),
#                 "question": value,
#                 "type": "notes",
#                 "options": {},
#                 "columns": {},
#                 "rows": {},
#                 "logic": [],
#                 "Randomize": False,
#                 "raw_data": value
#             }
#             processed_data[current_section].append(note_data)
    
#     return processed_data

def process_new_format_data(input_data: dict, question_block_map: dict = None) -> dict:
    """
    Process the new format data into blocks and questions.
    Returns a dictionary with blocks as keys and lists of questions as values.
    
    Args:
        input_data: Dictionary containing question data
        question_block_map: Dictionary mapping question keys to their block types
    """
    processed_data = {}
    
    # Now process the questions, assigning them to the correct blocks
    for key in input_data.keys():
        value = input_data[key]
        
        # Determine the block type for this question using the map
        if question_block_map and key in question_block_map:
            current_block_type = question_block_map[key]
        else:
            # Default to "objective" for non-mapped questions
            current_block_type = "objective"
        
        # Ensure the current block type exists in processed_data
        if current_block_type not in processed_data:
            processed_data[current_block_type] = []
            
        # Process different types of questions
        if key.endswith('_m'):  # Transition message
            if isinstance(value, list) and len(value) >= 2:
                question_data = {
                    "questionLabel": value[0],
                    "question": value[1],
                    "type": "message",
                    "options": {},
                    "columns": {},
                    "rows": {},
                    "logic": [],
                    "Randomize": False,
                    "raw_data": value[1]
                }
            else:
                # Fallback for old format or invalid input
                question_data = {
                    "questionLabel": generate_nano_id_for_label(),
                    "question": str(value),
                    "type": "message",
                    "options": {},
                    "columns": {},
                    "rows": {},
                    "logic": [],
                    "Randomize": False,
                    "raw_data": str(value)
                }
            processed_data[current_block_type].append(question_data)
            
        elif key.endswith('_d'):  # Normal question
            # The value is already in the correct format, just append it
            processed_data[current_block_type].append(value)
            
        elif not key.endswith('_Section'):  # Notes (skip section markers)
            # Create a note type question
            note_data = {
                "questionLabel": generate_nano_id_for_label(),
                "question": value,
                "type": "notes",
                "options": {},
                "columns": {},
                "rows": {},
                "logic": [],
                "Randomize": False,
                "raw_data": value
            }
            processed_data[current_block_type].append(note_data)
    
    return processed_data



# def transform_survey_data_new(input_data: dict) -> List[Dict[str, Any]]:
#     """
#     Main transformation function for the new input format
#     """
#     # First, process the new format into blocks
#     processed_blocks = process_new_format_data(input_data)

#     # print(processed_blocks)
    
#     # Then use the existing transformation logic with the processed blocks
#     return transform_new_survey_data(processed_blocks)


def transform_survey_data_new(input_data: dict, question_block_map: dict = None) -> List[Dict[str, Any]]:
    """
    Main transformation function for the new input format
    
    Args:
        input_data: Dictionary containing question data
        question_block_map: Dictionary mapping question keys to their block types
    """
    # Process the new format into blocks, passing the question block map
    processed_blocks = process_new_format_data(input_data, question_block_map)
    
    # Then use the existing transformation logic with the processed blocks
    return transform_new_survey_data(processed_blocks)


# def transform_final_data(input_data):
#     """
#     Transform survey data to have data as a dict with blocks and annotated_data arrays
#     """
#     survey_agent_id = input_data.get('survey_agent_id')
#     raw = input_data.get('raw', [])
#     processing_time = input_data.get('processing_time', {})
    
#     # Get ALL blocks instead of just the first one
#     blocks = input_data.get('data', [])
    
#     # Process questions to build annotated_data
#     annotated_data = []
    
#     # Iterate through all blocks to get all questions
#     for block in blocks:
#         questions = block.get('questions', [])
#         for question in questions:
#             annotated_text = question.get('annotated_text', {})
            
#             if isinstance(annotated_text, dict) and annotated_text.get('nodes'):
                
#                 # Use existing annotated_text if valid
#                 question_type = annotated_text.get('questionType', 'transition')
#                 if question_type == 'message':
#                     question_type = 'transition'
#                 annotated_data.append({
#                     'id': question['id'],
#                     'nodes': annotated_text['nodes'],
#                     'questionType': question_type
#                 })
#             else:
#                 print("Nanananaananananana")
#                 # Build nodes from scratch
#                 nodes = []
#                 if question.get('label'):
#                     nodes.append({
#                         'type': 'label',
#                         'text': f"{question['label']}. "
#                     })
#                 if question.get('text'):
#                     nodes.append({
#                         'type': 'question_text',
#                         'text': question['text']
#                     })
#                 nodes.append({'type': 'linebreak'})
                
#                 for i, option in enumerate(question.get('options', [])):
#                     nodes.append({
#                         'type': 'options',
#                         'text': f"{option.get('label', '')}. {option.get('text', '')}"
#                     })
#                     if i < len(question.get('options', [])) - 1:
#                         nodes.append({'type': 'linebreak'})
                
#                 question_type = 'transition'
#                 if question.get('type') == 'select':
#                     question_type = 'single-select' if question.get('subtype') == 'single' else 'multi-select'
                
#                 annotated_data.append({
#                     'id': question['id'],
#                     'nodes': nodes,
#                     'questionType': question_type
#                 })
    
#     return {
#         'survey_agent_id': survey_agent_id,
#         'raw': raw,
#         'data': {
#             'blocks': blocks,
#             'annotated_data': annotated_data
#         },
#         'processing_time': processing_time
#     }

# def process_input_string(input_str):
#     """Process input string to create proper JSON"""
#     import json
#     input_str = input_str.replace("'", '"').replace('None', 'null').replace('True', 'true').replace('False', 'false')
#     input_data = json.loads(input_str)
#     return transform_final_data(input_data)


def transform_final_data(input_data):
    """
    Transform survey data to have annotated data directly within each block
    """
    survey_agent_id = input_data.get('survey_agent_id')
    raw = input_data.get('raw', [])
    processing_time = input_data.get('processing_time', {})
    
    # Get all blocks
    blocks = input_data.get('data', [])
    
    # Process each block to include its annotated data
    for block in blocks:
        block_id = block.get('id')
        block_questions = block.get('questions', [])
        
        # Initialize the annotated array for this block
        block['annotated'] = []
        
        # Process each question to create the annotated data
        for question in block_questions:
            annotated_text = question.get('annotated_text', {})
            
            if isinstance(annotated_text, dict) and annotated_text.get('nodes'):
                # Use existing annotated_text if valid
                question_type = annotated_text.get('questionType', 'transition')
                if question_type == 'message':
                    question_type = 'transition'
                
                # Add to the block's annotated array
                block['annotated'].append({
                    'id': question['id'],
                    'nodes': annotated_text['nodes'],
                    'questionType': question_type
                })
            else:
                # Build nodes from scratch
                nodes = []
                if question.get('label'):
                    nodes.append({
                        'type': 'label',
                        'text': f"{question['label']}. "
                    })
                if question.get('text'):
                    nodes.append({
                        'type': 'question_text',
                        'text': question['text']
                    })
                nodes.append({'type': 'linebreak'})
                
                for i, option in enumerate(question.get('options', [])):
                    nodes.append({
                        'type': 'options',
                        'text': f"{option.get('label', '')}. {option.get('text', '')}"
                    })
                    if i < len(question.get('options', [])) - 1:
                        nodes.append({'type': 'linebreak'})
                
                question_type = 'transition'
                if question.get('type') == 'select':
                    question_type = 'single-select' if question.get('subtype') == 'single' else 'multi-select'
                
                # Add to the block's annotated array
                block['annotated'].append({
                    'id': question['id'],
                    'nodes': nodes,
                    'questionType': question_type
                })
    
    return {
        'survey_agent_id': survey_agent_id,
        'raw': raw,
        'data': {
            'blocks': blocks
        },
        'processing_time': processing_time
    }