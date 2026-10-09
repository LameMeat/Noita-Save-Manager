import logging
import os
import shutil
import subprocess
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, simpledialog

# Configure custom logger
logger = logging.getLogger('NoitaSaveManager')
handler = logging.FileHandler('noita_save_manager.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

username = os.getlogin()

default_variables = {
    "path_to_noita_saves_folder": f"C:/Users/{username}/AppData/LocalLow/Nolla_Games_Noita",
    "path_to_noita_mp_proxy": f"C:/Users/{username}/AppData/LocalLow/Nolla_Games_Noita/NoitaMPProxy.exe",
    "path_to_noita_exe": "C:/Program Files (x86)/Steam/steamapps/common/Noita/noita.exe",
    "backup_prefix": "BACKUP_"
}

current_variables = default_variables.copy()

def load_variables():
    try:
        with open("variables.txt", "r") as f:
            for line in f:
                key, value = line.split("=")
                current_variables[key] = value.strip()
        logger.info("Variables loaded successfully.")
    except FileNotFoundError:
        logger.warning("Variables file not found, using default variables.")
        print("Variables file not found, using default variables.")
    except Exception as e:
        logger.error(f"Error loading variables: {e}")
        print(f"Error loading variables: {e}")

def save_current_variables():
    try:
        with open("variables.txt", "w") as f:
            f.writelines(f"{key}={current_variables[key]}\n" for key in current_variables)
        logger.info("Current variables saved successfully.")
    except Exception as e:
        logger.error(f"Failed to save current variables: {e}")
        print(f"Failed to save current variables: {e}")

def launch_subprocess_and_log_errors(command):
    try:
        result = subprocess.run(command, check=True)
        if result.returncode == 0:
            logger.info(f"Command executed successfully: {command}")
        else:
            logger.error(f"Command failed with return code {result.returncode}: {command}")
            print(f"Command failed with return code {result.returncode}: {command}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        print(f"Command failed: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred: {e}")

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
        logger.info(f"Backup created at {backup_folder_path}")
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        print(f"Failed to create backup: {e}")

def restore_save(current_save_folder, backup_folder):
    try:
        total_files = sum([len(files) for r, d, files in os.walk(backup_folder)])
        copied_files = [0]
        shutil.rmtree(current_save_folder)
        shutil.copytree(backup_folder, current_save_folder, copy_function=lambda src, dst: copy_with_progress(src, dst, total_files, copied_files))
        print("Save restored.")
        logger.info("Save restored.")
    except Exception as e:
        logger.error(f"Failed to restore save: {e}")
        print(f"Failed to restore save: {e}")

def confirm_delete_backup(backup_folder):
    choice = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {backup_folder}?")
    if choice:
        delete_backup(backup_folder)

def delete_backup(backup_folder):
    backup_folder = os.path.join(current_variables["path_to_noita_saves_folder"], backup_folder)
    try:
        shutil.rmtree(backup_folder)
        print("Backup deleted.")
        logger.info("Backup deleted.")
    except Exception as e:
        logger.error(f"Failed to delete backup: {e}")
        print(f"Failed to delete backup: {e}")

def name_backup_save():
    save_name = simpledialog.askstring("Backup Save", "Enter a name for the backup save (type nothing and hit enter to cancel):")
    if not save_name:
        return
    backup_name = f"{current_variables['backup_prefix']}{save_name}_"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_folder_name = f"{backup_name}{timestamp}"
    backup_folder_path = os.path.join(current_variables["path_to_noita_saves_folder"], backup_folder_name)
    current_save_folder = os.path.join(current_variables["path_to_noita_saves_folder"], "save00")
    backup_save(current_save_folder, backup_folder_path)

def list_save_backups(mode):
    save_folder = current_variables["path_to_noita_saves_folder"]
    backup_prefix = current_variables["backup_prefix"]
    backup_folders = [f for f in os.listdir(save_folder) if os.path.isdir(os.path.join(save_folder, f)) and f.startswith(backup_prefix)]
    backup_folders.sort()
    if not backup_folders:
        messagebox.showinfo("No Backups", "No backups found.")
        return
    choice = simpledialog.askinteger("Choose Backup", "Enter the number of the backup to " + mode + ":",
                                      minvalue=1, maxvalue=len(backup_folders))
    if choice is None:
        return
    if mode == "delete":
        confirm_delete_backup(backup_folders[choice-1])
    else:
        activate_backup(backup_folders[choice-1])

def activate_backup(choice):
    save_folder = current_variables["path_to_noita_saves_folder"]
    backup_folder = os.path.join(save_folder, choice)
    current_save_folder = os.path.join(save_folder, "save00")
    temp_backup_folder = os.path.join(save_folder, f"{current_variables['backup_prefix']}TEMP")
    print("Creating temporary backup of current save...")
    backup_save(current_save_folder, temp_backup_folder)
    print("Activating save...")
    try:
        restore_save(current_save_folder, backup_folder)
        print("Removing temporary backup...")
        shutil.rmtree(temp_backup_folder)
    except Exception as e:
        logger.error(f"Failed to activate save: {e}")
        print(f"Failed to activate save: {e}")
        print("Restoring temporary backup...")
        restore_save(current_save_folder, temp_backup_folder)

def change_path_to_noita_saves_folder():
    path = filedialog.askdirectory()
    if os.path.isdir(path):
        current_variables["path_to_noita_saves_folder"] = path
        save_current_variables()
        messagebox.showinfo("Success", "Path to Noita save folder has been changed.")
        logger.info("Path to Noita save folder has been changed.")
    else:
        messagebox.showwarning("Invalid Path", "Invalid path. Please try again.")
        logger.warning("Invalid path entered for Noita save folder.")

def change_path_to_noita_mp_proxy():
    path = filedialog.askopenfilename()
    if os.path.isfile(path):
        current_variables["path_to_noita_mp_proxy"] = path
        save_current_variables()
        messagebox.showinfo("Success", "Path to Noita MP Proxy has been changed.")
        logger.info("Path to Noita MP Proxy has been changed.")
    else:
        messagebox.showwarning("Invalid Path", "Invalid path. Please try again.")
        logger.warning("Invalid path entered for Noita MP Proxy.")

def launch_noita():
    launch_subprocess_and_log_errors([current_variables["path_to_noita_exe"]])

def launch_noita_mp_proxy():
    launch_subprocess_and_log_errors([current_variables["path_to_noita_mp_proxy"]])

def create_main_window():
    root = tk.Tk()
    root.title("Noita Save Manager")

    def on_backup_save():
        name_backup_save()

    def on_activate_save():
        list_save_backups("activate")

    def on_delete_backup():
        list_save_backups("delete")

    def on_settings():
        create_settings_window(root)

    def on_help():
        messagebox.showinfo("Help", "1. Backup Current Save: Create a backup of your current Noita save.\n"
                                    "2. Activate Save: Restore a previously created backup.\n"
                                    "5. Delete Backup: Delete a previously created backup.\n"
                                    "7. Help: Display this help message.\n"
                                    "9. Exit: Exit the application.")

    def on_exit():
        root.destroy()

    buttons = [
        ("Backup Current Save", on_backup_save),
        ("Activate Save", on_activate_save),
        ("Delete Backup", on_delete_backup),
        ("Settings", on_settings),
        ("Help", on_help),
        ("Exit", on_exit)
    ]

    for (text, command) in buttons:
        button = tk.Button(root, text=text, command=command)
        button.pack(pady=5)

    return root

def create_settings_window(parent):
    settings_window = tk.Toplevel(parent)
    settings_window.title("Settings")

    def on_save_and_return():
        save_current_variables()
        settings_window.destroy()

    def on_restore_defaults():
        global current_variables
        current_variables = default_variables.copy()
        save_current_variables()
        messagebox.showinfo("Success", "Default settings restored.")
        logger.info("Default settings restored.")

    tk.Label(settings_window, text="Path to Noita Save Folder:").pack(pady=5)
    entry_save_folder = tk.Entry(settings_window, width=50)
    entry_save_folder.insert(0, current_variables["path_to_noita_saves_folder"])
    entry_save_folder.pack(pady=5)

    def on_change_save_folder():
        path = filedialog.askdirectory()
        if os.path.isdir(path):
            entry_save_folder.delete(0, tk.END)
            entry_save_folder.insert(0, path)

    tk.Button(settings_window, text="Browse", command=on_change_save_folder).pack(pady=5)

    tk.Label(settings_window, text="Path to Noita MP Proxy:").pack(pady=5)
    entry_mp_proxy = tk.Entry(settings_window, width=50)
    entry_mp_proxy.insert(0, current_variables["path_to_noita_mp_proxy"])
    entry_mp_proxy.pack(pady=5)

    def on_change_mp_proxy():
        path = filedialog.askopenfilename()
        if os.path.isfile(path):
            entry_mp_proxy.delete(0, tk.END)
            entry_mp_proxy.insert(0, path)

    tk.Button(settings_window, text="Browse", command=on_change_mp_proxy).pack(pady=5)

    buttons = [
        ("Save & Return to Main Menu", on_save_and_return),
        ("Restore default settings", on_restore_defaults)
    ]

    for (text, command) in buttons:
        button = tk.Button(settings_window, text=text, command=command)
        button.pack(pady=5)

if __name__ == "__main__":
    load_variables()
    root = create_main_window()
    root.mainloop()
