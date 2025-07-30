from abstract_security import *
import os, time
from datetime import datetime, timedelta
from itertools import permutations
from abstract_utilities import eatAll
def capitalize(string):
   string = str(string)
   return  string[0].upper()+string[1:]
def add_to_dict(key,value,_dict={}):
   _dict[key]=value
   return _dict
def get_dict(is_true=False,*args,**kwargs):
   return {key:value for key,value in kwargs.items() if is_true or value}      
def get_env(key=None,path=None):
   return get_env_value(**get_dict(key=key,path=path))
def unique_name(file_path,ext=None):
     dirName=os.path.dirname(file_path)
     baseName=os.path.basename(file_path)
     fileName,exts=os.path.splitext(baseName)
     ext=ext or exts
     dir_list = os.listdir(dirName)
     new_file_name=f"{fileName}{ext}"
     for i,file_name in enumerate(dir_list):
         if new_file_name not in dir_list:
             break
         new_file_name = f"{fileName}_{i}{ext}"
     file_path = f"{os.path.join(dirName,new_file_name)}"
     return file_path

def generate_date_formats():
    """
    Generates a list of datetime formats to try parsing date strings.
    Includes common and less-common variations with different separators.
    """
    base_formats = ['%Y', '%m', '%d', '%H', '%M', '%S', '%f']
    date_parts = ['%Y', '%m', '%d']
    time_parts = ['%H', '%M', '%S', '%f']
    separators = ['-', '/', ' ']
    
    date_formats = []
    for sep in separators:
        for order in permutations(date_parts, 3):
            date_format = f"{order[0]}{sep}{order[1]}{sep}{order[2]}"
            for time_sep in [':', '.']:
                for time_order in permutations(time_parts, 3):
                    time_format = f"{time_order[0]}{time_sep}{time_order[1]}{time_sep}{time_order[2]}"
                    date_formats.append(f"{date_format} {time_format}")
                    if '%f' in time_order:  # include formats with and without microseconds
                        short_time_format = time_format.replace('%f', '').rstrip(time_sep)
                        date_formats.append(f"{date_format} {short_time_format}")
            # Also add formats without time
            date_formats.append(date_format)
    
    return list(set(date_formats))  # Use set to remove duplicates and then convert back to list


def is_datetime_string(date_str):
    for format in generate_date_formats():
        try:
            datetime.strptime(date_str, format)
            return True
        except ValueError:
            continue
    return False

def find_datetime_format(date_str):
    for format in generate_date_formats():
        try:
            if datetime.strptime(date_str, format):
                return format
        except ValueError:
            continue
    return None

def compare_datetime_formats(format1, format2):
    return format1 == format2

def make_type(list_obj,types):
    listy_obj = make_list(list_obj)
    new_list = list_obj
    list_obj = []
    for obj in new_list:
        for ty in types:
            try:
                obj = ty(obj)
            except:
                pass
        list_obj.append(obj)
    return list_obj
def convert_column(df,column,ty):
    df = get_df(df)
    ty= make_list(ty)
    for typ in ty:
        try:
            df[column] = df[column].astype(typ)
        except:
            pass
    return df
def return_float_or_int(obj):
    try:
        if float(obj) == float(str(int(obj))):
            return int(obj)
        else:
            return float(obj)
    except:
        pass
def safe_get(obj,i):
    if len(obj) >abs(i):
        return obj[i]
def get_number(value):
    try:
        return float(value)  # Using float to handle fractional bounds if necessary
    except (ValueError, TypeError):
        return None

def all_combinations_of_strings(strings):
    """
    Generate all possible combinations of the input strings.
    Each combination is a concatenation of the input strings in different orders.

    :param strings: A list of strings for which we want to generate all combinations.
    :return: A list of strings representing all possible combinations.
    """
    all_perms = permutations(strings)
    combinations = [''.join(perm) for perm in all_perms]
    return combinations
def clean_list(list_obj):
    while '' in list_obj:
        list_obj.remove('')
    return list_obj
def split_and_clean_lines(query):
    query = query.replace('\n',',')
    return list(set([eatAll(quer,[',',' ','\t','\n']) for quer in clean_list(query.split(','))]))

def all_date_formats():
    date_formats = []
    for part in all_combinations_of_strings("Ymd"):
        for separator in ['/', '-', '_']:
            date_pattern = ''
            for piece in part:
                date_pattern += f"%{piece}{separator}"
            for time_format in ["%H:%M:%S.%f", "%H:%M:%S"]:
                date_format = f"{date_pattern[:-1]} {time_format}"
                if date_format not in date_formats:
                    date_formats.append(date_format)
    return date_formats

def convert_date_to_timestamp(date_string, date_formats=[]):
    default_date_formats = all_date_formats()  # This generates a comprehensive list of date formats to try
    date_string = str(date_string)
    date_formats = make_list(date_formats) + default_date_formats
    for format in date_formats:
        try:
            date_object = datetime.strptime(date_string, format)
            return date_object.timestamp()
        except ValueError:
            continue
    print(f"Date format not recognized: {date_string}")
    return None
def analyze_and_compare_dates(date_str1, date_str2):
    """
    Analyzes two date strings, checks if both are valid dates, finds their formats,
    and compares these formats.
    """
    is_date1 = is_datetime_string(date_str1)
    is_date2 = is_datetime_string(date_str2)
    
    if not is_date1 or not is_date2:
        return (False, "One or both strings are not valid datetime strings.")
    
    format1 = find_datetime_format(date_str1)
    format2 = find_datetime_format(date_str2)
    
    if format1 and format2:
        are_same_format = compare_datetime_formats(format1, format2)
        return (True, f"Both are datetime strings. Same format: {are_same_format}. Format1: {format1}, Format2: {format2}")
    else:
        return (False, "Could not determine the formats of one or both datetime strings.")


def is_file_path(file_path):
    """
    Check if the provided file_path is a valid file path pointing to an existing file.
    
    Args:
    file_path (str): The file path to check.

    Returns:
    bool: True if file_path is a string referring to a valid file, False otherwise.
    """
    if not isinstance(file_path, str):
        return False
    try:
        # This will return True if file_path is a file that exists
        return os.path.isfile(file_path)
    except OSError as e:
        # Optionally log the error or handle it if needed
        print(f"An error occurred: {e}")
        return False
def find_numbers_of_length(text, length):
    """
    Finds all numbers of a specified length within the given text.

    Parameters:
        text (str): The text to search within.
        length (int): The exact length of the numbers to match.

    Returns:
        list: A list of all numbers of the specified length found in the text.
    """
    pattern = r'\b\d{' + str(length) + r'}\b'
    matches = re.findall(pattern, text)
    return matches
