import re
import openai
import json
from datetime import datetime, timedelta
from dateutil.parser import parse

class Sanity_Utils:
    def find_gender_from_back(self, text):
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


    def is_valid_date(self, date_str):
        """Returns True if the string can be parsed as a valid date, regardless of format."""
        try:
            parse(date_str, fuzzy=False)
            return True
        except (ValueError, TypeError):
            return False


    def is_expiry_issue_diff_valid(self, issue_date_str, expiry_date_str):
        """Check if expiry date = issue date + 5 years - 1 day"""
        if self.is_valid_date(issue_date_str) and self.is_valid_date(expiry_date_str):
            issue_date = datetime.strptime(issue_date_str, "%Y/%m/%d")
            expiry_date = datetime.strptime(expiry_date_str, "%Y/%m/%d")
            expected_expiry = issue_date.replace(year=issue_date.year + 10) - timedelta(days=1)
            return expiry_date == expected_expiry
        return False

    def is_mrz_dob_mrz_field_match(self, dob_str, mrz_line2):
        """Check if DOB in MRZ matches the printed DOB"""
        dob = datetime.strptime(dob_str, "%Y/%m/%d")
        mrz_dob_raw = mrz_line2[:6]  # First 6 characters (YYMMDD)
        current_year_last2 = int(str(datetime.today().year)[-2:])
        year_prefix = "19" if int(mrz_dob_raw[:2]) > current_year_last2 else "20"
        mrz_dob = datetime.strptime(year_prefix + mrz_dob_raw, "%Y%m%d")
        return mrz_dob == dob

    def is_age_18_above(self, dob_str):
        """Check if the person is 18 or older as of today"""
        dob = datetime.strptime(dob_str, "%Y/%m/%d")
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age >= 18