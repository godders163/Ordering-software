import os
import re
import csv
import time
import logging
import sys
from typing import Optional, Tuple

# --- Certifi patch for PyInstaller SSL issues ---
import certifi

# Detect PyInstaller bundle
if getattr(sys, "frozen", False):
    base_path = sys._MEIPASS
    logging.info("Running in a PyInstaller bundle. Base path: %s", base_path)
else:
    base_path = os.path.dirname(__file__)

cert_path = certifi.where()
os.environ['SSL_CERT_FILE'] = cert_path
logging.basicConfig(
    level=logging.DEBUG,  # Full debug output
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("Program.log", mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logging.getLogger("selenium").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager

WAIT_TIMEOUT = 10

# --- Login Constants ---
WEBSITE = "https://www.victoria-os.com/UI/Home/AAHcascade"

# --- XPaths ---
LOGIN_BUTTON = "/html/body/div/div[2]/section/div/div[1]/p[4]/a"
USERNAME_FIELD = "/html/body/div/div[2]/section/section/form/div[1]/fieldset/div[2]/input"
PASSWORD_FIELD = "/html/body/div/div[2]/section/section/form/div[1]/fieldset/div[4]/input"
SECOND_LOGIN_BUTTON = "/html/body/div/div[2]/section/section/form/div[1]/fieldset/div[6]/input"
CASCADE_ORDER_PAD = "/html/body/div/div[1]/header/div[2]/nav/div[2]/ul/li[3]/a"
SEND_BUTTON = "/html/body/div[1]/div[2]/form/div[1]/div[2]/div[2]/div/div/input[2]"

PRODUCT_FIELD = "/html/body/div[1]/div[2]/form/div[1]/div[2]/div[1]/div[2]/div[1]/input[4]"
QUANTITY_FIELD = "/html/body/div[1]/div[2]/form/div[1]/div[2]/div[1]/div[2]/div[2]/input"
ADD_BUTTON = "/html/body/div[1]/div[2]/form/div[1]/div[2]/div[1]/div[2]/div[2]/button"

POPUP_LIST_ID = "ui-id-1"
FIRST_DROPDOWN_ITEM_SELECTOR = "#ui-id-1 li.ui-menu-item a"

# --- CSV Cleaner ---
def clean_csv_columns(csv_path):
    logging.info("Cleaning CSV: %s", csv_path)
    drugs = []
    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            reader.fieldnames = [h.strip().strip('"') for h in reader.fieldnames]
            for row in reader:
                drug = {
                    "Pip code": row.get("Pip code"),
                    "Quantity": row.get("Quantity"),
                    "Drug name": row.get("Drug name")
                }
                if all(drug.values()):
                    drugs.append(drug)
            logging.info("Loaded %d valid drugs from CSV.", len(drugs))
    except FileNotFoundError:
        logging.critical("CSV file not found at %s. Exiting.", csv_path)
        sys.exit(1)
    except Exception as e:
        logging.error("Error cleaning CSV %s: %s", csv_path, e, exc_info=True)
    return drugs

# --- Environment variable helper ---
def set_victoria_credentials(USERNAME: str, PASSWORD: str):
    if not USERNAME or not PASSWORD:
        logging.critical("Credentials missing. Cannot proceed.")
        sys.exit(1)
    os.environ["VICTORIA_USER"] = USERNAME
    os.environ["VICTORIA_PASS"] = PASSWORD
    logging.info("Environment variables for Victoria credentials set.")

# --- Main Ordering Logic ---
def order_stuff(drugs, USERNAME, PASSWORD, SEND_STATUS, DELAY_SHORT, DELAY_MEDIUM):
    set_victoria_credentials(USERNAME, PASSWORD)

    def wait_for_element(driver, locator: Tuple[str, str], timeout=WAIT_TIMEOUT) -> Optional[WebElement]:
        try:
            return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))
        except Exception as e:
            logging.warning("Element not found: %s | %s", locator, e)
            return None

    def wait_and_click(driver, locator: Tuple[str, str], timeout=WAIT_TIMEOUT) -> bool:
        try:
            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))
            element.click()
            logging.debug("Clicked element: %s", locator)
            time.sleep(DELAY_SHORT)
            return True
        except Exception as e:
            logging.warning("Click failed for %s: %s", locator, e)
            return False

    def wait_and_send_keys(driver, locator: Tuple[str, str], text: str, timeout=WAIT_TIMEOUT) -> bool:
        element = wait_for_element(driver, locator, timeout)
        if element:
            try:
                element.clear()
                time.sleep(DELAY_SHORT)
                element.send_keys(text)
                logging.debug("Sent keys to element: %s | Text: %s", locator, text)
                time.sleep(DELAY_SHORT)
                return True
            except Exception as e:
                logging.warning("Send keys failed for %s: %s", locator, e)
        return False

    def setup_driver():
        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--log-level=3")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument(f"--ssl-cert-file={cert_path}")
        logging.info("Starting Chrome WebDriver with patched certifi path.")
        driver_path = ChromeDriverManager().install()
        logging.info("ChromeDriver installed at: %s", driver_path)
        return webdriver.Chrome(service=Service(driver_path), options=options)

    def login_and_navigate(driver):
        driver.get(WEBSITE)
        time.sleep(DELAY_MEDIUM)
        logging.info("Loaded login page.")
        if not wait_and_click(driver, (By.XPATH, LOGIN_BUTTON)): return False
        if not wait_and_send_keys(driver, (By.XPATH, USERNAME_FIELD), USERNAME): return False
        if not wait_and_send_keys(driver, (By.XPATH, PASSWORD_FIELD), PASSWORD): return False
        if not wait_and_click(driver, (By.XPATH, SECOND_LOGIN_BUTTON)): return False
        if not wait_and_click(driver, (By.XPATH, CASCADE_ORDER_PAD)): return False
        logging.info("Login successful. Navigated to order pad.")
        time.sleep(DELAY_MEDIUM)
        return True

    def try_order(drug, driver):
        pip_code, quantity, name = drug["Pip code"], drug["Quantity"], drug["Drug name"]
        logging.info("Attempting to order: %s | Code: %s | Qty: %s", name, pip_code, quantity)

        if not wait_and_send_keys(driver, (By.XPATH, PRODUCT_FIELD), pip_code):
            return (name, pip_code, quantity, "FAIL: Could not enter drug code")

        try:
            element = WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.visibility_of_element_located((By.ID, POPUP_LIST_ID))
            )
            site_drug_name = element.text.strip()
            logging.debug("Dropdown appeared with text: %s", site_drug_name)
            time.sleep(DELAY_SHORT)
        except Exception as e:
            logging.warning("Dropdown did not appear for %s: %s", name, e)
            return (name, pip_code, quantity, "FAIL: Dropdown did not appear")

        csv_first_word = name.split()[0].lower() if name else ""
        site_first_word = site_drug_name.split()[0].lower() if site_drug_name else ""
        logging.info("Name Check | CSV: '%s' | Website: '%s'", csv_first_word, site_first_word)

        if csv_first_word != site_first_word:
            return (name, pip_code, quantity, f"FAIL: Mismatch (CSV: {csv_first_word}, Site: {site_first_word})")

        if not wait_and_click(driver, (By.CSS_SELECTOR, FIRST_DROPDOWN_ITEM_SELECTOR)):
            return (name, pip_code, quantity, "FAIL: Could not select from dropdown")

        if not wait_and_send_keys(driver, (By.XPATH, QUANTITY_FIELD), quantity):
            return (name, pip_code, quantity, "FAIL: Could not enter quantity")

        if not wait_and_click(driver, (By.XPATH, ADD_BUTTON)):
            return (name, pip_code, quantity, "FAIL: Could not click 'Add' button")

        logging.info("Order added for: %s", name)
        return (name, pip_code, quantity, "Success")

    attempt, max_attempts = 1, 3
    to_order = drugs.copy()
    successful_orders, failed_orders = [], []

    while attempt <= max_attempts and to_order:
        logging.info("--- Starting Order Attempt %d of %d (%d items remaining) ---", attempt, max_attempts, len(to_order))
        driver = setup_driver()

        try:
            if not login_and_navigate(driver):
                logging.critical("Login failed. Cannot proceed with ordering.")
                break

            current_failed = []
            for i, drug in enumerate(to_order):
                logging.info("[%d/%d] Processing: %s", i + 1, len(to_order), drug['Drug name'])
                result = try_order(drug, driver)

                if result[3] == "Success":
                    logging.info("-> SUCCESS: %s ordered.", result[0])
                    successful_orders.append(result)
                else:
                    logging.warning("-> FAILED: %s. Reason: %s", result[0], result[3])
                    current_failed.append(drug)

        finally:
            if SEND_STATUS:
                wait_and_click(driver, (By.XPATH, SEND_BUTTON))
                logging.info("Clicked Send")
            driver.quit()
            logging.info("Driver session for attempt %d closed.", attempt)

        to_order = current_failed
        if to_order:
            time.sleep(DELAY_MEDIUM)
        attempt += 1

    for drug in to_order:
        failed_orders.append((drug["Drug name"], drug["Pip code"], drug["Quantity"], "Failed after 3 attempts"))

    logging.info("--- Order Summary ---")
    logging.info("%d items ordered successfully.", len(successful_orders))
    logging.warning("%d items failed after all attempts.", len(failed_orders))

    return successful_orders, failed_orders
