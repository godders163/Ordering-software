import sys
import os
import logging
import json
import subprocess
import argparse
import requests
import certifi
import ctypes

from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QLineEdit
from PyQt6.QtGui import QIcon

# --- Local modules ---
from Ui_Main import Ui_Form  # renamed UI file to Ui_Main.py
from CSV_Cleaner import main as clean_csv
from Pip_code_ordering import clean_csv_columns, order_stuff
from send_order_summary import create_pdf, email_results as send_email_report

# --- Logging setup ---
log_file = "Program.log"
if getattr(sys, 'frozen', False):
    log_file = os.path.join(os.path.dirname(sys.executable), "Program.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode="w", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# --- Config file path ---
CONFIG_FILE = os.path.join(
    getattr(sys, 'frozen', False) and os.path.dirname(sys.executable) or os.path.dirname(os.path.abspath(__file__)),
    "config.json"
)




def load_config() -> dict:
    defaults = {
        "short_delay": 1.0,
        "medium_delay": 1.2,
        "username": "",
        "password": "",
        "email": "",
        "email_results": False,
        "send_results": False
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            defaults.update(data)
        except Exception as e:
            logging.warning(f"Failed to load config.json, using defaults: {e}")
    return defaults

def save_config(config: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        logging.error(f"Failed to save configuration: {e}")

# --- Processing logic ---
def run_processing_logic(config: dict):
    logging.info("--- Background process started ---")
    original_path = config.get("file_path")
    if not original_path or not os.path.exists(original_path):
        logging.error(f"Input file path not found: {original_path}. Exiting.")
        sys.exit(1)

    password = config.get("password")
    if not password:
        logging.critical("Password missing. Cannot proceed.")
        sys.exit(1)

    logging.info(f"Processing file: {original_path}")
    cleaned_path = ""
    try:
        cleaned_path = clean_csv(original_path)
        drugs = clean_csv_columns(cleaned_path)
        success, failure = order_stuff(
            drugs,
            config["username"],
            password,
            config["send_results"],
            config["short_delay"],
            config["medium_delay"]
        )

        summary_text = (
            f"Automated ordering complete.\n"
            f"Attempted: {len(drugs)}, Success: {len(success)}, Failed: {len(failure)}"
        )
        logging.info(summary_text)

        if config.get("email_results"):
            pdf_path = create_pdf(success, failure, summary_text)
            if send_email_report(pdf_path, config["email"]):
                logging.info("Summary report emailed successfully.")
            if pdf_path and os.path.exists(pdf_path):
                os.remove(pdf_path)

    except Exception as e:
        logging.critical(f"An error occurred during processing: {e}", exc_info=True)
    finally:
        if cleaned_path and os.path.exists(cleaned_path):
            os.remove(cleaned_path)
        logging.info("--- Background process finished ---")

# --- Helper for icon path ---
def get_image_path(filename: str) -> str | None:
    base_dir = getattr(sys, 'frozen', False) and os.path.dirname(sys.executable) or os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, filename)
    return full_path if os.path.exists(full_path) else None

# --- MainWindow ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self, get_image_path_func=get_image_path)
        self.setWindowTitle("FullSpeed Ordering")

        # --- Load config ---
        self.config = load_config()
        self._load_config_to_widgets()
        self._connect_signals()

        #DELETE LATER AFTER DEBUGGING
        # --- Debug certifi and requests paths ---
        logging.info("certifi.where(): %s", certifi.where())
        logging.info("file exists: %s", os.path.isfile(certifi.where()))
        logging.info("requests.utils.DEFAULT_CA_BUNDLE_PATH: %s", requests.utils.DEFAULT_CA_BUNDLE_PATH)
        ##################################################################################################

    def _load_config_to_widgets(self):
        self.ui.short_delay_box.setValue(self.config.get("short_delay", 1.0))
        self.ui.medium_delay_box.setValue(self.config.get("medium_delay", 1.2))
        self.ui.username_box.setText(self.config.get("username", ""))
        self.ui.password_box.setEchoMode(QLineEdit.EchoMode.Password)
        self.ui.email_box.setText(self.config.get("email", ""))
        self.ui.email_checkbox.setChecked(self.config.get("email_results", False))
        self.ui.send_checkbox.setChecked(self.config.get("send_results", False))

    def _connect_signals(self):
        self.ui.short_delay_box.valueChanged.connect(lambda v: self._update_config("short_delay", v))
        self.ui.medium_delay_box.valueChanged.connect(lambda v: self._update_config("medium_delay", v))
        self.ui.username_box.textChanged.connect(lambda t: self._update_config("username", t))
        self.ui.password_box.textChanged.connect(lambda t: self._update_config("password", t))
        self.ui.email_box.textChanged.connect(lambda t: self._update_config("email", t))
        self.ui.email_checkbox.stateChanged.connect(lambda s: self._update_config("email_results", bool(s)))
        self.ui.send_checkbox.stateChanged.connect(lambda s: self._update_config("send_results", bool(s)))
        self.ui.start_button.clicked.connect(self._on_start_button_pressed)

    def _update_config(self, key, value):
        self.config[key] = value
        save_config(self.config)

    def _on_start_button_pressed(self):
        file_path = self._select_file()
        if not file_path:
            return
        self.config["file_path"] = file_path
        save_config(self.config)

        if not self.config.get("password"):
            QMessageBox.warning(self, "Password missing", "Please enter a password.")
            return

        args = [
            sys.executable,
            __file__,
            "--run-main",
            "--config-file", CONFIG_FILE,
            "--password", self.config["password"]
        ]
        if sys.platform == "win32":
            subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(args)
        self.close()

    def _select_file(self) -> str | None:
        file_name, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        return file_name

# --- CLI entry point ---
def main_cli():
    parser = argparse.ArgumentParser(description="Ordering process runner.")
    parser.add_argument("--run-main", action="store_true")
    parser.add_argument("--config-file", type=str, required=True)
    parser.add_argument("--password", type=str, help="Plain password for ordering")
    args = parser.parse_args()

    with open(args.config_file, "r", encoding="utf-8") as f:
        config = json.load(f)
    if args.password:
        config["password"] = args.password

    run_processing_logic(config)

# --- Main ---
if __name__ == "__main__":
    if "--run-main" in sys.argv:
        main_cli()
    else:
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("mycompany.fullspeedordering")
        except Exception:
            pass

        app = QApplication(sys.argv)
        icon_path = get_image_path("Newport_Logo.ico")
        if icon_path:
            app.setWindowIcon(QIcon(icon_path))
        window = MainWindow()
        if icon_path:
            window.setWindowIcon(QIcon(icon_path))
        window.show()
        sys.exit(app.exec())
 