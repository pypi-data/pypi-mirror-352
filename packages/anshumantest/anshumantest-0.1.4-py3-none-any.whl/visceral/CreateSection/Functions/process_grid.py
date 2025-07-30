from CreateSection.Functions.generate_uuid import *
from CreateSection.Functions.helper import *

def process_grid_options(options, label_prefix):
    processed_options = []
    for i, text in enumerate(options.keys(), start=1):
        # Remove the "[XX]" prefix if it exists
        cleaned_text = clean_option_text(text)
        # label = f"{i:02d}"
        label=str(i)
        option = {
            "id": generate_nano_id(),
            "text": cleaned_text,
            "label": label,
            "mdText": cleaned_text
        }
        processed_options.append(option)
    return processed_options

def process_grid_question(question, label):
    grid_options = {"vertical": {"options": []}, "horizontal": {"options": []}}
    # skips = []

    # Process columns (vertical)
    if 'columns' in question:
   
        grid_options["vertical"]["options"] = process_grid_options(question['rows'], 'V')
        # for i, (text, skip_action) in enumerate(question['columns'].items(), start=1):
        #     if skip_action:
        #         condition = f"RESPONSE(`{label}`).VERTICAL == `V{i}`"
        #         skip = create_skip(condition, "complete" if skip_action == "THANK AND END" else "skip", 
        #                            skip_action if skip_action != "THANK AND END" else None)
        #         skips.append(skip)

    # Process rows (horizontal)
    if 'rows' in question:
    
        grid_options["horizontal"]["options"] = process_grid_options(question['columns'], 'H')
        # for i, (text, skip_action) in enumerate(question['rows'].items(), start=1):
        #     if skip_action:
        #         condition = f"RESPONSE(`{label}`).HORIZONTAL == `H{i}`"
        #         skip = create_skip(condition, "complete" if skip_action == "THANK AND END" else "skip", 
        #                            skip_action if skip_action != "THANK AND END" else None)
        #         skips.append(skip)

    # Handle cases where one of rows/columns is empty
    if not grid_options["vertical"]["options"] and 'options' in question:
        grid_options["vertical"]["options"] = process_grid_options(question['options'], 'V')
    elif not grid_options["horizontal"]["options"] and 'options' in question:
        grid_options["horizontal"]["options"] = process_grid_options(question['options'], 'H')

    return grid_options,[]
