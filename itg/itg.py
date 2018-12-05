# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 17:15:29 2018

@author: david alt
"""
import logging
import re
import pandas as pd

# ============================================================================
#  Setup logging
# ============================================================================
logging.basicConfig(level=logging.CRITICAL,
                    format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('itg')
log.setLevel(logging.DEBUG)


# ============================================================================
#  Parsing functions
# ============================================================================
def parse_flags(flags):
    if flags == 1:
        result = 'LINE'
    elif flags == 2:
        result = 'BOX'
    else:
        result = str(ControlFlag(flags)).replace('ControlFlag.','')
    return result


# Simple parse (no subparsing)
def PAGE(line):
    tokens = line.rstrip().split(',', maxsplit=9)
    return int(tokens[0])


def LEFT(line):
    tokens = line.rstrip().split(',', maxsplit=9)
    return int(tokens[1])


def TOP(line):
    tokens = line.rstrip().split(',', maxsplit=9)
    return int(tokens[2])


def RIGHT(line):
    tokens = line.rstrip().split(',', maxsplit=9)
    return int(tokens[3])


def BOTTOM(line):
    tokens = line.rstrip().split(',', maxsplit=9)
    return int(tokens[4])


def MEDCIN_ID(line):
    tokens = line.rstrip().split(',', maxsplit=9)
    return int(tokens[5])


def FLAGS(line):
    tokens = line.rstrip().split(',', maxsplit=9)
    return int(tokens[6])


# use with the Prefix enum for inner components
def PREFIX(line):
    tokens = line.rstrip().split(',', maxsplit=9)
    return tokens[7]


def ITEM_DATA(line):
    tokens = line.rstrip().split(',', maxsplit=9)
    return tokens[8]


def DESCRIPTION(line):
    tokens = line.rstrip().split(',', maxsplit=9)
    return tokens[9]


# Simple parse (no subparsing)
def simple_parse(item):
    item = item.rstrip()
    tokens = item.split(',', maxsplit=9)
    return tokens


# Detailed parse (subparsing of prefix etc)
#   Only use for "typical" items
#   Description may cause problems if doesn't have ~
def detailed_parse(item):
    tokens = simple_parse(item)
    prefix = tokens[7].replace('"', '').split('|')
    item_data = tokens[8]
    description = tokens[9].replace('"', '').split('~')
    result = tokens[0:7]
    result += prefix
    result.append(item_data)
    result += description
    return result


def item_to_simple_series(item):
    tokens = simple_parse(item)
    typed_tokens = []
    typed_tokens.append(int(tokens[0]))
    typed_tokens.append(int(tokens[1]))
    typed_tokens.append(int(tokens[2]))
    typed_tokens.append(int(tokens[3]))
    typed_tokens.append(int(tokens[4]))
    typed_tokens.append(int(tokens[5]))
    typed_tokens.append(int(tokens[6]))
    typed_tokens.append(tokens[7])
    typed_tokens.append(tokens[8])
    typed_tokens.append(tokens[9])

    cols = ['page', 'left', 'top', 'right', 'bottom', 'medcin', 'flags',
            'prefix', 'item_data', 'description']

    return pd.Series(typed_tokens, index=cols)


def parse_prefix(prefix):
    return prefix.replace('"', '').split('|')


def parse_options(item_data):

    options = {}
    if item_data != r'""':

        if ':' in item_data:  # TabStrip item
            tokens = [x.strip('"') for x in item_data.split(':')]

        elif '|' in item_data:  # all other items
            tokens = [x.strip('"') for x in item_data.split('|')]

        else:
            log.error('No valid delimiters ( | or : )')

        for token in tokens:
            key = re.search('(.*?)(?==)', token).group(1)
            value = re.search('(?<==)(.*)', token).group(1)

            if key == 'L':
                # split the value and add to dictionary
                new_key = re.search('(.*?)(?==)', value).group(1)
                new_value = re.search('(?<==)(.*)', value).group(1)

                value = ''  # replace L's value with ''
                options[key] = value
                options[new_key] = new_value

            else:
                options[key] = value

        # log.info(f'Tokens: {tokens}')
        # log.info(f'Dictionary: {options}')

    else:
        log.error('String didn\'t contain any options.')

    return options


def parse_description(description):
    return description.replace('"', '').split('~')


# ============================================================================
#  Validating functions
# ============================================================================
def validate_item_options(item):
    def_options = ['K', 'T', 'S', 'W', 'B', 'I', 'F', 'Z', 'U', 'C', 'N', 'L', 'O', 'P']
    checkbox_options = ['Y']
    frame_options = ['H', 'T']
    browsetree_options = ['I', 'B', 'S']
    grid_options = ['E', 'O', 'A', 'P', 'R', 'W']
    ribbon_options = ['G', 'T', 'R', 'Y', 'B', 'C', 'S', 'H', 'O']
    tabstrip_options = ['BS', 'CB', 'DF', 'EM', 'FB', 'HHL', 'MR', 'NB', 'PB', 'PL',
                        'PS', 'ROS', 'TP', 'TWS', 'V']
    medcin_options = ['O']
    list_options = ['G', 'O']
    valuebox_options = ['V']
    picture_options = ['MR', 'O']

    valid_options = True

    print(f'Flag: {FLAGS(item)}')
    print(f'Controls: {parse_flags(FLAGS(item))}')
    controls = parse_flags(FLAGS(item)).split('|')

    if 'CHKY' in controls or 'CHKN' in controls:
        print('chck present')
    # if


def validate_form_signature(form_signature):
    # line should contain 1 entry, enclosed in " "
    valid_count = True
    valid_entries = True

    form_signature = form_signature.rstrip()  # remove newline
    # use list comprehension to split and strip at once
    tokens = [x.strip() for x in form_signature.split(',')]
    if len(tokens) != 1:
        valid_count = False
        log.error(f'invalid number of entries ({len(tokens)}); should be 1.')

    if (form_signature[0] != r'"' or form_signature[len(form_signature) - 1] != r'"'):
        valid_entries = False
        log.error(f'\'{form_signature}\' is not enclosed in double quotes (\"...")')

    return (valid_count and valid_entries)


def validate_form_identification(form_identification):
    # line should contain 3 or 4 entries, each enclosed in " "
    valid_count = True
    valid_entries = True

    # use list comprehension to split and strip at once
    tokens = [x.strip() for x in form_identification.split(',')]
    if (len(tokens) < 3 or
            len(tokens) > 4):
        valid_count = False
        log.error(f'invalid number of entries ({len(tokens)}); should be 3 or 4.')

    for token in tokens:
        if (token[0] != r'"' or token[(len(token) - 1)] != r'"'):
            valid_entries = False
            log.error(f'\'{token}\' is not enclosed in double quotes (\"...")')

    return (valid_count and valid_entries)


def validate_form_obj(form_obj):
    valid_form_obj = True
    tokens = [x.strip() for x in form_obj.split(',', maxsplit=9)]

    # Vulnerability: doesn't check for >10 fields b/c too lazy to distinguish DESCRIPTION
    if (len(tokens) < 10):
        valid_form_obj = False
        log.error(f'invalid number of fields ({len(tokens)}) (should be 10)')

    if int(FLAGS(form_obj)) != ControlFlag.FORM:
        valid_form_obj = False
        log.error('Incorrect ControlFlag (should be 1048576)')

    # ToDo:
    #   PAGE should be 0
    #   LEFT and TOP should be int and 0
    #   RIGHT and BOTTOM should be int and >0
    #   MEDCIN_ID should be 0
    #   PREFIX should be ""
    #   ITEM_DATA should be ""
    #   DESCRIPTION should be ""

    return valid_form_obj


def validate_tabstrip_obj(tabstrip_obj):
    # ToDo:
    #   ControlFlag should be 32
    #   PAGE should be last page
    #   LEFT, TOP, RIGHT, BOTTOM should be 5,377,295,395 (but I don't know why)
    #   MEDCIN_ID should be 0
    #   valid PREFIX: 26 entries (even if blank; don't strip whitespace)
    #   valid ITEM_DATA: no invalid entries
    #   valid DESCRIPTION: page label count == PAGE
    #   5, 5, 377, 295, 395, 0, 32,
    #   " |||||||0|0||0|0|||0|||0|0|0|0|0|0|||",
    #   "L=V=13:DF=1:PS=1:TP=0:MR=T:BS=0:TWS=0:PB=2:NB=3:ROS=1:PL=1:FB=1:EM=1:CB=2:HHL=F",
    #   ":-2147483633:Provider|%3Development|%2Screening|Procedures|Resources"
    pass


def validate_browsetree_obj(browsetree_obj):
    pass


def validate_form_item(form_item):
    return len(form_item.split(',', maxsplit=9)) == 10


# ============================================================================
#  CONSTANTS (enums, flags)
# ============================================================================

from enum import Enum, IntFlag

class Prefix(Enum):
    # "0|1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25"
    PREFIX = 0
    MODIFIER = 1
    RESULT = 2
    STATUS = 3
    VALUE = 4
    LINK_GROUP = 5
    UNITS = 6
    BOX_OFFSET = 7
    INLINE_TEXTBOX_WIDTH = 8
    COMPONENT_SEQUENCE = 9
    INDEX_TO_REFERENCE_LIST = 10
    NARRATIVE_GROUP_ASSIGNMENT = 11
    CHKY_CAPTION = 12
    CHKN_CAPTION = 13
    BIT_FLAGS = 14
    LIMIT_MAX = 15
    LIMIT_MIN = 16
    RIBBON_TRIGGER_ID = 17
    CLUSTER_ID = 18
    PARENT_RIBBON_ID = 19
    RADIO_BUTTON_GROUP = 20
    IMAGE_ID = 21
    HOTSPOT_SET_ID = 22
    PARENT_FRAME = 23
    CODE_MAPPING = 24
    USER_ASSIGNED_SUBGROUP = 25


class ControlFlag(IntFlag):
    NONE = 0
    #LINE = 1 # maybe this should just be removed ...
    #BOX = 2 # Frame object; maybe this should just be removed ...
    LEFT = 1  # left alignment, where applicable
    RIGHT = 2 # right alignment, where applicable
    TREE = 4 # Data entry tree
    GRID = 8 # Grid object
    RIBBON = 16 # Ribbon object
    TABSTRIP = 32 # Page control (tab strip)
    PICTURE = 64 # picture object
    REQ = 128 # Medcin entry is required
    CHKY = 256 # Medcin yes checkbox component
    CHKN = 512 # Medcin no checkbox component
    ROS = 1024 # Medcin ROS state
    VALUE = 2048 # Medcin textbox to enter value
    BROWSE = 4096 # Medcin button to browse children findings
    NOTE = 8192 # Medcin Note button to popup note box for Medcinid > 0.
    """
    When the flag value is identical to fc_Note and the Medcinid is 0, the record either: 
    (Page=0) the pre-defined chapter headings in the description and itemdata properties 
            (substrings are delimited with a tilde character), or 
    (Page=1) the pre-defined Encounter-specific User SubGroup headings in the description 
             and itemdata properties (substrings are Tab delimited)
    """
    LINK = 16384 # button to link to another form
    LABEL = 32768 # label for captions
    UPDOWN = 65536 # Medcin UpDown button
    HASDATA = 131072 # Logic display indicator
    REFERENCE = 262144 # reference document, or finding reference button
    ONSET = 524288 # Medcin Onset combo
    FORM = 1048576 # form size
    SEARCH = 2097152 # Word search toolbar
    ACTION = 2097152 # Action component
    TEXTBOX = 4194304 # Medcin free-text entry box
    DROPBOX = 8388608 # Medcin Picklist ' dropdown listbox
    LISTBOX = 16777216 # Medcin Picklist Full listbox
    LISTVIEW = 20971520 # Medcin Picklist ' multi-column listview
    INLINENOTE = 33554432 # Medcin inline textbox
    RICHTEXTBX = 37748736 # Medcin rich textbox
    PICKLIST = 134217728 # Picklist
    ROSTGL = 268435456 # Medcin ROS toggle button
    WINDOW = 536870912 # Window
    TIMING = 1073741824 # Timing Button component