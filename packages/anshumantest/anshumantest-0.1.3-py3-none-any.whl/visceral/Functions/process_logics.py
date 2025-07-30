from Functions.helper import create_skip, clean_option_text
from Functions.nano_id import *
import re



def process_text_logic(question, processed_question, label):
    """
    Process text logic for questions, supporting both TERMINATING and SKIP TO conditions.
    Cleans conditions by removing dots from labels.
    
    Args:
        question: The original question dictionary
        processed_question: The processed question dictionary being built
        label: The question label
    """
    if not question.get('text_logic'):
        return

    # Remove any dots from the label for use in conditions
    clean_label = label.replace('.', '')

    for action, condition in question['text_logic'].items():
        # Clean the condition by replacing label with dot with clean label
        clean_condition = condition.replace(f"{label}.", clean_label)
        
        if action.lower() == 'terminating':
            skip = create_skip(clean_condition, "DISQUALIFY")
            processed_question["skips"].append(skip)
        elif action.startswith('SKIP TO '):
            skip_to = action.replace('SKIP TO ', '').strip()
            # Handle Q prefix in skip_to target
            if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                skip_to = skip_to[1:]
            skip = create_skip(clean_condition, "skip", skip_to)
            processed_question["skips"].append(skip)







def process_year_logic(question, processed_question, label):
    for action, condition in question['year_logic'].items():
        if action == 'Terminating':
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            # Check if condition already contains the label
            if not condition.startswith(label):
                condition = f"{label} {condition}"
            skip = create_skip(condition, "DISQUALIFY")
            processed_question["skips"].append(skip)
        elif action.startswith('SKIP TO '):
            skip_to = action.replace('SKIP TO ', '').strip()
            if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                skip_to = skip_to[1:]
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            skip = create_skip(f"{condition.strip()}", "skip", skip_to)
            processed_question["skips"].append(skip)




def process_percentage_logic(question, processed_question, label):
    for action, condition in question['percentage_logic'].items():
        if action == 'Terminating':
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            # Check if condition already contains the label
            if not condition.startswith(label):
                condition = f"{label} {condition}"
            skip = create_skip(condition, "DISQUALIFY")
            processed_question["skips"].append(skip)
        elif action.startswith('SKIP TO '):
            skip_to = action.replace('SKIP TO ', '').strip()
            if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                skip_to = skip_to[1:]
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            skip = create_skip(f"{condition.strip()}", "skip", skip_to)
            processed_question["skips"].append(skip)

def process_text_logic(question, processed_question, label):
    for action, condition in question['single_text_logic'].items():
        if action == 'Terminating':
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            # Check if condition already contains the label
            if not condition.startswith(label):
                condition = f"{label} {condition}"
            skip = create_skip(condition, "DISQUALIFY")
            processed_question["skips"].append(skip)
        elif action.startswith('SKIP TO '):
            skip_to = action.replace('SKIP TO ', '').strip()
            if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                skip_to = skip_to[1:]
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            skip = create_skip(f"{condition.strip()}", "skip", skip_to)
            processed_question["skips"].append(skip)

def process_zip_code_logic(question, processed_question, label):
    # Initialize skips if it doesn't exist
    if "skips" not in processed_question:
        processed_question["skips"] = []

    for action, condition in question['zip_code_logic'].items():
        if action == 'Terminating':
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            
            # Remove dots from both the label and condition
            clean_label = label.replace('.', '')
            condition = condition.replace('.', '')
            
            # Check if condition already contains the label
            if not condition.startswith(clean_label):
                condition = f"{clean_label} {condition}"
            
            skip = create_skip(condition, "DISQUALIFY")
            processed_question["skips"].append(skip)
            
        elif action.startswith('SKIP TO '):
            skip_to = action.replace('SKIP TO ', '').strip()
            if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                skip_to = skip_to[1:]
            
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            
            skip = create_skip(f"{condition.strip()}", "skip", skip_to)
            processed_question["skips"].append(skip)





def process_nps_logic(question, processed_question, label):
    for action, condition in question['nps_logic'].items():
        if action == 'Terminating':
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            # Check if condition already contains the label
            if not condition.startswith(label):
                condition = f"{label} {condition}"
            skip = create_skip(condition, "DISQUALIFY")
            processed_question["skips"].append(skip)
        elif action.startswith('SKIP TO '):
            skip_to = action.replace('SKIP TO ', '').strip()
            if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                skip_to = skip_to[1:]
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            skip = create_skip(f"{condition.strip()}", "skip", skip_to)
            processed_question["skips"].append(skip)





def process_grid_options(options, label_prefix):
    """
    Process grid options that can be either:
    - A dictionary with multiple keys
    - A list of dictionaries with single keys
    """
    processed_options = []
    
    # If options is a list, handle as list of dictionaries
    if isinstance(options, list):
        for i, option_dict in enumerate(options, start=1):
            # Get the first (and only) key from the dictionary
            text = next(iter(option_dict))
            # Remove the "[XX]" prefix if it exists
            cleaned_text = clean_option_text(text)
            # label = f"{i:02d}"
            label = str(i)
            option = {
                "id": generate_nano_id(),
                "text": cleaned_text,
                "label": label,
                "mdText": cleaned_text,
                "type": "user",  # Adding required fields
                "order": i - 1,
                "skip": None     # Adding skip field as None by default
            }
            processed_options.append(option)
    # If options is a dictionary, handle as before
    elif isinstance(options, dict):
        for i, text in enumerate(options.keys(), start=1):
            # Remove the "[XX]" prefix if it exists
            cleaned_text = clean_option_text(text)
            # label = f"{i:02d}"
            label = str(i)
            option = {
                "id": generate_nano_id(),
                "text": cleaned_text,
                "label": label,
                "mdText": cleaned_text,
                "type": "user",  # Adding required fields
                "order": i - 1,
                "skip": None     # Adding skip field as None by default
            }
            processed_options.append(option)
            
    return processed_options

def process_grid_question(question, label):
    grid_options = {"vertical": {"options": []}, "horizontal": {"options": []}}
    
    # Process columns (vertical)
    if 'columns' in question:
        grid_options["vertical"]["options"] = process_grid_options(question['rows'], 'V')
    
    # Process rows (horizontal)
    if 'rows' in question:
        grid_options["horizontal"]["options"] = process_grid_options(question['columns'], 'H')
    
    # Handle cases where one of rows/columns is empty
    if not grid_options["vertical"]["options"] and 'options' in question:
        grid_options["vertical"]["options"] = process_grid_options(question['options'], 'V')
    elif not grid_options["horizontal"]["options"] and 'options' in question:
        grid_options["horizontal"]["options"] = process_grid_options(question['options'], 'H')
    
    return grid_options, []





def process_number_logic(question, processed_question, label):
    for action, condition in question['number_logic'].items():
        if action == 'Terminating':
            # Don't add label since condition already has it
            skip = create_skip(condition, "DISQUALIFY")
            processed_question["skips"].append(skip)
        elif action.startswith('SKIP TO '):
            skip_to = action.replace('SKIP TO ', '').strip()
            if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                skip_to = skip_to[1:]
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            cleaned_condition = re.sub(r'[^\d\s<>=]+', '', condition)
            skip = create_skip(cleaned_condition.strip(), "skip", skip_to)
            processed_question["skips"].append(skip)





def process_currency_logic(question, processed_question, label):
    for action, condition in question['currency_logic'].items():
        if action == 'Terminating':
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            # Check if condition already contains the label
            if not condition.startswith(label):
                condition = f"{label} {condition}"
            skip = create_skip(condition, "DISQUALIFY")
            processed_question["skips"].append(skip)
        elif action.startswith('SKIP TO '):
            skip_to = action.replace('SKIP TO ', '').strip()
            if label.isdigit() and skip_to.startswith('Q') and skip_to[1:].isdigit():
                skip_to = skip_to[1:]
            if isinstance(condition, list):
                condition = ''.join(str(x) for x in condition)
            skip = create_skip(f"{condition.strip()}", "skip", skip_to)
            processed_question["skips"].append(skip)


def currency_symbol_to_code(symbol):
    currency_mapping = {
        '$': 'USD',  # US Dollar
        '€': 'EUR',  # Euro
        '£': 'GBP',  # British Pound Sterling
        '¥': 'JPY',  # Japanese Yen
        '₹': 'INR',  # Indian Rupee
        '₽': 'RUB',  # Russian Ruble
        '₣': 'CHF',  # Swiss Franc
        '₺': 'TRY',  # Turkish Lira
        '₩': 'KRW',  # South Korean Won
        '₴': 'UAH',  # Ukrainian Hryvnia
        'A$': 'AUD',  # Australian Dollar
        'C$': 'CAD',  # Canadian Dollar
        'HK$': 'HKD',  # Hong Kong Dollar
        '₱': 'PHP',  # Philippine Peso
        '฿': 'THB',  # Thai Baht
        'R$': 'BRL',  # Brazilian Real
        '₪': 'ILS',  # Israeli New Shekel
        '₦': 'NGN',  # Nigerian Naira
        '₡': 'CRC',  # Costa Rican Colón
        '₫': 'VND',  # Vietnamese Dong
        '៛': 'KHR',  # Cambodian Riel
        '₸': 'KZT',  # Kazakhstani Tenge
        '₿': 'BTC',  # Bitcoin
        'Ξ': 'ETH',  # Ethereum
        '₼': 'AZN',  # Azerbaijani Manat
        '₾': 'GEL',  # Georgian Lari
        '₻': 'MGA',  # Malagasy Ariary
        '₽': 'RUB',  # Russian Ruble (duplicate, keeping for compatibility)
        '₺': 'TRY',  # Turkish Lira (duplicate, keeping for compatibility)
    }
    return currency_mapping.get(symbol, 'USD')

