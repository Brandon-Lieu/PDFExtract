import os
import glob
import PyPDF2
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class FedexTrackingNumberExtractor:
    def __init__(self, path):
        # Init the result
        self.result = {}
        # Check if the input is a file or a folder
        if os.path.isfile(path):
            self.pdf_file = path
            self.folder_path = None
        elif os.path.isdir(path):
            self.folder_path = path
            self.pdf_file = None
        else:
            print(f"Invalid path: '{path}' is neither a file nor a directory.")
            #messagebox.showerror(f"Invalid Path: {path}")
            self.pdf_file = None
            self.folder_path = None

    # Private method to extract text from a PDF file
    def _extract_text_from_pdf(self, pdf_file):
        with open(pdf_file, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''.join([page.extract_text() for page in reader.pages])
        return text

    # Method to find tracking numbers from the extracted text (supports multiple tracking numbers)
    def find_tracking_numbers(self, text):
        tracking_numbers = re.search(r'Tracking ID:\s*(\d{12})', text)  # Use findall to capture multiple tracking numbers
        if not tracking_numbers:
            # Think a way to implement this
            raise ValueError("No tracking number found.")
        return tracking_numbers.group(1)

    # Method to find order numbers from the extracted text
    def find_order_number(self, text):
        order_number = re.search(r'Order ID:\s*(SA\d{9})', text)
        if not order_number:
            # Think a way to implement this
            raise ValueError("No order number found.")
        return order_number.group(1)

    def find_due_date(self,text):
        due_date = re.search(r'Be sure to ship your package by\s*(\S.*)', text)
        if not due_date:
            raise ValueError("No due date found.")
        return due_date.group(1)

    def find_trade_in_devices(self,text):
        trade_in_devices = re.search(r'about your\s*(.*?)\s*trade-in', text)
        if not trade_in_devices:
            raise ValueError("No trade in devices found.")
        return trade_in_devices.group(1)

    # Method to process a single PDF file
    def extract_tracking_from_file(self):

        pdf_text = self._extract_text_from_pdf(self.pdf_file)

        order_number = self.find_order_number(pdf_text)
        tracking_numbers = self.find_tracking_numbers(pdf_text)
        due_date = self.find_due_date(pdf_text)
        trade_in_devices = self.find_trade_in_devices(pdf_text)

        self.result[order_number] = [[tracking_numbers, due_date, trade_in_devices]]

        return self.result

    # Method to process all PDFs in the folder
    def extract_tracking_from_folder(self):
        pdf_files = glob.glob(os.path.join(self.folder_path, "*.pdf"))

        if not pdf_files:
            print(f"No PDF files found in the folder: {self.folder_path}")
            return self.result

        for pdf_file in pdf_files:
            pdf_text = self._extract_text_from_pdf(pdf_file)

            order_number = self.find_order_number(pdf_text)
            tracking_numbers = self.find_tracking_numbers(pdf_text)

            due_date = self.find_due_date(pdf_text)
            trade_in_devices = self.find_trade_in_devices(pdf_text)

            if order_number in self.result:
                # Append the new tracking numbers and other details if order number already exists
                self.result[order_number].append([tracking_numbers, due_date, trade_in_devices])
            else:
                # Create a new entry with a list of list
                self.result[order_number] = [[tracking_numbers, due_date, trade_in_devices]]

        return self.result

class FedexTrackingExtractorTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Fedex Tracking Number Extractor")
        # Initialize result variable
        self.result = {}
        # Initialize path variable
        self.path = ''  # Initialize self.path as an empty string

        # Create a button to choose a file (using ttk)
        self.choose_file_button = ttk.Button(self.root, text="Choose File",command=self.choose_file)
        # Create a button to choose a folder (using ttk)
        self.choose_folder_button = ttk.Button(self.root, text="Choose Folder", command=self.choose_folder)
        # Create a label to display the chosen path
        self.path_label = ttk.Label(self.root, text="No path selected", wraplength=300)
        # Create a button to extract tracking numbers
        self.extract_button = ttk.Button(self.root, text="Extract Tracking Numbers", command=self.extract_data)
        # Create a text widget to display the results
        self.result_text = tk.Text(self.root, height=10, width=60)

        # Configure the grid to reduce the gap between columns
        self.root.grid_columnconfigure(0, weight=1)  # Left column (buttons)
        self.root.grid_columnconfigure(1, weight=1)  # Right column (path label and button)

        # Place widgets in the grid
        # Buttons on the left
        self.choose_file_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.choose_folder_button.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Path label on the right (row 0)
        self.path_label.grid(row=0, column=1, padx=10, pady=10, sticky="ne")

        # Extract button on the right, below the path label (row 1)
        self.extract_button.grid(row=1, column=1, padx=10, pady=10, sticky="ne")

        # Output text at the bottom, spanning both columns
        self.result_text.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def choose_file(self):
        """Allow the user to choose a file."""
        self.path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])  # Filter for PDF files
        if self.path:
            self.path_label.config(text=f"Selected File: {self.path}")
        else:
            self.path_label.config(text="No valid file selected.")

    def choose_folder(self):
        """Allow the user to choose a folder."""
        self.path = filedialog.askdirectory()  # This will allow folder selection
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

        if self.result is None:
            messagebox.showerror("Error")

    def display_results(self):
        """Display the extracted tracking numbers in the result text widget."""
        self.result_text.delete(1.0, tk.END)  # Clear previous results
        if not self.result:
            self.result_text.insert(tk.END, "No tracking numbers found.")
        else:
            formatted_result = self.format_output()
            # Display the formatted result in the Text widget
            self.result_text.insert(tk.END, formatted_result)

    # def save_results_to_file(self):
    #     """Save the extracted tracking numbers to a text file."""
    #     formatted_result = self.format_results()  # Get the formatted result string
    #     file_path = 'tracking_numbers.txt'
    #     with open(file_path, 'w') as file:
    #         file.write(formatted_result)  # Write the result to the file

    def format_output(self):
        """Format the extracted tracking numbers into a string."""
        result_str = "Order Number\tTracking Number\tDue Date\tTrade-In Devices\n"  # Header for the table
        result_str += "-" * 40 + "\n"  # Add a separator line

        if not self.result:
            result_str += "No tracking numbers found.\n"
        else:
            for order_number, tracking_numbers in self.result.items():
                # If there are multiple tracking numbers, display each on a new line
                for tracking_number in tracking_numbers:
                    result_str += f"{order_number:<15} {tracking_number}\n"  # Add order and tracking number
        return result_str

# Main application loop
if __name__ == "__main__":
    root = tk.Tk()
    app = FedexTrackingExtractorTool(root)
    root.mainloop()