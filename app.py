import streamlit as st
import db_helper as db # Importing your backend logic

st.set_page_config(page_title="My Ledger", layout="wide")
st.title("💰 Personal Payment Manager")

# --- SIDEBAR: Navigation ---
# Update this line:
menu = st.sidebar.radio("Menu", ["Dashboard", "New Transaction", "Add Person", "History", "Manage Accounts"])

# --- PAGE 1: DASHBOARD ---
# --- PAGE 1: DASHBOARD ---
if menu == "Dashboard":
    st.subheader("My Accounts")
    df_accounts = db.get_all_accounts()
    
    # CHECK IF EMPTY BEFORE CREATING COLUMNS
    if not df_accounts.empty:
        cols = st.columns(len(df_accounts))
        for index, row in df_accounts.iterrows():
            with cols[index]: 
                st.metric(label=row['account_name'], value=f"₹{row['balance']:,.2f}")
    else:
        st.warning("No accounts found! Please add an account.")

    st.write("---")
    st.subheader("All Contacts")
    st.dataframe(db.get_all_people())

# --- PAGE 2: NEW TRANSACTION ---
elif menu == "New Transaction":
    st.subheader("💸 Record a Payment")
    
    # Load data for dropdowns
    accounts = db.get_all_accounts()
    people = db.get_all_people()
    
    # Create Dropdowns mapping Names to IDs
    account_map = dict(zip(accounts['account_name'], accounts['account_id']))
    people_map = dict(zip(people['person_name'], people['person_id']))
    
    with st.form("transaction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            selected_acc_name = st.selectbox("Select Account", list(account_map.keys()))
            trans_type = st.selectbox("Type", ["PAID", "RECEIVED"])
            amount = st.number_input("Amount", min_value=1.0)
            
        with col2:
            selected_person_name = st.selectbox("Select Person", list(people_map.keys()))
            note = st.text_input("Note (Optional)")
            
        submitted = st.form_submit_button("Submit Transaction")
        
        if submitted:
            acc_id = account_map[selected_acc_name]
            person_id = people_map[selected_person_name]
            
            success, message = db.add_transaction(acc_id, person_id, amount, note, trans_type)
            if success:
                st.success(message)
            else:
                st.error(message)

# --- PAGE 3: ADD PERSON ---
elif menu == "Add Person":
    st.subheader("Add New Contact")
    with st.form("add_person_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        
        if st.form_submit_button("Add Person"):
            success, msg = db.add_person(name, email, phone)
            if success:
                st.success(msg)
            else:
                st.error(msg)

# --- PAGE 4: HISTORY & MANAGEMENT ---
elif menu == "History":
    st.subheader("📜 Transaction History & Management")
    
    # 1. Select Person
    people = db.get_all_people()
    people_map = dict(zip(people['person_name'], people['person_id']))
    search_person = st.selectbox("Select Person", list(people_map.keys()))
    
    p_id = people_map[search_person]
    
    # 2. Show Table (Include IDs now so user can see them)
    # We create a custom query here to ensure we get IDs
    conn = db.get_connection()
    history_df = pd.read_sql("""
        SELECT t.transaction_id, t.transaction_time, t.amount, t.transaction_type, t.note, a.account_name
        FROM transactions t
        JOIN my_account a ON t.my_account_id = a.account_id
        WHERE t.person_id = %s
        ORDER BY t.transaction_time DESC
    """, conn, params=(p_id,))
    conn.close()
    
    if not history_df.empty:
        st.dataframe(history_df)
        
        st.write("---")
        st.subheader("🖊️ Edit or Delete")
        
        # 3. Selection Box
        # Create a list of IDs for the dropdown: "ID - Amount - Note"
        options = history_df.apply(lambda x: f"{x['transaction_id']} - ₹{x['amount']} ({x['note']})", axis=1)
        selected_option = st.selectbox("Select Transaction to Modify", options)
        
        # Extract the ID from the string "12 - ₹500 (Dinner)" -> 12
        selected_trans_id = int(selected_option.split(" - ")[0])
        
        col1, col2 = st.columns(2)
        
        # DELETE BUTTON
        with col1:
            if st.button("🗑️ Delete Transaction", type="primary"):
                success, msg = db.delete_transaction(selected_trans_id)
                if success:
                    st.success(msg)
                    st.rerun() # Refresh page to show new balance
                else:
                    st.error(msg)
        
        # EDIT FORM
        with col2:
            with st.expander("Edit Amount/Note"):
                with st.form("edit_form"):
                    new_amount = st.number_input("New Amount", min_value=1.0)
                    new_note = st.text_input("New Note")
                    if st.form_submit_button("Update Transaction"):
                        success, msg = db.update_transaction(selected_trans_id, new_amount, new_note)
                        if success:
                            st.success("✅ Transaction Updated!")
                            st.rerun()
                        else:
                            st.error(msg)
                            
    else:
        st.info("No transactions found for this person.")
# --- PAGE 5: MANAGE ACCOUNTS ---
elif menu == "Manage Accounts":
    st.subheader("🏦 Add a New Account")
    
    with st.form("add_account_form"):
        new_acc_name = st.text_input("Account Name (e.g., 'Travel Fund', 'HDFC')")
        initial_bal = st.number_input("Initial Balance", min_value=0.0, value=0.0)
        
        submitted = st.form_submit_button("Create Account")
        
        if submitted:
            if new_acc_name:
                success, msg = db.create_new_account(new_acc_name, initial_bal)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.warning("Please enter an account name.")
    
    st.write("---")
    st.subheader("Existing Accounts")

    st.dataframe(db.get_all_accounts())

