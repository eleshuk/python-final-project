from datetime import datetime

def get_farm_input():
    """
    Collect and validate latitude, longitude, start date, and end date from the user.
    Returns a dictionary with the validated inputs.
    """
    while True:
        try:
            lat = float(input("Enter latitude (between -90 and 90): "))
            if not -90 <= lat <= 90:
                raise ValueError("Latitude must be between -90 and 90.")
            break
        except ValueError as e:
            print(f"Invalid input: {e}")

    while True:
        try:
            long = float(input("Enter longitude (between -180 and 180): "))
            if not -180 <= long <= 180:
                raise ValueError("Longitude must be between -180 and 180.")
            break
        except ValueError as e:
            print(f"Invalid input: {e}")

    while True:
        try:
            start_date = input("Enter start date (YYYY-MM-DD): ")
            datetime.strptime(start_date, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

    while True:
        try:
            end_date = input("Enter end date (YYYY-MM-DD): ")
            datetime.strptime(end_date, "%Y-%m-%d")
            if end_date < start_date:
                raise ValueError("End date must not be earlier than start date.")
            break
        except ValueError as e:
            print(f"Invalid input: {e}")

    return {
        "latitude": lat,
        "longitude": long,
        "start_date": start_date,
        "end_date": end_date,
    }

if __name__ == "__main__":
    farm_data = get_farm_input()
    print("Collected inputs:", farm_data)
