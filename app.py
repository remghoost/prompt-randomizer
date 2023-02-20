# if you are reading this. hi, and welcome to my garbage-fest of code.
# 90% of this was made with ChatGPT. though i'll give myself some credit for coaxing it into the right solutions. 80-20.

import csv
import pyperclip
import random
import re
import string

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk


class App:

######################
### USER INTERFACE ###
######################

    def __init__(self, master):
        self.master = master
        master.title("Random Phrase Generator")
        master.geometry("400x600")
        master.configure(bg="#2b2b2b")

        # Create frame for top buttons
        self.top_button_frame = tk.Frame(master, bg="#2b2b2b")
        self.top_button_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        # Create button to import phrases from CSV
        self.import_button = tk.Button(
            self.top_button_frame, text="Import Phrases from CSV", command=self.import_phrases_from_csv, bg="#555555", fg="white", relief="flat"
        )
        self.import_button.pack(side="right", pady=(10, 0), padx=10)

#        # create button to save the current list
#        self.save_button = tk.Button(
#            self.top_button_frame, text="Save list", command=self.save_phrases, bg="#555555", fg="white", relief="flat"
#        )
#        self.save_button.pack(side="left", pady=(10, 0), padx=10)

    ####

        # Create button to add phrases
        self.add_button = tk.Button(
            master, text="Add Phrases", command=self.add_phrases, bg="#555555", fg="white", relief="flat"
        )
        self.add_button.pack(side="top", pady=(0, 0))

        # Create input box for adding phrases
        self.add_phrase_label = tk.Label(
            master, text="Add phrases (separated by commas):", bg="#2b2b2b", fg="white"
        )
        self.add_phrase_label.pack(pady=(0, 0))
        self.add_phrase = tk.Entry(master, width=50)
        self.add_phrase.pack(pady=(0, 0))

    ####

        # Create a frame to hold the buttons
        button_frame = tk.Frame(master, bg="#2b2b2b")
        button_frame.pack(pady=10)

        # Create button to sort phrases
        self.sort_button = tk.Button(
            button_frame, text="Sort by comma", command=self.sort_table, bg="#555555", fg="white", relief="flat"
        )
        self.sort_button.pack(side=tk.LEFT, padx=5)

        # Create button to sort and reformat to put multiword lines into just one word 
        self.sort_reformat_button = tk.Button(
            button_frame, text="Sort by word", command=self.sort_table_reformat, bg="#555555", fg="white", relief="flat"
        )
        self.sort_reformat_button.pack(side=tk.LEFT, padx=5)

    ####

        # Create a frame to contain the table and scrollbar
        self.table_frame = tk.Frame(master, bg="#2b2b2b")
        self.table_frame.pack(fill="both", expand=True)

        # Create table to display phrases
        self.table = ttk.Treeview(self.table_frame, columns=("Phrase",), show="headings", height=4)
        self.table.heading("Phrase", text="Phrase")
        self.table.pack(side="left", fill="both", expand=True)

        # Create scrollbar for table
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.table.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=self.scrollbar.set)

        # Create a context menu
        self.context_menu = tk.Menu(self.table, tearoff=0)
        self.context_menu.add_command(label="Delete", command=self.delete_selected_entries)

        # Bind the right-click event to the table
        self.table.bind("<Button-3>", self.show_context_menu)

    ####

        # Create label and input box for number of phrases to generate
        self.num_phrases_label = tk.Label(
            master, text="Number of phrases to generate:", bg="#2b2b2b", fg="white"
        )
        self.num_phrases_label.pack()
        self.num_phrases_frame = tk.Frame(master, bg="#2b2b2b")
        self.num_phrases_frame.pack(pady=(5, 0))
        self.num_phrases = tk.Entry(self.num_phrases_frame, width=5)
        self.num_phrases.pack(side="left")
        self.generate_button = tk.Button(
            self.num_phrases_frame,
            text="Generate Phrases",
            command=self.generate_phrase,
            bg="#555555",
            fg="white",
            relief="flat",
        )
        self.generate_button.pack(side="left", padx=(10, 0))

    ####

        # create another frame for these buttons
        button_frame_second = tk.Frame(master, bg="#2b2b2b")
        button_frame_second.pack(pady=(5, 0))
        
        # Create button to copy generated phrases to clipboard
        self.copy_button = tk.Button(
            button_frame_second, text="Copy", command=lambda: pyperclip.copy(self.output_text.get("1.0", "end")), bg="#555555", fg="white", relief="flat"
        )
        self.copy_button.pack(side=tk.LEFT, padx=5)

        # Create button to randomize the output text box
        self.randomize_button = tk.Button(
            button_frame_second, text="Randomize output order", command=self.randomize_word_order, bg= "#555555", fg="white", relief="flat"
        )
        self.randomize_button.pack(side=tk.LEFT, padx=5)

    ####

        # create frame for output textbox and scroll bar
        output_frame = tk.Frame(master, bg="#2b2b2b")
        output_frame.pack(pady=0, fill="both", expand=True)

        # Create label and text box for generated phrases
        self.output_label = tk.Label(output_frame, text="Generated Phrases:", bg="#2b2b2b", fg="white")
        self.output_label.pack(pady=(0, 0))

        self.output_text = tk.Text(output_frame, width=20, height=5)
        self.output_text.pack(side="left", padx=10, pady=(0, 10), fill="both", expand=True)

        # Create scrollbar for textbox
        self.scrollbar2 = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        self.scrollbar2.pack(side="left", fill="y")
        self.output_text.configure(yscrollcommand=self.scrollbar2.set)

    ####

        # Load phrases from file
        self.phrases = []
        self.load_phrases()

        # Set up a dark theme for the Treeview widget
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#2b2b2b",
            fieldbackground="#2b2b2b",
            foreground="white",
            rowheight=20,
        )
        style.map("Treeview", background=[("selected", "#555555")])
        

###############
### METHODS ###
###############

# initial load from the phrases.txt
    def load_phrases(self):
        try:
            with open("phrases.txt", "r") as f:
                self.phrases = [line.strip() for line in f.readlines()]
                self.update_table()
        except FileNotFoundError:
            pass

# main method for saving to the phrases.txt file 
## (THIS IS BORKED SOMEHOW. IT WORKS ON THE IMPORT CSV METHOD BUT NOT ANYWHERE ELSE IDK MAN) ##
    def save_phrases(self):
        self.update_table()
        with open("phrases.txt", "w") as f:
            for item in self.table.get_children():
                phrase = self.table.item(item)["values"][0]
                f.write(phrase + "\n")


# refreshes the table
    def update_table(self):
        # Clear old data from table
        for row in self.table.get_children():
            self.table.delete(row)

        # Add phrases to table
        for phrase in self.phrases:
            self.table.insert("", "end", values=(phrase,))

# sort by comma method
    def sort_table(self):
        # Preprocess the phrases in the table
        new_phrases = []
        for phrase in self.phrases:
            # Replace underscores, adjust parentheses, and remove innermost parentheses
            words = phrase.split()
            new_line = []
            for word in words:
                # Replace underscores using regular expressions
                word = re.sub(r"_", " ", word)

                num_parens = word.count('(')
                if num_parens == 0 or word.count(')') == 0:
                    new_line.append(word)
                else:
                    # Remove innermost pairs of parentheses
                    word = self.remove_inner_parentheses(word)

                    # Remove parentheses from the beginning and end of the word
                    word = re.sub(r"^(\(+)(.+?)(\)+)$", r"\1\2\3", word)
                    
                    new_word = '(' * num_parens + word + ')' * num_parens
                    new_line.append(new_word)
            new_phrases.append(' '.join(new_line))
        
        # Sort the preprocessed phrases and update the table
        new_phrases = list(set(new_phrases))
        new_phrases.sort()
        self.phrases = new_phrases
        self.update_table()
        self.update_table()
        self.save_phrases()
        
# sort by word method
# breaking the table into individual words and removing parentheses. 
# would like to keep them, but had issues with trailing/leading parentheses
    def sort_table_reformat(self):
        # Get the phrases from the table and split them into words
        table_phrases = [self.table.item(item)["values"][0] for item in self.table.get_children()]
        table_words = [re.findall(r'\w+|\S', phrase) for phrase in table_phrases]

        # Remove all parentheses and punctuation from the words
        table_words_no_parens = []
        for words in table_words:
            words_no_parens = []
            for word in words:
                if word.startswith('(') and word.endswith(')'):
                    word_no_parens = word[1:-1]
                else:
                    word_no_parens = word.replace('(', '').replace(')', '')
                word_no_punc = ''.join(char for char in word_no_parens if char not in string.punctuation)
                if word_no_punc:
                    words_no_parens.append(word_no_punc)
            table_words_no_parens.append(words_no_parens)

        # Split each word onto a separate line
        table_lines = []
        for words in table_words_no_parens:
            for word in words:
                table_lines.append([word])

        # Remove duplicates and sort the lines
        unique_table_lines = sorted(set(tuple(lines) for lines in table_lines))

        # Join the lines back together into phrases and insert them into the table
        self.table.delete(*self.table.get_children())
        for phrase_lines in unique_table_lines:
            phrase_str = " ".join(phrase_lines)
            self.table.insert("", "end", values=(phrase_str,))
        
# fixing problems with my own imported CSV file. back when i was trying to do nested parentheses.
    def remove_inner_parentheses(self, word):
        while True:
            match = re.search(r"\(([^()]*)\)", word)
            if not match:
                break
            word = word.replace(match.group(), match.group(1))
        return word
    
# the actual phrase generation script. uses the self.table to randomly get words.
    def generate_phrase(self):
        num_words = int(self.num_phrases.get())
        children = self.table.get_children()  # get a list of all rows in the table
        generated_words = []
        for i in range(num_words):
            row_id = random.choice(children)  # select a random row id from the list
            row = self.table.item(row_id)  # get the row data using the row id
            word = row['values'][0]  # get the word from the first column
            generated_words.append(word)
        phrase_str = ", ".join(generated_words)
        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", phrase_str)
    
# randomizes output textbox contents. just for getting more variations.
    def randomize_word_order(self):
        text = self.text_output.get("1.0", "end-1c")
        words = text.split(", ")
        random.shuffle(words)
        shuffled_text = ", ".join(words)
        self.text_output.delete("1.0", "end")
        self.text_output.insert("1.0", shuffled_text)

# can't remember. lol. important though. probably....
    def add_phrases(self):
        new_phrases = [p.strip() for p in self.add_phrase.get().split(",")]
        for phrase in new_phrases:
            if phrase not in self.phrases:
                self.phrases.append(phrase)
        self.update_table()
        self.save_phrases()

# import phrases from csv. duh.
    def import_phrases_from_csv(self):
        # Open file dialog to select CSV file
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])

        # Return if no file is selected
        if not file_path:
            return
            
        # Open and read CSV file
        with open(file_path, "r") as file:
            csv_reader = csv.reader(file)
            phrases = []
            for row in csv_reader:
                # Skip empty rows
                if not row:
                    continue
                # Extract phrases from column 1
                row_phrases = row[1].split(",")
                for phrase in row_phrases:
                    phrases.append(phrase.strip(' "'))

            # Add new phrases to list and update table
            self.phrases += phrases
            self.update_table()
            self.save_phrases()
            self.sort_table()
    
# used for randomizing the output text to get new variations
    def randomize_word_order(self):
        text = self.output_text.get("1.0", "end-1c")
        words = text.split(", ")
        random.shuffle(words)
        shuffled_text = ", ".join(words)
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", shuffled_text)

# Method to show the context menu at the mouse position
    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

# Method to delete the selected entries
    def delete_selected_entries(self):
        print("ummm, mic check")
        selected_items = self.table.selection() # Get the selected items
        if len(selected_items) > 0:
            for item in selected_items:
                self.table.delete(item) # Delete each selected item
            #self.save_phrases() # Save the changes to the file


# Create and run the GUI
root = tk.Tk()
app = App(root)
root.mainloop()

