import logging
import re
import itg

# ============================================================================
#  Setup logging
# ============================================================================
logging.basicConfig(level=logging.CRITICAL,
                    format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('template_models')
log.setLevel(logging.DEBUG)


# ============================================================================
#  AhltaTemplate: dictionary-based template model
# ============================================================================
class AhltaTemplate:
    
    # Constructor
    def __init__(self, fhand, logging=True):
        self.header = []
        self.pages = {}
        self.logging = logging

        with open(fhand, 'r', encoding='latin1') as f:
            if self.logging:
                log.warning('file arbitrarily opened as latin1 encoding')
            self.template = f.readlines()

        # TODO make this a try block
        if self._validate_template():
            self._parse_items()
            self._parse_header()
        else:
            log.error('Template validation failed.')

    # Private Methods
    def _validate_template(self):
        if self.logging:
            log.warning('partially implemented')
            log.info(f'Form Signature:       {itg.validate_form_signature(self.template[0])}')
            log.info(f'Form Identification:  {itg.validate_form_identification(self.template[1])}')
            log.info(f'Form Object:          {itg.validate_form_obj(self.template[2])}')
            log.info(f'Tabstrip Object:      {itg.validate_tabstrip_obj(self.template[3])}')
            log.info(f'BrowseTree Object:    {itg.validate_browsetree_obj(self.template[4])}')
            #log.info(f'Form Item:            {itg.Validator.validate_form_item(self.template[5])}')
        return True


    def _parse_items(self):
        # Store items by page in a dictionary, using page numbers as keys
        line_num = 1
        for line in self.template:
            if line_num <= 5: # first five lines belong to the header
                self.header.append(line) 
            else:
                #line = line.rstrip() # strip any newline characters
                tokens = line.split(',', maxsplit=9) # split into tokens
                key = int(tokens[0]) # use the first token as the key
                if key not in self.pages:
                    self.pages[key] = [] # add that key with an empty (unnamed) list
                self.pages[key].append(line) # otherwise add the line to an existing list
            line_num += 1

            
    def _parse_header(self):
        # Extract template-level information
        self.form_signature = self.header[0].rstrip() #version of medcin form designer software
        self.form_name = self.header[1].split(',', maxsplit=9)[0]
        self.form_owner = self.header[1].split(',', maxsplit=9)[1]
        self.form_group = self.header[1].rstrip().split(',', maxsplit=9)[2]
        self.form_sid = 'none'
        if len(self.header[1].split(',', maxsplit=9)) == 4:
            self.form_sid = self.header[1].rstrip().split(',', maxsplit=9)[3]
        
        # get page names and count
        self.page_names = self._parse_page_names()
        #self.page_count = len(self.visible_page_names)
        self.page_count = len(self.pages)
        
        # Setup important header pieces
        self.form_obj = self.header[2]
        self.tabstrip = self.header[3]
        self.browsetree = self.header[4]
        
        # ensure we've got the Form line (3rd line of header) before getting width, height
        if int(itg.FLAGS(self.form_obj)) == itg.ControlFlag.FORM:
            
            self.form_width = itg.RIGHT(self.form_obj)
            self.form_height = itg.BOTTOM(self.form_obj)
            
        else:
            print('ERROR: Incorrect flag on line 3 of header (should be 1048576')
            print(f'Line 3 of header:  {self.form_obj}')
            
        # ensure we've got the TabStrip obj
        if int(itg.FLAGS(self.tabstrip)) == itg.ControlFlag.TABSTRIP:
            form_backcolor_search = re.search('(?<=:)(.*?)(?=:)', itg.DESCRIPTION(self.tabstrip))
            if form_backcolor_search:
                self.form_backcolor = form_backcolor_search.group(1)
                
            #self.form_border_style -BS
            #self.form_default_checkbox_style -CB
            #self.details_frame -DF
            #self.form_em_button -EM
            #self.form_flowsheet_button -FB
            #self.form_multirow -MR
            #self.form_negative_buttons -NB
            #self.form_positive_buttons -PB
            #self.form_picklist_button -PL
            #self.form_page_style -PS
            #self.form_ros_button -ROS
            #self.form_tabstrip_button_placement -TP
            #self.form_tabstrip_tab_width -TWS
            #self.form_version -V
            # often you see L=V= ... unclear why or if necessary
        else:
            print('ERROR: Incorrect flag on line 4 of header (should be 32)')
            print(f'Line 4 of header:  {self.tabstrip}')

    def _parse_page_names(self):
        # Page names need to be cleaned of prefixes and suffixes:
        #   :numbers: for page 1 indicates back color of the form
        #   # (no_browsing), < (left_lateral), > (right_lateral)
        #   %int denotes number of columns on the page
        #   ~int as a suffix denotes a narrative chapter assignment
        raw = itg.DESCRIPTION(self.header[3])
        
        tokens = raw.strip('\"').split('|')
        clean_tokens = []
        clean_tokens.append('<universal>')
        
        page_one = re.sub(r'\%\d','',tokens[0].split(':')[len(tokens[0].split(':')) - 1])
        clean_tokens.append(page_one)
        
        for page in range(len(tokens)):
            if page == 0:
                continue
            else:
                cleaned_page = re.sub(r'\%\d','',tokens[page])
            clean_tokens.append(cleaned_page)
        
        return clean_tokens


    def _parse_form_properties(self):
        pass


    def _validate_header(self):
        # ToDo:
        #   header lines are in the expected place
        #   form_sid is accounted for
        #   specified page count matches number of page names (for visible pages,
        #       ignoring page 0)
        #   Form object is the third item, and has a width and height
        #   TabStrip object is appropriate
        #   BrowseTree object is appropriate
        pass

    
    # Public Methods
    def info(self):
        page_info = f'Pages ({self.page_count}):\n'
        for page, item_list in sorted(self.pages.items()):
            page_label = str(page) + f' [{self.page_names[page]}]'
            page_info += f'  {page_label}:  {len(item_list)} items\n'
            
        return(f'Template: {self.form_name}\n' +
               f'Owner: {self.form_owner}\n' +
               f'Group: {self.form_group}\n' +
               f'Software: {self.form_signature}\n' +
               f'Security ID: {self.form_sid}\n\n' +
               f'Width: {self.form_width} pixels\n' +
               f'Height: {self.form_height} pixels\n\n' +
               page_info +
               f'Total (including header): {len(self.template)} items'
               )
    
    def print_info(self):
        print(self.info())
        
    def print_header(self):
        for line in self.header:
            print(line)
            
    def print_by_page(self, page):
        print(f'Page: {page} ({(len(self.pages[page]))} items)')
        for line in self.pages[page]:
            print(line.rstrip())

# ============================================================================
#  AhltaTemplateDF: dataframe-based template model
# ============================================================================
import pandas as pd

class AhltaTemplateDF:
    # Constructor
    def __init__(self, fhand, logging=True):
        self.header = []
        self.pages = {}
        self.logging = logging

        with open(fhand, 'r', encoding='latin1') as f:
            if self.logging:
                log.warning('File arbitrarily opened as latin1 encoding.')
            self.template = f.readlines()

        self._parse_items()

    def _parse_items(self):
        # Store items in a dataframe of series
        imported_items = []
        cols = ['page', 'left', 'top', 'right', 'bottom', 'medcin', 'flags',
                'prefix', 'item_data', 'description']

        line_num = 1
        for line in self.template:
            if line_num <= 5: # first five lines belong to the header
                self.header.append(line)
            else:
                imported_items.append(pd.Series(itg.item_to_simple_series(line), index=cols))

            line_num += 1

        self.items = pd.DataFrame(imported_items, columns=cols)

    # Public methods
    def info(self):
        print('Item counts by page:')
        print(self.items.page.value_counts().sort_index())
        print('\nFlag counts:')
        print(self.items.flags.value_counts().sort_index())

# ============================================================================
#  AhltaTemplateXml: xml-based template model
# ============================================================================
class AhltaTemplateXml:
    pass


# ===========================================================================+
#  XML-related functions
#      TODO: MOVE INTO ITEM_PARSER OR MAKE ITS OWN CLASS
# ===========================================================================+
import xml.etree.ElementTree as ET
#from ahlta_template import ahlta_template
#from ahlta_item import item_Parser as ip

# Takes a parsed item (from parse_template_item) and returns an xml node
#   This WILL break if used for items without every property 
#   e.g., "" for prefix or description without a tilde
def detailed_parsed_item_to_xml(parsed_item, name='item'):
    subelements = [
        'page',
        'left', 'top', 'right', 'bottom',
        'medcin_id', 'flags', 
        'prefix', 'modifier', 'result',
        'status', 'value', 'link_group',
        'units', 'box_offset', 'inline_textbox_width',
        'component_sequence', 'index_to_reference_list',
        'narrative_group_assignment', 
        'chky_caption', 'chkn_caption', 'bit_flags',
        'limit_max', 'limit_min', 'ribbon_trigger_id',
        'cluster_id', 'parent_ribbon_id', 'radio_button_group',
        'image_id', 'hotspot_set_id', 'parent_frame',
        'code_mapping', 'user_assigned_subgroup',
        'item_data', 'caption', 'content'
    ]
    
    item_node = ET.Element(name)
    
    for i in range(len(subelements)):
        sub_el = ET.SubElement(item_node, subelements[i])
        sub_el.text = parsed_item[i]
    
    return item_node


def simple_parsed_item_to_xml(item, name):
    subelements = [
            'page',
            'left', 'top', 'right', 'bottom',
            'medcin_id', 'flags', 
            'prefix', 'item_data', 'description'
            ]
    
    item_node = ET.Element(name)
    
    for i in range(len(subelements)):
        sub_el = ET.SubElement(item_node, subelements[i])
        sub_el.text = item[i]
    
    return item_node   


def unparsed_item_to_xml(item, name):
    parsed = item.rstrip().split(',', maxsplit=9) # simple parse
    return simple_parsed_item_to_xml(parsed, name)     


def convert_template_to_xml(template):
    # TODO: Do we need to write xml version/encoding info first?
    
    template_xml = ET.Element('template')
    header = ET.SubElement(template_xml, 'header')
    
    for i in range(template.page_count+1): # +1 b/c page_count ignores page_0
        # setup the node for the page
        node_name = 'page_' + str(i)
        page_node = ET.SubElement(template_xml, node_name)
        
        for item in template.pages[i]:
            ctrl_flag = str(itg.FLAGS(item))
            item_node = unparsed_item_to_xml(item, ctrl_flag)
            page_node.append(item_node)
    
    # Use template name as filename
    f_out = template.form_name.strip('"') + '.xml'
    
    # Write to file with xml declaration
    ET.ElementTree(template_xml).write(f_out, encoding='utf-8', xml_declaration=True) 


#convert_template_to_xml(template)