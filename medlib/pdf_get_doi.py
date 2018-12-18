import PyPDF2
import re

import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)s : %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('pdf_get_doi')
log.setLevel(logging.DEBUG)


def find_doi(text):
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
    

def extract_all_doi(pdf_path): 
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

    aap2015 = extract_all_doi('samples/AAP_2015.pdf')
    nejm2015 = extract_all_doi('samples/NEJM_2015.pdf')
    neo2016 = extract_all_doi('samples/NEO_2016.pdf')
    ped2013 = extract_all_doi('samples/PED_2013.pdf')
    pedemp2013 = extract_all_doi('samples/PedEMP_2013.pdf')
    pir2010 = extract_all_doi('samples/PIR_2010.pdf')
    pir2016 = extract_all_doi('samples/PIR_2016.pdf')
    ppt = extract_all_doi('samples/PPT.pdf')
    utd2018 = extract_all_doi('samples/UTDPrintout_2018.pdf')

    print(f'AAP_2015: {aap2015}')
    print(f'NEJM_2015: {nejm2015}')
    print(f'NEO_2016: {neo2016}')
    print(f'PED_2013: {ped2013}')
    print(f'PedEMP_2013: {pedemp2013}')
    print(f'PIR_2010: {pir2010}')
    print(f'PIR_2016: {pir2016}')
    print(f'PPT: {ppt}')
    print(f'UTDPrintout_2018: {utd2018}')
    