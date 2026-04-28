import json
import csv
import os
from connect import get_connection, init_db
from datetime import datetime

def print_menu():
    print("\n--- PhoneBook CLI ---")
    print("1. Search Contacts (General)")
    print("2. Search by Email")
    print("3. Filter by Group")
    print("4. List All (Paginated)")
    print("5. Add Phone to Contact")
    print("6. Move Contact to Group")
    print("7. Export to JSON")
    print("8. Import from JSON")
    print("9. Import from CSV")
    print("0. Exit")

def search_contacts_ui():
    query = input("Enter search term (name, phone, or email): ")
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            results = cur.fetchall()
            display_results(results)
        conn.close()

def search_by_email_ui():
    email_query = input("Enter partial email (e.g., gmail): ")
    conn = get_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.name, c.email, c.birthday, g.name, string_agg(p.phone, ', ')
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                LEFT JOIN phones p ON c.id = p.contact_id
                WHERE c.email ILIKE %s
                GROUP BY c.id, g.name
            """, (f'%{email_query}%',))
            results = cur.fetchall()
            display_results(results)
        conn.close()

def filter_by_group_ui():
    conn = get_connection()
    if not conn: return
    with conn.cursor() as cur:
        cur.execute("SELECT name FROM groups")
        groups = [row[0] for row in cur.fetchall()]
        print(f"Available groups: {', '.join(groups)}")
        group_name = input("Enter group name to filter: ")
        
        cur.execute("""
            SELECT c.id, c.name, c.email, c.birthday, g.name, string_agg(p.phone, ', ')
            FROM contacts c
            JOIN groups g ON c.group_id = g.id
            LEFT JOIN phones p ON c.id = p.contact_id
            WHERE g.name = %s
            GROUP BY c.id, g.name
        """, (group_name,))
        results = cur.fetchall()
        display_results(results)
    conn.close()

def list_all_paginated():
    limit = 5
    offset = 0
    sort_by = "name"
    
    while True:
        conn = get_connection()
        if not conn: break
        with conn.cursor() as cur:
            # Query with pagination and sorting
            allowed_sort = {"name", "birthday", "created_at"}
            sort_key = sort_by if sort_by in allowed_sort else "name"
            query = f"""
                SELECT c.id, c.name, c.email, c.birthday, g.name, string_agg(p.phone, ', ')
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                LEFT JOIN phones p ON c.id = p.contact_id
                GROUP BY c.id, g.name
                ORDER BY {sort_key}
                LIMIT %s OFFSET %s
            """
            cur.execute(query, (limit, offset))
            results = cur.fetchall()
            display_results(results)
            print(f"\nPage starting at record {offset + 1}")
            
        conn.close()
        
        cmd = input("\n[n]ext, [p]rev, [s]ort, [q]uit: ").lower()
        if cmd == 'n':
            offset += limit
        elif cmd == 'p':
            offset = max(0, offset - limit)
        elif cmd == 's':
            sort_by = input("Sort by (name, birthday, created_at): ") or "name"
        elif cmd == 'q':
            break

def display_results(results):
    if not results:
        print("No contacts found.")
        return
    print(f"{'ID':<4} {'Name':<20} {'Email':<25} {'Birthday':<12} {'Group':<10} {'Phones'}")
    print("-" * 100)
    for row in results:
        bday = row[3].strftime('%Y-%m-%d') if row[3] else "N/A"
        print(f"{row[0]:<4} {row[1]:<20} {row[2] or 'N/A':<25} {bday:<12} {row[4] or 'N/A':<10} {row[5] or 'N/A'}")

def add_phone_ui():
    name = input("Contact name: ")
    phone = input("Phone number: ")
    p_type = input("Type (home/work/mobile): ")
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, p_type))
            conn.commit()
            print("Phone added.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn.close()

def move_to_group_ui():
    name = input("Contact name: ")
    group = input("New group name: ")
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("CALL move_to_group(%s, %s)", (name, group))
            conn.commit()
            print("Group updated.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn.close()

def export_to_json():
    conn = get_connection()
    if not conn: return
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.name, c.email, c.birthday, g.name as group_name,
                   json_agg(json_build_object('phone', p.phone, 'type', p.type)) as phones
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
            LEFT JOIN phones p ON c.id = p.contact_id
            GROUP BY c.id, g.name
        """)
        rows = cur.fetchall()
        contacts = []
        for row in rows:
            contacts.append({
                "name": row[0],
                "email": row[1],
                "birthday": str(row[2]) if row[2] else None,
                "group": row[3],
                "phones": row[4] if row[4] != [None] else []
            })
    
    with open('contacts_export.json', 'w') as f:
        json.dump(contacts, f, indent=4)
    print(f"Exported {len(contacts)} contacts to contacts_export.json")
    conn.close()

def import_from_json():
    filename = input("Enter JSON filename: ")
    if not os.path.exists(filename):
        print("File not found.")
        return
    
    with open(filename, 'r') as f:
        data = json.load(f)
        
    conn = get_connection()
    if not conn: return
    
    for item in data:
        name = item.get('name')
        email = item.get('email')
        birthday = item.get('birthday')
        group_name = item.get('group')
        phones = item.get('phones', [])
        
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
            existing = cur.fetchone()
            
            if existing:
                choice = input(f"Contact '{name}' already exists. Overwrite? (y/n): ").lower()
                if choice != 'y':
                    continue
                cur.execute("DELETE FROM contacts WHERE id = %s", (existing[0],))
            
            # Insert Group if not exists
            group_id = None
            if group_name:
                cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name RETURNING id", (group_name,))
                group_id = cur.fetchone()[0]
            
            # Insert Contact
            cur.execute("""
                INSERT INTO contacts (name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (name, email, birthday, group_id))
            contact_id = cur.fetchone()[0]
            
            # Insert Phones
            for p in phones:
                if p and p.get('phone'):
                    cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                                (contact_id, p['phone'], p.get('type', 'mobile')))
        conn.commit()
    print("Import complete.")
    conn.close()

def import_from_csv():
    # Expecting CSV: name,email,birthday,group,phone,phone_type
    filename = input("Enter CSV filename: ")
    if not os.path.exists(filename):
        print("File not found.")
        return
    
    conn = get_connection()
    if not conn: return
    
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['name']
            email = row.get('email')
            birthday = row.get('birthday')
            group_name = row.get('group')
            phone = row.get('phone')
            p_type = row.get('phone_type', 'mobile')
            
            with conn.cursor() as cur:
                # Get or create group
                group_id = None
                if group_name:
                    cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name RETURNING id", (group_name,))
                    group_id = cur.fetchone()[0]
                
                # Check if contact exists
                cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
                existing = cur.fetchone()
                
                if existing:
                    contact_id = existing[0]
                    # Update other fields if provided
                    if email or birthday or group_id:
                        cur.execute("UPDATE contacts SET email=COALESCE(%s, email), birthday=COALESCE(%s, birthday), group_id=COALESCE(%s, group_id) WHERE id=%s",
                                    (email, birthday, group_id, contact_id))
                else:
                    cur.execute("INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s, %s, %s, %s) RETURNING id",
                                (name, email, birthday, group_id))
                    contact_id = cur.fetchone()[0]
                
                if phone:
                    cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)", (contact_id, phone, p_type))
        conn.commit()
    print("CSV Import complete.")
    conn.close()

def main():
    init_db()
    while True:
        print_menu()
        choice = input("Select an option: ")
        if choice == '1': search_contacts_ui()
        elif choice == '2': search_by_email_ui()
        elif choice == '3': filter_by_group_ui()
        elif choice == '4': list_all_paginated()
        elif choice == '5': add_phone_ui()
        elif choice == '6': move_to_group_ui()
        elif choice == '7': export_to_json()
        elif choice == '8': import_from_json()
        elif choice == '9': import_from_csv()
        elif choice == '0': break
        else: print("Invalid choice.")

if __name__ == "__main__":
    main()
