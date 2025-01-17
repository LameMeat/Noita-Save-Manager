import sys
import shutil
import os
from datetime import datetime
import logging
import subprocess

# Configure logging
logging.basicConfig(filename='noita_save_manager.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

username = os.getlogin()

default_variables = {
    "path_to_noita_saves_folder": f"C:/Users/{username}/AppData/LocalLow/Nolla_Games_Noita",
    "path_to_noita_mp_proxy": f"C:/Users/{username}/AppData/LocalLow/Nolla_Games_Noita/NoitaMPProxy.exe",
    "path_to_noita_exe": f"C:/Program Files (x86)/Steam/steamapps/common/Noita/noita.exe",
    "backup_prefix": f"BACKUP_"
}

current_variables = default_variables.copy()

# Menu options
# I am using * to indicate that the option is not implemented yet
menu_options = {
    "main_menu": {
        "Title": "Noita Save Manager",
        "1": "Backup Current Save",
        "2": "Activate Save",
        "*3": "Launch Noita",
        "*4": "Launch Noita MP Proxy",
        "5": "Delete Backup",
        "*6": "Settings",
        "7": "Help",
        "9": "Exit"
    },
    "settings_menu": {
        "Title": "Settings",
        "1": "Change path to Noita save folder",
        "2": "Change path to Noita MP Proxy",
        "3": "Save & Return to Main Menu",
        "9": "Restore default settings"
    }
}

def load_variables():
    try:
        with open("variables.txt", "r") as f:
            for line in f:
                key, value = line.split("=")
                current_variables[key] = value.strip()
        logging.info("Variables loaded successfully.")
    except FileNotFoundError:
        logging.warning("Variables file not found, using default variables.")
        print("Variables file not found, using default variables.")
    except Exception as e:
        logging.error(f"Error loading variables: {e}")
        print(f"Error loading variables: {e}")

def print_menu(menu_name):
    os.system('cls' if os.name == 'nt' else 'clear')
    menu = menu_options[menu_name]
    print(f"\n\n{menu['Title']}\n" + "-" * len(menu['Title']))
    for key in menu:
        if key != "Title" and key[0] != "*":
            print(f"{key}. {menu[key]}")
    print()

def main_menu_choice(choice):
    try:
        menu = menu_options["main_menu"]
        if choice in menu:
            action = menu[choice]
            if action == "Backup Current Save":
                name_backup_save()
            elif action == "Activate Save":
                list_save_backups("activate")
            elif action == "Delete Backup":
                list_save_backups("delete")
            elif action == "Settings":
                print_menu("settings_menu")
                choice = input("Enter choice: ").strip()
                settings_menu_choice(choice)
            elif action == "Help":
                help()
            elif action == "Exit":
                print("Exiting...")
                logging.info("Exiting application.")
                sys.exit()
            else:
                print("Invalid choice, please try again.")
        else:
            print("Invalid choice, please try again.")
    except Exception as e:
        logging.error(f"Error in main_menu_choice: {e}")
        print(f"Error: {e}")

def help():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\nNoita Save Manager Help")
    print("-----------------------")
    print("1. Backup Current Save: Create a backup of your current Noita save.")
    print("2. Activate Save: Restore a previously created backup.")
    print("5. Delete Backup: Delete a previously created backup.")
    print("7. Help: Display this help message.")
    print("9. Exit: Exit the application.")
    print("\nUse the Settings menu to change paths to Noita save folder and Noita MP Proxy.")
    wait_for_input()

def settings_menu_choice(choice):
    try:
        menu = menu_options["settings_menu"]
        if choice in menu:
            action = menu[choice]
            if action == "Change path to Noita save folder":
                change_path_to_noita_saves_folder()
            elif action == "Change path to Noita MP Proxy":
                change_path_to_noita_mp_proxy()
            elif action == "Save & Return to Main Menu":
                save_current_variables()
                main()
            elif action == "Restore default settings":
                restore_default_settings()
            else:
                print("Invalid choice, please try again.")
        else:
            print("Invalid choice, please try again.")
    except Exception as e:
        logging.error(f"Error in settings_menu_choice: {e}")
        print(f"Error: {e}")

def restore_default_settings():
    current_variables = default_variables.copy()

def name_backup_save():
    save_folder = current_variables["path_to_noita_saves_folder"]
    save_name = input("Enter a name for the backup save (type nothing and hit enter to cancel): ").strip()
    if not save_name:
        return
    backup_name = f"{current_variables['backup_prefix']}{save_name}_"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_folder_name = f"{backup_name}{timestamp}"
    backup_folder_path = os.path.join(save_folder, backup_folder_name)
    current_save_folder = os.path.join(save_folder, "save00")
    backup_save(current_save_folder, backup_folder_path)

def copy_with_progress(src, dst, total_files, copied_files):
    shutil.copy2(src, dst)
    copied_files[0] += 1
    progress = (copied_files[0] / total_files) * 100
    print(f"\rProgress: [{int(progress)}%]", end='')

def backup_save(current_save_folder, backup_folder_path):
    try:
        total_files = sum([len(files) for r, d, files in os.walk(current_save_folder)])
        copied_files = [0]  # Use a list to keep track of copied files
        shutil.copytree(current_save_folder, backup_folder_path, copy_function=lambda src, dst: copy_with_progress(src, dst, total_files, copied_files))
        print(f"\nBackup created at {backup_folder_path}")
        logging.info(f"Backup created at {backup_folder_path}")
    except Exception as e:
        logging.error(f"Failed to create backup: {e}")
        print(f"Failed to create backup: {e}")
    if not backup_folder_path.endswith("TEMP"):
        wait_for_input()

def wait_for_input():
    input("Press Enter to continue...")

def list_save_backups(mode):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Choose a backup to " + mode + ":")
    save_folder = current_variables["path_to_noita_saves_folder"]
    backup_prefix = current_variables["backup_prefix"]
    backup_folders = [f for f in os.listdir(save_folder) if os.path.isdir(os.path.join(save_folder, f)) and f.startswith(backup_prefix)]
    backup_folders.sort()
    if not backup_folders:
        print("No backups found.")
        return
    choice = prompt_for_save_choice(backup_folders)
    if choice == 'x':
        return
    if mode == "delete":
        confirm_delete_backup(backup_folders[choice-1])
    else:
        activate_backup(backup_folders[choice-1])

def prompt_for_save_choice(backup_folders):
    for i, folder in enumerate(backup_folders):
        print(f"{i+1}. {folder}")
    choice = input("Enter the number of the backup to restore (type X to exit): ").strip()
    if choice.lower() == 'x':
        return 'x'
    try:
        choice = int(choice)
        if choice < 1 or choice > len(backup_folders):
            print("Invalid choice, please try again.")
            return prompt_for_save_choice(backup_folders)
        return choice
    except ValueError:
        print("Invalid choice, please try again.")
        return prompt_for_save_choice(backup_folders)

def activate_backup(choice):
    save_folder = current_variables["path_to_noita_saves_folder"]
    backup_folder = os.path.join(save_folder, choice)
    current_save_folder = os.path.join(save_folder, "save00")
    temp_backup_folder = os.path.join(save_folder, f"{current_variables['backup_prefix']}TEMP")
    print(f"Creating temporary backup of current save...")
    backup_save(current_save_folder, temp_backup_folder)
    print(f"Activating save...")
    try:
        restore_save(current_save_folder, backup_folder)
        print(f"Removing temporary backup...")
        shutil.rmtree(temp_backup_folder)
    except Exception as e:
        logging.error(f"Failed to activate save: {e}")
        print(f"Failed to activate save: {e}")
        print(f"Restoring temporary backup...")
        restore_save(current_save_folder, temp_backup_folder)
    wait_for_input()

def restore_save(current_save_folder, backup_folder):
    try:
        total_files = sum([len(files) for r, d, files in os.walk(backup_folder)])
        copied_files = [0]
        shutil.rmtree(current_save_folder)
        shutil.copytree(backup_folder, current_save_folder, copy_function=lambda src, dst: copy_with_progress(src, dst, total_files, copied_files))
        print("Save restored.")
        logging.info(" Save restored.")
    except Exception as e:
        logging.error(f"Failed to restore save: {e}")
        print(f"Failed to restore save: {e}")

def confirm_delete_backup(backup_folder):
    choice = input(f"Are you sure you want to delete {backup_folder}? (Y/N): ").strip().lower()
    if choice == 'y':
        delete_backup(backup_folder)
    elif choice == 'n':
        print("Deletion cancelled.")
    else:
        print("Invalid choice, please try again.")
        confirm_delete_backup(backup_folder)

def delete_backup(backup_folder):
    backup_folder = os.path.join(current_variables["path_to_noita_saves_folder"], backup_folder)
    try:
        shutil.rmtree(backup_folder)
        print("Backup deleted.")
        logging.info("Backup deleted.")
    except Exception as e:
        logging.error(f"Failed to delete backup: {e}")
        print(f"Failed to delete backup: {e}")
    wait_for_input()

def launch_noita():
    launch_subprocess_and_log_errors(current_variables["path_to_noita_exe"])

def launch_noita_mp_proxy():
    launch_subprocess_and_log_errors(current_variables["path_to_noita_mp_proxy"])

def change_path_to_noita_saves_folder():
    print("Please drag and drop the Noita save folder to the console.")
    path = input("Enter path: ").strip()
    if os.path.isdir(path):
        current_variables["path_to_noita_saves_folder"] = path
        print("Path to Noita save folder has been changed.")
        logging.info("Path to Noita save folder has been changed.")
    else:
        print("Invalid path. Please try again.")
        logging.warning("Invalid path entered for Noita save folder.")

def change_path_to_noita_mp_proxy():
    print("Please drag and drop the Noita MP Proxy to the console.")
    path = input("Enter path: ").strip()
    if os.path.isfile(path):
        current_variables["path_to_noita_mp_proxy"] = path
        print("Path to Noita MP Proxy has been changed.")
        logging.info("Path to Noita MP Proxy has been changed.")
    else:
        print("Invalid path. Please try again.")
        logging.warning("Invalid path entered for Noita MP Proxy.")

def save_current_variables():
    try:
        with open("variables.txt", "w") as f:
            for key in current_variables:
                f.write(f"{key}={current_variables[key]}\n")
        logging.info("Current variables saved successfully.")
    except Exception as e:
        logging.error(f"Failed to save current variables: {e}")
        print(f"Failed to save current variables: {e}")

def launch_subprocess_and_log_errors(command):
    try:
        result = subprocess.run(command, check=True)
        if result.returncode == 0:
            logging.info(f"Command executed successfully: {command}")
        else:
            logging.error(f"Command failed with return code {result.returncode}: {command}")
            print(f"Command failed with return code {result.returncode}: {command}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {e}")
        print(f"Command failed: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred: {e}")

def main():
    while True:
        print_menu("main_menu")
        choice = input("Enter choice: ").strip()
        main_menu_choice(choice)

if __name__ == "__main__":
    load_variables()
    main()