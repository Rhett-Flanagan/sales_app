# Sales App

This is a Django-based sales transaction system.

## Setup and Run

1.  **Prerequisites:**
    *   Python 3.x installed.
    *   `pip` (Python package installer) installed.
    *   `virtualenv` installed (if you prefer to use it, otherwise skip to step 3):
        ```bash
        pip install virtualenv
        ```

2.  **Create and Activate a Virtual Environment (recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    ```bash
    uv pip install -r requirements.txt
    ```

4.  **Initialize the Database:**
    The database models have already been defined and migrated. If you need to re-create the database or apply new migrations, use:
    ```bash
    python manage.py makemigrations core
    python manage.py migrate
    ```

5.  **Populate Sample Data (Optional):**
    To add some initial sample data to your database, run:
    ```bash
    python manage.py populate_data
    ```

6.  **Run the Development Server:**
    ```bash
    python manage.py runserver
    ```

    The application will be accessible at `http://127.0.0.1:8000/`.

## Application Features

### Customer Management (CRUD)
*   **List Customers:** Access at `http://127.0.0.1:8000/customers/`
*   **Add New Customer:** Click the "Add New Customer" button on the customer list page.
*   **Edit Customer:** Click the "Edit" link next to a customer on the list page. Only the Name field is editable.
*   **Delete Customer:** Click the "Delete" link next to a customer on the list page.

### Transaction Management (CRUD)
*   **List Transactions:** Access at `http://127.0.0.1:8000/transactions/`
*   **Add New Transaction:** Click the "Add New Transaction" button on the transaction list page.
*   **Bulk Add Transactions:** Click the "Bulk Add Transactions" button on the transaction list page. You can specify the number of transaction forms to display.
*   **Edit Transaction:** Click the "Edit" link next to a transaction on the list page.
*   **Delete Transaction:** Click the "Delete" link next to a transaction on the list page.

### Enquiries
*   **View Customer Transactions:** Access at `http://127.0.0.1:8000/enquiries/`. Select a customer to view their past transactions.

## Database Schema

### Customers Table
*   **Account:** Alphanumeric, Length 15, Unique Identifier (Primary Key). Strictly 15 alphanumeric characters.
*   **Name:** Alphanumeric, Length 30
*   **Balance:** Decimal. Negative balances appear in red.

### Transactions Table
*   **Number:** Autoincremented record number, Unique Identifier (Primary Key).
*   **Account:** Alphanumeric, Length 15 (Foreign Key to Customers.Account)
*   **Date:** Datetime. Editable with a date and time picker.
*   **Amount:** Decimal
*   **DC:** Alphanumeric, Length 1 ('D' for Debit, 'C' for Credit)
*   **Reference:** Alphanumeric, Length 10, Unique. Strictly 10 alphanumeric characters. This field is mandatory.
