import csv

csv.field_size_limit(104857600)

# def extract_string(input_str):
#     """
#     Extracts the abstract from the input string.

#     input_str (str): The whole text from the dataset.
    
#     Returns:
#         str: The abstract of the paper.
#     """
#     start_str = '"abstractHtml":'
#     end_str = '"backgroundTextHtml"'
#     start_index = input_str.find(start_str) + len(start_str)
#     end_index = input_str.find(end_str)
#     return input_str[start_index:end_index]

# def zip_dicts(key_dict, abs_dict):
#     """
#     Zips two dictionaries into a single dictionary of tuples.

#     key_dict (dict): Dictionary containing keys.
#     abs_dict (dict): Dictionary containing abstracts.

#     Returns:
#         dict: Merged dictionary with tuples of (key, abstract).
#     """
#     big_dict = {}
#     for key in key_dict.keys():
#         big_dict[key] = (key_dict[key], abs_dict[key])
#     return big_dict

def tuple_list_to_strings(tuple_list):
    """
    Converts a list of tuples into a list of strings.

    tuple_list (list): List of tuples.

    Returns:
        list: List of strings.
    """
    result = []
    for tuple_item in tuple_list:
        string = " ".join(tuple_item)
        result.append(string)
    return result

def count_frequency(keywordlist, ngram_list):
    """
    Counts the frequency of keywords in a list of n-grams.

    keywordlist (list): List of keywords.
    ngram_list (list): List of n-grams.

    Returns:
        dict: Dictionary containing keyword frequencies.
    """
    frequency = {}
    for element in keywordlist:
        frequency[element] = ngram_list.count(element)
    return frequency

# def merge_dicts(key_freq, safe_freq):
#     """
#     Merges two dictionaries together.

#     key_freq (dict): Keywords frequency.
#     safe_freq (dict): Safe words frequency.

#     Returns:
#         dict: Merged dictionary.
#     """
#     merged = {}
#     for key in key_freq.keys():
#         merged[key] = {**key_freq[key], **safe_freq[key]}
#     return merged

# def write_2csv(tuple_name, key_file, abs_file):
#     """
#     Writes two dictionaries into two CSV files.

#     tuple_name (tuple): Tuple containing dictionaries of keywords and abstracts.
#     key_file (str): File path for keywords CSV.
#     abs_file (str): File path for abstracts CSV.
#     """
#     with open(key_file, 'w', newline='') as file0:
#         writer0 = csv.writer(file0)
#         keywords = tuple_name[0]
#         for key, value in keywords.items():
#             writer0.writerow([key, value])
#     with open(abs_file, 'w', newline='') as file1:
#         writer1 = csv.writer(file1)
#         abstracts = tuple_name[1]
#         for key, value in abstracts.items():
#             writer1.writerow([key, value])
            
# def readback(file_name):
#     """
#     Reads a CSV file and returns a dictionary.

#     file_name (str): File path of the CSV file.

#     Returns:
#         dict: Dictionary read from the CSV file.
#     """
#     dict_name = {}
#     with open(file_name, 'r', newline='') as file:
#         reader = csv.reader(file)
#         for row in reader:
#             key = row[0]
#             value = row[1]
#             dict_name[key] = value
#     return dict_name

# def write_1csv(dict_name, file_name):
#     with open (file_name, 'w', newline='') as file0:
#         writer0 = csv.writer(file0)
#         #write the header row
#         #writer.writerow(['key', 'list'])
#         #write each key-value pair as a row in the CSV file
#         for key, value in dict_name.items():
#             writer0.writerow([key, value])