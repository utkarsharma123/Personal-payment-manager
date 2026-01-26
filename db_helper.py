import psycopg2
import pandas as pd # You will need to install pandas: pip install pandas

def get_connection():
    return psycopg2.connect(
        database="Ddc",
        user="postgres",
        password="Manu@1234", # Ideally, use environment variables for this!
        host="localhost",
        port="5432"
    )

# --- Fetch Functions (For Dropdowns & Tables) ---
def get_all_accounts():
    conn = get_connection()
    # Pandas reads SQL directly into a neat table format
    df = pd.read_sql("SELECT * FROM my_account", conn)
    conn.close()
    return df

def get_all_people():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM peoples", conn)
    conn.close()
    return df

def get_person_history(person_id):
    conn = get_connection()
    query = """
        SELECT a.account_name, t.transaction_type, t.amount, t.transaction_time, t.note
        FROM transactions t
        JOIN my_account a ON t.my_account_id = a.account_id
        WHERE t.person_id = %s
        ORDER BY t.transaction_time DESC
    """
    df = pd.read_sql(query, conn, params=(person_id,))
    conn.close()
    return df

# --- Action Functions (For Buttons) ---
def add_person(name, email, phone):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO peoples(person_name, email, phone) VALUES (%s,%s,%s)", (name, email, phone))
        conn.commit()
        return True, "✅ Person added successfully"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def add_transaction(account_id, person_id, amount, note, trans_type):
    conn = get_connection()
    cur = conn.cursor()
    
    # Check Balance first if paying
    if trans_type == 'PAID':
        cur.execute("SELECT balance FROM my_account WHERE account_id=%s", (account_id,))
        bal = cur.fetchone()[0]
        if bal < amount:
            conn.close()
            return False, "❌ Insufficient Balance"
        
        # Deduct
        cur.execute("UPDATE my_account SET balance = balance - %s WHERE account_id=%s", (amount, account_id))
    else:
        # Add (Received)
        cur.execute("UPDATE my_account SET balance = balance + %s WHERE account_id=%s", (amount, account_id))

    # Insert Record
    cur.execute("""
        INSERT INTO transactions (amount, my_account_id, person_id, transaction_type, note)
        VALUES (%s,%s,%s,%s,%s)
    """, (amount, account_id, person_id, trans_type, note))
    
    conn.commit()
    conn.close()
    return True, "✅ Transaction Recorded"
def create_new_account(account_name, initial_balance):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Check if account already exists to prevent duplicates
        cur.execute("SELECT account_id FROM my_account WHERE account_name = %s", (account_name,))
        if cur.fetchone():
            return False, "❌ Account with this name already exists!"

        # Create the account
        cur.execute(
            "INSERT INTO my_account (account_name, balance) VALUES (%s, %s)",
            (account_name, initial_balance)
        )
        conn.commit()
        return True, "✅ New account created successfully!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()