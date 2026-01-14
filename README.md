# Inventory Management System (AmiBom™)

A **desktop inventory management system** built in **Python** using **Tkinter** and **SQLite**.  
This system allows users to **add, modify, remove, search, sort, and view inventory items**, including product images. The database is automatically created if none exists, making it portable across computers.

---

## Features

1. **Add Row**
   - Insert a new inventory item with ID, date, AMI P/N, MFG P/N, stock quantity, unit price, and optional image.
   - Input validation prevents empty fields or invalid entries.

2. **Modify Row**
   - Select an existing row and edit all fields.
   - Temporary image upload supported.
   - Buttons and table are disabled during modification to prevent conflicts.

3. **Remove Row**
   - Delete a selected inventory item.
   - Confirmation prompt prevents accidental deletion.

4. **Search & Sort**
   - Search by any keyword (case-insensitive).
   - Sort columns ascending/descending: ID, Date, Stock Qty., Unit Price.

5. **View Image**
   - View uploaded product images in a modal window.
   - Images are automatically resized to fit display area.

6. **Auto-Database Creation**
   - If no database exists, a new SQLite DB is created automatically in the project folder.
   - One-time popup notifies the user of database creation.

7. **Export to Excel**
   - Export all inventory items to an Excel file using pandas.

---

## Screenshots

Put screenshots in `screenshots/` folder.

| Screenshot | What to show |
|------------|--------------|
| main_window.png | Full main GUI window with table and form fields |
| add_row.png | Adding a new inventory item (show fields filled + item in table) |
| modify_row.png | Modifying an existing row (show temporary upload image button) |
| remove_row.png | Confirmation dialog for deleting a row |
| search_sort.png | Search bar usage and sorting by a column |
| view_image.png | Modal popup showing product image |

> Tip: Use **clear, readable images**. Highlight buttons or fields if possible.

---

## Installation

1. Clone the repository:
```bash
git clone https://github.com/<your-username>/Inventory-Management-System.git
