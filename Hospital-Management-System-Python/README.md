# Hospital Management System

A Streamlit-based hospital administration application connected to MySQL.

## Features
- Dashboard metrics
- Patient registration, search, edit and delete
- Doctor registration, search, edit and active status
- Department and service management
- Appointment booking and status updates
- Room inventory and availability
- Bill creation and outstanding balance views
- Payment recording through the database stored procedure
- Reports for revenue, doctor activity, service usage and patient history

## Structure
```text
hospital_management_python/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── hospital/
    ├── __init__.py
    ├── db.py
    └── repositories.py
```

## Database setup
First create the MySQL database and objects using your SQL project files, in this order:
1. schema.sql
2. seed_data.sql
3. views.sql
4. procedures.sql
5. triggers.sql
6. indexes.sql

The database name defaults to `hospital_management`.
**Warning:** schema.sql drops and recreates existing project tables. Back up data first.

## Install and run
Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

Set your MySQL credentials in `.env`:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=hospital_management
```

## Notes and limitations
- SQL values are parameterized.
- Appointment booking and payment entry use the supplied stored procedures.
- Patient deletion can be blocked by foreign-key references. This is intentional.
- The current schema has no room-admission table, so rooms can only be managed as inventory/status.
- The bill form currently creates one bill item per bill.
- This is a portfolio/demo system, not suitable for real patient data without authentication,
  authorization, privacy controls, stronger audit coverage, backups and security review.
