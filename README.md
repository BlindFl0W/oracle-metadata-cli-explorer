# Oracle Metadata Explorer

A terminal-based application for exploring Oracle Database metadata interactively, similar to Oracle SQL Developer's visual interface.

## Features

- Interactive menu-driven interface
- Explore database objects:
  - **Tables**: View columns, constraints, and indexes
  - **Views**: View column information
  - **Sequences**: View sequence details
  - **Users**: List all database users
- Clean, formatted output
- Error handling and validation

## Requirements

- Python 3.7 or higher
- Oracle Database (local or remote)
- Oracle Client libraries (Oracle Instant Client)

## Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install Oracle Instant Client:
   - Download from [Oracle's website](https://www.oracle.com/database/technologies/instant-client/downloads.html)
   - Extract and add to your system PATH
   - On Windows, you may need to add the Instant Client directory to your PATH environment variable

## Usage

Run the application:
```bash
python oracle_metadata_explorer.py
```

You will be prompted to enter:
- **Username**: Your Oracle database username
- **Password**: Your Oracle database password
- **Service name**: The service name or connection string (e.g., `orcl`, `localhost:8521/orcl`, or a TNS name)

## Example Session

```
Welcome to Oracle Metadata Explorer!
-----------------------------------
Enter username: HR
Enter password: *****
Enter service name: orcl

✓ Successfully connected to Oracle Database!

Select the object type you want to view:
1. Tables
2. Views
3. Sequences
4. Users
5. Exit

Enter option number: 1

Available Tables:
1. EMPLOYEES
2. DEPARTMENTS
3. JOBS
4. LOCATIONS
5. COUNTRIES

Select a table number: 1

You selected: EMPLOYEES
Choose what to view about EMPLOYEES:
1. Columns
2. Constraints
3. Indexes
4. Back to main menu

Enter option number: 1

================================================================================
Columns for EMPLOYEES
================================================================================

Column Name                    Data Type            Length     Nullable   Default
--------------------------------------------------------------------------------
EMPLOYEE_ID                    NUMBER               22         NO         
FIRST_NAME                     VARCHAR2             20         YES        
LAST_NAME                      VARCHAR2             25         NO         
...
```

## Notes

- The application uses Oracle data dictionary views (`USER_TABLES`, `USER_VIEWS`, etc.) to retrieve metadata
- For viewing all users, you may need DBA privileges or appropriate system privileges
- The connection supports both service name format and full connection strings

## Troubleshooting

**Connection Issues:**
- Ensure Oracle Instant Client is installed and in your PATH
- Verify the service name is correct
- Check network connectivity to the database server
- Try using a full connection string: `host:port/service_name`

**Permission Errors:**
- Some views may require specific privileges
- Contact your DBA if you need access to additional objects

