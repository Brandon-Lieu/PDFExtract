import os
import glob
import PyPDF2
import re
import pandas as pd

class FedexTrackingNumberExtractor:
    def __init__(self, path):
        # Check if the input is a file or a folder
        if os.path.isfile(path):
            self.pdf_file = path
            self.folder_path = None
        elif os.path.isdir(path):
            self.folder_path = path
            self.pdf_file = None
        else:
            raise ValueError(f"The path '{path}' is neither a file nor a directory.")

    # Private method to extract text from a PDF file
    def _extract_text_from_pdf(self, pdf_file):
        try:
            with open(pdf_file, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ''.join([page.extract_text() for page in reader.pages])
            return text
        except FileNotFoundError:
            print(f"File {pdf_file} not found.")
            return ""

    # Method to find tracking numbers from the extracted text
    def find_tracking_numbers(self, text):
        tracking_numbers = re.search(r'Tracking ID:\s*(\d{12})', text)
        return tracking_numbers.group(1)

    # Method to find order numbers from the extracted text
    def find_order_number(self, text):
        order_number = re.search(r'Order ID:\s*(SA\d{9})', text)
        return order_number.group(1)

    # Method to process a single PDF file
    def extract_tracking_from_file(self):
        if self.pdf_file:
            pdf_text = self._extract_text_from_pdf(self.pdf_file)
            order_number = self.find_order_number(pdf_text)
            tracking_numbers = self.find_tracking_numbers(pdf_text)

            return {order_number: tracking_numbers}
        else:
            raise ValueError("No PDF file provided for extraction.")

    # Method to process all PDFs in the folder
    def extract_tracking_from_folder(self):
        if self.folder_path:
            pdf_files = glob.glob(os.path.join(self.folder_path, "*.pdf"))

            if not pdf_files:
                print(f"No PDF files found in the folder: {self.folder_path}")
                return

            for pdf_file in pdf_files:
                #print(f"Processing file: {pdf_file}")
                pdf_text = self._extract_text_from_pdf(pdf_file)
                order_number = self.find_order_number(pdf_text)
                tracking_numbers = self.find_tracking_numbers(pdf_text)

                result[order_number] = tracking_numbers

        else:
            raise ValueError("No folder path provided for extraction.")

        return result

# Example usage
if __name__ == "__main__":
    result = {} #Create an empty dict
    #path = "Trade-In Instructions - SA357783085.pdf"
    path = "/Users/csuftitan/Library/CloudStorage/OneDrive-CalStateFullerton/Github/ReadPDF/pythonProject/Trade-In Files"
    if os.path.exists(path):
        print(f"The directory exists: {path}")
    else:
        raise ValueError(f"The directory does not exist: {path}")

    # If everything is good
    extractor = FedexTrackingNumberExtractor(path)

    if extractor.pdf_file:
        result = extractor.extract_tracking_from_file()
    elif extractor.folder_path:
        result = extractor.extract_tracking_from_folder()

    # Create a DataFrame and explode lists into individual rows
    df = pd.DataFrame.from_dict(result, orient='index', columns=['Tracking Numbers']).explode('Tracking Numbers')

    # Reset the index to turn the 'index' into a column and rename it to 'Order Number'
    df = df.reset_index().rename(columns={'index': 'Order Number'})

    # Print the DataFrame
    print(df)

    #Print the Raw Dict
    #print(f"Extracted Order and Tracking Numbers: {result}")