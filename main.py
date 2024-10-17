import os
import glob
import PyPDF2
import re


class FedexTrackingNumberExtractor:
    def __init__(self, pdf_file):
        self.pdf_file = pdf_file
        self.text = self._extract_text_from_pdf()

    # Private method to extract text from PDF
    def _extract_text_from_pdf(self):
        text = ''
        try:
            with open(self.pdf_file, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text()
        except FileNotFoundError:
            print(f"File {self.pdf_file} not found.")
        return text

    # Method to find tracking numbers
    def find_tracking_numbers(self):
        # Modify the regex if needed, based on the tracking number pattern
        tracking_numbers = re.findall(r'Tracking ID:\s*(\d{12})', self.text)
        return tracking_numbers
    # Method to find order numbers
    def find_order_numbers(self):
        order_numbers = re.findall(r'Order ID:\s*(\w{11})', self.text)
        return order_numbers

# Example usage
if __name__ == "__main__":
    # Prompt the user to input the PDF file path
    pdf_file = "Trade-In Instructions - SA357783085.pdf"

    extractor = FedexTrackingNumberExtractor(pdf_file)

    tracking_numbers = extractor.find_tracking_numbers()
    order_numbers = extractor.find_order_numbers()

    if tracking_numbers:
        print("Extracted Tracking Numbers:", tracking_numbers)
    else:
        print("No tracking numbers found.")

    if order_numbers:
        print("Extracted Order Numbers:", order_numbers)
    else:
        print("No Order numbers found.")