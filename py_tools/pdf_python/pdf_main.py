import PyPDF2
import pdfplumber
from termcolor import cprint
from tqdm import tqdm

try:
    from pdf_average import *
    from pdf_significant import *
except:
    from .pdf_average import *
    from .pdf_significant import *


def split_pdf(input_file, output_prefix, num_sections):
    average = average_length(input_file)
    
    with pdfplumber.open(input_file) as pdf_file:
        total_pages = len(pdf_file.pages)
        writer = PyPDF2.PdfWriter()
        skipped_pages = 0

        for i in tqdm(range(total_pages)):
            page = pdf_file.pages[i]
            if lot_of_text(page, average):
                writer.add_page(PyPDF2.PdfReader(input_file).pages[i])
            else:
                skipped_pages += 1

        total_valid_pages = total_pages - skipped_pages
        pages_per_split = total_valid_pages // num_sections
        remainder = total_valid_pages % num_sections

        start = 0
        current_section = 1
        for section in range(num_sections):
            output_writer = PyPDF2.PdfWriter()
            
            end = start + pages_per_split + (1 if section < remainder else 0)

            for page_num in range(start, end):
                if page_num < len(writer.pages):
                    output_writer.add_page(writer.pages[page_num])

            if len(output_writer.pages) > 0:
                output_filename = f'{output_prefix}_part_{current_section}.pdf'
                with open(output_filename, 'wb') as output_pdf:
                    output_writer.write(output_pdf)

            start = end
            current_section += 1
            
def main() -> None:
    split_pdf('py_tools/pdf_python/GEOMETRY.pdf', 'output_file', 51)

if __name__ == '__main__':
    main()
