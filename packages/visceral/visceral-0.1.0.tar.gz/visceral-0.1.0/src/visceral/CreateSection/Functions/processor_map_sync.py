
from CreateSection.Question_TypesV2.single_select import single_select_question, single_select_logic
from CreateSection.Question_TypesV2.multi_select import multi_select_question, multi_select_logic
from CreateSection.Question_TypesV2.contact_form import contact_form_question
from CreateSection.Question_TypesV2.currency import currency_question, currency_logic
from CreateSection.Question_TypesV2.year import year_question, year_logic
from CreateSection.Question_TypesV2.number import number_question, number_logic
from CreateSection.Question_TypesV2.nps import nps_question, nps_logic
from CreateSection.Question_TypesV2.percent_sum import percent_sum_question, percent_sum_logic
from CreateSection.Question_TypesV2.percentage import percentage_question, percentage_logic
from CreateSection.Question_TypesV2.ranking import ranking_question, ranking_logic
from CreateSection.Question_TypesV2.grid import grid_question, grid_logic
from CreateSection.Question_TypesV2.single_text import single_text_question, single_text_logic
from CreateSection.Question_TypesV2.multi_text import multi_text_question, multi_text_logic 
from CreateSection.Question_TypesV2.transition import transition_question
from CreateSection.Question_TypesV2.maxdiff import maxdiff_question
from CreateSection.Question_TypesV2.hidden_variable import hidden_variable_question
from CreateSection.Question_TypesV2.ask_if import ask_if_logic
from CreateSection.Question_TypesV2.van_westendorp import van_westerndorp_question
from CreateSection.Question_TypesV2.multi_percentage import multi_percentage_question
from CreateSection.Question_TypesV2.zip_code import zip_code_question, zip_code_logic
from CreateSection.Question_TypesV2.notes import notes_question
from CreateSection.Question_TypesV2.multi_percentage import multi_percentage_question, multi_percentage_logic


from CreateSection.Question_TypesV2.unknown import unknown_question




def get_processor_map_sync():
    """Get the appropriate processor map based on AMI check"""


    
    return {
        "single-select": (single_select_question, single_select_logic),
        "single_select": (single_select_question, single_select_logic),
        "multi-select": (multi_select_question, multi_select_logic),
        "multi_select": (multi_select_question, multi_select_logic),
        "contact-form": (contact_form_question, None),
        "contact_form": (contact_form_question, None),
        "currency": (currency_question, None),
        "year": (year_question, None),
        "number": (number_question, None),
        "nps": (nps_question, None),
        "percent-sum": (percent_sum_question, None),
        "percent_sum": (percent_sum_question, None),
        "percentage": (percentage_question,None),
        "ranking": (ranking_question, None),
        "grid": (grid_question, None),
        "single-text": (single_text_question, None),
        "single_text": (single_text_question, None),
        "multi-text": (multi_text_question, None),
        "multi_text": (multi_text_question, None),
        "message": (transition_question, None),
        "transition": (transition_question, None),
        "maxdiff": (maxdiff_question, None),
        "max_diff":(maxdiff_question,None),
  

        "multi-percent": (multi_percentage_question, None),
        "multi_percent": (multi_percentage_question,None),
        "van-westendorp": (van_westerndorp_question, None),
        "van_westendorp": (van_westerndorp_question, None),
        "multi-percentage": (multi_percentage_question, None),
        "multi_percentage": (multi_percentage_question, None),
        "zipcode": (zip_code_question,None),
        "zip_code": (zip_code_question, None),
        "notes":(notes_question, None)
    }
    


