
import psycopg2
import csv
from connect import get_connection, init_database, close_connection



def execute_sql_file(filename):
    """Execute SQL file"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        cur = conn.cursor()
        cur.execute(sql_content)
        conn.commit()
        cur.close()
        print(f"Executed: {filename}")
        return True
        
    except Exception as e:
        print(f"Error executing {filename}: {e}")
        conn.rollback()
        return False
    finally:
        close_connection(conn)

def init_advanced_features():
    """Initialize stored functions and procedures"""
    print("\n--- Initializing advanced features ---")
    execute_sql_file('functions.sql')
    execute_sql_file('procedures.sql')
    print("Advanced features initialized")

#NEW FUNCTIONS
# ==================== NEW FUNCTIONS ====================

def search_by_pattern():
    """1. Search contacts by pattern (uses stored function)"""
    print("\n--- Search by Pattern ---")
    pattern = input("Enter search pattern (part of name or phone): ").strip()
    
    if not pattern:
        print("Pattern cannot be empty!")
        return
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM search_contacts_pattern(%s)", (pattern,))
        results = cur.fetchall()
        cur.close()
        
        if not results:
            print("\nNo contacts found\n")
            return
        
        print("\n" + "="*65)
        print(f"{'ID':<5} {'Name':<30} {'Phone':<15} {'Created':<20}")
        print("="*65)
        for contact in results:
            print(f"{contact[0]:<5} {contact[1]:<30} {contact[2]:<15} {str(contact[3])[:19]:<20}")
        print("="*65)
        print(f"Found: {len(results)} contacts\n")
        
    except Exception as e:
        print(f"Search error: {e}")
    finally:
        close_connection(conn)

def insert_or_update():
    """2. Insert or update contact (stored procedure)"""
    print("\n--- Insert or Update Contact ---")
    
    name = input("Name: ").strip()
    if not name:
        print("Name cannot be empty!")
        return
    
    phone = input("Phone: ").strip()
    if not phone:
        print("Phone cannot be empty!")
        return
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        cur.execute("CALL insert_or_update_contact(%s, %s)", (name, phone))
        conn.commit()
        cur.close()
        print(f"Contact '{name}' - {phone} processed successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        close_connection(conn)

def insert_many_contacts():
    """3. Insert many contacts with validation (stored procedure)"""
    print("\n--- Insert Many Contacts ---")
    print("Enter contacts in format: name,phone")
    print("Type 'done' when finished")
    
    contacts_list = []
    
    while True:
        entry = input("Contact: ").strip()
        if entry.lower() == 'done':
            break
        if entry:
            contacts_list.append(entry)
    
    if not contacts_list:
        print("No contacts entered!")
        return
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        cur.execute("CALL insert_many_contacts(%s)", (contacts_list,))
        conn.commit()
        cur.close()
        print("Batch processing completed")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        close_connection(conn)

def show_paginated():
    """4. Paginated contacts (stored function)"""
    print("\n--- Paginated Contacts ---")
    
    try:
        page_size = int(input("Number of contacts per page: ").strip())
        if page_size <= 0:
            print("Page size must be positive!")
            return
    except ValueError:
        print("Invalid page size!")
        return
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        
        page = 1
        while True:
            offset = (page - 1) * page_size
            
            cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (page_size, offset))
            results = cur.fetchall()
            
            if not results:
                if page == 1:
                    print("\nNo contacts found")
                else:
                    print("\nNo more pages")
                break
            
            total = results[0][4] if results else 0
            
            print(f"\n{'='*60}")
            print(f"Page {page} (Showing {len(results)} of {total} contacts)")
            print(f"{'ID':<5} {'Name':<30} {'Phone':<15}")
            print('='*60)
            for contact in results:
                print(f"{contact[0]:<5} {contact[1]:<30} {contact[2]:<15}")
            print('='*60)
            
            if offset + page_size >= total:
                print("End of contacts")
                break
            
            next_page = input("\nNext page? (y/n): ").strip().lower()
            if next_page != 'y':
                break
            
            page += 1
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        close_connection(conn)

def delete_by_identifier():
    """5. Delete contact by name or phone (stored procedure)"""
    print("\n--- Delete Contact by Name or Phone ---")
    
    identifier = input("Enter name or phone to delete: ").strip()
    if not identifier:
        print("Identifier cannot be empty!")
        return
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        cur.execute("CALL delete_contact_by_name_or_phone(%s)", (identifier,))
        conn.commit()
        cur.close()
        print(f"Deletion processed for: {identifier}")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        close_connection(conn)

#REMAINING FUNCTIONS FROM PRACTICE7

def show_all_contacts():
    """Show all contacts"""
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, phone FROM contacts ORDER BY name")
        contacts = cur.fetchall()
        cur.close()
        
        if not contacts:
            print("\nThe contact list is empty\n")
            return
        
        print("\n" + "="*55)
        print(f"{'ID':<5} {'Name':<30} {'Phone':<15}")
        print("="*55)
        for contact in contacts:
            print(f"{contact[0]:<5} {contact[1]:<30} {contact[2]:<15}")
        print("="*55)
        print(f"Total: {len(contacts)} contacts\n")
        
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        close_connection(conn)

def insert_from_csv(filename):
    """Import contacts from CSV file"""
    import os
    
    if not os.path.exists(filename):
        print(f"File '{filename}' not found!")
        return
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        added = 0
        skipped = 0
        
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            
            for row in reader:
                if len(row) >= 2:
                    name = row[0].strip()
                    phone = row[1].strip()
                    
                    if not name or not phone:
                        skipped += 1
                        continue
                    
                    try:
                        cur.execute(
                            "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
                            (name, phone)
                        )
                        added += 1
                        print(f"Added: {name} - {phone}")
                    except psycopg2.IntegrityError:
                        print(f"Skipped: {name} - {phone} (phone already exists)")
                        skipped += 1
                        conn.rollback()
        
        conn.commit()
        cur.close()
        print(f"\nImport completed: added {added}, skipped {skipped}")
        
    except Exception as e:
        print(f"Error during import: {e}")
        conn.rollback()
    finally:
        close_connection(conn)

def insert_from_console():
    """Add contact from console"""
    print("\n--- Add New Contact ---")
    
    name = input("Name: ").strip()
    if not name:
        print("Name cannot be empty!")
        return
    
    phone = input("Phone: ").strip()
    if not phone:
        print("Phone cannot be empty!")
        return
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
            (name, phone)
        )
        conn.commit()
        cur.close()
        print(f"Contact '{name}' successfully added!")
        
    except psycopg2.IntegrityError:
        print(f"Phone {phone} already exists!")
        conn.rollback()
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
    finally:
        close_connection(conn)

def update_contact():
    """Update contact"""
    print("\n--- Update Contact ---")
    
    search = input("Enter name or phone to search: ").strip()
    if not search:
        print("Search query cannot be empty!")
        return
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, name, phone FROM contacts 
            WHERE name ILIKE %s OR phone LIKE %s
            ORDER BY name
        """, (f"%{search}%", f"%{search}%"))
        
        contacts = cur.fetchall()
        
        if not contacts:
            print("No contacts found")
            cur.close()
            return
        
        print("\nFound contacts:")
        print("-" * 50)
        for i, contact in enumerate(contacts, 1):
            print(f"{i}. ID: {contact[0]} | {contact[1]} - {contact[2]}")
        
        try:
            choice = int(input("\nSelect contact number to update: ")) - 1
            if choice < 0 or choice >= len(contacts):
                print("Invalid choice!")
                cur.close()
                return
            
            contact_id = contacts[choice][0]
            current_name = contacts[choice][1]
            current_phone = contacts[choice][2]
            
            print(f"\nCurrent data: {current_name} - {current_phone}")
            print("What to update?")
            print("1. Only name")
            print("2. Only phone")
            print("3. Both")
            
            option = input("Choose (1/2/3): ").strip()
            
            if option == '1':
                new_name = input("New name: ").strip()
                if new_name:
                    cur.execute(
                        "UPDATE contacts SET name = %s WHERE id = %s",
                        (new_name, contact_id)
                    )
                    print(f"Name updated: {current_name} -> {new_name}")
            elif option == '2':
                new_phone = input("New phone: ").strip()
                if new_phone:
                    try:
                        cur.execute(
                            "UPDATE contacts SET phone = %s WHERE id = %s",
                            (new_phone, contact_id)
                        )
                        print(f"Phone updated: {current_phone} -> {new_phone}")
                    except psycopg2.IntegrityError:
                        print(f"Phone {new_phone} already exists!")
                        conn.rollback()
                        return
            elif option == '3':
                new_name = input("New name: ").strip()
                new_phone = input("New phone: ").strip()
                if new_name and new_phone:
                    try:
                        cur.execute(
                            "UPDATE contacts SET name = %s, phone = %s WHERE id = %s",
                            (new_name, new_phone, contact_id)
                        )
                        print(f"Contact updated: {current_name} - {current_phone} -> {new_name} - {new_phone}")
                    except psycopg2.IntegrityError:
                        print(f"Phone {new_phone} already exists!")
                        conn.rollback()
                        return
            else:
                print("Invalid option!")
                return
            
            conn.commit()
            
        except ValueError:
            print("Invalid input!")
            
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
    finally:
        cur.close()
        close_connection(conn)

def search_contacts():
    """Search contacts"""
    print("\n--- Contact Search ---")
    print("Search options:")
    print("1. By name (partial match)")
    print("2. By phone (exact match)")
    print("3. By phone prefix")
    print("4. By name or phone (partial match)")
    
    option = input("Choose (1/2/3/4): ").strip()
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        
        if option == '1':
            name = input("Enter name (or part): ").strip()
            cur.execute(
                "SELECT id, name, phone FROM contacts WHERE name ILIKE %s ORDER BY name",
                (f"%{name}%",)
            )
        elif option == '2':
            phone = input("Enter phone: ").strip()
            cur.execute(
                "SELECT id, name, phone FROM contacts WHERE phone = %s",
                (phone,)
            )
        elif option == '3':
            prefix = input("Enter prefix (e.g., 8701): ").strip()
            cur.execute(
                "SELECT id, name, phone FROM contacts WHERE phone LIKE %s ORDER BY phone",
                (f"{prefix}%",)
            )
        elif option == '4':
            text = input("Enter search query: ").strip()
            cur.execute("""
                SELECT id, name, phone FROM contacts 
                WHERE name ILIKE %s OR phone LIKE %s
                ORDER BY name
            """, (f"%{text}%", f"%{text}%"))
        else:
            print("Invalid option!")
            return
        
        contacts = cur.fetchall()
        cur.close()
        
        if not contacts:
            print("\nNo contacts found\n")
            return
        
        print("\n" + "="*55)
        print(f"{'ID':<5} {'Name':<30} {'Phone':<15}")
        print("="*55)
        for contact in contacts:
            print(f"{contact[0]:<5} {contact[1]:<30} {contact[2]:<15}")
        print("="*55)
        print(f"Found: {len(contacts)} contacts\n")
        
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        close_connection(conn)

def delete_contact():
    """Delete contact"""
    print("\n--- Delete Contact ---")
    
    search = input("Enter name or phone to delete: ").strip()
    if not search:
        print("Search query cannot be empty!")
        return
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, name, phone FROM contacts 
            WHERE name ILIKE %s OR phone LIKE %s
            ORDER BY name
        """, (f"%{search}%", f"%{search}%"))
        
        contacts = cur.fetchall()
        
        if not contacts:
            print("No contacts found")
            cur.close()
            return
        
        print("\nContacts to delete:")
        print("-" * 50)
        for i, contact in enumerate(contacts, 1):
            print(f"{i}. {contact[1]} - {contact[2]}")
        
        confirm = input(f"\nDelete {len(contacts)} contact(s)? (y/n): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            deleted = 0
            for contact in contacts:
                cur.execute("DELETE FROM contacts WHERE id = %s", (contact[0],))
                deleted += 1
            conn.commit()
            print(f"Deleted {deleted} contact(s)")
        else:
            print("Deletion cancelled")
            
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
    finally:
        cur.close()
        close_connection(conn)

#MAIN MENU

def main_menu():
    """Main menu of the application"""
    while True:
        print("\n" + "="*50)
        print("PHONEBOOK APPLICATION (Practice 8)")
        print("="*50)
        print("BASIC OPERATIONS:")
        print("1. Import contacts from CSV")
        print("2. Add contact (console)")
        print("3. Update contact")
        print("4. Search contacts")
        print("5. Delete contact")
        print("6. Show all contacts")
        print("-" * 50)
        print("ADVANCED OPERATIONS (Stored Functions/Procedures):")
        print("7. Search by pattern (FUNCTION)")
        print("8. Insert or update contact (PROCEDURE)")
        print("9. Insert many contacts with validation (PROCEDURE)")
        print("10. Paginated contacts (FUNCTION)")
        print("11. Delete by name/phone (PROCEDURE)")
        print("-" * 50)
        print("0. Exit")
        print("="*50)
        
        choice = input("Select option: ").strip()
        
        if choice == '1':
            filename = input("CSV filename (e.g., contacts.csv): ").strip()
            insert_from_csv(filename)
        elif choice == '2':
            insert_from_console()
        elif choice == '3':
            update_contact()
        elif choice == '4':
            search_contacts()
        elif choice == '5':
            delete_contact()
        elif choice == '6':
            show_all_contacts()
        elif choice == '7':
            search_by_pattern()
        elif choice == '8':
            insert_or_update()
        elif choice == '9':
            insert_many_contacts()
        elif choice == '10':
            show_paginated()
        elif choice == '11':
            delete_by_identifier()
        elif choice == '0':
            print("\nGoodbye!")
            break
        else:
            print("Invalid option! Try again.")

# MAIN ENTRY POINT
if __name__ == "__main__":
    print("\n" + "="*50)
    print("PHONEBOOK APPLICATION")
    print("="*50)
    
    # Initialize database
    if init_database():
        # Initialize stored functions and procedures
        init_advanced_features()
        main_menu()
    else:
        print("Database could not be initialized. Check config.py")