import os
import sqlite3
import tkinter as tk
import sqlite3
from datetime import datetime
from tkinter import font
from tkinter import Scrollbar
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk
from tkinter import PhotoImage
from tkinter import Toplevel

# Database connection
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "inventory_database.db")
is_new_db = not os.path.exists(DB_PATH)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()


# Create table (including the "date" column)
c.execute('''CREATE TABLE IF NOT EXISTS table_data
             (ID TEXT PRIMARY KEY,
              date TEXT,      -- Add the 'date' column
              ami_pn TEXT,
              mfg_pn TEXT,
              stock_qty INTEGER,
              unit_price REAL,
              image_path TEXT)''')

def add_row():
    id_value = id_entry.get()
    date_value = date_entry.get()
    ami_pn = ami_pn_entry.get()
    mfg_pn = mfg_pn_entry.get()
    stock_qty = stock_qty_entry.get()
    unit_price = unit_price_entry.get()


    # Check if any field is empty
    if not (id_value and ami_pn and mfg_pn and stock_qty and unit_price and date_value):
        messagebox.showerror("Error", "All fields must be filled")
        return

    # Check if ID already exists
    c.execute("SELECT ID FROM table_data WHERE ID=?", (id_value,))
    existing_id = c.fetchone()
    if existing_id:
        messagebox.showerror("Error", "ID already exists")
        return

    # Check if ID contains alphanumeric characters
    if not id_value.isalnum():
        messagebox.showerror("Error", "ID must contain alphanumeric characters")
        return

    # Validate stock qty as a number
    if not stock_qty.isdigit():
        messagebox.showerror("Error", "Stock Qty must be a number")
        return

    #stock_qty = "{:,}".format(int(stock_qty))  # Format stock qty with thousands separator

    # Format date as mm-dd-yyyy
    try:
        datetime_obj = datetime.strptime(date_value, '%m-%d-%Y')
        formatted_date = datetime_obj.strftime('%m-%d-%Y')
    except ValueError:
        messagebox.showerror("Error", "Invalid date format. Please use mm-dd-yyyy.")
        return

    # Validate unit price as a number with two decimal places
    try:
        unit_price = float(unit_price)
    except ValueError:
        messagebox.showerror("Error", "Unit Price must be a number")
        return

    c.execute("INSERT INTO table_data (ID, date, ami_pn, mfg_pn, stock_qty, unit_price) VALUES (?, ?, ?, ?, ?, ?)",
              (id_value, formatted_date, ami_pn, mfg_pn, stock_qty, unit_price))
    conn.commit()
    update_table()


def remove_row():
    selected_row = table.focus()

    if not table.selection():
        messagebox.showerror("Error", "No row selected. Please select a row to perform this action.")
        return

    if not selected_row:
        messagebox.showerror("Error", "No row selected. Please select a row to remove.")
        return

    if selected_row:
        row_id = table.item(selected_row)['values'][0]

        # Show a confirmation dialog
        confirm = messagebox.askyesno("Confirm Removal", "Are you sure you want to remove this row?")

        if confirm:
            c.execute("DELETE FROM table_data WHERE ID=?", (row_id,))
            conn.commit()
            update_table()
            deselect_table()  # Clear the image label


def modify_row():
    selected_row = table.focus()

    if not table.selection():
        messagebox.showerror("Error", "No row selected. Please select a row to perform this action.")
        return

    if not selected_row:
        messagebox.showerror("Error", "No row selected. Please select a row to modify.")
        return

    # Disable table selection
    table.unbind("<ButtonRelease-1>")
    table.configure(selectmode="none")

    # Disable search bar and clear button
    search_entry.config(state="disabled")
    clear_search_button.config(state="disabled")

    # Disable Esc key and deselect during modify
    window.unbind("<Escape>")


    selected_row = table.focus()
    if selected_row:
        row_id = table.item(selected_row)['values'][0]
        c.execute("SELECT * FROM table_data WHERE ID=?", (row_id,))
        result = c.fetchone()
        if result:
            date = result[1]
            ami_pn = result[2]
            mfg_pn = result[3]
            stock_qty = result[4]
            unit_price = result[5]

            # Populate form fields
            id_entry.delete(0, tk.END)
            id_entry.insert(0, row_id)

            date_entry.delete(0, tk.END)
            date_entry.insert(0, date)

            ami_pn_entry.delete(0, tk.END)
            ami_pn_entry.insert(0, ami_pn)

            mfg_pn_entry.delete(0, tk.END)
            mfg_pn_entry.insert(0, mfg_pn)

            stock_qty_entry.delete(0, tk.END)
            stock_qty_entry.insert(0, stock_qty)

            unit_price_entry.delete(0, tk.END)
            unit_price_entry.insert(0, unit_price)

            # Disable Add and Remove buttons
            add_button.config(state="disabled")
            remove_button.config(state="disabled")
            modify_button.config(state="disabled")  # Disable the Modify button

            global save_changes_button, cancel_button, upload_image_button

            # Create "Upload Image" button with updated command
            upload_image_button = tk.Button(window, text="Upload Image", command=lambda: upload_image(row_id),
                                            font=("Helvetica", 15), width=12, height=2, bg="#2196F3", fg="white")
            upload_image_button.place(x=490, y=30)

            # Create "Save Changes" button
            save_changes_button = tk.Button(window, text="Save Changes", command=lambda: save_changes(row_id),
                                            font=("Helvetica", 15), width=12, height=2, bg="#FFA500", fg="white")
            save_changes_button.place(x=490, y=100)

            # Create "Cancel" button
            cancel_button = tk.Button(window, text="Cancel", command=cancel_modify, font=("Helvetica", 15), width=12,
                                      height=2, bg="#b51f1f", fg="white")
            cancel_button.place(x=490, y=170)





def save_changes(row_id):
    global save_changes_button, cancel_button, temp_image_path

    modified_id = id_entry.get()
    modified_date = date_entry.get()

    # Validate date format as mm-dd-yyyy
    try:
        datetime_obj = datetime.strptime(modified_date, '%m-%d-%Y')
        modified_date = datetime_obj.strftime('%m-%d-%Y')  # Optional: reformat to be clean
    except ValueError:
        messagebox.showerror("Error", "Invalid date format. Please use mm-dd-yyyy.")
        return

    modified_ami_pn = ami_pn_entry.get()
    modified_mfg_pn = mfg_pn_entry.get()
    modified_stock_qty = stock_qty_entry.get()
    modified_unit_price = unit_price_entry.get()

    if not (modified_id and modified_date and modified_ami_pn and modified_mfg_pn and modified_stock_qty and modified_unit_price):
        messagebox.showerror("Error", "All fields must be filled")
        return

    # Validate stock qty as a number
    if not modified_stock_qty.isdigit():
        messagebox.showerror("Error", "Stock Qty must be a number")
        return

    # Validate unit price as a number with two decimal places
    try:
        modified_unit_price = float(modified_unit_price)
    except ValueError:
        messagebox.showerror("Error", "Unit Price must be a number")
        return

    c.execute("UPDATE table_data SET ID=?, date=?, ami_pn=?, mfg_pn=?, stock_qty=?, unit_price=? WHERE ID=?",
              (modified_id, modified_date, modified_ami_pn, modified_mfg_pn, modified_stock_qty, modified_unit_price, row_id))
    conn.commit()

    # Update the table without clearing the selection
    updated_row = (modified_id, modified_date, modified_ami_pn, modified_mfg_pn, modified_stock_qty, modified_unit_price)
    selected_item = table.selection()[0]  # Get the currently selected item
    table.item(selected_item, values=updated_row)  # Update the values of the selected item

    if temp_image_path:  # If a temporary image path is set, assign and save the image
        c.execute("UPDATE table_data SET image_path=? WHERE ID=?", (temp_image_path, row_id))
        conn.commit()

    temp_image_path = None  # Clear the temporary image path

    clear_fields()

    save_changes_button.place_forget()
    cancel_button.place_forget()
    upload_image_button.place_forget()

    add_button.config(state=tk.NORMAL)
    remove_button.config(state=tk.NORMAL)

    # Re-enable search bar and clear and modify button
    search_entry.config(state="normal")
    clear_search_button.config(state="normal")
    modify_button.config(state="normal")

    # Re-enable Esc key and deselect
    window.bind("<Escape>", deselect_table)
    table.bind("<ButtonRelease-1>", lambda event: show_image())
    table.configure(selectmode="browse")
    show_image()  # Refresh the image display after save


def cancel_modify():
    global save_changes_button, cancel_button, upload_image_button, temp_image_path
    clear_fields()
    enable_buttons()

    if save_changes_button:
        save_changes_button.place_forget()
    if cancel_button:
        cancel_button.place_forget()
    if upload_image_button:
        upload_image_button.place_forget()

    # Re-enable search bar and clear button
    search_entry.config(state="normal")
    clear_search_button.config(state="normal")
    modify_button.config(state="normal")

    # Re-enable Esc key and deselect
    window.bind("<Escape>", deselect_table)
    table.bind("<ButtonRelease-1>", lambda event: show_image())
    table.configure(selectmode="browse")

    temp_image_path = None  # Clear the temporary image path


def enable_buttons():
    add_button.config(state="normal")
    remove_button.config(state="normal")

def show_image(event=None):
    selected_row = table.selection()
    if selected_row:
        row_id = table.item(selected_row)['values'][0]
        c.execute("SELECT * FROM table_data WHERE ID=?", (row_id,))
        result = c.fetchone()
        if result:
            id_entry.delete(0, tk.END)
            date_entry.delete(0, tk.END)
            ami_pn_entry.delete(0, tk.END)
            mfg_pn_entry.delete(0, tk.END)
            stock_qty_entry.delete(0, tk.END)
            unit_price_entry.delete(0, tk.END)

            id_entry.insert(0, result[0])
            date_entry.insert(0, result[1])
            ami_pn_entry.insert(0, result[2])
            mfg_pn_entry.insert(0, result[3])
            stock_qty_entry.insert(0, result[4])
            unit_price_entry.insert(0, result[5])

            image_path = result[6]
            if temp_image_path:
                image_path = temp_image_path  # Use the temporary image path if available

            if image_path:
                image = Image.open(image_path)
                image = image.resize((250, 250))
                photo = ImageTk.PhotoImage(image)
                image_label.configure(image=photo)
                image_label.image = photo
                image_label.pack()  # Ensure the image label is visible
            else:
                clear_image_label()  # Clear the image label when no image is assigned
        else:
            clear_image_label()  # Clear the image label when no row is found

# Create a global variable to store the temporary image path
temp_image_path = None

def upload_image(row_id):
    global temp_image_path
    temp_image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if temp_image_path:
        show_image()  # Display the image immediately after selecting

def view_image():
    selected_row = table.selection()
    if selected_row:
        row_id = table.item(selected_row)['values'][0]
        c.execute("SELECT * FROM table_data WHERE ID=?", (row_id,))
        result = c.fetchone()
        if result:
            image_path = result[6]
            if temp_image_path:
                image_path = temp_image_path  # Use the temporary image path if available

            if image_path:
                image = Image.open(image_path)
                image = image.resize((600, 600))  # Adjust the size of the displayed image
                photo = ImageTk.PhotoImage(image)

                # Create a modal window to display the image
                modal_window = Toplevel(window)
                modal_window.title("View Image")

                # Calculate the center position of the screen
                screen_width = modal_window.winfo_screenwidth()
                screen_height = modal_window.winfo_screenheight()
                x_coordinate = (screen_width - 600) // 2
                y_coordinate = (screen_height - 600) // 2
                modal_window.geometry(f"600x600+{x_coordinate}+{y_coordinate}")

                image_label_modal = ttk.Label(modal_window, image=photo)
                image_label_modal.image = photo
                image_label_modal.pack()

                # Disable window resizing (both width and height)
                modal_window.resizable(False, False)


# Function to select the previous row in the table
def select_previous_row():
    selected_item = table.selection()
    if selected_item:
        prev_item = table.prev(selected_item[0])
        if prev_item:
            table.selection_set(prev_item)
            show_image()

# Function to select the next row in the table
def select_next_row():
    selected_item = table.selection()
    if selected_item:
        next_item = table.next(selected_item[0])
        if next_item:
            table.selection_set(next_item)
            show_image()

def select_previous_row_key(event):
    select_previous_row()

def select_next_row_key(event):
    select_next_row()

def disable_arrow_keys(event):
    return "break"

def view_row_info():
    selected_row = table.focus()

    if not table.selection():
        messagebox.showerror("Error", "No row selected. Please select a row to view.")
        return

    if not selected_row:
        messagebox.showerror("Error", "No row selected. Please select a row to view.")
        return

    row_id = table.item(selected_row)['values'][0]
    c.execute("SELECT * FROM table_data WHERE ID=?", (row_id,))
    result = c.fetchone()

    if result:
        id_value = result[0]
        date = result[1]
        stock_qty = result[4]
        ami_pn = result[2]
        mfg_pn = result[3]
        unit_price = result[5]

        # Create a modal window to display the row information
        modal_window = Toplevel(window)
        modal_window.title("View Row Information")

        # Calculate the center position of the screen
        screen_width = modal_window.winfo_screenwidth()
        screen_height = modal_window.winfo_screenheight()
        x_coordinate = (screen_width - 400) // 2
        y_coordinate = (screen_height - 610) // 2
        modal_window.geometry(f"400x610+{x_coordinate}+{y_coordinate}")

        # Add labels and entry widgets to display information
        def create_labeled_entry(parent, label_text, entry_value, is_text=False):
            label = ttk.Label(parent, text=label_text, font=("Helvetica", 15))
            label.pack(padx=10, pady=5)

            if is_text:
                entry = tk.Text(parent, font=("Helvetica", 12), wrap="word", height=5, width=40, background="#f0f0f0")
                entry.insert("1.0", entry_value)
                entry.config(state="disabled")
            else:
                entry = ttk.Entry(parent, font=("Helvetica", 12))
                entry.insert(0, entry_value)
                entry.config(state="readonly")

            entry.pack(padx=10, pady=5)
            return entry

        id_entry = create_labeled_entry(modal_window, "ID:", id_value)
        date_entry = create_labeled_entry(modal_window, "Date", date)
        stock_qty_entry = create_labeled_entry(modal_window, "Stock Qty:", stock_qty)
        ami_pn_entry = create_labeled_entry(modal_window, "Ami P/N:", ami_pn, is_text=True)
        mfg_pn_entry = create_labeled_entry(modal_window, "Mfg P/N:", mfg_pn, is_text=True)
        unit_price_entry = create_labeled_entry(modal_window, "Unit Price:", unit_price)

        # Set the border style for Ami P/N and Mfg P/N
        for entry in [ami_pn_entry, mfg_pn_entry]:
            entry.configure({"highlightthickness": 1, "highlightbackground": "#808080"})

        # Disable window resizing (both width and height)
        modal_window.resizable(False, False)

        modal_window.mainloop()

def clear_fields():
    id_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)
    ami_pn_entry.delete(0, tk.END)
    mfg_pn_entry.delete(0, tk.END)
    stock_qty_entry.delete(0, tk.END)
    unit_price_entry.delete(0, tk.END)
    clear_image_label()

def clear_image_label(hide_completely=False):
    if hide_completely:
        image_label.image = None
        image_label.place_forget()
    else:
        image_label.image = None
        image_label.configure(
            image='',
            text="No Image Available",
            justify="center",
            fg="white",
            bg="#1f234a",
            font=("Helvetica", 14),
            anchor="center"
        )
        image_label.place(relx=0.5, rely=0.5, anchor="center", width=250, height=250)


def deselect_table(event=None):
    clear_fields()

    if image_label.image:
        image_label.image = None
        image_label.config(image=None)
        clear_image_label()

    table.selection_remove(table.focus())
    table.selection_set("")

    enable_buttons()

    search_entry.config(state="normal")
    clear_search_button.config(state="normal")

    window.bind("<Escape>", deselect_table)
    table.bind("<ButtonRelease-1>", lambda event: show_image())
    table.configure(selectmode="browse")


def update_table():
    table.delete(*table.get_children())
    c.execute("SELECT * FROM table_data")
    rows = c.fetchall()
    for row in rows:
        table.insert("", "end", values=row)

def search_table(event=None):
    keyword = search_entry.get().lower()
    table.delete(*table.get_children())
    c.execute("SELECT * FROM table_data")
    rows = c.fetchall()
    for row in rows:
        if keyword in str(row).lower():
            table.insert("", "end", values=row)
    if not keyword:  # If search bar is empty, show all entries
        update_table()

def clear_search(event=None):
    search_entry.delete(0, "end")
    update_table()

# Function to handle choosing a new database file location
def choose_database_location():
    global conn, c
    file_path = filedialog.askopenfilename(filetypes=[("Database files", "*.db")])
    if file_path:
        conn.close()  # Close the existing connection
        conn = sqlite3.connect(file_path)  # Connect to the new database file
        c = conn.cursor()
        update_table()

def export_excel():
    try:
        import pandas as pd
        df = pd.read_sql_query("SELECT * FROM table_data", conn)

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Success", "Data exported to Excel successfully.")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


# Create GUI window
window = tk.Tk()

# Show a one-time message to the user if a new database was created.
# Must run after the Tk root window is initialized so the messagebox displays correctly.
if is_new_db:
    messagebox.showinfo(
        "Database Created",
        f"No database detected. A new database has been created at:\n{DB_PATH}"
    )

window.title("AmiBom™")
window_width = 1200
window_height = 800
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x_coordinate = (screen_width - window_width) // 2
y_coordinate = (screen_height - window_height) // 2
window.geometry(f"{window_width}x{window_height}+{x_coordinate}+0")

# Set the background color of the main window
window.configure(bg="#1f234a")

# Create a custom style for the Treeview headings
style = ttk.Style()
style.configure("Treeview.Heading", font=("Helvetica", 15))

# Table frame
table_frame = ttk.Frame(window)
table_frame.place(x=30, y=410)  # Adjust the x and y coordinates

# Table
table = ttk.Treeview(table_frame, columns=("ID", "DATE", "AMI P/N", "MFG P/N", "STOCK QTY", "UNIT PRICE"), show="headings",
                     height=10)
table.column("ID", width=184)
table.column("DATE", width=184)
table.column("AMI P/N", width=184)
table.column("MFG P/N", width=184)
table.column("STOCK QTY", width=184)
table.column("UNIT PRICE", width=184)
table.heading("ID", text="ID")
table.heading("DATE", text="DATE")
table.heading("AMI P/N", text="AMI P/N")
table.heading("MFG P/N", text="MFG P/N")
table.heading("STOCK QTY", text="STOCK QTY")
table.heading("UNIT PRICE", text="UNIT PRICE")
table.bind("<ButtonRelease-1>", lambda event: show_image())
table.pack(side="top")

# Set the font size for Treeview rows
style.configure("Treeview", font=("Helvetica", 15), rowheight=25)

# Create a vertical scrollbar
scrollbar = Scrollbar(table_frame, orient="vertical", command=table.yview)
table.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

table.pack(side="left", padx=10, pady=10)  # Placing the table at the bottom

# Create "Save Changes" button and "Cancel" button
save_changes_button = None
cancel_button = None

# Image frame
image_frame = ttk.Frame(window)
image_frame.place(x=824, y=30, width=250, height=250)  # fix frame size same as image size

# Image label
image_label = tk.Label(image_frame, bg="#1f234a", fg="white", font=("Helvetica", 14), width=250, height=250)
#image_label.pack()

# Form frame
form_frame = ttk.Frame(window)
form_frame.place(x=30, y=30)  # Adjust the x and y coordinates

# Form inputs with borders
entry_style = ttk.Style()
entry_style.configure(
    "TEntry",
    font=("Helvetica", 15),
    padding=(10, 5),
    borderwidth=2,  # Adjust the borderwidth as needed
    relief="sunken",
    border=5  # Adjust the border thickness as needed
)

id_label = ttk.Label(form_frame, text="ID:", font=("Helvetica", 15))
id_label.grid(row=0, column=0, padx=5, pady=5)
id_entry = ttk.Entry(form_frame, style="TEntry", font=("Helvetica", 15), width=20)
id_entry.grid(row=0, column=1, padx=5, pady=5)

date_label = ttk.Label(form_frame, text="Date (mm-dd-yyyy):", font=("Helvetica", 15))
date_label.grid(row=1, column=0, padx=5, pady=5)
date_entry = ttk.Entry(form_frame, style="TEntry", font=("Helvetica", 15), width=20)
date_entry.grid(row=1, column=1, padx=5, pady=5)

ami_pn_label = ttk.Label(form_frame, text="AMI P/N:", font=("Helvetica", 15))
ami_pn_label.grid(row=2, column=0, padx=5, pady=5)
ami_pn_entry = ttk.Entry(form_frame, style="TEntry", font=("Helvetica", 15), width=20)
ami_pn_entry.grid(row=2, column=1, padx=5, pady=5)

mfg_pn_label = ttk.Label(form_frame, text="MFG P/N:", font=("Helvetica", 15))
mfg_pn_label.grid(row=3, column=0, padx=5, pady=5)
mfg_pn_entry = ttk.Entry(form_frame, style="TEntry", font=("Helvetica", 15), width=20)
mfg_pn_entry.grid(row=3, column=1, padx=5, pady=5)

stock_qty_label = ttk.Label(form_frame, text="STOCK QTY.:", font=("Helvetica", 15))
stock_qty_label.grid(row=4, column=0, padx=5, pady=5)
stock_qty_entry = ttk.Entry(form_frame, style="TEntry", font=("Helvetica", 15), validate="key", width=20)
stock_qty_entry.grid(row=4, column=1, padx=5, pady=5)

unit_price_label = ttk.Label(form_frame, text="UNIT PRICE:", font=("Helvetica", 15))
unit_price_label.grid(row=5, column=0, padx=5, pady=5)
unit_price_entry = ttk.Entry(form_frame, style="TEntry", font=("Helvetica", 15), validate="key", width=20)
unit_price_entry.grid(row=5, column=1, padx=5, pady=5)

# Validation callback for stock_qty_entry
def validate_stock_qty(action, value_if_allowed):
    if action == "1":  # Insertion or deletion of a character
        return value_if_allowed.isdigit() or value_if_allowed == ""
    return True

# Register the validation callback for stock_qty_entry
validate_stock_qty_callback = form_frame.register(validate_stock_qty)
stock_qty_entry.configure(validatecommand=(validate_stock_qty_callback, "%d", "%P"))

# Validation callback for unit_price_entry
def validate_unit_price(action, value_if_allowed):
    if action == "1":  # Insertion or deletion of a character
        try:
            if value_if_allowed:
                float(value_if_allowed)  # Validate the input as a float
            return True
        except ValueError:
            return False
    return True

# Register the validation callback for unit_price_entry
validate_unit_price_callback = form_frame.register(validate_unit_price)
unit_price_entry.configure(validatecommand=(validate_unit_price_callback, "%d", "%P"))


# Add Button to insert data from text boxes to the table
add_button = tk.Button(window, text="ADD", command=add_row, font=("Helvetica", 15), width=10, height=2,
                       bg="#4CAF50", fg="white")
add_button.place(x=30, y=330)


# Remove Button to remove selected data from the table
remove_button = tk.Button(window, text="REMOVE", command=remove_row, font=("Helvetica", 15), width=10, height=2,
                          bg="#b51f1f", fg="white")
remove_button.place(x=160, y=330)

# Modify Button to modify selected data in the table
modify_button = tk.Button(window, text="MODIFY", command=modify_row, font=("Helvetica", 15), width=10,
                          height=2, bg="#FFA500", fg="white")
modify_button.place(x=290, y=330)

# View Image button
view_image_button = tk.Button(window, text="View Image", command=view_image, font=("Helvetica", 12), width=10,
                              height=2, bg="#2196F3", fg="white")
view_image_button.place(x=903, y=337)  # Adjust the position of the button

# Create "Previous" button to switch to the previous row in the table
prev_button = tk.Button(window, text="◄", command=select_previous_row, font=("Helvetica", 12), width=2,
                        height=2, bg="#2196F3", fg="white")
prev_button.place(x=860, y=337)

# Create "Next" button to switch to the next row in the table
next_button = tk.Button(window, text="►", command=select_next_row, font=("Helvetica", 12), width=2,
                        height=2, bg="#2196F3", fg="white")
next_button.place(x=1018, y=337)

# Create "View Info" button to view the information of the selected row
view_info_button = tk.Button(window, text="View Info", command=view_row_info, font=("Helvetica"), width=10,
                             height=2, bg="#2196F3", fg="white")
view_info_button.place(x=512, y=330)  # Adjust the position of the button


# Search frame
search_frame = ttk.Frame(window)
search_frame.place(x=30, y=730)

# Search label
search_label = ttk.Label(search_frame, text="Search", font=("Helvetica", 15))
search_label.grid(row=0, column=0, padx=5, pady=5)

# Search entry
search_entry = ttk.Entry(search_frame, font=("Helvetica", 15))
search_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=2)
search_entry.bind("<KeyRelease>", search_table)

# Clear search button
clear_search_button = ttk.Button(search_frame, text="Clear", command=clear_search, style="TButton")
clear_search_button.grid(row=0, column=3, padx=5, pady=5)

# Create a style
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 15))


# Create menu bar
menu_bar = tk.Menu(window)
window.config(menu=menu_bar)

# Create "File" menu
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)

# Create "Database" submenu under "File" menu
database_submenu = tk.Menu(file_menu, tearoff=0)
file_menu.add_cascade(label="Database", menu=database_submenu)
database_submenu.add_command(label="Open Database", command=choose_database_location)

# Create "Sort By" menu
sort_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Sort By", menu=sort_menu)

# Create "Ascending Order" submenu under "Sort By" menu
ascending_submenu = tk.Menu(sort_menu, tearoff=0)
sort_menu.add_cascade(label="Ascending Order", menu=ascending_submenu)
ascending_submenu.add_command(label="ID", command=lambda: sort_table("ID", False))
ascending_submenu.add_command(label="Date Modified", command=lambda: sort_table("DATE", False))
ascending_submenu.add_command(label="Stock Qty.", command=lambda: sort_table("STOCK QTY", False))
ascending_submenu.add_command(label="Unit Price", command=lambda: sort_table("UNIT PRICE", False))

# Create "Descending Order" submenu under "Sort By" menu
descending_submenu = tk.Menu(sort_menu, tearoff=0)
sort_menu.add_cascade(label="Descending Order", menu=descending_submenu)
descending_submenu.add_command(label="ID", command=lambda: sort_table("ID", True))
descending_submenu.add_command(label="Date Modified", command=lambda: sort_table("DATE", True))
descending_submenu.add_command(label="Stock Qty.", command=lambda: sort_table("STOCK QTY", True))
descending_submenu.add_command(label="Unit Price", command=lambda: sort_table("UNIT PRICE", True))

column_mapping = {
    "ID": "ID",
    "DATE": "date",
    "STOCK QTY": "stock_qty",
    "UNIT PRICE": "unit_price"
}

def sort_table(column, descending):
    db_column = column_mapping.get(column, column)  # Get actual DB column name

    if column == "DATE":
        rows = c.execute("SELECT * FROM table_data").fetchall()
        rows.sort(key=lambda row: datetime.strptime(row[1], "%m-%d-%Y"), reverse=descending)
    else:
        rows = c.execute(f'SELECT * FROM table_data ORDER BY "{db_column}" {"DESC" if descending else "ASC"}').fetchall()

    table.delete(*table.get_children())
    for row in rows:
        table.insert("", "end", values=row)



# Key binding
window.bind("<Escape>", deselect_table)

window.bind("<Left>", select_previous_row_key)
window.bind("<Right>", select_next_row_key)

# Bind arrow keys to the disable_arrow_keys function
window.bind("<Up>", disable_arrow_keys)
window.bind("<Down>", disable_arrow_keys)


# Update table initially
update_table()

# Run the GUI
window.mainloop()

# Close the database connection
c.close()
conn.close()