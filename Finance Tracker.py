import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.font import Font
import json
import os
import matplotlib.pyplot as plt

# Default configuration
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "file_name": "finance_data.csv",
    "theme": "light",
    "primary_color": "#4CAF50",  # Green
    "secondary_color": "#f44336",  # Red
    "title": "Personal Finance Tracker",
}

# Load or initialize configuration
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

# Initialize CSV file if not present
def initialize_file(file_name):
    try:
        with open(file_name, "r"):
            pass
    except FileNotFoundError:
        with open(file_name, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Type", "Amount", "Category", "Description"])

# Add a transaction
def add_transaction(config, transaction_type, amount, category, description):
    try:
        amount = float(amount)
        with open(config["file_name"], "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([transaction_type, amount, category, description])
        messagebox.showinfo("Success", f"Transaction added: {transaction_type} - ${amount:.2f} in {category}.")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid amount.")

# View transactions
def view_transactions(config):
    try:
        with open(config["file_name"], "r") as file:
            reader = csv.reader(file)
            transactions = list(reader)
            if len(transactions) > 1:
                transactions_window = tk.Toplevel()
                transactions_window.title("All Transactions")
                transactions_window.geometry("800x500")

                tree = ttk.Treeview(transactions_window, columns=("Type", "Amount", "Category", "Description"), show="headings")
                tree.heading("Type", text="Type")
                tree.heading("Amount", text="Amount")
                tree.heading("Category", text="Category")
                tree.heading("Description", text="Description")
                tree.pack(fill=tk.BOTH, expand=True)

                for row in transactions[1:]:
                    tree.insert("", tk.END, values=row)
            else:
                messagebox.showinfo("No Transactions", "No transactions found.")
    except FileNotFoundError:
        messagebox.showerror("Error", "No transactions file found. Start by adding transactions.")

# Generate report with Pie Chart
def generate_report(config):
    try:
        income, expenses = 0, 0
        with open(config["file_name"], "r") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                if row[0] == "Income":
                    income += float(row[1])
                elif row[0] == "Expense":
                    expenses += float(row[1])
        
        plt.pie([income, expenses], labels=["Income", "Expenses"], autopct='%1.1f%%', colors=["#4CAF50", "#f44336"])
        plt.title("Income vs Expenses", fontsize=16, fontweight="bold")
        plt.show()
    except FileNotFoundError:
        messagebox.showerror("Error", "No transactions found. Start by adding transactions.")

# Main App
def main_app():
    config = load_config()
    initialize_file(config["file_name"])

    root = tk.Tk()
    root.title(config["title"])
    root.geometry("600x500")

    primary_color = config.get("primary_color", "#4CAF50")
    secondary_color = config.get("secondary_color", "#f44336")

    # Custom Fonts
    title_font = Font(family="Helvetica", size=20, weight="bold")
    button_font = Font(family="Verdana", size=12, weight="bold")
    label_font = Font(family="Georgia", size=14, weight="normal")

    style = ttk.Style()
    style.configure("TButton", font=button_font, padding=10)
    style.map("TButton", background=[("active", secondary_color)], foreground=[("active", "white")])

    frame = ttk.Frame(root, padding=20)
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text=config["title"], font=title_font, foreground=primary_color).pack(pady=20)

    # Button Row
    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=10)

    ttk.Button(button_frame, text="Add Income", command=lambda: open_transaction_window(config, "Income"), style="TButton").grid(row=0, column=0, padx=10)
    ttk.Button(button_frame, text="Add Expense", command=lambda: open_transaction_window(config, "Expense"), style="TButton").grid(row=0, column=1, padx=10)
    ttk.Button(button_frame, text="View Transactions", command=lambda: view_transactions(config), style="TButton").grid(row=0, column=2, padx=10)
    ttk.Button(button_frame, text="Generate Report", command=lambda: generate_report(config), style="TButton").grid(row=0, column=3, padx=10)
    ttk.Button(button_frame, text="Export Transactions", command=lambda: export_transactions(config), style="TButton").grid(row=0, column=4, padx=10)

    root.mainloop()

# Filter transactions by month and year
def filter_transactions(config):
    filter_window = tk.Toplevel()
    filter_window.title("Filter Transactions by Month and Year")
    filter_window.geometry("400x300")

    ttk.Label(filter_window, text="Select Month:", font=("Georgia", 14)).pack(pady=10)
    month_combobox = ttk.Combobox(filter_window, values=[
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ])
    month_combobox.pack(pady=5)

    ttk.Label(filter_window, text="Select Year:", font=("Georgia", 14)).pack(pady=10)
    year_combobox = ttk.Combobox(filter_window, values=[str(year) for year in range(2000, 2101)])
    year_combobox.pack(pady=5)

    def apply_filter():
        selected_month = month_combobox.get()
        selected_year = year_combobox.get()
        if not selected_month or not selected_year:
            messagebox.showerror("Error", "Please select both month and year.")
            return

        try:
            with open(config["file_name"], "r") as file:
                reader = csv.reader(file)
                transactions = list(reader)

            # Month index mapping for comparison
            month_mapping = {
                "January": "01", "February": "02", "March": "03", "April": "04",
                "May": "05", "June": "06", "July": "07", "August": "08",
                "September": "09", "October": "10", "November": "11", "December": "12"
            }

            filtered_transactions = [
                row for row in transactions[1:]  # Exclude header
                if f"{selected_year}-{month_mapping[selected_month]}" in row[3]  # Assuming 'Description' holds the date
            ]

            if filtered_transactions:
                filtered_window = tk.Toplevel()
                filtered_window.title(f"Transactions for {selected_month} {selected_year}")
                filtered_window.geometry("800x500")

                tree = ttk.Treeview(filtered_window, columns=("Type", "Amount", "Category", "Description"), show="headings")
                tree.heading("Type", text="Type")
                tree.heading("Amount", text="Amount")
                tree.heading("Category", text="Category")
                tree.heading("Description", text="Description")
                tree.pack(fill=tk.BOTH, expand=True)

                for row in filtered_transactions:
                    tree.insert("", tk.END, values=row)
            else:
                messagebox.showinfo("No Transactions", f"No transactions found for {selected_month} {selected_year}.")
        except FileNotFoundError:
            messagebox.showerror("Error", "No transactions file found.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    ttk.Button(filter_window, text="Apply Filter", command=apply_filter).pack(pady=20)

# Add Filter Button in Main App
def main_app():
    config = load_config()
    initialize_file(config["file_name"])

    root = tk.Tk()
    root.title(config["title"])
    root.geometry("600x500")

    primary_color = config.get("primary_color", "#4CAF50")
    secondary_color = config.get("secondary_color", "#f44336")

    # Custom Fonts
    title_font = Font(family="Helvetica", size=20, weight="bold")
    button_font = Font(family="Verdana", size=12, weight="bold")
    label_font = Font(family="Georgia", size=14, weight="normal")

    style = ttk.Style()
    style.configure("TButton", font=button_font, padding=10)
    style.map("TButton", background=[("active", secondary_color)], foreground=[("active", "white")])

    frame = ttk.Frame(root, padding=20)
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text=config["title"], font=title_font, foreground=primary_color).pack(pady=20)

    # Button Row
    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=10)

    ttk.Button(button_frame, text="Add Income", command=lambda: open_transaction_window(config, "Income"), style="TButton").grid(row=0, column=0, padx=10)
    ttk.Button(button_frame, text="Add Expense", command=lambda: open_transaction_window(config, "Expense"), style="TButton").grid(row=0, column=1, padx=10)
    ttk.Button(button_frame, text="View Transactions", command=lambda: view_transactions(config), style="TButton").grid(row=0, column=2, padx=10)
    ttk.Button(button_frame, text="Generate Report", command=lambda: generate_report(config), style="TButton").grid(row=0, column=3, padx=10)
    ttk.Button(button_frame, text="Export Transactions", command=lambda: export_transactions(config), style="TButton").grid(row=0, column=4, padx=10)
    ttk.Button(button_frame, text="Filter Transactions", command=lambda: filter_transactions(config), style="TButton").grid(row=0, column=5, padx=10)

    root.mainloop()

# Add Transaction Window
def open_transaction_window(config, transaction_type):
    transaction_window = tk.Toplevel()
    transaction_window.title(f"Add {transaction_type}")
    transaction_window.geometry("400x300")

    # Custom Fonts
    label_font = Font(family="Georgia", size=14, weight="normal")

    ttk.Label(transaction_window, text=f"Add {transaction_type}", font=label_font).pack(pady=10)

    ttk.Label(transaction_window, text="Amount:", font=label_font).pack(pady=5)
    amount_entry = ttk.Entry(transaction_window)
    amount_entry.pack(pady=5)

    ttk.Label(transaction_window, text="Category:", font=label_font).pack(pady=5)
    category_entry = ttk.Entry(transaction_window)
    category_entry.pack(pady=5)

    ttk.Label(transaction_window, text="Description (Optional):", font=label_font).pack(pady=5)
    description_entry = ttk.Entry(transaction_window)
    description_entry.pack(pady=5)

    ttk.Button(transaction_window, text="Add", 
               command=lambda: [add_transaction(config, transaction_type, amount_entry.get(), category_entry.get(), description_entry.get()), transaction_window.destroy()]).pack(pady=20)

# Export transactions to a file
def export_transactions(config):
    try:
        with open(config["file_name"], "r") as file:
            transactions = file.read()

        # Save as CSV
        export_file = filedialog.asksaveasfilename(
            title="Export Transactions",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if export_file:
            with open(export_file, "w") as export_file_obj:
                export_file_obj.write(transactions)
            messagebox.showinfo("Success", f"Transactions exported successfully to {export_file}.")
    except FileNotFoundError:
        messagebox.showerror("Error", "No transactions file found to export.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    main_app()
