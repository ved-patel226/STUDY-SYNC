import os

class PDFSaver:
    def __init__(self, name: str, pdf_path:str ="PDFS") -> None:
        self.pdf_path = pdf_path
        self.name = name
        
        full_path = os.path.join(self.pdf_path, self.name)
        os.makedirs(full_path, exist_ok=True)

    def load_pdf(self, pdf_path: str) -> None:
        self.pdf_path = pdf_path
        
def main() -> None:
    pdf = PDFSaver('ved-patel226')

if __name__ == '__main__':
    main()