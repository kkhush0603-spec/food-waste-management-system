import streamlit as st
from datetime import datetime, timedelta
import backend

st.set_page_config(
    page_title="FoodShare Hub",
    page_icon="🍽️",
    layout="wide"
)

st.sidebar.markdown(
    "<h2 style='color:#2E8B57;'>FoodShare Hub</h2>",
    unsafe_allow_html=True
)

menu = st.sidebar.radio(
    "Menu",
    [
        "Home",
        "Add Listing",
        "Active Listings",
        "Pickup Portal",
        "Analytics"
    ]
)

# ---------- HOME ----------

if menu == "Home":
    st.markdown(
        """
        <h1 style='text-align:center; color:#2E8B57; font-size:58px;'>
        FoodShare Hub
        </h1>
        <h3 style='text-align:center; color:#555; font-weight:400;'>
        Connecting surplus food with people who need it.
        </h3>
        """,
        unsafe_allow_html=True
    )

    donations = backend.get_donations()

    completed = len([d for d in donations if d["status"] == "Delivered"])
    total_meals = sum(d["quantity"] for d in donations)

    col1, col2, col3 = st.columns(3)

    col1.metric("Active Listings", len(donations))
    col2.metric("Completed Pickups", completed)
    col3.metric("Meals Shared", total_meals)

    st.image(
        "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c",
        use_container_width=True
    )

# ---------- ADD LISTING ----------

elif menu == "Add Listing":
    st.title("Add Food Listing")
    st.write("Create a surplus food listing for pickup.")

    with st.form("listing_form"):
        restaurant_name = st.text_input("Restaurant / Event Name")
        food_name = st.text_input("Food Name")
        quantity = st.number_input("Quantity in Plates", min_value=1, step=1)

        st.subheader("Pickup Location")
        x = st.number_input("X Coordinate", step=1)
        y = st.number_input("Y Coordinate", step=1)

        expiry_hours = st.number_input(
            "Food is safe for next how many hours?",
            min_value=1,
            step=1
        )

        submitted = st.form_submit_button("Create Listing")

        if submitted:
            if restaurant_name.strip() == "" or food_name.strip() == "":
                st.error("Please fill all required details.")
            else:
                expiry_time = datetime.now() + timedelta(hours=expiry_hours)

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
                    st.success("Listing created successfully.")
                    st.info(f"Matched NGO: {donation['ngo']}")
                    st.warning(f"Pickup OTP: {donation['otp']}")
                    st.write("Share this OTP only with the pickup person.")

# ---------- ACTIVE LISTINGS ----------

elif menu == "Active Listings":
    st.title("Active Food Listings")

    donations = backend.get_donations()

    if not donations:
        st.warning("No active listings available.")
    else:
        for i, d in enumerate(donations, start=1):
            st.subheader(f"{i}. {d['food']}")

            col1, col2, col3 = st.columns(3)

            col1.write(f"**Donor:** {d['restaurant']}")
            col2.write(f"**Quantity:** {d['quantity']} plates")
            col3.write(f"**NGO:** {d['ngo']}")

            st.write(f"**Location:** {d['location']}")
            st.write(f"**Expiry:** {d['expiry'].strftime('%d-%m-%Y %H:%M')}")
            st.write(f"**Status:** {d['status']}")

            if d["status"] == "Pending":
                st.warning("Awaiting pickup")
            else:
                st.success("Delivered")

            st.divider()

# ---------- PICKUP PORTAL ----------

elif menu == "Pickup Portal":
    st.title("Pickup Portal")
    st.write("Verify pickup using the OTP shared by the donor.")

    donations = backend.get_donations()

    pending_donations = [
        (i, d) for i, d in enumerate(donations)
        if d["status"] == "Pending"
    ]

    if not pending_donations:
        st.warning("No pending pickups available.")
    else:
        options = [
            f"{d['food']} - {d['restaurant']} → {d['ngo']}"
            for i, d in pending_donations
        ]

        selected_option = st.selectbox(
            "Select Pickup",
            range(len(options)),
            format_func=lambda i: options[i]
        )

        original_index = pending_donations[selected_option][0]
        donation = pending_donations[selected_option][1]

        st.subheader("Pickup Details")
        st.write(f"**Food:** {donation['food']}")
        st.write(f"**Donor:** {donation['restaurant']}")
        st.write(f"**Quantity:** {donation['quantity']} plates")
        st.write(f"**Assigned NGO:** {donation['ngo']}")
        st.write(f"**Pickup Location:** {donation['location']}")

        entered_otp = st.number_input(
            "Enter Pickup OTP",
            min_value=1000,
            max_value=9999,
            step=1
        )

        if st.button("Verify Pickup"):
            verified = backend.verify_otp(original_index, entered_otp)

            if verified:
                st.success("Pickup verified successfully. Donation completed.")
            else:
                st.error("Invalid OTP. Pickup not verified.")

# ---------- ANALYTICS ----------

elif menu == "Analytics":
    st.title("Analytics")

    donations = backend.get_donations()

    completed = [d for d in donations if d["status"] == "Delivered"]
    total_meals = sum(d["quantity"] for d in donations)
    predicted = backend.predict_surplus()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Listings", len(donations))
    col2.metric("Completed Pickups", len(completed))
    col3.metric("Predicted Surplus", f"{predicted} plates")

    st.divider()

    if not donations:
        st.info("Analytics will appear after listings are created.")
    else:
        st.subheader("Recent Activity")

        for d in donations:
            st.write(
                f"🍽️ **{d['food']}** | {d['quantity']} plates | "
                f"{d['restaurant']} → {d['ngo']} | {d['status']}"
            )
