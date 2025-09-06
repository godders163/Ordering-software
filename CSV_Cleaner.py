import csv
import os
import sys
import logging

# --- Functions ---

def clean_csv_columns(csv_path):
    print(f"Reading and cleaning CSV columns from: {csv_path}")
    drugs = []

    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            if reader.fieldnames is None:
                print("CSV file has no headers.")
                return drugs

            # Strip quotes from headers
            reader.fieldnames = [h.strip('"') for h in reader.fieldnames]

            for row in reader:
                drug = {
                    "Drug name": row.get("textBox11", "").strip(),
                    "Price": row.get("textBox12", "").strip(),
                    "Pip code": row.get("textBox10", "").strip(),
                    "Quantity": row.get("textBox9", "").strip()
                }

                if drug["Drug name"] and drug["Pip code"]:
                    drugs.append(drug)

        print(f"Extracted {len(drugs)} valid drug entries.")
    except Exception as e:
        print(f"Error while reading CSV: {e}")

    return drugs


def write_csv(drug_list, new_csv_name):
    print(f"Writing cleaned data to: {new_csv_name}")

    try:
        with open(new_csv_name, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Drug name', 'Price', 'Pip code', 'Quantity']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for drug in drug_list:
                writer.writerow(drug)

        print(f"Successfully wrote {len(drug_list)} drugs to CSV.")
    except Exception as e:
        print(f"Failed to write CSV: {e}")


def rename_csv():
    script_path = os.path.abspath(sys.argv[0])
    script_dir = os.path.dirname(script_path)
    new_csv_name = os.path.join(script_dir, "Order item summary.csv")
    print(f"Output CSV will be: {new_csv_name}")
    return new_csv_name


def main(original_path):
    print("🧹 Cleaning CSV...")
    print("Starting CSV cleaning process.")

    cleaned_path = rename_csv()
    drugs = clean_csv_columns(original_path)
    write_csv(drugs, cleaned_path)

    print(f"📄 Cleaned CSV ready: {cleaned_path}")
    print(f"Cleaning process completed. Cleaned CSV at: {cleaned_path}")
    return cleaned_path
