import os, fnmatch, sys, shutil
from pathlib import Path
import random
import string

input_file = Path('C:/Users/wesleykruger/Documents/BBVA/pii-shuffle/test.txt')
output_file = Path('C:/Users/wesleykruger/Documents/BBVA/pii-shuffle/test2.txt')

class ScrambleObject:
    def __init__(self, record_type_start_pos: int, record_type_indicator_length: int, record_value: str, scramble_start_pos: int, scramble_length: int, data_type: str):
        self.record_type_start_pos = record_type_start_pos
        self.record_type_indicator_length = record_type_indicator_length
        self.record_value = record_value
        self.scramble_start_pos = scramble_start_pos
        self.scramble_length = scramble_length
        self.data_type = data_type

#Enter your lines to scramble
scramble_array = [
    ScrambleObject(0, 1, 'c', 2, 4, 'string')
]


def randomString(text_or_int, data_type):
    length = len(text_or_int)
    if data_type == 'int':
        numbers = list(range(10))
        characters = ''.join(random.choice(numbers) for i in range(length))
    else:
        letters = string.ascii_lowercase
        characters = ''.join(random.choice(letters) for i in range(length))
    return characters


def scramble(scramble_array):
    lines = []
    with open(input_file, encoding='utf8') as f:
        s = f.readlines()
        for line in s:
            lines.append(line)
    for entry in scramble_array:
        for index, line in enumerate(lines):
            if line[entry.record_type_start_pos: entry.record_type_start_pos + entry.record_type_indicator_length] == entry.record_value:
                text_to_replace = line[entry.scramble_start_pos:entry.scramble_start_pos + entry.scramble_length]
                scramble_values = randomString(text_to_replace, entry.data_type)
                line = line[:entry.scramble_start_pos] + scramble_values + line[entry.scramble_start_pos + len(scramble_values):]
                print(line)
            lines[index] = line
    with open(output_file, 'w', encoding='utf8') as w:
        w.write(''.join(lines))
    w.close()


if __name__ == '__main__':
    scramble(scramble_array)