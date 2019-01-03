import PyPDF2
import re

import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)s : %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('pdf_metadata')
log.setLevel(logging.DEBUG)

'''
    getDocumentInfo() : retrieves the file's document information dictionary, if it exists. 
                        will not access metadata streams, if the file uses that instead
    DocumentInformation class: 'raw' versions return ByteStringObjects
        author, author_raw, creator, creator_raw, producer, producer_raw,
        subject, subject_raw, title, title_raw

    The XmpInformation class is much more extensive, see:
    https://pythonhosted.org/PyPDF2/XmpInformation.html#PyPDF2.xmp.XmpInformation

'''


def pdf_info(pdf_path):
    pdf_file = open(pdf_path, 'rb')
    pdf = PyPDF2.PdfFileReader(pdf_file)
    # condensed version:
    # pdf = PyPDF2.PdfFileReader(open(pdf_path, 'rb'))

    page_count = pdf.getNumPages()
    page_mode = pdf.getPageMode()
    first_page = pdf.getPage(0)
    first_page_content = first_page.extractText()
    last_page = pdf.getPage(page_count-1)
    last_page_content = last_page.extractText()
    title = pdf.getDocumentInfo().title
    
    log.info(f'Page count: {page_count}')
    log.info(f'Page mode: {page_mode}')
    log.info(f'Title: {title}')
    log.info(f'First page content: \n{first_page_content}')
    print('')
    log.info(f'Last page content:  \n{last_page_content}')

    # metadata extraction
    m_title = pdf.getXmpMetadata().dc_title
    m_lang = pdf.getXmpMetadata().dc_language
    m_rights = pdf.getXmpMetadata().dc_rights
    m_subject = pdf.getXmpMetadata().dc_subject
    m_keywords = pdf.getXmpMetadata().pdf_keywords

    log.info(f'M title: {m_title}')
    log.info(f'M language: {m_lang}')
    log.info(f'M rights: {m_rights}')
    log.info(f'M subject: {m_subject}')
    log.info(f'M keywords: {m_keywords}')

if __name__ == '__main__':

    print('You should probably do something here.')
    pdf_info('samples/PIR_2010.pdf')