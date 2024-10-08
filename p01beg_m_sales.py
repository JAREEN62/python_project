from functools import singledispatch
from pathlib import Path
import csv

# Regions
VALID_REGIONS = {"w": "West", "m": "Mountain", "c": "Central", "e": "East"}
# Sales date
DATE_FORMAT = "%Y-%m-%d"
MIN_YEAR, MAX_YEAR = 2000, 2999
# Files
FILEPATH = Path(__file__).parent.parent / 'p01_files'
IMPORTED_FILES = 'imported_files.txt'
ALL_SALES = 'all_sales.csv'
NAMING_CONVENTION = "sales_qn_yyyy_r.csv"

# --------------- Sales Input and Files (Data Access) ------------------------
def input_amount() -> float:
    while True:
        entry = float(input(f"{'Amount:':20}"))
        if entry > 0:
            return entry
        else:
            print(f"Amount must be greater than zero.")

def input_int(entry_item: str, high: int, low: int = 1, fmt_width: int = 20) -> int:
    prompt = f"{entry_item.capitalize()} ({low}-{high}):"
    while True:
        entry = int(input(f"{prompt:{fmt_width}}"))
        if low <= entry <= high:
            return entry
        else:
            print(f"{entry_item.capitalize()} must be between {low} and {high}.")

def input_year() -> int:
    return input_int("year", MAX_YEAR, MIN_YEAR)

def input_month() -> int:
    return input_int("month", 12)

def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def cal_max_day(year: int, month: int) -> int:
    if month == 2:
        return 29 if is_leap_year(year) else 28
    elif month in (4, 6, 9, 11):
        return 30
    else:
        return 31

def input_day(year: int, month: int) -> int:
    max_day = cal_max_day(year, month)
    return input_int("day", max_day)

def is_valid_region(region_code: str) -> bool:
    return region_code in VALID_REGIONS

def get_region_name(region_code: str) -> str:
    return VALID_REGIONS[region_code]

def input_region_code() -> str:
    while True:
        fmt = 20
        valid_codes = tuple(VALID_REGIONS.keys())
        prompt = f"{f'Region {valid_codes}:':{fmt}}"
        code = input(prompt)
        if is_valid_region(code):
            return code
        else:
            print(f"Region must be one of the following: {valid_codes}.")

def input_date() -> str:
    while True:
        entry = input(f"{'Date (yyyy-mm-dd):':20}").strip()
        if len(entry) == 10 and entry[4] == '-' and entry[7] == '-' \
                and entry[:4].isdigit() and entry[5:7].isdigit() \
                and entry[8:].isdigit():
            yyyy, mm, dd = int(entry[:4]), int(entry[5:7]), int(entry[8:])
            if (1 <= mm <= 12) and (1 <= dd <= cal_max_day(yyyy, mm)):
                if MIN_YEAR <= yyyy <= MAX_YEAR:
                    return entry
                else:
                    print(f"Year of the date must be between {MIN_YEAR} and {MAX_YEAR}.")
            else:
                print(f"{entry} is not in a valid date format.")
        else:
            print(f"{entry} is not in a valid date format.")

def cal_quarter(month: int) -> int:
    if month in (1, 2, 3):
        return 1
    elif month in (4, 5, 6):
        return 2
    elif month in (7, 8, 9):
        return 3
    elif month in (10, 11, 12):
        return 4
    return 0

def correct_data_types(row):
    try:
        row[0] = float(row[0])
    except ValueError:
        row[0] = "?"
    if len(row[1]) == 10 and row[1][4] == '-' and row[1][7] == '-' \
            and row[1][:4].isdigit() and row[1][5:7].isdigit() and row[1][8:10].isdigit():
        yyyy, mm, dd = int(row[1][:4]), int(row[1][5:7]), int(row[1][8:10])
        if not (1 <= mm <= 12) or not (1 <= dd <= cal_max_day(yyyy, mm)):
            row[1] = "?"
    else:
        row[1] = "?"

def has_bad_amount(data: dict) -> bool:
    return data["amount"] == "?"

def has_bad_date(data: dict) -> bool:
    return data["sales_date"] == "?"

def has_bad_data(data: dict) -> bool:
    return has_bad_amount(data) or has_bad_date(data)

def from_input1():
    amount = input_amount()
    year = input_year()
    month = input_month()
    day = input_day(year, month)
    sales_date = f"{year}-{str(month).zfill(2)}-{day:02}"
    region_code = input_region_code()
    return {"amount": amount, "sales_date": sales_date, "region": region_code}

def from_input2():
    amount = input_amount()
    sales_date = input_date()
    region_code = input_region_code()
    return {"amount": amount, "sales_date": sales_date, "region": region_code}

def is_valid_filename_format(filename):
    return filename.startswith("sales_q") and filename.endswith(".csv") and len(filename) >= 14

def get_region_code(sales_filename: str) -> str:
    return sales_filename[-5]  # Assumes the region code is the character before the extension

def already_imported(filepath_name: Path) -> bool:
    with open(FILEPATH / IMPORTED_FILES, 'r') as file:
        return filepath_name.name in file.read()

def add_imported_file(filepath_name: Path):
    with open(FILEPATH / IMPORTED_FILES, 'a') as file:
        file.write(filepath_name.name + '\n')

@singledispatch
def import_sales(filepath_name: Path, delimiter: str = ',') -> list:
    with open(filepath_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        filename = filepath_name.name
        region_code = get_region_code(filename)
        imported_sales_list = []
        for amount_sales_date in reader:
            correct_data_types(amount_sales_date)
            amount, sales_date = amount_sales_date[0], amount_sales_date[1]
            data = {"amount": amount, "sales_date": sales_date, "region": region_code}
            imported_sales_list.append(data)
        return imported_sales_list

def import_all_sales() -> list:
    try:
        with open(FILEPATH / ALL_SALES, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            return [row for row in reader]
    except FileNotFoundError:
        return []

def view_sales(sales_list: list) -> bool:
    col1_w, col2_w, col3_w, col4_w, col5_w = 5, 15, 15, 15, 15
    bad_data_flag = False
    if not sales_list:
        print("No sales to view.\n")
    else:
        total_w = col1_w + col2_w + col3_w + col4_w + col5_w
        print(f"{' ':{col1_w}}{'Date':{col2_w}}{'Quarter':{col3_w}}{'Region':{col4_w}}{'Amount':>{col5_w}}")
        print(horizontal_line := f"{'-' * total_w}")
        total = 0.0

        for idx, sales in enumerate(sales_list, start=1):
            if has_bad_data(sales):
                bad_data_flag = True
                num = f"{idx}.*"
            else:
                num = f"{idx}."

            amount = sales["amount"]
            if not has_bad_amount(sales):
                total += amount

            sales_date = sales["sales_date"]
            if has_bad_date(sales):
                bad_data_flag = True
                month = 0
            else:
                month = int(sales_date.split("-")[1])

            region = get_region_name(sales["region"])
            quarter = f"{cal_quarter(month)}"
            print(f"{num:<{col1_w}}{sales_date:{col2_w}}{quarter:<{col3_w}}{region:{col4_w}}{amount:>{col5_w}}")

        print(horizontal_line)
        print(f"{'TOTAL':{col1_w}}{' ':{col2_w + col3_w + col4_w}}{total:>{col5_w}}\n")
    return bad_data_flag

def add_sales1(sales_list) -> None:
    sales_data = from_input1()
    sales_list.append(sales_data)
    print("Sales data added successfully.\n")

def add_sales2(sales_list) -> None:
    sales_data = from_input2()
    sales_list.append(sales_data)
    print("Sales data added successfully.\n")

def main():
    sales_list = import_all_sales()
    while True:
        print("1. Add Sales Data (input 1)")
        print("2. Add Sales Data (input 2)")
        print("3. View Sales Data")
        print("4. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            add_sales1(sales_list)
        elif choice == '2':
            add_sales2(sales_list)
        elif choice == '3':
            view_sales(sales_list)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
