import tkinter as tk

# Create the main application window
root = tk.Tk()

# Set the window title
root.title("Label Test")

# Create a label with explicit text, background, and text color
label = tk.Label(root, text="This text appears immediately after opening!", bg="white", fg="black", font=("Helvetica", 16), height=5, width=200)

# Add the label to the window
label.pack(pady=20)

# Start the Tkinter event loop (this keeps the window open)
root.mainloop()