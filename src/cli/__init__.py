
options = ["Data collection","Data preparation","Statistical Analysis","Launch Streamlit"] 
OPTIONS = enumerate(options)

def print_menu():
    print("\n==============================")
    print(" Virtual Economy GARCH")
    print("==============================")
    for n, options in menu_options:
        print(f"{n}. {options}")
    print("==============================")


def main():
    while True:
        print_menu()

        choice = input("Select an option: ").strip()

        if choice == "1":
            print("Running return calculation...")
            # statistical_analysis.calculate_returns(...)

        elif choice == "2":
            print("Running squared-return calculation...")
            # statistical_analysis.calculate_returns_squared(...)

        elif choice == "3":
            print("Running rolling-volatility calculation...")
            # statistical_analysis.calculate_rolling_volatility(...)

        elif choice == "4":
            print("Running statistical summary...")
            # statistical_analysis.calculate_statistics(...)

        elif choice == "5":
            print("Exiting...")
            break

        else:
            print("Invalid selection. Please choose 1-5.")