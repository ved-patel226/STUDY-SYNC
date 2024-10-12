import pdfplumber

def average_length(input_file):
    total_text_length = 0
    total_pages = 0
    
    with pdfplumber.open(input_file) as pdf:
        total_pages = len(pdf.pages)
        
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                total_text_length += len(text.strip())
    
    average_length = total_text_length / total_pages if total_pages > 0 else 0
    return average_length

def main() -> None:
    avg_text_length = average_length('py_tools/pdf_python/GEOMETRY.pdf')
    print(type(avg_text_length))
    print(f'The average text length per page in the PDF is: {avg_text_length:.2f} characters')

if __name__ == '__main__':
    main()
    
