import re

import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)s : %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('pdf_miner')
log.setLevel(logging.DEBUG)

#from pdfminer.pdfparser import PDFParser
#from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
#from pdfminer.pdfpage import PDFTextExtractionNotAllowed
#from pdfminer.pdfdevice import PDFDevice

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO




def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text



def find_doi(text):
    # regex pattern for DOI: \b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)\b
    #  see: https://stackoverflow.com/questions/27910/finding-a-doi-in-a-document-or-page
    rex = r'\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)\b'
    
    try:
        doi = re.findall(rex, text)
    except AttributeError: # might not need this; was thrown using re.search with no results
        return False
    else:
        return doi


def get_dois(pdf_path): 
    pdf = PyPDF2.PdfFileReader(open(pdf_path, 'rb')) # open the pdf
    
    # Extract all the text
    all_text = ''
    for i in range(0, pdf.getNumPages()):
        all_text += pdf.getPage(i).extractText()
    all_doi = find_doi(all_text)

    unique_doi = set(all_doi) # remove duplicates by converting to a set
    
    if not unique_doi: # empty set / no DOIs were found
        return False
    else: 
        return unique_doi

if __name__ == '__main__':
    #print('Something')
    PIR_2010 = convert_pdf_to_txt('samples/PIR_2010.pdf')
    #print(PIR_2010)
    all_doi = find_doi(PIR_2010)
    print(f'all_doi: {all_doi}')
    unique_doi = set(all_doi)
    print(f'unique doi: {unique_doi}')
    
