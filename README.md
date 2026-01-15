# Inventory Management System (AmiBom™)

A **desktop inventory management system** built in **Python** using **Tkinter** and **SQLite**.  
This system allows users to **add, modify, remove, search, sort, and view inventory items**, including product images.  
The database is **automatically created** if none exists, making the system portable across computers.

---

## Features

### Add Row
- Insert a new inventory item with **ID, Date, AMI P/N, MFG P/N, Stock Quantity, Unit Price**, and optional image.  
- Input validation prevents empty fields or invalid entries.

### Modify Row
- Edit all fields of an existing inventory item.  
- Upload and display product images; image paths are saved in the database automatically.  
- Buttons and table are disabled during modification to prevent conflicts.

### Remove Row
- Delete a selected inventory item.  
- Confirmation prompt prevents accidental deletion.

### Search & Sort
- Search by any keyword (**case-insensitive**).  
- Sort columns ascending/descending: **ID, Date, Stock Qty., Unit Price**.

### View Image
- View uploaded product images in a modal window.  
- Images are automatically resized to fit the display area.

### Auto-Database Creation
- If no database exists, a new SQLite database is created automatically in the project folder.  
- One-time popup notifies the user of database creation.

---

## Screenshots

| Screenshot | Description |
|------------|-------------|
| ![main_window](Screenshots/01%20-%20main%20window.png) | Full main GUI window with table and form fields |
| ![add_row](Screenshots/02%20-%20add_row.png) | Adding a new inventory item (fields filled + item in table) |
| ![no_image](Screenshots/03%20-%20no%20image%20available.png) | Placeholder for missing image |
| ![modify_row](Screenshots/04%20-%20modify_row.png) | Modifying an existing row (with upload image button) |
| ![upload_image](Screenshots/05%20-%20upload_image.png) | Uploading an image  |
| ![remove_row](Screenshots/06%20-%20remove_row.png) | Confirmation dialog for deleting a row |
| ![sort_date](Screenshots/07%20-%20sort%20by%20date%20(ascending).png) | Sorting by date (ascending) |
| ![sort_price](Screenshots/08%20-%20sort%20by%20unit%20price%20(descending).png) | Sorting by unit price (descending) |
| ![search_bar](Screenshots/09%20-%20search%20bar.png) | Search bar functionality |
| ![view_image](Screenshots/10%20-%20view_image.png) | Modal popup showing product image |


---

## Installation

> Note: Run the commands in your terminal (PowerShell, Command Prompt, Git Bash, or macOS/Linux Terminal). GitHub itself does not execute code.

1. Clone the repository:
```
git clone https://github.com/SE-Looweh05/Inventory-Management-System.git
```

2. Navigate to the project folder:
```
cd Inventory-Management-System
```

3. Run the Python application:
```
python IMS.py
```




