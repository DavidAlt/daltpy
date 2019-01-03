import os, sys, time, threading
import re

# pdfminer.six
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from io import StringIO

import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)s : %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('pdf_get_doi')
log.setLevel(logging.DEBUG)


# Threaded console progress indicator
class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1: 
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator)) # write the character to the buffer
            sys.stdout.flush()  # force the buffer to print to stdout immediately (clearing the buffer)
            time.sleep(self.delay) # wait
            sys.stdout.write('\b') # backspace one character
            sys.stdout.flush() # empty the buffer so it's ready for the next character

    def start(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def stop(self):
        self.busy = False
        time.sleep(self.delay)
        


def convert_pdf_to_text(path):
    resource_manager = PDFResourceManager()
    return_string = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(resource_manager, return_string, codec=codec, laparams=laparams)
    file_path = open(path, 'rb')
    interpreter = PDFPageInterpreter(resource_manager, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(file_path, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    result = return_string.getvalue()

    file_path.close()
    device.close()
    return_string.close()

    return result


def find_all_doi(text):
    # regex pattern for DOI: \b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)\b
    #  see: https://stackoverflow.com/questions/27910/finding-a-doi-in-a-document-or-page
    #  fancy sanity checking: run the doi against https://doi.org/ and test that you get
    #    a 200 OK http status and that the returned page is not the "DOI not found" page
    rex = r'\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)\b'
    
    try:
        doi = re.findall(rex, text)
    except AttributeError: # might not need this; was thrown using re.search with no results
        return False
    else:
        return doi
    

def get_doi(file_path):
    pdf = convert_pdf_to_text(file_path) # convert PDF to text
    all_doi = find_all_doi(pdf) # extract DOIs
    unique = set(all_doi) # only keep unique DOIs

    if not unique: # empty set / no DOIs found
        return False
    else:
        return unique


def get_doi_from_dir(folder_path, recursive=False):

    results = {}

    if recursive:
        for subdir, dirs, files in os.walk(folder_path):

            for file in files:
                filename = os.fsdecode(file)
                file_path = os.path.join(subdir, filename)

                if filename.endswith('.pdf'): 
                    doi = get_doi(file_path)

                    if doi: # the set is not empty
                        if len(doi) == 1: 
                            pretty_doi = min(doi) # return the only item in the set
                            results[file_path] = pretty_doi
                            #print(f'{file_path}:  {pretty_doi}')
                        else: # more than one DOI identified
                            #print(f'Oops ... More than one DOI identified ({len(dois)} DOIs)')
                            continue
                    else: # no DOI was found; log this to a separate list for manual review
                        results[file_path] = ''
                        #print(f'{file_path}:  {doi}')

    else: # process the specified directory only
        for file in os.listdir(folder_path):
            
            filename = os.fsdecode(file)
            file_path = os.path.join(folder_path, filename)

            if filename.endswith('.pdf'):
                doi = get_doi(file_path)

                if doi: # the set is not empty
                    if len(doi) == 1: 
                        pretty_doi = min(doi) # return the only item in the set
                        results[file_path] = pretty_doi
                        #print(f'{file_path}:  {pretty_doi}')
                    else: # more than one DOI identified
                        #print(f'Oops ... More than one DOI identified ({len(dois)} DOIs)')
                        continue
                else: # no DOI was found; log this to a separate list for manual review
                    #print(f'{file_path}:  {doi}')
                    results[file_path] = ''
                    #continue                    
    
    return results


def get_doi_from_dir_console(folder_path, recursive=False):

    results = {}

    try:
        spinner = Spinner()

        if recursive:
            for subdir, dirs, files in os.walk(folder_path):

                for file in files:
                    filename = os.fsdecode(file)
                    file_path = os.path.join(subdir, filename)

                    if filename.endswith('.pdf'): 
                        spinner.start()
                        doi = get_doi(file_path)
                        spinner.stop()

                        if doi: # the set is not empty
                            if len(doi) == 1: 
                                pretty_doi = min(doi) # return the only item in the set
                                results[file_path] = pretty_doi
                                print(f'{file_path}:  {pretty_doi}')
                            else: # more than one DOI identified
                                print(f'Oops ... More than one DOI identified ({len(dois)} DOIs)')
                        else: # no DOI was found; log this to a separate list for manual review
                            print(f'{file_path}:  {doi}')

        else: # process the specified directory only
            for file in os.listdir(folder_path):
                
                filename = os.fsdecode(file)
                file_path = os.path.join(folder_path, filename)

                if filename.endswith('.pdf'):
                    spinner.start()
                    doi = get_doi(file_path)
                    spinner.stop()

                    if doi: # the set is not empty
                        if len(doi) == 1: 
                            pretty_doi = min(doi) # return the only item in the set
                            results[file_path] = pretty_doi
                            print(f'{file_path}:  {pretty_doi}')
                        else: # more than one DOI identified
                            print(f'Oops ... More than one DOI identified ({len(dois)} DOIs)')
                    else: # no DOI was found; log this to a separate list for manual review
                        print(f'{file_path}:  {doi}')                    
        
        return results

    except KeyboardInterrupt:
        spinner.stop()        
        log.error('Script terminated')


if __name__ == '__main__':


    cur_dir = os.getcwd()
    work_dir = cur_dir + '\samples'
    
    results = get_doi_from_dir(work_dir)

    print(results)

