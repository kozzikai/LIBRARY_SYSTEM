# Interactive GUI Application

This is an interactive GUI application developed using Tkinter, Python, and MySQL. It is platform-independent and can be used across various operating systems.

## Software Requirements

Before installing the application, ensure you have the following software installed:

- **MySQL Community Server - GPL** (Version 8.1.0)
- **Python** (Version 3.7 or higher)

## Software Library Requirements

The application requires the following Python libraries:

- **Tkinter**: Usually comes pre-installed with Python.
- **PyMySQL** (Version 1.1.0): Required for MySQL database interactions.
- **Python-dotenv** (Version 1.0.0): Used for loading environment variables from the `.env` file.

## Installation

Follow these steps to install and set up the application:

1. **Unzip the Package**:
   - Extract the provided package into a directory, maintaining the original directory structure.

2. **Configure Environment Variables**:
   - Edit the `.env` file to include the following environment variables:
     - `DB_HOST`: Your MySQL server host.
     - `DB_USERNAME`: Your MySQL database username.
     - `DB_PASSWORD`: Your MySQL database password.
     - `DB_SCHEMA_FILE`: Path to the database schema file Database-Library-Schema.sql
     - `BOOKS_CSV_FILE`: Path to your books CSV file.
     - `BORROWERS_CSV_FILE`: Path to your borrowers CSV file.
   - These variables are mandatory for the application to function correctly.

3. **Initialize the Database**:
   - Run the following command in your terminal:
     ```
     python3 <absolute file path of pre_processing.py>
     ```
   - This script will initialize the database and create the necessary tables with the provided data. This is a one-time setup process.

## Application Usage

To start the application:

1. Run the following command:
    ```
    python3 <absolute file path of main.py>
    ```

This command will launch the main interface of the application.

## Additional Notes

- Ensure you have the necessary permissions for installing and running the software and scripts mentioned above.
- It is recommended to back up your database before performing any new installations or running scripts.

---

