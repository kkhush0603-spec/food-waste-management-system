import streamlit as st
from datetime import datetime, timedelta
import random

st.set_page_config(
    page_title="Food Waste Reduction System",
    page_icon="🍱",
    layout="wide"
)

# ---------------- SESSION STATE ----------------

if "foods" not in st.session_state:
    st.session_state.foods = []

if "donation_history" not in st.session_state:
    st.session_state.donation_history = []

if "current_otp" not in st.session_state:
    st.session_state.current_otp = None

if "selected_food" not in st.session_state:
    st.session_state.selected_food = None

if "selected_ngo" not in st.session_state:
    st.session_state.selected_ngo = None

if "selected_volunteer" not in st.session_state:
    st.session_state.selected_volunteer = None


# ---------------- DATA ----------------

RESTAURANT_LOCATION = 10

ngos = [
    {"name": "Helping Hands NGO", "location": 12, "capacity": 50, "type": "Any"},
    {"name": "Food For All", "location": 18, "capacity": 30, "type": "Veg"},
    {"name": "Care Shelter", "location": 8, "capacity": 40, "type": "Non-Veg"},
    {"name": "Hope Foundation", "location": 15, "capacity": 60, "type": "Any"},
]

volunteers = [
    {"name": "Rahul", "location": 11},
    {"name": "Aisha", "location": 18},
    {"name": "Kiran", "location": 7},
    {"name": "Meena", "location": 13},
]


# ---------------- FUNCTIONS ----------------

def is_food_valid(food):
    return (
        food["quantity"] > 0
        and food["is_safe"]
        and datetime.now() < food["expiry_time"]
    )


def find_nearest_ngo(food):
    suitable_ngos = []

    for ngo in ngos:
        type_match = ngo["type"] == "Any" or ngo["type"] == food["food_type"]
        capacity_match = food["quantity"] <= ngo["capacity"]

        if type_match and capacity_match:
            distance = abs(RESTAURANT_LOCATION - ngo["location"])
            suitable_ngos.append((distance, ngo))

    suitable_ngos.sort(key=lambda x: x[0])

    if suitable_ngos:
        return suitable_ngos[0][1]

    return None


def assign_volunteer():
    nearest_volunteer = min(
        volunteers,
        key=lambda v: abs(RESTAURANT_LOCATION - v["location"])
    )
    return nearest_volunteer


# ---------------- UI ----------------

st.sidebar.title("🍱 Food Waste System")
menu = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Add Surplus Food",
        "View Available Food",
        "Donate Food",
        "Prediction Dashboard",
        "About Project"
    ]
)

# ---------------- HOME ----------------

if menu == "Home":
    st.title("🍱 Food Waste Reduction System")
    st.subheader("Python-Based Food Donation Management Platform")

    st.write(
        """
        This system helps restaurants reduce food wastage by connecting surplus food
        with nearby NGOs and volunteers. It validates food safety, checks expiry time,
        matches the nearest NGO, assigns volunteers, and verifies delivery using OTP.
        """
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Available Food Items", len(st.session_state.foods))

    with col2:
        st.metric("Completed Donations", len(st.session_state.donation_history))

    with col3:
        total = sum(st.session_state.donation_history)
        st.metric("Total Plates Donated", total)

    st.info("Use the sidebar to add food, view items, donate food, and check prediction.")


# ---------------- ADD FOOD ----------------

elif menu == "Add Surplus Food":
    st.title("➕ Add Surplus Food")

    with st.form("food_form"):
        food_name = st.text_input("Food Name")
        quantity = st.number_input("Quantity in Plates", min_value=1, step=1)
        food_type = st.selectbox("Food Type", ["Veg", "Non-Veg"])
        expiry_hours = st.number_input("Expiry Time in Hours", min_value=1, step=1)

        st.subheader("Food Safety Checklist")
        fresh = st.checkbox("Food is freshly prepared")
        stored = st.checkbox("Food was stored properly")
        packed = st.checkbox("Food is packed properly")

        submit = st.form_submit_button("Add Food")

        if submit:
            if food_name.strip() == "":
                st.error("Please enter food name.")
            else:
                is_safe = fresh and stored and packed
                expiry_time = datetime.now() + timedelta(hours=expiry_hours)

                food = {
                    "food_name": food_name,
                    "quantity": quantity,
                    "food_type": food_type,
                    "added_time": datetime.now(),
                    "expiry_time": expiry_time,
                    "is_safe": is_safe
                }

                if is_food_valid(food):
                    st.session_state.foods.append(food)
                    st.success("Food added successfully!")
                else:
                    st.error("Food rejected due to safety or validity issue.")


# ---------------- VIEW FOOD ----------------

elif menu == "View Available Food":
    st.title("📦 Available Food Items")

    if not st.session_state.foods:
        st.warning("No food items available.")
    else:
        for index, food in enumerate(st.session_state.foods):
            with st.container():
                st.subheader(f"{index + 1}. {food['food_name']}")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.write(f"**Quantity:** {food['quantity']} plates")

                with col2:
                    st.write(f"**Type:** {food['food_type']}")

                with col3:
                    st.write(f"**Expiry:** {food['expiry_time'].strftime('%d-%m-%Y %H:%M')}")

                if is_food_valid(food):
                    st.success("Status: Valid for donation")
                else:
                    st.error("Status: Expired or unsafe")

                st.divider()


# ---------------- DONATE FOOD ----------------

elif menu == "Donate Food":
    st.title("🤝 Donate Food")

    if not st.session_state.foods:
        st.warning("No food available for donation.")
    else:
        food_names = [food["food_name"] for food in st.session_state.foods]

        selected_index = st.selectbox(
            "Select Food Item",
            range(len(food_names)),
            format_func=lambda i: food_names[i]
        )

        food = st.session_state.foods[selected_index]

        st.subheader("Selected Food Details")
        st.write(f"**Food Name:** {food['food_name']}")
        st.write(f"**Quantity:** {food['quantity']} plates")
        st.write(f"**Food Type:** {food['food_type']}")
        st.write(f"**Expiry Time:** {food['expiry_time'].strftime('%d-%m-%Y %H:%M')}")

        if not is_food_valid(food):
            st.error("This food is expired or unsafe. It cannot be donated.")
        else:
            if st.button("Find NGO and Generate OTP"):
                ngo = find_nearest_ngo(food)

                if ngo is None:
                    st.error("No suitable NGO found.")
                else:
                    volunteer = assign_volunteer()
                    otp = random.randint(1000, 9999)

                    st.session_state.selected_food = selected_index
                    st.session_state.selected_ngo = ngo
                    st.session_state.selected_volunteer = volunteer
                    st.session_state.current_otp = otp

                    st.success("NGO matched successfully!")
                    st.info(f"Matched NGO: {ngo['name']}")
                    st.info(f"Volunteer Assigned: {volunteer['name']}")
                    st.warning(f"Generated OTP: {otp}")

            if st.session_state.current_otp is not None:
                st.subheader("OTP Verification")

                entered_otp = st.number_input(
                    "Enter OTP to complete donation",
                    min_value=1000,
                    max_value=9999,
                    step=1
                )

                if st.button("Complete Donation"):
                    if entered_otp == st.session_state.current_otp:
                        donated_food = st.session_state.foods.pop(
                            st.session_state.selected_food
                        )

                        st.session_state.donation_history.append(
                            donated_food["quantity"]
                        )

                        st.success("Donation completed successfully!")

                        st.session_state.current_otp = None
                        st.session_state.selected_food = None
                        st.session_state.selected_ngo = None
                        st.session_state.selected_volunteer = None

                    else:
                        st.error("Incorrect OTP. Donation failed.")


# ---------------- PREDICTION ----------------

elif menu == "Prediction Dashboard":
    st.title("📊 Surplus Prediction Dashboard")

    if not st.session_state.donation_history:
        st.warning("Not enough donation data for prediction.")
    else:
        total = sum(st.session_state.donation_history)
        count = len(st.session_state.donation_history)
        average = total / count

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Donations", count)

        with col2:
            st.metric("Total Plates Donated", total)

        with col3:
            st.metric("Average Surplus", f"{average:.2f} plates")

        st.success(
            f"Suggestion: Prepare around {int(average)} fewer plates next time to reduce wastage."
        )

        st.subheader("Donation History")
        for i, quantity in enumerate(st.session_state.donation_history, start=1):
            st.write(f"Donation {i}: {quantity} plates")


# ---------------- ABOUT ----------------

elif menu == "About Project":
    st.title("ℹ️ About the Project")

    st.write(
        """
        The Food Waste Reduction System is designed to reduce food wastage by
        automating the process of food donation from restaurants to NGOs.
        """
    )

    st.subheader("Main Features")
    st.write("- Add surplus food details")
    st.write("- Validate food safety and expiry")
    st.write("- Match nearest NGO")
    st.write("- Assign volunteer")
    st.write("- OTP-based delivery verification")
    st.write("- Track donation history")
    st.write("- Predict future surplus food")

    st.subheader("Technology Used")
    st.write("- Python")
    st.write("- Streamlit")
    st.write("- Datetime module")
    st.write("- Random module")