""" interface for technical user to initiate and populate data"""


import subprocess
import sys
from pathlib import Path

from cli.data_interface import data_menu


def launch_streamlit():
    project_root = Path(__file__).resolve().parents[1]

    streamlit_app = (
        project_root
        / "src"
        / "streamlit"
        / "streamlit_application.py"
    )

    subprocess.Popen([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(streamlit_app)
    ])

def print_menu():

    options_list = ["Data Management", "Launch Streamlit application","exit application"]
    options = enumerate(options_list,1)

    print("\n==============================")
    print(" Virtual Economy GARCH")
    print("==============================")
    for n, option in options:
        print(f"{n}. {option}")
    print("==============================")
    


def main_menu():
    while True:
        print_menu()

        choice = input("Select an option: ").strip()

        if choice == "1":
            print("Fetching data menu...")
            data_menu()
            
        elif choice == "2":
            print("Launching Streamlit application...")
            print("Press CTRL+C to stop the application")
            launch_streamlit()


        elif choice == "3":
            break

        else:
            print("Invalid selection. Please choose 1 - 3.")