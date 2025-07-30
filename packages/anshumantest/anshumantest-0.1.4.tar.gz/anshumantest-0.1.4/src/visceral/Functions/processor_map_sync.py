
import time
import requests
from Functions.helper import *
from fastapi import Request, HTTPException
from Question_TypesV2.categorizer import categorizer_for_questions
from Question_TypesV2.single_select import single_select_question, single_select_logic
from Question_TypesV2.nps import nps_question, nps_logic
from Question_TypesV2.contact_form import contact_form_question
from Question_TypesV2.currency import currency_question, currency_logic
from Question_TypesV2.year import year_question, year_logic
from Question_TypesV2.number import number_question, number_logic
from Question_TypesV2.ranking import ranking_question, ranking_logic
from Question_TypesV2.transition import transition_question
from Question_TypesV2.single_text import single_text_question, single_text_logic
from Question_TypesV2.grid import grid_question, grid_logic
from Question_TypesV2.percentage import percentage_question, percentage_logic
from Question_TypesV2.percent_sum import percent_sum_question, percent_sum_logic
from Question_TypesV2.notes import notes_question
from Question_TypesV2.maxdiff import maxdiff_question
from Question_TypesV2.multi_text import multi_text_question, multi_text_logic
from Question_TypesV2.multi_select import multi_select_question, multi_select_logic
from Question_TypesV2.ask_if import ask_if_logic
from Question_TypesV2.hidden_variable import hidden_variable_question
from Question_TypesV2.multi_percentage import multi_percentage_question, multi_percentage_logic
from Question_TypesV2.van_westendorp import van_westerndorp_question
from Question_TypesV2.unknown import unknown_question
from Question_TypesV2.zip_code import zip_code_question, zip_code_logic
from Question_TypesV2.terminate import terminate_question
from Question_TypesV2.multi_select_grid import multi_select_grid_question, multi_select_grid_logic
from Question_TypesV2.clean_json import clean_json_with_backticks
from Question_TypesV2.ai_chat import ai_question
from Question_TypesV2.annotation import annotation
from Question_TypesV2.categorizer_v2 import categorizer_for_questions_v2
from Question_TypesV2.sync import generate_sync
from Functions.post_learning import send_to_ingest_api
from Functions.get_learning import get_learning
from Question_TypesV2.split_questions import split_questions
from Functions.process_single_question import *
from Functions.get_learning import get_learning
import asyncio



from American_Directions.single_select import single_select_question_AMI, single_select_logic_AMI
from American_Directions.nps import nps_question_AMI, nps_logic_AMI
from American_Directions.contact_form import contact_form_question_AMI
from American_Directions.currency import currency_question_AMI, currency_logic_AMI
from American_Directions.year import year_question_AMI, year_logic_AMI
from American_Directions.number import number_question_AMI, number_logic_AMI
from American_Directions.ranking import ranking_question_AMI, ranking_logic_AMI
from American_Directions.transition import transition_question_AMI
from American_Directions.single_text import single_text_question_AMI, single_text_logic_AMI
from American_Directions.grid import grid_question_AMI, grid_logic_AMI
from American_Directions.percentage import percentage_question_AMI, percentage_logic_AMI
from American_Directions.percent_sum import percent_sum_question_AMI, percent_sum_logic_AMI
from American_Directions.notes import notes_question_AMI
from American_Directions.maxdiff import maxdiff_question_AMI
from American_Directions.multi_text import multi_text_question_AMI
from American_Directions.multi_select import multi_select_question_AMI, multi_select_logic_AMI
from American_Directions.ask_if import ask_if_logic_AMI
from American_Directions.hidden_variable import hidden_variable_question_AMI
from American_Directions.multi_percentage import multi_percentage_question_AMI, multi_percentage_logic_AMI
from American_Directions.van_westendorp import van_westerndorp_question_AMI
from American_Directions.unknown import unknown_question_AMI
from American_Directions.zip_code import zip_code_question_AMI, zip_code_logic_AMI
from American_Directions.terminate import terminate_question_AMI
from American_Directions.multi_select_grid import multi_select_grid_question_AMI, multi_select_grid_logic_AMI
from American_Directions.clean_json import clean_json_with_backticks
from American_Directions.ai_chat import ai_question_AMI
from American_Directions.annotation import annotation
from American_Directions.categorizer_v2 import categorizer_for_question_AMIs_v2
from American_Directions.sync import generate_sync



def get_processor_map_sync(use_ami,use_dyn,use_gen, USW_Template):
    """Get the appropriate processor map based on AMI check"""


    if use_ami:
        print("we are using AMI direction.")
        return {
            "single-select": (single_select_question_AMI, single_select_logic_AMI),
            "nps": (nps_question_AMI, nps_logic_AMI),
            "ai-chat": (ai_question_AMI, None),
            "contact-form": (contact_form_question_AMI, None),
            "currency": (currency_question_AMI, currency_logic_AMI),
            "terminate": (terminate_question_AMI, None),
            "year": (year_question_AMI, year_logic_AMI),
            "number": (number_question_AMI, number_logic_AMI),
            "ranking": (ranking_question_AMI, ranking_logic_AMI),
            "transition": (transition_question_AMI, None),
            "single-text": (single_text_question_AMI, single_text_logic_AMI),
            "grid": (grid_question_AMI, grid_logic_AMI),
            "multi-select-grid": (multi_select_grid_question_AMI, multi_select_grid_logic_AMI),
            "multi_select_grid": (multi_select_grid_question_AMI, multi_select_grid_logic_AMI),
            "multi-grid": (multi_select_grid_question_AMI, multi_select_grid_logic_AMI),
            "multi_grid": (multi_select_grid_question_AMI, multi_select_grid_logic_AMI),
            "percentage": (percentage_question_AMI, percentage_logic_AMI),
            "percent-sum": (percent_sum_question_AMI, percent_sum_logic_AMI),
            "notes": (notes_question_AMI, None),
            "maxdiff": (maxdiff_question_AMI, None),
            "multi-text": (multi_text_question_AMI, None),
            "multi_text": (multi_text_question_AMI, None),
            "multi-select": (multi_select_question_AMI, multi_select_logic_AMI),
            "variable": (hidden_variable_question_AMI, None),
            "hidden_variable": (hidden_variable_question_AMI, None),
            "multi-percentage": (multi_percentage_question_AMI, multi_percentage_logic_AMI),
            "van-westendorp": (van_westerndorp_question_AMI, None),
            "zip_code": (zip_code_question_AMI, zip_code_logic_AMI),
            "zipcode": (zip_code_question_AMI, zip_code_logic_AMI),
            "unknown": (unknown_question_AMI, None)
            
        }
    else:
        
        print("We are using the general template")
        return {
            "single-select": (single_select_question, single_select_logic),
            "nps": (nps_question, nps_logic),
            "ai-chat": (ai_question, None),
            "contact-form": (contact_form_question, None),
            "currency": (currency_question, currency_logic),
            "terminate": (terminate_question, None),
            "year": (year_question, year_logic),
            "number": (number_question, number_logic),
            "ranking": (ranking_question, ranking_logic),
            "transition": (transition_question, None),
            "single-text": (single_text_question, single_text_logic),
            "grid": (grid_question, grid_logic),
            "multi-select-grid": (multi_select_grid_question, multi_select_grid_logic),
            "multi_select_grid": (multi_select_grid_question, multi_select_grid_logic),
            "multi-grid": (multi_select_grid_question, multi_select_grid_logic),
            "multi_grid": (multi_select_grid_question, multi_select_grid_logic),
            "percentage": (percentage_question, percentage_logic),
            "percent-sum": (percent_sum_question, percent_sum_logic),
            "notes": (notes_question, None),
            "maxdiff": (maxdiff_question, None),
            "multi-text": (multi_text_question, None),
            "multi_text": (multi_text_question, None),
            "multi-select": (multi_select_question, multi_select_logic),
            "variable": (hidden_variable_question, None),
            "hidden_variable": (hidden_variable_question, None),
            "multi-percentage": (multi_percentage_question, multi_percentage_logic),
            "van-westendorp": (van_westerndorp_question, None),
            "zip_code": (zip_code_question, zip_code_logic),
            "zipcode": (zip_code_question, zip_code_logic),
            "unknown": (unknown_question, None)
        }
    
