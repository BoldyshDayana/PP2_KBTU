import csv
import psycopg2
from connect import get_connection, init_database, close_connection


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
    """Importing contacts from a CSV file"""
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
                        print(f"Skipped: {name} - {phone} (The phone already exists)")
                        skipped += 1
                        conn.rollback()
        
        conn.commit()
        cur.close()
        print(f"\n Import completed: added {added}, skipped {skipped}")
        
    except FileNotFoundError:
        print(f"File {filename} not found!")
    except Exception as e:
        print(f"Error during import:{e}")
        conn.rollback()
    finally:
        close_connection(conn)

def insert_from_console():
    """Adding a contact via the console"""
    print("\n Adding a new contact")
    
    name = input("Name: ").strip()
    if not name:
        print("The name can't be empty!")
        return
    
    phone = input("Phone: ").strip()
    if not phone:
        print("The phone can't be empty!")
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
        print(f"Phone {phone} already exists in the database!")
        conn.rollback()
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
    finally:
        close_connection(conn)

def update_contact():
    """Updating a contact (name or phone number)"""
    print("\nUpdating a contact")
    
    search = input("Enter a name or phone number to search for: ").strip()
    if not search:
        print("Can not be empty!")
        return
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        
        #searching
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
        
        #choose contact for updating
        try:
            choice = int(input("\nSelect the contact number to update: ")) - 1
            if choice < 0 or choice >= len(contacts):
                print("ERROR!")
                cur.close()
                return
            
            contact_id = contacts[choice][0]
            current_name = contacts[choice][1]
            current_phone = contacts[choice][2]
            
            print(f"\n Current data:{current_name} - {current_phone}")
            print("\n What do you want to update?")
            print("1. only name")
            print("2. only phone")
            print("3. name and phone")
            
            option = input("Choose (1/2/3): ").strip()
            
            if option == '1':
                new_name = input("New name: ").strip()
                if new_name:
                    cur.execute(
                        "UPDATE contacts SET name = %s WHERE id = %s",
                        (new_name, contact_id)
                    )
                    print(f"Name updated: {current_name} → {new_name}")
                else:
                    print("The name can't be empty!")
                    return
                    
            elif option == '2':
                new_phone = input("New phone: ").strip()
                if new_phone:
                    try:
                        cur.execute(
                            "UPDATE contacts SET phone = %s WHERE id = %s",
                            (new_phone, contact_id)
                        )
                        print(f"The phone has been updated: {current_phone} → {new_phone}")
                    except psycopg2.IntegrityError:
                        print(f"Phone {new_phone} already exists!")
                        conn.rollback()
                        return
                else:
                    print("The phone can't be empty!")
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
                        print(f"The contact has been updated {current_name} - {current_phone} → {new_name} - {new_phone}")
                    except psycopg2.IntegrityError:
                        print(f"The {new_phone} phone already exists!")
                        conn.rollback()
                        return
                else:
                    print("The name and phone number cannot be empty!")
                    return
            else:
                print("Wrong choice!")
                return
            
            conn.commit()
            
        except ValueError:
            print("Incorrect input!")
            
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
    finally:
        cur.close()
        close_connection(conn)

def search_contacts():
    """Search for contacts with different filters"""
    print("\nContact Search")
    print("Search Options:")
    print("1. By name")
    print("2. By phone")
    print("3. By phone prefix")
    print("4. In terms of name or phone number")
    
    option = input("Choose an option (1/2/3/4): ").strip()
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        
        if option == '1':
            name = input("Enter the name (or part of it):").strip()
            cur.execute(
                "SELECT id, name, phone FROM contacts WHERE name ILIKE %s ORDER BY name",
                (f"%{name}%",)
            )
        elif option == '2':
            phone = input("Enter the phone: ").strip()
            cur.execute(
                "SELECT id, name, phone FROM contacts WHERE phone = %s",
                (phone,)
            )
        elif option == '3':
            prefix = input("Enter the prefix (for example: 8701): ").strip()
            cur.execute(
                "SELECT id, name, phone FROM contacts WHERE phone LIKE %s ORDER BY phone",
                (f"{prefix}%",)
            )
        elif option == '4':
            text = input("Enter your search query: ").strip()
            cur.execute("""
                SELECT id, name, phone FROM contacts 
                WHERE name ILIKE %s OR phone LIKE %s
                ORDER BY name
            """, (f"%{text}%", f"%{text}%"))
        else:
            print("Wrong choice!")
            return
        
        contacts = cur.fetchall()
        cur.close()
        
        if not contacts:
            print("\n no contacts found\n")
            return
        
        print("\n" + "="*55)
        print(f"{'ID':<5} {'Name':<30} {'Phone':<15}")
        print("="*55)
        for contact in contacts:
            print(f"{contact[0]:<5} {contact[1]:<30} {contact[2]:<15}")
        print("="*55)
        print(f"Found: {len(contacts)} contacts\n")
        
    except Exception as e:
        print(f"ERROR {e}")
    finally:
        close_connection(conn)

def delete_contact():
    """Deleting a contact by name or phone number"""
    print("\nDeleting a contact")
    
    search = input("Enter a name or phone number to delete: ").strip()
    if not search:
        print("The search query cannot be empty!")
        return
    
    conn = get_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        
        #searching contacts
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
        
        # show findings
        print("\nThe following contacts will be deleted:")
        print("-" * 50)
        for i, contact in enumerate(contacts, 1):
            print(f"{i}. {contact[1]} - {contact[2]}")
        
        confirm = input(f"\nDelete {len(contacts)} contacts? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
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




def main_menu():
    """Main menu of the application"""
    while True:
        print("\n" + "="*50)
        print("PHONEBOOK APPLICATION")
        print("="*50)
        print("1. Importing contacts from CSV")
        print("2. Add a contact")
        print("3. Update a contact")
        print("4. Contact Search")
        print("5. Delete a contact")
        print("6. Show all contacts")
        print("0. Exit")
        print("="*50)
        
        choice = input("Select an option: ").strip()
        
        if choice == '1':
            filename = input("Enter the name of the CSV file (for example, contacts.csv): ").strip()
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
        elif choice == '0':
            print("\nBye!")
            break
        else:
            print("Wrong choice! Try again.")



if __name__ == "__main__":
    print("\n" + "="*50)
    print("PHONEBOOK APPLICATION")
    print("="*50)
    
    #Initializing the database
    if init_database():
        main_menu()
    else:
        print(" The database could not be initialized. Check it out config.py")