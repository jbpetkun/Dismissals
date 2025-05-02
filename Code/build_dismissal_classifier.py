import pandas as pd
import tkinter as tk
from tkinter import filedialog

#csv_file_input = filedialog.askopenfilename(title="Select CSV file")
csv_file_input = '/Users/jbp56/Dropbox/Research/Dismissals/Training_Data/entries_with_DISMISS_short.csv'
# Insert "handcoded" at the end of the filename
csv_file_output = csv_file_input.replace('.csv', '_handcoded.csv')

# Read the CSV file
data = pd.read_csv(csv_file_input)

# Create a GUI application
root = tk.Tk()

global row_index  # Add this line to access the global variable

# Function to handle the classification
def classify(row_index, classification, voluntary, with_prejudice):
    # Save the classification in the 'entryclass' column
    data.at[row_index, 'entryclass'] = classification
    
    if classification == 1:
        # Ask for voluntary or involuntary dismissal
        voluntary_input = int(input("Is the dismissal voluntary (1), involuntary (2), or unknown (0)? "))
        data.at[row_index, 'voluntary'] = voluntary_input
        
        # Ask for with or without prejudice
        with_prejudice_input = int(input("Is the dismissal with prejudice (1), without prejudice (2), or unknown (0)? "))
        data.at[row_index, 'withprej'] = with_prejudice_input
    
    # Increment the row_index
    row_index += 1

    # Move to the next row
    next_row(row_index)

# Function to move to the next row
def next_row(row_index):
    print("Row index: " + str(row_index))

    # Check if there are more rows to classify
    if row_index < len(data):
        # Show the value of 'entrytext' to the user
        entrytext = data.at[row_index, 'entrytext']
        print(f"Entry Text: {entrytext}")
        
        # Ask the user for the classification
        classification = int(input("Classify the row as an order of dismissal (1), a motion to dismiss (2), or neither (0): "))
        
        # Define the variables voluntary and with_prejudice
        voluntary = 0
        with_prejudice = 0
        
        # Call the classify function
        classify(row_index, classification, voluntary, with_prejudice)
        
        
    else:
        # Save the updated data to a new CSV file
        data.to_csv(csv_file_output, index=False)
        print("Classification complete. Updated data saved to file.")

# Start the classification process
next_row(0)

# Start the GUI event loop
root.mainloop()
