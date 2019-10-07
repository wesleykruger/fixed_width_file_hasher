from pathlib import Path
import random
import string
import os.path
from datetime import date, timedelta
import re


# This must come before the user definition section
class RedactObject:
    def __init__(self, record_type_start_pos: int, record_value: str,
                 redact_start_pos: int, redact_length: int, data_type: str):
        self.record_type_start_pos = record_type_start_pos
        self.record_value = record_value
        self.redact_start_pos = redact_start_pos
        self.redact_length = redact_length
        self.data_type = data_type


# *****************************************************************
# USER INPUT SECTION

# Define the FILES you will be reading/writing. Ensure these are not directories.
# Ensure that the output file directory can be written to. If a file already exists with this name it WILL be overwritten.
input_file = Path(r''.replace(r'\&', '/'))
output_file = Path(r''.replace(r'\&', '/'))

# This is the number of lines that the program will store in memory before writing to a file
# Recommend keeping it fairly high (thousands), this is mostly to strike a balance between a) too many writes to the drive b) excessive memory usage
line_limit = 1000

# Enter your lines to mask here, each as a new RedactObject.
# Each should follow this format, and they should be separated by commas within the array:

# record_type_start_pos(int): This is where we should begin looking for an indicator that a value needs to be redacted on this line. If it is the first character, it will be 0.
# record_value(str): This is the value that we should be looking for to know to redact a different part of the line.
# redact_start_pos(int): This is the first character in the string that needs to be redacted. Remember it is 0-based.
# redact_length(int): This is the length of the string starting at redact_start_pos that needs to be redacted.
# data_type: This tells us the necessary format of the redaction. The purpose of this is to ensure that the output can still be processed as valid data.
# data_type property in each object should be 'str', 'int', 'date', or 'state'. Anything else will produce an error.

# Ex: redact_array = [
#     RedactObject(record_type_start_pos=0, record_value='A', redact_start_pos=43, redact_length=18, data_type='str'),
#     RedactObject(record_type_start_pos=0, record_value='C', redact_start_pos=9, redact_length=10, data_type='int'),
#     RedactObject(record_type_start_pos=0, record_value="LA\d\d", redact_start_pos=41, redact_length=4, data_type='str'),
# ]
# All strings are case-sensitive
# Record value search supports regular expressions
# Care when using overlapping record values ('C' and 'CA\d\d'), as ALL matching results will be redacted

redact_array = [
    RedactObject(record_type_start_pos=0, record_value='A', redact_start_pos=43, redact_length=18, data_type='str'),
    RedactObject(record_type_start_pos=0, record_value='B', redact_start_pos=33, redact_length=9, data_type='str'),
    RedactObject(record_type_start_pos=0, record_value='C', redact_start_pos=9, redact_length=10, data_type='int'),
    RedactObject(record_type_start_pos=0, record_value='D', redact_start_pos=28, redact_length=1, data_type='int'),
    RedactObject(record_type_start_pos=0, record_value='E', redact_start_pos=62, redact_length=5, data_type='int'),
    RedactObject(record_type_start_pos=0, record_value='H', redact_start_pos=59, redact_length=8, data_type='date'),
    RedactObject(record_type_start_pos=0, record_value='F', redact_start_pos=19, redact_length=2, data_type='state'),
    RedactObject(record_type_start_pos=0, record_value="LA\d\d", redact_start_pos=41, redact_length=4, data_type='str'),
]

# END USER DEFINITIONS
# ********************************************************************


def validate_objects(obj):
    if type(obj.record_type_start_pos) != int or type(obj.record_value) != str \
            or type(obj.redact_start_pos) != int or type(obj.redact_length) != int:
        return 'TypeError'
    elif obj.data_type != 'str' and obj.data_type != 'int' and obj.data_type != 'date' and obj.data_type != 'state':
        return 'DataType'
    else:
        return True


def random_string(text_or_int, non_blank_indexes, data_type):
    length = len(text_or_int)
    if data_type == 'int':
        numbers = '0123456789'
        characters = ''.join(random.choice(numbers) for i in range(length) if i not in non_blank_indexes)
    elif data_type == 'date':
        # Pick a random date between 18-60 years ago
        start_dt = (date.today() - timedelta(weeks=3120)).toordinal()
        end_dt = (date.today() - timedelta(weeks=936)).toordinal()
        characters = date.fromordinal(random.randint(start_dt, end_dt)).strftime("%Y%m%d")
    elif data_type == 'state':
        state_tuple = (
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS',
            'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY',
            'NC,' 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV',
            'WI', 'WY'
        )
        characters = random.choice(state_tuple)
    else:
        letters = string.ascii_letters
        characters = ''.join(random.choice(letters) for i in range(length))
    list_to_return = []
    for i, value in enumerate(characters):
        if i in non_blank_indexes:
            list_to_return.append(value)
        else:
            list_to_return.append(" ")
    return ''.join(list_to_return)


def redact(arr):
    lines = []
    if not os.path.isfile(input_file):
        raise FileNotFoundError('Input file does not exist, please enter a valid path.')
    # Initial quick sweep to make sure that all entries are valid
    for index, validate_entry in enumerate(arr):
        # Zero-based index is confusing for error message
        error_index = index + 1
        if validate_objects(validate_entry) == 'TypeError':
            raise TypeError('You are using the incorrect data type for one of your properties '
                            'in object number {}'.format(error_index))
        elif validate_objects(validate_entry) == 'DataType':
            raise Exception("The data type you selected in redact object number {} is incorrect. "
                            "Please select either 'str', 'int', 'state', or 'date'.".format(error_index))

    # Overwrite output file if it already exists so we're not appending each time
    if os.path.isfile(output_file):
        open(output_file, 'w',).close()
    # Read through each line one at a time, write when we hit our limit to ensure we don't go over available memory
    with open(input_file, 'r', encoding='utf8') as fileobject:
        for line in fileobject:
            for entry in arr:
                x = re.search(entry.record_value, line)
                if x is not None:
                    if x.span()[0] == entry.record_type_start_pos:
                        text_to_replace = line[entry.redact_start_pos:entry.redact_start_pos + entry.redact_length]
                        text_to_replace_value_check = []
                        for i, value in enumerate(text_to_replace):
                            if value != " ":
                                text_to_replace_value_check.append(i)
                        redact_values = random_string(text_to_replace, text_to_replace_value_check, entry.data_type)
                        line = line[:entry.redact_start_pos] + redact_values + line[entry.redact_start_pos + len(redact_values):]
            lines.append(line)
            if len(lines) >= line_limit:
                with open(output_file, 'a+', encoding='utf8') as a:
                    a.write(''.join(lines))
                    lines = []
    # Final append write for any lines left over
    if len(lines) > 0:
        with open(output_file, 'a+', encoding='utf8') as w:
            w.write(''.join(lines))
            w.close()


if __name__ == '__main__':
    redact(redact_array)
