import csv
import os
import time
import serial
from datetime import datetime

# ============================================================
# SETTINGS
# ============================================================
BAUD_RATE = 115200
OUTPUT_FILE = "footwear_dataset.csv"
COLLECTION_SECONDS = 5 * 60

SCENARIOS = [
    "Standing",
    "Walking",
    "Sitting",
    "No_Load",
    "Toe_Pressure",
    "Heel_Pressure",
    "Left_Shift",
    "Right_Shift",
    "High_Pressure",
]

# ============================================================
# HELPERS
# ============================================================
def choose_person():
    while True:
        print("\nSelect person:")
        print("1. Person A")
        print("2. Person B")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            return "Person A"
        if choice == "2":
            return "Person B"

        print("Invalid choice. Enter 1 or 2.")


def choose_scenario():
    while True:
        print("\nSelect scenario:")
        for i, scenario in enumerate(SCENARIOS, 1):
            print(f"{i}. {scenario}")

        choice = input("Enter choice: ").strip()

        if choice.isdigit():
            number = int(choice)
            if 1 <= number <= len(SCENARIOS):
                return SCENARIOS[number - 1]

        print("Invalid choice.")


def send_command(ser, command):
    ser.write((command + "\n").encode("utf-8"))


def prepare_csv():
    file_exists = os.path.exists(OUTPUT_FILE)
    file_empty = not file_exists or os.path.getsize(OUTPUT_FILE) == 0

    file = open(OUTPUT_FILE, "a", newline="", encoding="utf-8")
    writer = csv.writer(file)

    if file_empty:
        writer.writerow([
            "RecordNo",
            "Type",
            "Person",
            "Scenario",
            "FSR1",
            "FSR2",
            "FSR3",
            "FSR4",
            "Temperature",
            "LoggedAt",
        ])
        file.flush()

    return file, writer


def collect_session(ser, writer, person, scenario):
    send_command(ser, f"PERSON={person}")
    send_command(ser, f"SCENARIO={scenario}")

    # Give ESP32 time to process the commands.
    time.sleep(0.5)

    print("\n" + "=" * 60)
    print(f"Person   : {person}")
    print(f"Scenario : {scenario}")
    print("Duration : 5 minutes")
    print("Starting collection...")
    print("=" * 60)

    # Flush old serial lines before starting the session.
    ser.reset_input_buffer()

    start_time = time.monotonic()
    end_time = start_time + COLLECTION_SECONDS
    rows_saved = 0

    while time.monotonic() < end_time:
        remaining = int(end_time - time.monotonic())

        if ser.in_waiting:
            raw = ser.readline().decode("utf-8", errors="ignore").strip()

            if not raw:
                continue

            # ESP32 CSV data format:
            # RecordNo,Type,Person,Scenario,FSR1,FSR2,FSR3,FSR4,Temperature
            parts = raw.split(",")

            if len(parts) == 9:
                try:
                    int(parts[0])
                    if parts[1] not in ("RAW", "AVG10"):
                        continue

                    # Use the values coming from the ESP32.
                    writer.writerow(parts + [datetime.now().isoformat(timespec="seconds")])
                    rows_saved += 1

                    print(
                        f"Saved: {parts[0]:>5} | "
                        f"{parts[1]:>5} | "
                        f"{parts[4]:>4} {parts[5]:>4} "
                        f"{parts[6]:>4} {parts[7]:>4} | "
                        f"{parts[8]:>6} C | "
                        f"Remaining: {remaining:>3}s",
                        end="\r",
                    )

                    # Make data immediately available in the CSV.
                    writer.dialect
                    csv_file.flush()

                except (ValueError, IndexError):
                    pass

        else:
            time.sleep(0.02)

    print()
    print(f"✓ {scenario} completed. {rows_saved} rows saved.")


# ============================================================
# MAIN
# ============================================================
def main():
    global csv_file

    print("=" * 60)
    print("SMART FOOTWEAR - 5 MINUTE DATA LOGGER")
    print("=" * 60)
    print(f"CSV file: {OUTPUT_FILE}")

    port = input("\nEnter ESP32 COM port (example: COM5): ").strip()

    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=0.2)
    except serial.SerialException as error:
        print(f"Could not open {port}: {error}")
        return

    csv_file, writer = prepare_csv()

    try:
        person = choose_person()

        while True:
            scenario = choose_scenario()

            input(
                f"\nPrepare {person} for '{scenario}'. "
                "Press ENTER to start the 5-minute collection..."
            )

            collect_session(ser, writer, person, scenario)

            again = input(
                "\nDo you want to collect another scenario for this person? "
                "(y/n): "
            ).strip().lower()

            if again != "y":
                break

        print("\nData collection finished.")
        print(f"All data saved in: {os.path.abspath(OUTPUT_FILE)}")

    except KeyboardInterrupt:
        print("\n\nCollection stopped by user.")

    finally:
        csv_file.close()
        ser.close()


if __name__ == "__main__":
    main()
