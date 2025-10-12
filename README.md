# Code Yatra Banking App

## Overview

Code Yatra Banking App is a comprehensive digital banking web application built with Flask, designed to simulate a modern banking experience. It provides secure user authentication, account management, money transfers, transaction tracking, and administrative controls. The app aims to demonstrate full-stack web development concepts, including user interfaces, backend logic, database integration, and PDF generation for passbooks.

This project serves as an educational tool for learning web development with Python and Flask, showcasing features like user registration, login, dashboards for users and admins, secure transactions, and request management. It is not intended for production use in real banking scenarios.

**Developer:** Narendra Vaniya , Shreya Vaghela

## Purpose

The purpose of this project is to create a functional banking application prototype that includes:
- User-friendly interfaces for customers to manage their accounts.
- Administrative tools for bank staff to oversee operations.
- Secure handling of financial transactions and data.
- Educational value for developers interested in building web applications with Flask and MongoDB.

## Technologies Used

- **Backend:** Python 3.x, Flask (web framework)
- **Database:** MongoDB (NoSQL database for storing users, transactions, requests)
- **Forms and Validation:** WTForms, Flask-WTF
- **Authentication:** bcrypt for password hashing
- **PDF Generation:** ReportLab for generating passbook PDFs
- **Frontend:** HTML5, CSS3, Bootstrap 5 (for responsive design), JavaScript
- **Templating:** Jinja2 (Flask's default templating engine)
- **Other Libraries:** Flask-PyMongo (MongoDB integration), Flask-Login (session management)

## Features

### User Features
- **Registration and Login:** Users can register with personal details and login using account number and MPIN.
- **Dashboard:** Overview of account information and recent transactions.
- **Balance Inquiry:** Check current account balance.
- **Money Transfer:** Transfer funds to other users securely.
- **Transaction History:** View detailed list of transactions (credits, debits, transfers).
- **Passbook:** Digital passbook with transaction details, filterable by date range.
- **PDF Download:** Generate and download passbook as PDF.
- **Service Requests:** Submit requests for cheque books or physical passbooks.
- **Request Tracking:** View status of submitted requests.

### Admin Features
- **Admin Login:** Secure login for administrators.
- **Dashboard:** Overview of users and transactions.
- **User Management:** View all users, add new users, delete users.
- **Credit/Debit Operations:** Manually credit or debit user accounts.
- **Transaction Monitoring:** View all transactions across the system.
- **Request Management:** Approve or reject user requests.

### General Features
- **Responsive Design:** Works on desktop and mobile devices.
- **Security:** Password hashing, session management, input validation.
- **Data Masking:** Sensitive information like Aadhar numbers are masked in views.
- **Sample Data:** Automatically creates default admin and sample users on first run.

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- MongoDB installed and running locally (default port 27017)
- Git (for cloning the repository)

### Installation Steps
1. **Clone the Repository:**
   ```
   git clone <repository-url>
   cd codeyatra-bank
   ```

2. **Install Dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Start MongoDB:**
   Ensure MongoDB is running on your system. If using default settings, no additional configuration is needed.

4. **Run the Application:**
   ```
   python app.py
   ```

5. **Access the App:**
   Open a web browser and go to `http://localhost:5000`.

### Default Credentials
- **Admin Login:** Username: `admin`, Password: `admin123`
- **Sample Users:** Created automatically (e.g., Account: `1234567890`, MPIN: `1234`)

## Project Structure

- `app.py`: Main Flask application with routes and logic.
- `models.py`: Database models for User, Transaction, Request, Admin.
- `forms.py`: WTForms classes for form handling and validation.
- `utils.py`: Utility functions for transactions, requests, and data masking.
- `db.py`: Database connection setup.
- `pdf.py`: PDF generation logic for passbooks.
- `admin_config.py`: Admin configuration utilities.
- `static/`: Static assets (CSS, JS, images).
- `templates/`: Jinja2 HTML templates for pages.
  - `base.html`: Base template with navigation.
  - `home.html`: Landing page.
  - `login.html`: Login and registration page.
  - `admin/`: Admin-specific templates (dashboard, users, etc.).
  - `user/`: User-specific templates (dashboard, transfer, etc.).
- `data/`: MongoDB data files (auto-generated).
- `requirements.txt`: Python dependencies.
- `TODO.md`: Task list for development.
- `README.md`: This file.

## Usage

1. **Home Page:** Visit the home page to learn about the bank and its services.
2. **User Registration:** Click "Login as User" and use the registration form.
3. **User Operations:** Login to perform transfers, view balance, transactions, etc.
4. **Admin Operations:** Login as admin to manage users and transactions.
5. **PDF Passbook:** From the passbook page, select date range and download PDF.


## License

This project is for educational purposes only.

## Contact

For questions or feedback, contact the developer: Narendra Vaniya, Shreya Vaghela.
