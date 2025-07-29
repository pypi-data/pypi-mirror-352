import re
import openai
import json

def find_gender_from_back(text):
    gender = ''
    gender_pattern = r'(\d)([A-Za-z])(\d)'
    gender_match = re.search(gender_pattern, text)
    if gender_match:
        gender = gender_match.group(2)

    if not gender:
        gender_pattern = r'(\d)([MFmf])(\d)'
        gender_match = re.search(gender_pattern, text)
        if gender_match:
            gender = gender_match.group(2)

    return gender
