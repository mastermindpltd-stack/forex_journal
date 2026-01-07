import streamlit as st
import csv
import os
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Forex Trading Journal", layout="centered")

DATA_FILE = "trades.csv"

# Create image folders safely
os.makedirs("images/before", exist_ok=True)
os.makedirs("images/after", exist_ok=True)

# ---------------- LOGIN SYSTEM ----------------
def check_user(username, password):
    try:
        with open("users.csv", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if (
                    row["username"] == username
                    and row["password"] == password
                    and row["active"] == "yes"
                ):
                    return True
    except:
        return False
    return False

st.sidebar.markdown("### 🔐 Paid User Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

is_paid_user = check_user(username, password)

if is_paid_user:
    st.sidebar.success("✅ Paid User")
else:
    st.sidebar.warning("🔒 Free User")

menu = st.sidebar.radio("Menu", ["Add Trade", "Journal Stats"])

# ---------------- ADD TRADE ----------------
if menu == "Add Trade":
    st.title("📝 Add Trade")

    pair = st.text_input("Pair (EURUSD, XAUUSD, etc)")
    direction = st.selectbox("Direction", ["Buy", "Sell"])
    risk = st.number_input("Risk %", min_value=0.1, value=1.0)
    rr = st.number_input("RR (Loss = -1 | BE = 0 | Win = 2)", value=1.0)
    notes = st.text_area("Notes")

    before_img = None
    after_img = None

    if is_paid_user:
        st.markdown("### 📸 Trade Images (Paid)")
        before_img = st.file_uploader("Before Trade Image", type=["png", "jpg", "jpeg"])
        after_img = st.file_uploader("After Trade Image", type=["png", "jpg", "jpeg"])
    else:
        st.info("🔒 Image upload is a Paid Feature")

    if st.button("Save Trade"):
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M")

        if rr > 0:
            result = "Win"
        elif rr < 0:
            result = "Loss"
        else:
            result = "BE"

        before_path = ""
        after_path = ""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        if before_img:
            before_path = f"images/before/{ts}_{before_img.name}"
            with open(before_path, "wb") as f:
                f.write(before_img.getbuffer())

        if after_img:
            after_path = f"images/after/{ts}_{after_img.name}"
            with open(after_path, "wb") as f:
                f.write(after_img.getbuffer())

        trade = [
            date_time,
            pair,
            direction,
            risk,
            rr,
            result,
            rr,
            before_path,
            after_path,
            notes
        ]

        with open(DATA_FILE, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(trade)

        st.success("✅ Trade Saved Successfully")

# ---------------- JOURNAL STATS ----------------
elif menu == "Journal Stats":
    st.title("📊 Journal Analytics")

    trades = []
    try:
        with open(DATA_FILE, newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                trades.append(row)
    except:
        st.info("No trades yet")
        st.stop()

    if not trades:
        st.info("No trades yet")
        st.stop()

    # ----- BASIC STATS -----
    total = len(trades)
    wins = len([t for t in trades if t["Result"] == "Win"])
    winrate = (wins / total) * 100
    avg_rr = sum(float(t["RR"]) for t in trades) / total

    st.metric("Total Trades", total)
    st.metric("Winrate %", round(winrate, 2))
    st.metric("Average RR", round(avg_rr, 2))

    # ----- EQUITY CURVE -----
    st.subheader("📈 Equity Curve (R-based)")
    equity = []
    running = 0
    for t in trades:
        running += float(t["RR"])
        equity.append(running)
    st.line_chart(equity)

    # ----- LOSS ANALYSIS -----
    st.subheader("🔻 Loss Trades")
    losses = [t for t in trades if t["Result"] == "Loss"]
    st.metric("Total Losses", len(losses))
    if losses:
        st.dataframe(losses[::-1])

    # ----- IMAGE REVIEW (SAFE FOR CLOUD) -----
    st.subheader("🖼️ Trade Image Review")

    labels = [
        f"{t['DateTime']} | {t['Pair']} | RR {t['RR']}"
        for t in trades
    ]

    selected = st.selectbox("Select Trade", labels)
    trade = trades[labels.index(selected)]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Before Trade**")
        if (
            is_paid_user
            and trade.get("BeforeImage")
            and os.path.exists(trade["BeforeImage"])
        ):
            st.image(trade["BeforeImage"], width=300)
        else:
            st.info("No before image")

    with col2:
        st.markdown("**After Trade**")
        if (
            is_paid_user
            and trade.get("AfterImage")
            and os.path.exists(trade["AfterImage"])
        ):
            st.image(trade["AfterImage"], width=300)
        else:
            st.info("No after image")

