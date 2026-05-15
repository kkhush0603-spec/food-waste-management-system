from datetime import datetime
import random
import math

restaurants = []

ngos = [
    {"name": "Helping Hands NGO", "location": (2, 3)},
    {"name": "Food For All NGO", "location": (5, 1)},
    {"name": "Care Foundation", "location": (8, 6)}
]

donations = []


# ---------- DISTANCE CALCULATION ----------

def calculate_distance(loc1, loc2):
    return math.sqrt(
        (loc1[0] - loc2[0]) ** 2 +
        (loc1[1] - loc2[1]) ** 2
    )


# ---------- OTP GENERATION ----------

def generate_otp():
    return random.randint(1000, 9999)


# ---------- FIND NEAREST NGO ----------

def find_nearest_ngo(restaurant_location):
    nearest_ngo = None
    min_distance = float("inf")

    for ngo in ngos:
        distance = calculate_distance(
            restaurant_location,
            ngo["location"]
        )

        if distance < min_distance:
            min_distance = distance
            nearest_ngo = ngo

    return nearest_ngo


# ---------- CREATE DONATION ----------

def create_donation(
    restaurant_name,
    food_name,
    quantity,
    location,
    expiry_time
):

    current_time = datetime.now()

    if expiry_time <= current_time:
        return None, "Food is expired. Donation rejected."

    nearest_ngo = find_nearest_ngo(location)

    otp = generate_otp()

    donation = {
        "restaurant": restaurant_name,
        "food": food_name,
        "quantity": quantity,
        "location": location,
        "expiry": expiry_time,
        "ngo": nearest_ngo["name"],
        "otp": otp,
        "status": "Pending"
    }

    donations.append(donation)

    return donation, "Donation request created successfully."


# ---------- VIEW DONATIONS ----------

def get_donations():
    return donations


# ---------- VERIFY DELIVERY ----------

def verify_otp(index, entered_otp):

    if index < 0 or index >= len(donations):
        return False

    if entered_otp == donations[index]["otp"]:
        donations[index]["status"] = "Delivered"
        return True

    return False


# ---------- PREDICT SURPLUS ----------

def predict_surplus():

    if len(donations) == 0:
        return 0

    total_quantity = sum(
        donation["quantity"]
        for donation in donations
    )

    average = total_quantity / len(donations)

    return round(average)


# ---------- NGO LIST ----------

def get_ngos():
    return ngos