import streamlit as st
from datetime import datetime, timedelta
import backend

st.set_page_config(
    page_title="FoodShare Hub",
    page_icon="🍽️",
    layout="wide"
)

# ---------------- SESSION STATE ----------------

if "selected_index" not in st.session_state:
    st.session_state.selected_index = None


# ---------------- HOME ----------------

st.sidebar.title("FoodShare Hub")

menu = st.sidebar.radio(
    "Menu",
    [
        "Home",
        "List Food",
        "Available Donations",
        "Verify Pickup",
        "Dashboard"
    ]
)

# ---------------- HOME PAGE ----------------

if menu == "Home":

    st.markdown(
        """
        <h1 style='text-align:center; color:#2E8B57; font-size:60px;'>
        FoodShare Hub
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <h3 style='text-align:center; color:gray; font-weight:400;'>
        Connecting surplus food with people who need it.
        </h3>
        """,
        unsafe_allow_html=True
    )

    st.write("")
    st.write("")

    donations = backend.get_donations()

    total_pickups = len(
        [d for d in donations if d["status"] == "Delivered"]
    )

    total_meals = sum(d["quantity"] for d in donations)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Food Listings", len(donations))

    with col2:
        st.metric("Completed Pickups", total_pickups)

    with col3:
        st.metric("Meals Shared", total_meals)

    st.write("")
    st.image(
        "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c",
        use_container_width=True
    )

    st.write("")

    st.markdown(
        """
        <h3 style='text-align:center; color:#2E8B57;'>
        Donate surplus food safely, quickly, and responsibly.
        </h3>
        """,
        unsafe_allow_html=True
    )


# ---------------- LIST FOOD ----------------

elif menu == "List Food":

    st.title("List Surplus Food")

    with st.form("food_form"):

        restaurant_name = st.text_input("Restaurant / Event Name")

        food_name = st.text_input("Food Name")

        quantity = st.number_input(
            "Quantity in Plates",
            min_value=1,
            step=1
        )

        st.subheader("Location")

        x = st.number_input("X Coordinate", step=1)
        y = st.number_input("Y Coordinate", step=1)

        st.subheader("Expiry")

        expiry_hours = st.number_input(
            "Safe for Next How Many Hours?",
            min_value=1,
            step=1
        )

        submitted = st.form_submit_button("Submit Listing")

        if submitted:

            expiry_time = datetime.now() + timedelta(
                hours=expiry_hours
            )

            donation, message = backend.create_donation(
                restaurant_name,
                food_name,
                quantity,
                (x, y),
                expiry_time
            )

            if donation is None:
                st.error(message)

            else:
                st.success(message)

                st.info(
                    f"Matched NGO: {donation['ngo']}"
                )

                st.warning(
                    f"Pickup OTP: {donation['otp']}"
                )


# ---------------- AVAILABLE DONATIONS ----------------

elif menu == "Available Donations":

    st.title("Available Donations")

    donations = backend.get_donations()

    if len(donations) == 0:
        st.warning("No donations available.")

    else:

        for i, donation in enumerate(donations, start=1):

            st.subheader(f"{donation['food']}")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(
                    f"**Restaurant:** {donation['restaurant']}"
                )

            with col2:
                st.write(
                    f"**Quantity:** {donation['quantity']} plates"
                )

            with col3:
                st.write(
                    f"**NGO:** {donation['ngo']}"
                )

            st.write(
                f"**Location:** {donation['location']}"
            )

            st.write(
                f"**Expiry:** {donation['expiry']}"
            )

            if donation["status"] == "Delivered":
                st.success("Delivered")

            else:
                st.warning("Pending Pickup")

            st.divider()


# ---------------- VERIFY PICKUP ----------------

elif menu == "Verify Pickup":

    st.title("Pickup Verification")

    donations = backend.get_donations()

    if len(donations) == 0:
        st.warning("No donations available.")

    else:

        options = [
            f"{d['food']} - {d['restaurant']}"
            for d in donations
        ]

        selected = st.selectbox(
            "Select Donation",
            range(len(options)),
            format_func=lambda i: options[i]
        )

        st.session_state.selected_index = selected

        donation = donations[selected]

        st.subheader("Donation Details")

        st.write(
            f"**Food:** {donation['food']}"
        )

        st.write(
            f"**Restaurant:** {donation['restaurant']}"
        )

        st.write(
            f"**NGO:** {donation['ngo']}"
        )

        st.write(
            f"**Quantity:** {donation['quantity']} plates"
        )

        if donation["status"] == "Delivered":

            st.success("Already Delivered")

        else:

            entered_otp = st.number_input(
                "Enter OTP",
                min_value=1000,
                max_value=9999,
                step=1
            )

            if st.button("Verify Delivery"):

                verified = backend.verify_otp(
                    selected,
                    entered_otp
                )

                if verified:
                    st.success(
                        "Delivery verified successfully!"
                    )

                else:
                    st.error(
                        "Invalid OTP."
                    )


# ---------------- DASHBOARD ----------------

elif menu == "Dashboard":

    st.title("Impact Dashboard")

    donations = backend.get_donations()

    total_pickups = len(
        [d for d in donations if d["status"] == "Delivered"]
    )

    total_meals = sum(
        d["quantity"] for d in donations
    )

    average_surplus = backend.predict_surplus()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Completed Pickups",
            total_pickups
        )

    with col2:
        st.metric(
            "Meals Shared",
            total_meals
        )

    with col3:
        st.metric(
            "Average Surplus",
            average_surplus
        )

    st.divider()

    if len(donations) == 0:

        st.info(
            "Donation activity will appear here."
        )

    else:

        for donation in donations:

            st.write(
                f"🍱 {donation['food']} | "
                f"{donation['quantity']} plates | "
                f"{donation['status']}"
            )