                         Inventory Management Web App (Flask Project)

This is my simple Inventory Management System built using Flask.  
The main idea of this project is to manage products, locations, and movements between locations in a clean and easy way.  

Project Description
This web app helps in tracking items in an inventory.  
You can:
- Add products with name, quantity, and location.  
- Add locations where products are stored.  
- Move products from one location to another.  
- View a report that shows how many items are present in each location.  

Whenever a product is moved, its count automatically updates in the report page.


 Tech Stack Used
- Frontend: HTML, CSS, Jinja Templates  
- Backend: Flask (Python)  
- Database: SQLite (through SQLAlchemy ORM)  
- Deployment: Render  
- Version Control:Git & GitHub  


 Project Structure
 Inventory_Management/
│
├── app.py → main Flask file (routes and logic)
├── models.py → database models (Product, Location, Movement)
├── requirements.txt → dependencies
├── Procfile → deployment setup for Render
├── README.md
├── .gitignore
│
├── templates/ → HTML pages
│ ├── base.html
│ ├── add_product.html
│ ├── products.html
│ ├── add_location.html
│ ├── locations.html
│ ├── add_movement.html
│ ├── movements.html
│ └── report.html
│
└── static/ → CSS and images
└── style.css

 Working Logic 
1. Add Product Page → You can add product name, quantity, and select a location from the dropdown.  
2. Add Location Page → You can add a new location (like Warehouse A, Warehouse B, etc.).  
3. Movement Page → You can move products from one location to another, and it automatically adjusts the quantity in both places.  
4. Report Page → Shows all products with their current quantities and locations in a table view.  
So, it basically acts like a mini warehouse manager.

How to Run This Project Locally

1) Clone this project
git clone https://github.com/PKSowmiya05/Inventory_Management.git
2️) Create virtual environment and activate it
python -m venv venv
venv\Scripts\activate      # for Windows
3️) Install the required dependencies
pip install -r requirements.txt
4️) Run the Flask app
python app.py
5️) Open in browser
 http://127.0.0.1:5000

 Demo Video
You can watch the full working demo here 
https://drive.google.com/file/d/1zqOkxzfZnoA2_ciscnNeX7Os_Gts3VX4/view?usp=drivesdk

