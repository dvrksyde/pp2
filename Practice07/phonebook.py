import csv
from config import *
from connect import connect

def create_table():
    conn = connect()
    if conn is None:
        return

    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT exists phonebook (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            phone VARCHAR(20) UNIQUE NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("Table created successfull.")

def insert_from_console():
    first_name = input("Enter name: ")
    phone = input("Enter phone: ")

    conn = connect()
    if conn is None:
        return

    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO phonebook (first_name, phone)
            VALUES (%s, %s)
        """, (first_name, phone))
        conn.commit()
        print("Contact added successfully.")
    except Exception as e:
        print("Insert error:", e)
    cur.close()
    conn.close()

def insert_from_csv(filename="contacts.csv"):
    conn = connect()
    if conn is None:
        return

    cur = conn.cursor()

    try:
        with open(filename, mode="r") as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    cur.execute("""
                        INSERT INTO phonebook (first_name, phone)
                        VALUES (%s, %s)
                        ON CONFLICT (phone) DO NOTHING
                    """, (row["first_name"], row["phone"]))
                except Exception as e:
                    print(f"Error inserting row {row}: {e}")

        conn.commit()
        print("CSV data inserted successfully.")
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
    finally:
        cur.close()
        conn.close()

def show_all_contacts():
    conn = connect()
    if conn is None:
        return

    cur = conn.cursor()
    cur.execute("SELECT id, first_name, phone FROM phonebook ORDER BY id;")
    rows = cur.fetchall()

    print("\n--- Contact List ---")
    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]}, Phone: {row[2]}")

    cur.close()
    conn.close()

def search_by_name():
    name = input("Enter name to search: ")

    conn = connect()
    if conn is None:
        return

    cur = conn.cursor()
    cur.execute("""
        SELECT id, first_name, phone
        FROM phonebook
        WHERE first_name ILIKE %s
    """, (f"%{name}%",))

    rows = cur.fetchall()

    print("\n--- Search Results ---")
    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]}, Phone: {row[2]}")

    cur.close()
    conn.close()

def search_by_phone_prefix():
    prefix = input("Enter phone prefix (example: 701): ")

    conn = connect()
    if conn is None:
        return

    cur = conn.cursor()
    cur.execute("""
        SELECT id, first_name, phone
        FROM phonebook
        WHERE phone LIKE %s
    """, (f"{prefix}%",))

    rows = cur.fetchall()

    print("\n--- Search Results ---")
    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]}, Phone: {row[2]}")

    cur.close()
    conn.close()

def update_name():
    old_name = input("Enter current name: ")
    new_name = input("Enter new name: ")

    conn = connect()
    if conn is None:
        return

    cur = conn.cursor()
    cur.execute("""
        UPDATE phonebook
        SET first_name = %s
        WHERE first_name = %s
    """, (new_name, old_name))

    conn.commit()
    print(f"{cur.rowcount} record(s) updated.")

    cur.close()
    conn.close()

def update_phone():
    old_phone = input("Enter current phone: ")
    new_phone = input("Enter new phone: ")

    conn = connect()
    if conn is None:
        return

    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE phonebook
            SET phone = %s
            WHERE phone = %s
        """, (new_phone, old_phone))
        conn.commit()
        print(f"{cur.rowcount} record(s) updated.")
    except Exception as e:
        print("Update error:", e)
    finally:
        cur.close()
        conn.close()

def delete_by_name():
    name = input("Enter name to delete: ")

    conn = connect()
    if conn is None:
        return

    cur = conn.cursor()
    cur.execute("""DELETE FROM phonebook WHERE first_name = %s""", (name,))

    conn.commit()
    print(f"{cur.rowcount} record(s) deleted.")

    cur.close()
    conn.close()

def delete_by_phone():
    phone = input("Enter phone to delete: ")

    conn = connect()
    if conn is None:
        return

    cur = conn.cursor()
    cur.execute("""
        DELETE FROM phonebook
        WHERE phone = %s
    """, (phone,))

    conn.commit()
    print(f"{cur.rowcount} record(s) deleted.")

    cur.close()
    conn.close()

def menu():
    while True:
        print("\n===== PHONEBOOK MENU =====")
        print("1. Create table")
        print("2. Insert contact from console")
        print("3. Insert contacts from CSV")
        print("4. Show all contacts")
        print("5. Search contacts by name")
        print("6. Search contacts by phone prefix")
        print("7. Update contact name")
        print("8. Update contact phone")
        print("9. Delete contact by name")
        print("10. Delete contact by phone")
        print("0. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            create_table()
        elif choice == "2":
            insert_from_console()
        elif choice == "3":
            insert_from_csv()
        elif choice == "4":
            show_all_contacts()
        elif choice == "5":
            search_by_name()
        elif choice == "6":
            search_by_phone_prefix()
        elif choice == "7":
            update_name()
        elif choice == "8":
            update_phone()
        elif choice == "9":
            delete_by_name()
        elif choice == "10":
            delete_by_phone()
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    menu()