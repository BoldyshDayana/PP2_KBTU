import psycopg2
import csv
import json
import os
from datetime import date, datetime
from connect import get_connection, init_database, close_connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _resolve_path(filename: str) -> str:
    if os.path.isabs(filename):
        return filename
    if os.path.exists(filename):
        return filename
    return os.path.join(BASE_DIR, filename)



# Helpers

def _json_serial(obj):
    """JSON serializer for date/datetime objects."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def _print_contacts(rows, columns):
    """Generic pretty-printer for contact rows."""
    if not rows:
        print("\n(no contacts found)\n")
        return
    col_w = 18
    header = "  ".join(f"{c:<{col_w}}" for c in columns)
    sep = "-" * len(header)
    print(f"\n{sep}")
    print(header)
    print(sep)
    for row in rows:
        line = "  ".join(f"{str(v or ''):<{col_w}}" for v in row)
        print(line)
    print(sep)
    print(f"  {len(rows)} row(s)\n")



# Initialisation


def execute_sql_file(filename: str) -> bool:
    """Execute a multi-statement .sql file against the database."""
    conn = get_connection()
    if not conn:
        return False
    try:
        filename = _resolve_path(filename)
        with open(filename, "r", encoding="utf-8") as f:
            sql = f.read()
        cur = conn.cursor()
        # Use autocommit-safe execution for DDL files with multiple statements
        old_isolation = conn.isolation_level
        conn.set_isolation_level(0)          # autocommit for DDL
        cur.execute(sql)
        conn.set_isolation_level(old_isolation)
        cur.close()
        print(f"Executed: {filename}")
        return True
    except Exception as e:
        print(f"Error executing {filename}: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        return False
    finally:
        close_connection(conn)


def init_all():
    """Initialise DB schema, stored functions and procedures."""
    print("\n--- Initialising database ---")
    init_database()  #creates base contacts table
    # schema.sql MUST run first (creates groups + phones tables)
    for f in ("schema.sql", "functions.sql", "procedures.sql"):
        path = _resolve_path(f)
        if os.path.exists(path):
            execute_sql_file(path)
        else:
            print(f"{f} not found – skipping")
    print("Initialisation complete.\n")



# Extended schema helpers


def _get_groups(cur):
    cur.execute("SELECT id, name FROM groups ORDER BY name")
    return cur.fetchall()


def _pick_group(cur) -> int | None:
    groups = _get_groups(cur)
    print("\n  Groups:")
    for g in groups:
        print(f"    {g[0]}. {g[1]}")
    print("(leave blank to skip)")
    raw = input("  Select group number: ").strip()
    if not raw:
        return None
    try:
        gid = int(raw)
        if any(g[0] == gid for g in groups):
            return gid
    except ValueError:
        pass
    print("  Invalid group – skipping.")
    return None


# Advanced Console Search & Filter


def filter_by_group():
    """Show contacts belonging to a chosen group, with sort."""
    print("\n--- Filter by Group ---")
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        groups = _get_groups(cur)
        if not groups:
            print("No groups found.")
            return
        print("\n  Available groups:")
        for g in groups:
            print(f"    {g[0]}. {g[1]}")
        raw = input("  Select group number: ").strip()
        try:
            gid = int(raw)
        except ValueError:
            print("Invalid input.")
            return

        sort_col = _ask_sort()
        cur.execute(f"""
            SELECT c.id, c.name, c.email, c.birthday, g.name AS grp, c.created_at
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            WHERE c.group_id = %s
            ORDER BY {sort_col}
        """, (gid,))
        rows = cur.fetchall()
        _print_contacts(rows, ["ID", "Name", "Email", "Birthday", "Group", "Created"])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        close_connection(conn)


def search_by_email():
    """Partial-match search by email."""
    print("\n--- Search by Email ---")
    query = input("  Email fragment (e.g. gmail): ").strip()
    if not query:
        print("Query cannot be empty.")
        return

    sort_col = _ask_sort()
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT c.id, c.name, c.email, c.birthday, g.name AS grp, c.created_at
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            WHERE c.email ILIKE %s
            ORDER BY {sort_col}
        """, (f"%{query}%",))
        rows = cur.fetchall()
        _print_contacts(rows, ["ID", "Name", "Email", "Birthday", "Group", "Created"])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        close_connection(conn)


def _ask_sort() -> str:
    """Ask user to choose a sort column; returns safe SQL fragment."""
    print("  Sort by:")
    print("    1. Name (default)")
    print("    2. Birthday")
    print("    3. Date added")
    choice = input("  Choose (1/2/3): ").strip()
    ALLOWED = {
        "1": "c.name",
        "2": "c.birthday NULLS LAST",
        "3": "c.created_at",
    }
    return ALLOWED.get(choice, "c.name")


def search_all_fields():
    """Extended search: name, email, all phone numbers (calls DB function)."""
    print("\n--- Extended Search (name / email / phones) ---")
    query = input("  Search query: ").strip()
    if not query:
        print("Query cannot be empty.")
        return

    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM search_contacts(%s)", (query,))
        rows = cur.fetchall()
        _print_contacts(rows, ["ID", "Name", "Email", "Birthday", "Group", "Phone", "Type", "Created"])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        close_connection(conn)



# Paginated navigation  (uses existing DB function)


def browse_paginated():
    """Navigate pages with next / prev / quit."""
    print("\n--- Browse Contacts (paginated) ---")
    try:
        page_size = int(input("  Contacts per page [10]: ").strip() or "10")
        if page_size <= 0:
            page_size = 10
    except ValueError:
        page_size = 10

    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        page = 1
        while True:
            offset = (page - 1) * page_size
            cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (page_size, offset))
            rows = cur.fetchall()

            if not rows:
                print("  No contacts." if page == 1 else "  No more pages.")
                break

            total = rows[0][4]
            total_pages = (total + page_size - 1) // page_size

            print(f"\n  Page {page}/{total_pages}  ({total} total contacts)")
            _print_contacts(
                [(r[0], r[1], r[2], str(r[3])[:10]) for r in rows],
                ["ID", "Name", "Phone", "Created"],
            )

            at_last = offset + page_size >= total
            prompt_parts = []
            if page > 1:
                prompt_parts.append("prev")
            if not at_last:
                prompt_parts.append("next")
            prompt_parts.append("quit")
            cmd = input(f"  [{' / '.join(prompt_parts)}]: ").strip().lower()

            if cmd == "next" and not at_last:
                page += 1
            elif cmd == "prev" and page > 1:
                page -= 1
            elif cmd == "quit":
                break
            else:
                print("  Invalid command.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        close_connection(conn)



# JSON Export / Import

def export_to_json():
    """Export all contacts (with phones and group) to a JSON file."""
    print("\n--- Export to JSON ---")
    filename = _resolve_path(input("  Output filename [contacts.json]: ").strip() or "contacts.json")

    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()

        # Fetch contacts
        cur.execute("""
            SELECT c.id, c.name, c.email, c.birthday, g.name AS grp, c.created_at
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            ORDER BY c.name
        """)
        contact_rows = cur.fetchall()

        # Fetch phones per contact
        cur.execute("SELECT contact_id, phone, type FROM phones ORDER BY contact_id")
        phone_rows = cur.fetchall()

        phones_map: dict[int, list] = {}
        for cid, phone, ptype in phone_rows:
            phones_map.setdefault(cid, []).append({"phone": phone, "type": ptype})

        data = []
        for cid, name, email, birthday, grp, created_at in contact_rows:
            data.append({
                "id": cid,
                "name": name,
                "email": email,
                "birthday": birthday,
                "group": grp,
                "phones": phones_map.get(cid, []),
                "created_at": created_at,
            })

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=_json_serial)

        print(f"Exported {len(data)} contacts to '{filename}'")
    except Exception as e:
        print(f"Export error: {e}")
    finally:
        close_connection(conn)


def import_from_json():
    """Import contacts from a JSON file; ask skip/overwrite on duplicates."""
    print("\n--- Import from JSON ---")
    filename = _resolve_path(input("  JSON filename [contacts.json]: ").strip() or "contacts.json")

    if not os.path.exists(filename):
        print(f"  File '{filename}' not found.")
        return

    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("  Invalid JSON format – expected a list of contacts.")
        return

    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        inserted = updated = skipped = 0

        for entry in data:
            name = (entry.get("name") or "").strip()
            if not name:
                print("  Skipping entry with no name.")
                skipped += 1
                continue

            email    = entry.get("email")
            birthday = entry.get("birthday")  # string or None
            grp_name = entry.get("group")
            phones   = entry.get("phones", [])

            # Resolve group
            group_id = None
            if grp_name:
                cur.execute("SELECT id FROM groups WHERE name ILIKE %s LIMIT 1", (grp_name,))
                row = cur.fetchone()
                if row:
                    group_id = row[0]
                else:
                    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (grp_name,))
                    group_id = cur.fetchone()[0]

            # Check duplicate
            cur.execute("SELECT id FROM contacts WHERE name ILIKE %s LIMIT 1", (name,))
            existing = cur.fetchone()

            if existing:
                contact_id = existing[0]
                print(f"\n  Contact '{name}' already exists.")
                action = input("    [s]kip / [o]verwrite? ").strip().lower()
                if action != "o":
                    skipped += 1
                    continue
                # Overwrite
                cur.execute("""
                    UPDATE contacts
                    SET email=%s, birthday=%s, group_id=%s
                    WHERE id=%s
                """, (email, birthday, group_id, contact_id))
                # Replace phones
                cur.execute("DELETE FROM phones WHERE contact_id=%s", (contact_id,))
                updated += 1
            else:
                cur.execute("""
                    INSERT INTO contacts (name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s) RETURNING id
                """, (name, email, birthday, group_id))
                contact_id = cur.fetchone()[0]
                inserted += 1

            # Insert phones
            for ph in phones:
                phone_val = (ph.get("phone") or "").strip()
                phone_type = ph.get("type", "mobile")
                if phone_val:
                    cur.execute("""
                        INSERT INTO phones (contact_id, phone, type)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (contact_id, phone_val, phone_type))

        conn.commit()
        print(f"\n  ✔  Done – inserted: {inserted}, updated: {updated}, skipped: {skipped}")
    except Exception as e:
        print(f"  ✗  Import error: {e}")
        conn.rollback()
    finally:
        close_connection(conn)



# Extended CSV import


def insert_from_csv_extended():
    """
    Import contacts from CSV with extended fields.
    """
    print("\n--- Extended CSV Import ---")
    filename = _resolve_path(input("  CSV filename [contacts.csv]: ").strip() or "contacts.csv")

    if not os.path.exists(filename):
        print(f"  File '{filename}' not found.")
        return

    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()

        # Создаём таблицы если ещё не существуют
        cur.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL
            )
        """)
        cur.execute("""
            INSERT INTO groups (name) VALUES
                ('Family'), ('Work'), ('Friend'), ('Other')
            ON CONFLICT (name) DO NOTHING
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS phones (
                id SERIAL PRIMARY KEY,
                contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
                phone VARCHAR(20) NOT NULL,
                type VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile')) DEFAULT 'mobile'
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_phones_contact_id ON phones(contact_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_phones_phone ON phones(phone)")
        conn.commit()

        inserted = skipped = 0

        with open(filename, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = (row.get("name") or "").strip()
                phone = (row.get("phone") or "").strip()
                phone_type = (row.get("phone_type") or "mobile").strip().lower()
                email = (row.get("email") or "").strip() or None
                birthday = (row.get("birthday") or "").strip() or None
                grp_name = (row.get("group") or "").strip() or None

                if not name:
                    print(f"Skipping row (no name): {dict(row)}")
                    skipped += 1
                    continue

                if phone_type not in ("home", "work", "mobile"):
                    phone_type = "mobile"

                # Resolve group
                group_id = None
                if grp_name:
                    cur.execute(
                        "SELECT id FROM groups WHERE name ILIKE %s LIMIT 1",
                        (grp_name,)
                    )
                    g_row = cur.fetchone()
                    if g_row:
                        group_id = g_row[0]
                    else:
                        cur.execute(
                            "INSERT INTO groups (name) VALUES (%s) RETURNING id",
                            (grp_name,)
                        )
                        group_id = cur.fetchone()[0]

                # Upsert contact
                cur.execute(
                    "SELECT id FROM contacts WHERE name ILIKE %s LIMIT 1",
                    (name,)
                )
                existing = cur.fetchone()
                if existing:
                    contact_id = existing[0]
                    cur.execute("""
                        UPDATE contacts
                        SET email=%s, birthday=%s, group_id=%s
                        WHERE id=%s
                    """, (email, birthday, group_id, contact_id))
                    # Удаляем старые телефоны чтобы заменить на новые из CSV
                    if phone:
                        cur.execute("DELETE FROM phones WHERE contact_id=%s", (contact_id,))
                else:
                    cur.execute("""
                        INSERT INTO contacts (name, email, birthday, group_id)
                        VALUES (%s, %s, %s, %s) RETURNING id
                    """, (name, email, birthday, group_id))
                    contact_id = cur.fetchone()[0]
                    inserted += 1

                # Add phone if present
                if phone:
                    cur.execute("""
                        INSERT INTO phones (contact_id, phone, type)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING
                    """, (contact_id, phone, phone_type))

        conn.commit()
        print(f" Done – inserted: {inserted}, skipped/updated: {skipped}")
    except Exception as e:
        print(f" CSV import error: {e}")
        conn.rollback()
    finally:
        close_connection(conn)



# New stored procedure wrappers


def add_phone_to_contact():
    """Call add_phone procedure to add a phone number to a contact."""
    print("\n--- Add Phone to Contact ---")
    name = input("  Contact name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    phone = input("  Phone number: ").strip()
    if not phone:
        print("Phone cannot be empty.")
        return
    print("  Phone type: 1. mobile (default)  2. home  3. work")
    t = input("  Choose: ").strip()
    phone_type = {"2": "home", "3": "work"}.get(t, "mobile")

    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, phone_type))
        conn.commit()
        print(f"Phone added.")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        close_connection(conn)


def move_contact_to_group():
    """Call move_to_group procedure."""
    print("\n--- Move Contact to Group ---")
    name = input("  Contact name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    grp = input("Group name (existing or new): ").strip()
    if not grp:
        print("Group name cannot be empty.")
        return

    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("CALL move_to_group(%s, %s)", (name, grp))
        conn.commit()
        print("Contact moved.")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        close_connection(conn)



# Legacy Practice 7 / 8 functions (unchanged, kept for menu)

def show_all_contacts():
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        # Check if extended schema exists before joining groups
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = 'groups'
            )
        """)
        has_groups = cur.fetchone()[0]

        if has_groups:
            cur.execute("""
                SELECT c.id, c.name, c.email, c.birthday, g.name AS grp, c.created_at
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                ORDER BY c.name
            """)
            rows = cur.fetchall()
            _print_contacts(rows, ["ID", "Name", "Email", "Birthday", "Group", "Created"])
        else:
            print("\n  Extended schema not applied yet – run schema.sql first.")
            cur.execute("SELECT id, name, phone FROM contacts ORDER BY name")
            rows = cur.fetchall()
            _print_contacts(rows, ["ID", "Name", "Phone"])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        close_connection(conn)


def insert_from_console():
    """Add a single contact with all extended fields."""
    print("\n--- Add Contact ---")
    name = input("  Name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    email    = input("  Email (optional): ").strip() or None
    birthday = input("  Birthday YYYY-MM-DD (optional): ").strip() or None

    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        group_id = _pick_group(cur)

        cur.execute("""
            INSERT INTO contacts (name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (name, email, birthday, group_id))
        contact_id = cur.fetchone()[0]

        # Phones
        while True:
            ph = input("  Add phone (leave blank to finish): ").strip()
            if not ph:
                break
            print("  Type: 1. mobile  2. home  3. work")
            t = input("  Choose: ").strip()
            ptype = {"2": "home", "3": "work"}.get(t, "mobile")
            cur.execute(
                "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                (contact_id, ph, ptype)
            )

        conn.commit()
        print(f"  ✔  Contact '{name}' added (ID {contact_id}).")
    except Exception as e:
        print(f"  ✗  Error: {e}")
        conn.rollback()
    finally:
        close_connection(conn)


def search_by_pattern():
    """Pattern search (Practice 8 stored function – name/phone in contacts.phone)."""
    print("\n--- Search by Pattern ---")
    pattern = input("  Pattern: ").strip()
    if not pattern:
        return
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM search_contacts_pattern(%s)", (pattern,))
        rows = cur.fetchall()
        _print_contacts(rows, ["ID", "Name", "Phone", "Created"])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        close_connection(conn)


def insert_or_update():
    """Upsert via Practice 8 procedure."""
    print("\n--- Upsert Contact ---")
    name  = input("  Name: ").strip()
    phone = input("  Phone: ").strip()
    if not name or not phone:
        print("Both fields required.")
        return
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("CALL insert_or_update_contact(%s, %s)", (name, phone))
        conn.commit()
        print("Processed.")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        close_connection(conn)


def insert_many_contacts():
    """Bulk insert via Practice 8 procedure."""
    print("\n--- Bulk Insert ---")
    print("  Enter contacts as  name,phone  – type 'done' to finish")
    contacts_list = []
    while True:
        entry = input("  Contact: ").strip()
        if entry.lower() == "done":
            break
        if entry:
            contacts_list.append(entry)
    if not contacts_list:
        print("No contacts entered.")
        return
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("CALL insert_many_contacts(%s)", (contacts_list,))
        conn.commit()
        print("Batch done.")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        close_connection(conn)


def delete_by_identifier():
    """Delete via Practice 8 procedure."""
    print("\n--- Delete by Name/Phone---")
    identifier = input("  Name or phone: ").strip()
    if not identifier:
        return
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute("CALL delete_contact_by_name_or_phone(%s)", (identifier,))
        conn.commit()
        print("Deletion processed.")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        close_connection(conn)



# Main Menu


def main_menu():
    while True:
        print("\n" + "=" * 60)
        print("  PHONEBOOK  –  Practice 9")
        print("=" * 60)
        print("  BASIC")
        print("    1.  Show all contacts")
        print("    2.  Add contact (console)")
        print("  SEARCH & FILTER")
        print("    3.  Extended search  (name / email / phones)")
        print("    4.  Filter by group ")
        print("    5.  Search by email ")
        print("    6.  Browse paginated  (next/prev/quit)")
        print("  IMPORT / EXPORT")
        print("    7.  Extended CSV import  (email, birthday…) ")
        print("    8.  Export to JSON  ")
        print("    9.  Import from JSON")
        print("  STORED PROCEDURES  (new)")
        print("   10.  Add phone to contact ")
        print("   11.  Move contact to group  (move_to_group)")
        print("  PRACTICE 7 / 8  (unchanged)")
        print("   20.  Pattern search (function)")
        print("   21.  Upsert contact (procedure)")
        print("   22.  Bulk insert  (procedure)")
        print("   23.  Delete by name/phone (procedure)")
        print("  ─────────────────────────────────────────────")
        print("    0.  Exit")
        print("=" * 60)

        choice = input("  Select: ").strip()

        if   choice == "1":  show_all_contacts()
        elif choice == "2":  insert_from_console()
        elif choice == "3":  search_all_fields()
        elif choice == "4":  filter_by_group()
        elif choice == "5":  search_by_email()
        elif choice == "6":  browse_paginated()
        elif choice == "7":  insert_from_csv_extended()
        elif choice == "8":  export_to_json()
        elif choice == "9":  import_from_json()
        elif choice == "10": add_phone_to_contact()
        elif choice == "11": move_contact_to_group()
        elif choice == "20": search_by_pattern()
        elif choice == "21": insert_or_update()
        elif choice == "22": insert_many_contacts()
        elif choice == "23": delete_by_identifier()
        elif choice == "0":
            print("\nGoodbye!\n")
            break
        else:
            print("Invalid option – try again.")



# Entry point

if __name__ == "__main__":
    init_all()
    main_menu()