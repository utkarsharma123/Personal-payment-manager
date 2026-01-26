import streamlit as st
import db_helper as db # Importing your backend logic

st.set_page_config(page_title="My Ledger", layout="wide")
st.title("💰 Personal Payment Manager")

# --- SIDEBAR: Navigation ---
# Update this line:
menu = st.sidebar.radio("Menu", ["Dashboard", "New Transaction", "Add Person", "History", "Manage Accounts"])

# --- PAGE 1: DASHBOARD ---
if menu == "Dashboard":
    st.subheader("My Accounts")
    df_accounts = db.get_all_accounts()
    
    # Display accounts as metric cards
    cols = st.columns(len(df_accounts))
    for index, row in df_accounts.iterrows():
        with cols[index % 3]: # prevent error if too many accounts
            st.metric(label=row['account_name'], value=f"₹{row['balance']:,.2f}")
            
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

# --- PAGE 4: HISTORY ---
elif menu == "History":
    st.subheader("📜 Person History")
    
    people = db.get_all_people()
    people_map = dict(zip(people['person_name'], people['person_id']))
    
    search_person = st.selectbox("Select Person to view history", list(people_map.keys()))
    
    if st.button("Show History"):
        p_id = people_map[search_person]
        history_df = db.get_person_history(p_id)
        
        if not history_df.empty:
            st.dataframe(history_df)
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