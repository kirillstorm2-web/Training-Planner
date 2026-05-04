import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "workouts.json"


class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("800x500")

        # Data storage
        self.workouts = []  # list of dicts: {date, type, duration}
        self.load_from_json()

        # --- Input Frame ---
        input_frame = tk.LabelFrame(root, text="Add New Workout", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Date
        tk.Label(input_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.date_entry = tk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

        # Type
        tk.Label(input_frame, text="Workout Type:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(input_frame, textvariable=self.type_var, values=["Running", "Swimming", "Cycling", "Yoga", "Gym"], width=12)
        self.type_combo.grid(row=0, column=3, padx=5, pady=5)
        self.type_combo.set("Running")

        # Duration
        tk.Label(input_frame, text="Duration (min):").grid(row=0, column=4, sticky="e", padx=5, pady=5)
        self.duration_entry = tk.Entry(input_frame, width=10)
        self.duration_entry.grid(row=0, column=5, padx=5, pady=5)

        # Add button
        self.add_btn = tk.Button(input_frame, text="Add Workout", command=self.add_workout, bg="lightgreen")
        self.add_btn.grid(row=0, column=6, padx=10, pady=5)

        # --- Filter Frame ---
        filter_frame = tk.LabelFrame(root, text="Filter", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Filter by Type:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_type_var = tk.StringVar()
        self.filter_type_combo = ttk.Combobox(filter_frame, textvariable=self.filter_type_var,
                                              values=["All", "Running", "Swimming", "Cycling", "Yoga", "Gym"], width=12)
        self.filter_type_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_type_combo.set("All")
        self.filter_type_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        tk.Label(filter_frame, text="Filter by Date (YYYY-MM-DD):").grid(row=0, column=2, padx=5, pady=5)
        self.filter_date_entry = tk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=3, padx=5, pady=5)
        self.filter_date_entry.bind("<KeyRelease>", lambda e: self.refresh_table())

        self.clear_filter_btn = tk.Button(filter_frame, text="Clear Filters", command=self.clear_filters)
        self.clear_filter_btn.grid(row=0, column=4, padx=10, pady=5)

        # --- Table (Treeview) ---
        self.tree = ttk.Treeview(root, columns=("Date", "Type", "Duration"), show="headings", height=15)
        self.tree.heading("Date", text="Date")
        self.tree.heading("Type", text="Workout Type")
        self.tree.heading("Duration", text="Duration (min)")
        self.tree.column("Date", width=120)
        self.tree.column("Type", width=120)
        self.tree.column("Duration", width=120)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Buttons (Save / Load are automatic, but manual reload/export for clarity)
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)
        self.save_btn = tk.Button(button_frame, text="Save to JSON", command=self.save_to_json)
        self.save_btn.pack(side="left", padx=5)
        self.load_btn = tk.Button(button_frame, text="Load from JSON", command=self.load_from_json)
        self.load_btn.pack(side="left", padx=5)

        # Initial display
        self.refresh_table()

    # ---------- Validation ----------
    def validate_inputs(self, date_str, duration_str):
        # Validate date format
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid date", "Date must be in YYYY-MM-DD format")
            return False

        # Validate duration (positive number)
        try:
            duration = float(duration_str)
            if duration <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid duration", "Duration must be a positive number")
            return False
        return True

    # ---------- Add Workout ----------
    def add_workout(self):
        date = self.date_entry.get().strip()
        wtype = self.type_var.get().strip()
        duration = self.duration_entry.get().strip()

        if not date or not wtype or not duration:
            messagebox.showwarning("Missing data", "All fields are required")
            return

        if not self.validate_inputs(date, duration):
            return

        # Add to list
        self.workouts.append({
            "date": date,
            "type": wtype,
            "duration": float(duration)
        })

        # Auto-save after adding
        self.save_to_json()
        self.refresh_table()

        # Clear duration entry for next entry
        self.duration_entry.delete(0, tk.END)

    # ---------- Filter Logic ----------
    def get_filtered_workouts(self):
        filtered = self.workouts[:]

        # Filter by type
        selected_type = self.filter_type_var.get()
        if selected_type != "All":
            filtered = [w for w in filtered if w["type"] == selected_type]

        # Filter by date (exact match if not empty)
        filter_date = self.filter_date_entry.get().strip()
        if filter_date:
            filtered = [w for w in filtered if w["date"] == filter_date]

        return filtered

    # ---------- Refresh Table ----------
    def refresh_table(self):
        # Clear current table
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insert filtered workouts
        for w in self.get_filtered_workouts():
            self.tree.insert("", tk.END, values=(w["date"], w["type"], w["duration"]))

    # ---------- JSON Save / Load ----------
    def save_to_json(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.workouts, f, indent=4, ensure_ascii=False)
            print(f"Saved {len(self.workouts)} workouts to {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Save error", f"Cannot save file:\n{e}")

    def load_from_json(self):
        if not os.path.exists(DATA_FILE):
            self.workouts = []
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.workouts = json.load(f)
            print(f"Loaded {len(self.workouts)} workouts from {DATA_FILE}")
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Load error", f"Cannot load file:\n{e}")
            self.workouts = []

    # ---------- Clear Filters ----------
    def clear_filters(self):
        self.filter_type_var.set("All")
        self.filter_date_entry.delete(0, tk.END)
        self.refresh_table()


if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()
