import os
import glob
import PyPDF2
import re
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

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
        result = {}
        if self.pdf_file:
            pdf_text = self._extract_text_from_pdf(self.pdf_file)
            order_number = self.find_order_number(pdf_text)
            tracking_numbers = self.find_tracking_numbers(pdf_text)

            result[order_number] = tracking_numbers
            return result
        else:
            raise ValueError("No PDF file provided for extraction.")

    # Method to process all PDFs in the folder
    def extract_tracking_from_folder(self):
        result = {}
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

class FedexTrackingExtractorTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Fedex Tracking Number Extractor")
        self.result = {}

        # Initialize path variable
        self.path = ''  # Initialize self.path as an empty string

        #Create a button to choose a file or folder
        self.choose_path_button = tk.Button(self.root, text = "Choose File or Folder", command=self.choose_path)
        self.choose_path_button.pack(pady=20)

        #Create a label to display chosen path
        self.path_label = tk.Label(self.root, text="No path selected", wraplength=300)
        self.path_label.pack(pady=10)

        # Create a button to extract tracking numbers
        self.extract_button = tk.Button(self.root, text="Extract Tracking Numbers", command=self.extract_data)
        self.extract_button.pack(pady=20)

        # Create a text widget to display the results
        self.result_text = tk.Text(self.root, height=10, width=60)
        self.result_text.pack(pady=20)

    def choose_file(self):
        """Allow the user to choose a file."""
        self.path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if self.path:
            self.path_label.config(text=f"Selected File: {self.path}")
        else:
            self.path_label.config(text="No valid file selected.")

    def choose_folder(self):
        """Allow the user to choose a folder."""
        self.path = filedialog.askdirectory()
        if self.path:
            self.path_label.config(text=f"Selected Folder: {self.path}")
        else:
            self.path_label.config(text="No valid folder selected.")

    def extract_data(self):
        """Extract tracking numbers from the selected file or folder."""
        if not os.path.exists(self.path):
            messagebox.showerror("Error", "Invalid path selected.")
            return
        extractor = FedexTrackingNumberExtractor(self.path)

        if extractor.pdf_file:
            self.result = extractor.extract_tracking_from_file()
        elif extractor.folder_path:
            self.result = extractor.extract_tracking_from_folder()

        # Display the results in the text widget
        self.display_results()

    def display_results(self):
        """Display the extracted tracking numbers in the result text widget."""
        self.result_text.delete(1.0, tk.END)  # Clear previous results
        if not self.result:
            self.result_text.insert(tk.END, "No tracking numbers found.")
        else:
            df = pd.DataFrame.from_dict(self.result, orient='index', columns=['Tracking Numbers']).explode(
                'Tracking Numbers')
            df = df.reset_index().rename(columns={'index': 'Order Number'})
            self.result_text.insert(tk.END, df.to_string(index=False))

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    app = FedexTrackingExtractorTool(root)
    root.mainloop()

    #Print the Raw Dict
    #print(f"Extracted Order and Tracking Numbers: {result}")