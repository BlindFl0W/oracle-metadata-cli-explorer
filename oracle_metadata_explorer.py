"""
Oracle Metadata Explorer
A terminal-based application for exploring Oracle Database metadata interactively.
"""

import oracledb
import sys
from typing import Optional, List, Dict, Tuple


class OracleMetadataExplorer:
    """Main class for Oracle Metadata Explorer application."""
    
    def __init__(self):
        self.connection: Optional[oracledb.Connection] = None
        self.username: str = ""
    
    def connect(self, username: str, password: str, service_name: str) -> bool:
        """
        Establish connection to Oracle database.
        
        Args:
            username: Database username
            password: Database password
            service_name: Service name or connection string (e.g., 'orcl', 'host:port/service_name', TNS name)
            
        Returns:
            True if connection successful, False otherwise
        """
        # Try multiple connection methods
        connection_methods = [
            # Method 1: Try as full connection string or TNS name (host:port/service_name or tnsname)
            lambda: oracledb.connect(user=username, password=password, dsn=service_name),
            # Method 2: Try as service name with localhost
            lambda: oracledb.connect(user=username, password=password, dsn=oracledb.makedsn(host="localhost", port=8521, service_name=service_name))
        ]
        
        for i, connect_method in enumerate(connection_methods):
            try:
                self.connection = connect_method()
                self.username = username.upper()
                print("\n✓ Successfully connected to Oracle Database!\n")
                return True
            except oracledb.Error as e:
                if i == len(connection_methods) - 1:
                    # Last method failed, show error
                    print(f"\n✗ Connection failed: {e}")
                    print("\nTip: Try using one of these formats:")
                    print("  - Service name only: 'orcl'")
                    print("  - Full connection string: 'hostname:port/service_name'")
                    print("  - TNS name: 'tns_name' (requires tnsnames.ora configuration)")
                    return False
                continue
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("\n✓ Disconnected from database.\n")
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Tuple]:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Optional parameters for the query
            
        Returns:
            List of tuples containing query results
        """
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except oracledb.Error as e:
            print(f"\n✗ Query error: {e}\n")
            return []
    
    def get_tables(self) -> List[str]:
        """Get list of all tables accessible to the user."""
        query = """
            SELECT table_name 
            FROM user_tables 
            ORDER BY table_name
        """
        results = self.execute_query(query)
        return [row[0] for row in results]
    
    def get_views(self) -> List[str]:
        """Get list of all views accessible to the user."""
        query = """
            SELECT view_name 
            FROM user_views 
            ORDER BY view_name
        """
        results = self.execute_query(query)
        return [row[0] for row in results]
    
    def get_sequences(self) -> List[str]:
        """Get list of all sequences accessible to the user."""
        query = """
            SELECT sequence_name 
            FROM user_sequences 
            ORDER BY sequence_name
        """
        results = self.execute_query(query)
        return [row[0] for row in results]
    
    def get_users(self) -> List[str]:
        """Get list of all users in the database (requires DBA privileges)."""
        try:
            query = """
                SELECT username 
                FROM all_users 
                ORDER BY username
            """
            results = self.execute_query(query)
            return [row[0] for row in results]
        except oracledb.Error:
            # If user doesn't have access to all_users, try user_users
            try:
                query = """
                    SELECT username 
                    FROM user_users 
                    ORDER BY username
                """
                results = self.execute_query(query)
                return [row[0] for row in results]
            except oracledb.Error:
                return []
    
    def get_table_columns(self, table_name: str) -> List[Tuple]:
        """Get column information for a table."""
        query = """
            SELECT column_name, data_type, data_length, 
                   nullable, data_default
            FROM user_tab_columns 
            WHERE table_name = :table_name
            ORDER BY column_id
        """
        return self.execute_query(query, {"table_name": table_name})
    
    def get_table_constraints(self, table_name: str) -> List[Tuple]:
        """Get constraint information for a table."""
        query = """
            SELECT constraint_name, constraint_type, 
                   search_condition, status
            FROM user_constraints 
            WHERE table_name = :table_name
            ORDER BY constraint_type, constraint_name
        """
        return self.execute_query(query, {"table_name": table_name})
    
    def get_table_indexes(self, table_name: str) -> List[Tuple]:
        """Get index information for a table."""
        query = """
            SELECT index_name, index_type, uniqueness, status
            FROM user_indexes 
            WHERE table_name = :table_name
            ORDER BY index_name
        """
        return self.execute_query(query, {"table_name": table_name})
    
    def get_view_columns(self, view_name: str) -> List[Tuple]:
        """Get column information for a view."""
        query = """
            SELECT column_name, data_type, data_length, nullable
            FROM user_tab_columns 
            WHERE table_name = :view_name
            ORDER BY column_id
        """
        return self.execute_query(query, {"view_name": view_name})
    
    def get_sequence_details(self, sequence_name: str) -> List[Tuple]:
        """Get details for a sequence."""
        query = """
            SELECT min_value, max_value, increment_by, 
                   cycle_flag, order_flag, cache_size, last_number
            FROM user_sequences 
            WHERE sequence_name = :sequence_name
        """
        return self.execute_query(query, {"sequence_name": sequence_name})
    
    def display_table_metadata_menu(self, table_name: str):
        """Display metadata options for a selected table."""
        while True:
            print(f"\nYou selected: {table_name}")
            print("Choose what to view about {}:".format(table_name))
            print("1. Columns")
            print("2. Constraints")
            print("3. Indexes")
            print("4. Back to main menu")
            
            choice = input("Enter option number: ").strip()
            
            if choice == "1":
                self.display_table_columns(table_name)
            elif choice == "2":
                self.display_table_constraints(table_name)
            elif choice == "3":
                self.display_table_indexes(table_name)
            elif choice == "4":
                break
            else:
                print("\n✗ Invalid option. Please try again.")
    
    def display_table_columns(self, table_name: str):
        """Display column information for a table."""
        print(f"\n{'='*80}")
        print(f"Columns for {table_name}")
        print(f"{'='*80}")
        columns = self.get_table_columns(table_name)
        
        if not columns:
            print("No columns found.")
            return
        
        print(f"\n{'Column Name':<30} {'Data Type':<20} {'Length':<10} {'Nullable':<10} {'Default'}")
        print("-" * 80)
        
        for col in columns:
            col_name, data_type, data_length, nullable, data_default = col
            nullable_str = "YES" if nullable == "Y" else "NO"
            default_str = str(data_default) if data_default else ""
            print(f"{col_name:<30} {data_type:<20} {str(data_length):<10} {nullable_str:<10} {default_str}")
        
        input("\nPress Enter to continue...")
    
    def display_table_constraints(self, table_name: str):
        """Display constraint information for a table."""
        print(f"\n{'='*80}")
        print(f"Constraints for {table_name}")
        print(f"{'='*80}")
        constraints = self.get_table_constraints(table_name)
        
        if not constraints:
            print("No constraints found.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n{'Constraint Name':<35} {'Type':<15} {'Status':<10} {'Condition'}")
        print("-" * 80)
        
        constraint_type_map = {
            'P': 'Primary Key',
            'R': 'Foreign Key',
            'U': 'Unique',
            'C': 'Check',
            'V': 'Check Option',
            'O': 'Read Only'
        }
        
        for constraint in constraints:
            const_name, const_type, search_condition, status = constraint
            type_str = constraint_type_map.get(const_type, const_type)
            condition_str = search_condition if search_condition else ""
            print(f"{const_name:<35} {type_str:<15} {status:<10} {condition_str}")
        
        input("\nPress Enter to continue...")
    
    def display_table_indexes(self, table_name: str):
        """Display index information for a table."""
        print(f"\n{'='*80}")
        print(f"Indexes for {table_name}")
        print(f"{'='*80}")
        indexes = self.get_table_indexes(table_name)
        
        if not indexes:
            print("No indexes found.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n{'Index Name':<35} {'Type':<20} {'Uniqueness':<15} {'Status':<10}")
        print("-" * 80)
        
        for index in indexes:
            idx_name, idx_type, uniqueness, status = index
            uniqueness_str = "UNIQUE" if uniqueness == "UNIQUE" else "NONUNIQUE"
            print(f"{idx_name:<35} {idx_type:<20} {uniqueness_str:<15} {status:<10}")
        
        input("\nPress Enter to continue...")
    
    def display_view_metadata_menu(self, view_name: str):
        """Display metadata options for a selected view."""
        while True:
            print(f"\nYou selected: {view_name}")
            print("Choose what to view about {}:".format(view_name))
            print("1. Columns")
            print("2. Back to main menu")
            
            choice = input("Enter option number: ").strip()
            
            if choice == "1":
                self.display_view_columns(view_name)
            elif choice == "2":
                break
            else:
                print("\n✗ Invalid option. Please try again.")
    
    def display_view_columns(self, view_name: str):
        """Display column information for a view."""
        print(f"\n{'='*80}")
        print(f"Columns for {view_name}")
        print(f"{'='*80}")
        columns = self.get_view_columns(view_name)
        
        if not columns:
            print("No columns found.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n{'Column Name':<30} {'Data Type':<20} {'Length':<10} {'Nullable':<10}")
        print("-" * 80)
        
        for col in columns:
            col_name, data_type, data_length, nullable = col
            nullable_str = "YES" if nullable == "Y" else "NO"
            print(f"{col_name:<30} {data_type:<20} {str(data_length):<10} {nullable_str:<10}")
        
        input("\nPress Enter to continue...")
    
    def display_sequence_details(self, sequence_name: str):
        """Display details for a sequence."""
        print(f"\n{'='*80}")
        print(f"Sequence Details for {sequence_name}")
        print(f"{'='*80}")
        details = self.get_sequence_details(sequence_name)
        
        if not details:
            print("Sequence details not found.")
            input("\nPress Enter to continue...")
            return
        
        detail = details[0]
        min_val, max_val, increment_by, cycle_flag, order_flag, cache_size, last_number = detail
        
        print(f"\nMinimum Value: {min_val}")
        print(f"Maximum Value: {max_val}")
        print(f"Increment By: {increment_by}")
        print(f"Cycle: {'YES' if cycle_flag == 'Y' else 'NO'}")
        print(f"Order: {'YES' if order_flag == 'Y' else 'NO'}")
        print(f"Cache Size: {cache_size}")
        print(f"Last Number: {last_number}")
        
        input("\nPress Enter to continue...")
    
    def select_object(self, objects: List[str], object_type: str) -> Optional[str]:
        """Display list of objects and let user select one."""
        if not objects:
            print(f"\nNo {object_type.lower()} found.")
            input("Press Enter to continue...")
            return None
        
        print(f"\nAvailable {object_type}:")
        for i, obj in enumerate(objects, 1):
            print(f"{i}. {obj}")
        
        try:
            choice = int(input(f"\nSelect a {object_type.lower().rstrip('s')} number: ").strip())
            if 1 <= choice <= len(objects):
                return objects[choice - 1]
            else:
                print(f"\n✗ Invalid selection. Please choose a number between 1 and {len(objects)}.")
                return None
        except ValueError:
            print("\n✗ Invalid input. Please enter a number.")
            return None
    
    def main_menu(self):
        """Display and handle main menu."""
        while True:
            print("\n" + "="*80)
            print("Welcome to Oracle Metadata Explorer!")
            print("="*80)
            print("Select the object type you want to view:")
            print("1. Tables")
            print("2. Views")
            print("3. Sequences")
            print("4. Users")
            print("5. Exit")
            
            choice = input("\nEnter option number: ").strip()
            
            if choice == "1":
                tables = self.get_tables()
                selected_table = self.select_object(tables, "Tables")
                if selected_table:
                    self.display_table_metadata_menu(selected_table)
            
            elif choice == "2":
                views = self.get_views()
                selected_view = self.select_object(views, "Views")
                if selected_view:
                    self.display_view_metadata_menu(selected_view)
            
            elif choice == "3":
                sequences = self.get_sequences()
                selected_sequence = self.select_object(sequences, "Sequences")
                if selected_sequence:
                    self.display_sequence_details(selected_sequence)
            
            elif choice == "4":
                users = self.get_users()
                if users:
                    print(f"\nAvailable Users:")
                    for i, user in enumerate(users, 1):
                        print(f"{i}. {user}")
                    input("\nPress Enter to continue...")
            
            elif choice == "5":
                print("\nThank you for using Oracle Metadata Explorer!")
                break
            
            else:
                print("\n✗ Invalid option. Please try again.")


def main():
    """Main entry point of the application."""
    print("="*80)
    print("Oracle Metadata Explorer")
    print("="*80)
    
    # Get database credentials
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    service_name = input("Enter service name: ").strip()
    
    # Create explorer instance and connect
    explorer = OracleMetadataExplorer()
    
    if not explorer.connect(username, password, service_name):
        print("Failed to connect to database. Exiting...")
        sys.exit(1)
    
    try:
        # Run main menu loop
        explorer.main_menu()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
    except Exception as e:
        print(f"\n✗ An error occurred: {e}")
    finally:
        explorer.disconnect()


if __name__ == "__main__":
    main()

