import streamlit as st
import json
import os

# --- PERSISTENT DATA STORAGE ---
DB_FILE = "lambda_db.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    # Initial state based on MATH180 rules
    return {"students": {}, "phase": 1, "slots_left": 10}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- APP INITIALIZATION ---
st.set_page_config(page_title="MATH180 λ Economy", layout="wide")
data = load_data()

st.title("λ MATH180: The Lambda Economy")
st.sidebar.header("Professor Control Panel")

# --- STUDENT ENROLLMENT ---
new_student = st.sidebar.text_input("Enroll New Student")
if st.sidebar.button("Add to Class"):
    if new_student and new_student not in data["students"]:
        data["students"][new_student] = {
            "lambda": 0, 
            "bonus": 0, 
            "shielded": False, 
            "cooldown": False
        }
        save_data(data)
        st.sidebar.success(f"{new_student} enrolled!")

# --- MAIN DASHBOARD ---
col_ledger, col_actions = st.columns([2, 1])

with col_ledger:
    st.subheader("Class Ledger")
    if data["students"]:
        # Displaying the current state of the economy
        st.table(data["students"])
    else:
        st.info("No students enrolled yet. Use the sidebar to add your class.")

with col_actions:
    st.subheader("Log Boardwork")
    if data["students"]:
        student_list = list(data["students"].keys())
        selected = st.selectbox("Select Student", student_list)
        
        # Specific point values from sources [cite: 4, 5, 6]
        action = st.radio("Performance", [
            "Successful Boardwork (50λ)", 
            "Partial/Good Attempt (25λ)", 
            "Peer Review (10λ)"
        ])
        
        if st.button("Confirm Points"):
            points = {
                "Successful Boardwork (50λ)": 50, 
                "Partial/Good Attempt (25λ)": 25, 
                "Peer Review (10λ)": 10
            }[action]
            
            data["students"][selected]["lambda"] += points
            
            # Rule: Representative Sampling / Cool Down [cite: 21, 22]
            for s in data["students"]:
                data["students"][s]["cooldown"] = (s == selected)
                
            save_data(data)
            st.rerun()
    else:
        st.write("Enroll students to start logging points.")

# --- PHASE 1: EARLY BIRD FLASH SALE ---
st.divider()
if data["phase"] == 1:
    st.header(f"Phase 1: Early Bird Flash Sale ({data['slots_left']} Slots Left) [cite: 7]")
    st.write("5 Bonus Points = ONLY 50λ [cite: 10]")
    
    if data["students"]:
        buyer = st.selectbox("Select Buyer", list(data["students"].keys()), key="sale_buyer")
        if st.button("Purchase 5 Bonus Points"):
            if data["students"][buyer]["lambda"] >= 50:
                data["students"][buyer]["lambda"] -= 50
                data["students"][buyer]["bonus"] += 5
                data["slots_left"] -= 1
                
                # Check if Phase 1 is over [cite: 13, 14]
                if data["slots_left"] <= 0:
                    data["phase"] = 2
                
                save_data(data)
                st.success(f"Points claimed by {buyer}!")
                st.rerun()
            else:
                st.error("Insufficient λ!")

# --- PHASE 2: REDISTRIBUTION MARKET ---
else:
    st.header("Phase 2: High-Stakes Redistribution Market ")
    st.warning("The Shop is CLOSED. You must now enter the market. [cite: 14, 15]")
    
    market_action = st.selectbox("Market Move", ["Double Steal (100λ)", "Chaos Transfer (50λ)", "SOS Shield (50λ)"])
    
    # Logic for Stealing [cite: 16]
    if market_action == "Double Steal (100λ)":
        attacker = st.selectbox("Attacker", list(data["students"].keys()))
        victim = st.selectbox("Target (Steal 10 pts)", list(data["students"].keys()))
        if st.button("Execute Double Steal"):
            if data["students"][attacker]["lambda"] >= 100:
                data["students"][attacker]["lambda"] -= 100
                if not data["students"][victim]["shielded"]:
                    stolen = min(data["students"][victim]["bonus"], 10)
                    data["students"][victim]["bonus"] -= stolen
                    data["students"][attacker]["bonus"] += stolen
                    st.success("Steal Successful!")
                else:
                    data["students"][victim]["shielded"] = False
                    st.warning("Shield Blocked the Steal!")
                save_data(data)
                st.rerun()