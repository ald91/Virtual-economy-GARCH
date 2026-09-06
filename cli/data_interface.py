""" interface for technical user to initiate and populate data"""

import src.data.data_management as dm
import src.analysis.analysis_data_generation as adg

def print_menu():
    options_list = ["initialize data sets", "prepare economic data", "prepare events data", "generate statistical data", "perform GARCH suitability tests","back"]
    options = enumerate(options_list,1)

    print("\n==============================")
    print(" Data Management Interface")
    print("==============================")
    for n, option in options:
        print(f"{n}. {option}")
    print("==============================")
    


def data_menu():
    while True:
        print_menu()
        choice = input("Select an option: ").strip()

        if choice == "1":
            print("Initialising data sets...")
            dm.initialize_data()

        elif choice == "2":
            print("Preparing economic data...")
            dm.clean_economic_data()

        elif choice == "3":
            print("Preparing events data...")
            dm.update_events_data()
            dm.clean_events_data()

        elif choice == "4":
            print("Generating statistical data...")
            adg.generate_statistical_data()

        elif choice == "5":
            print("Calculating GARCH suitability for indecies...")
            adg.garch_suitability_test()

        elif choice == "6":
            print("Returning to main menu...")
            break

        else:
            print("Invalid selection. Please choose 1-5.")
