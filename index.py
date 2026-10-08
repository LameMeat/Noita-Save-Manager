import os
from datetime import datetime
import logging
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog

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

def load_variables():
    try:
        with open("variables.txt", "r") as f:
            for line in f:
                key, value = line.split("=")
                current_variables[key] = value.strip()
        logging.info("Variables loaded successfully.")
    except FileNotFoundError:
        logging.warning("Variables file not found, using default variables.")
    except Exception as e:
        logging.error(f"Error loading variables: {e}")

def save_current_variables():
    try:
        with open("variables.txt", "w") as f:
            for key in current_variables:
                f.write(f"{key}={current_variables[key]}\n")
        logging.info("Current variables saved successfully.")
    except Exception as e:
        logging.error(f"Failed to save current variables: {e}")

def backup_save(save_name):
    save_folder = current_variables["path_to_noita_saves_folder"]
    if not save_name:
        messagebox.showwarning("Invalid Input", "Backup name cannot be empty.")
        return
    backup_name = f"{current_variables['backup_prefix']}{save_name}_"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_folder_name = f"{backup_name}{timestamp}"
    backup_folder_path = os.path.join(save_folder, backup_folder_name)
    current_save_folder = os.path.join(save_folder, "save00")
    try:
        shutil.copytree(current_save_folder, backup_folder_path)
        messagebox.showinfo("Success", f"Backup created at {backup_folder_path}")
        logging.info(f"Backup created at {backup_folder_path}")
    except Exception as e:
        logging.error(f"Failed to create backup: {e}")
        messagebox.showerror("Error", f"Failed to create backup: {e}")

def list_save_backups(mode):
    save_folder = current_variables["path_to_noita_saves_folder"]
    backup_prefix = current_variables["backup_prefix"]
    backup_folders = [f for f in os.listdir(save_folder) if os.path.isdir(os.path.join(save_folder, f)) and f.startswith(backup_prefix)]
    backup_folders.sort()
    if not backup_folders:
        messagebox.showinfo("No Backups", "No backups found.")
        return
    choice = simpledialog.askinteger("Choose Backup", "Enter the number of the backup to " + mode + " (type X to exit):", minvalue=1, maxvalue=len(backup_folders))
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
    try:
        shutil.copytree(current_save_folder, temp_backup_folder)
        restore_save(current_save_folder, backup_folder)
        shutil.rmtree(temp_backup_folder)
        messagebox.showinfo("Success", "Save restored.")
        logging.info("Save restored.")
    except Exception as e:
        logging.error(f"Failed to activate save: {e}")
        messagebox.showerror("Error", f"Failed to activate save: {e}")
        try:
            restore_save(current_save_folder, temp_backup_folder)
            shutil.rmtree(temp_backup_folder)
        except Exception as e:
            logging.error(f"Failed to restore temporary backup: {e}")

def restore_save(current_save_folder, backup_folder):
    try:
        shutil.rmtree(current_save_folder)
        shutil.copytree(backup_folder, current_save_folder)
    except Exception as e:
        logging.error(f"Failed to restore save: {e}")
        raise

def confirm_delete_backup(backup_folder):
    choice = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {backup_folder}?")
    if choice:
        delete_backup(backup_folder)

def delete_backup(backup_folder):
    backup_folder_path = os.path.join(current_variables["path_to_noita_saves_folder"], backup_folder)
    try:
        shutil.rmtree(backup_folder_path)
        messagebox.showinfo("Success", "Backup deleted.")
        logging.info("Backup deleted.")
    except Exception as e:
        logging.error(f"Failed to delete backup: {e}")
        messagebox.showerror("Error", f"Failed to delete backup: {e}")

def launch_noita():
    launch_subprocess_and_log_errors(current_variables["path_to_noita_exe"])

def launch_noita_mp_proxy():
    launch_subprocess_and_log_errors(current_variables["path_to_noita_mp_proxy"])

def change_path_to_noita_saves_folder():
    path = filedialog.askdirectory()
    if os.path.isdir(path):
        current_variables["path_to_noita_saves_folder"] = path
        save_current_variables()
        messagebox.showinfo("Success", "Path to Noita save folder has been changed.")
        logging.info("Path to Noita save folder has been changed.")
    else:
        messagebox.showwarning("Invalid Path", "Invalid path. Please try again.")
        logging.warning("Invalid path entered for Noita save folder.")

def change_path_to_noita_mp_proxy():
    path = filedialog.askopenfilename()
    if os.path.isfile(path):
        current_variables["path_to_noita_mp_proxy"] = path
        save_current_variables()
        messagebox.showinfo("Success", "Path to Noita MP Proxy has been changed.")
        logging.info("Path to Noita MP Proxy has been changed.")
    else:
        messagebox.showwarning("Invalid Path", "Invalid path. Please try again.")
        logging.warning("Invalid path entered for Noita MP Proxy.")

def launch_subprocess_and_log_errors(command):
    try:
        result = subprocess.run(command, check=True)
        if result.returncode == 0:
            logging.info(f"Command executed successfully: {command}")
        else:
            logging.error(f"Command failed with return code {result.returncode}: {command}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

def create_main_window():
    root = tk.Tk()
    root.title("Noita Save Manager")

    def on_backup_save():
        save_name = simpledialog.askstring("Backup Name", "Enter a name for the backup save (type nothing and hit enter to cancel):")
        backup_save(save_name)

    def on_activate_save():
        list_save_backups("activate")

    def on_delete_backup():
        list_save_backups("delete")

    def on_settings():
        settings_window = tk.Toplevel(root)
        settings_window.title("Settings")

        def on_change_noita_saves_folder():
            change_path_to_noita_saves_folder()
            settings_window.destroy()

        def on_change_noita_mp_proxy():
            change_path_to_noita_mp_proxy()
            settings_window.destroy()

        def on_restore_default_settings():
            current_variables.update(default_variables)
            save_current_variables()
            messagebox.showinfo("Success", "Default settings restored.")
            logging.info("Default settings restored.")
            settings_window.destroy()

        tk.Button(settings_window, text="Change path to Noita save folder", command=on_change_noita_saves_folder).pack(pady=5)
        tk.Button(settings_window, text="Change path to Noita MP Proxy", command=on_change_noita_mp_proxy).pack(pady=5)
        tk.Button(settings_window, text="Restore default settings", command=on_restore_default_settings).pack(pady=5)

    def on_help():
        help_message = (
            "Noita Save Manager Help\n"
            "-----------------------\n"
            "1. Backup Current Save: Create a backup of your current Noita save.\n"
            "2. Activate Save: Restore a previously created backup.\n"
            "5. Delete Backup: Delete a previously created backup.\n"
            "7. Help: Display this help message.\n"
            "9. Exit: Exit the application.\n\n"
            "Use the Settings menu to change paths to Noita save folder and Noita MP Proxy."
        )
        messagebox.showinfo("Help", help_message)

    def on_exit():
        root.destroy()

    tk.Button(root, text="Backup Current Save", command=on_backup_save).pack(pady=5)
    tk.Button(root, text="Activate Save", command=on_activate_save).pack(pady=5)
    tk.Button(root, text="Delete Backup", command=on_delete_backup).pack(pady=5)
    tk.Button(root, text="Settings", command=on_settings).pack(pady=5)
    tk.Button(root, text="Help", command=on_help).pack(pady=5)
    tk.Button(root, text="Exit", command=on_exit).pack(pady=5)

    return root

if __name__ == "__main__":
    load_variables()
    root = create_main_window()
    root.mainloop()
