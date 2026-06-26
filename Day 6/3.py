"""
GUI application for Cinema Database
Based on your actual database structure
"""

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

# =====================================================
# DATABASE CONNECTION (CHANGE YOUR PASSWORD!)
# =====================================================
def connect_db():
    """Connect to MySQL database"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="19852912",  # ⚠️ CHANGE TO YOUR PASSWORD!
            database="cinima"
        )
        return connection
    except Error as e:
        messagebox.showerror("DB Error", f"Connection failed: {e}")
        return None
    
# =====================================================
# MAIN APPLICATION CLASS
# =====================================================
class DatabaseApp:
    def __init__(self, root, table_name, columns, table_label):
        self.root = root
        self.table_name = table_name
        self.columns = columns
        self.table_label = table_label
        
        self.root.title(f"Cinema - Manage: {table_label}")
        self.root.geometry("1100x650")
        self.root.configure(bg='#f0f0f0')
        
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        """Create all interface elements"""
        
        # Top panel for table selection
        top_frame = tk.Frame(self.root, bg='#f0f0f0')
        top_frame.pack(pady=10, fill='x')
        
        tk.Label(top_frame, text="Select Table:", font=("Arial", 12), bg='#f0f0f0').pack(side=tk.LEFT, padx=10)
        
        self.table_var = tk.StringVar(value=self.table_label)
        table_choice = ttk.Combobox(top_frame, textvariable=self.table_var, 
                                     values=["Armchairs", "Buyers", "Halls", "Movies", "Sessions", "Tickets"],
                                     width=15, state="readonly")
        table_choice.pack(side=tk.LEFT, padx=10)
        table_choice.bind("<<ComboboxSelected>>", self.on_table_change)
        
        # Title
        self.title_label = tk.Label(
            self.root, 
            text=f"MANAGE TABLE: {self.table_label.upper()}", 
            font=("Arial", 16, "bold"),
            bg='#f0f0f0',
            fg='#333333'
        )
        self.title_label.pack(pady=10)
        
        # Input fields frame
        self.input_frame = tk.LabelFrame(
            self.root, 
            text="Record Data", 
            font=("Arial", 12, "bold"),
            bg='#f0f0f0',
            padx=15, 
            pady=15
        )
        self.input_frame.pack(pady=10, padx=10, fill="x")
        
        self.entries = {}
        self.create_input_fields()
        
        # Buttons frame
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=15)
        
        buttons = [
            ("➕ Add", self.add_record, "#90EE90"),
            ("✏️ Update", self.update_record, "#FFD700"),
            ("🗑️ Delete", self.delete_record, "#FF6347"),
            ("🧹 Clear", self.clear_entries, "#D3D3D3"),
            ("🔄 Refresh", self.refresh_table, "#87CEEB"),
        ]
        
        for i, (text, command, color) in enumerate(buttons):
            btn = tk.Button(
                button_frame, 
                text=text, 
                command=command,
                bg=color,
                width=12,
                height=1,
                font=("Arial", 10, "bold"),
                cursor="hand2"
            )
            btn.grid(row=0, column=i, padx=5, pady=5)
        
        # Search frame
        search_frame = tk.Frame(self.root, bg='#f0f0f0')
        search_frame.pack(pady=10)
        
        tk.Label(search_frame, text="🔍 Search:", font=("Arial", 10, "bold"), bg='#f0f0f0').pack(side=tk.LEFT)
        
        self.search_entry = tk.Entry(search_frame, width=40, font=("Arial", 10))
        self.search_entry.pack(side=tk.LEFT, padx=10)
        
        tk.Button(search_frame, text="Find", command=self.search, bg="#4CAF50", fg="white", width=10).pack(side=tk.LEFT)
        tk.Button(search_frame, text="Show All", command=self.refresh_table, bg="#FF9800", fg="white", width=12).pack(side=tk.LEFT, padx=10)
        
        # Treeview table
        tree_frame = tk.Frame(self.root, bg='#f0f0f0')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scroll_y = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scroll_x = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns_display = [col['name'] for col in self.columns]
        self.tree = ttk.Treeview(
            tree_frame, 
            columns=columns_display, 
            show="headings",
            yscrollcommand=scroll_y.set, 
            xscrollcommand=scroll_x.set,
            height=15
        )
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        for col in self.columns:
            self.tree.heading(col['name'], text=col['label'])
            self.tree.column(col['name'], width=120, anchor="center")
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg='#f0f0f0')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_input_fields(self):
        """Create input fields based on current table"""
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        
        self.entries = {}
        
        row = 0
        col_count = 0
        for col in self.columns:
            if col.get('pk') and col.get('auto_increment'):
                continue
            
            label = tk.Label(self.input_frame, text=f"{col['label']}:", font=("Arial", 10, "bold"),
                            bg='#f0f0f0', width=15, anchor='e')
            label.grid(row=row, column=col_count*2, padx=5, pady=8, sticky="e")
            
            entry = tk.Entry(self.input_frame, width=25, font=("Arial", 10))
            entry.grid(row=row, column=col_count*2+1, padx=5, pady=8, sticky="w")
            self.entries[col['name']] = entry
            
            col_count += 1
            if col_count >= 3:
                col_count = 0
                row += 1

    def on_table_change(self, event):
        """Switch table when selection changes"""
        table = self.table_var.get()
        self.switch_table(table)

    def switch_table(self, table_name):
        """Switch between tables"""
        if table_name == "Armchairs":
            columns = ARMCHAIRS_COLUMNS
            table_db = "armchairs"
        elif table_name == "Buyers":
            columns = BUYERS_COLUMNS
            table_db = "buyers"
        elif table_name == "Halls":
            columns = HALLS_COLUMNS
            table_db = "halls"
        elif table_name == "Movies":
            columns = MOVIES_COLUMNS
            table_db = "movies"
        elif table_name == "Sessions":
            columns = SESSIONS_COLUMNS
            table_db = "sessions"
        elif table_name == "Tickets":
            columns = TICKETS_COLUMNS
            table_db = "tickets"
        else:
            return
        
        self.table_label = table_name
        self.table_name = table_db
        self.columns = columns
        
        self.title_label.config(text=f"MANAGE TABLE: {self.table_label.upper()}")
        self.create_input_fields()
        
        columns_display = [col['name'] for col in self.columns]
        self.tree.config(columns=columns_display)
        
        for col in self.columns:
            self.tree.heading(col['name'], text=col['label'])
            self.tree.column(col['name'], width=120, anchor="center")
        
        self.refresh_table()

    def set_status(self, message):
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    def refresh_table(self):
        """Refresh data in Treeview"""
        self.set_status("Loading data...")
        
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        conn = connect_db()
        if not conn:
            self.set_status("Connection error")
            return
        
        cursor = conn.cursor()
        columns_names = [col['name'] for col in self.columns]
        query = f"SELECT {', '.join(columns_names)} FROM {self.table_name}"
        
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                self.tree.insert("", tk.END, values=row)
            self.set_status(f"Loaded: {len(rows)} records")
        except Error as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
            self.set_status("Load error")
        finally:
            cursor.close()
            conn.close()

    def on_select(self, event):
        """Fill input fields when row selected"""
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0])['values']
        
        for i, col in enumerate(self.columns):
            col_name = col['name']
            if col_name in self.entries:
                self.entries[col_name].delete(0, tk.END)
                if values[i] is not None and i < len(values):
                    self.entries[col_name].insert(0, str(values[i]))

    def get_pk_name(self):
        for col in self.columns:
            if col.get('pk'):
                return col['name']
        return None

    def get_pk_value_from_selected(self):
        selected = self.tree.selection()
        if not selected:
            return None
        
        pk_name = self.get_pk_name()
        if not pk_name:
            return None
        
        values = self.tree.item(selected[0])['values']
        pk_index = [col['name'] for col in self.columns].index(pk_name)
        return values[pk_index] if pk_index < len(values) else None

    def add_record(self):
        """Add new record"""
        self.set_status("Adding record...")
        
        values = {}
        for col_name, entry in self.entries.items():
            values[col_name] = entry.get().strip()
        
        for col in self.columns:
            col_name = col['name']
            if col.get('required') and col_name in self.entries and not values[col_name]:
                messagebox.showwarning("Error", f"Field '{col['label']}' is required")
                return
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        columns_names = list(values.keys())
        placeholders = ", ".join(["%s"] * len(columns_names))
        query = f"INSERT INTO {self.table_name} ({', '.join(columns_names)}) VALUES ({placeholders})"
        
        try:
            cursor.execute(query, list(values.values()))
            conn.commit()
            messagebox.showinfo("Success", "Record added")
            self.clear_entries()
            self.refresh_table()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def update_record(self):
        """Update selected record"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a record to update")
            return
        
        pk_name = self.get_pk_name()
        if not pk_name:
            return
        
        pk_value = self.get_pk_value_from_selected()
        
        new_values = {}
        for col_name, entry in self.entries.items():
            new_values[col_name] = entry.get().strip()
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        set_clause = ", ".join([f"{col} = %s" for col in new_values.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {pk_name} = %s"
        
        try:
            params = list(new_values.values()) + [pk_value]
            cursor.execute(query, params)
            conn.commit()
            messagebox.showinfo("Success", "Record updated")
            self.refresh_table()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def delete_record(self):
        """Delete selected record"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a record to delete")
            return
        
        if not messagebox.askyesno("Confirm", "Delete this record?"):
            return
        
        pk_name = self.get_pk_name()
        if not pk_name:
            return
        
        pk_value = self.get_pk_value_from_selected()
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        query = f"DELETE FROM {self.table_name} WHERE {pk_name} = %s"
        
        try:
            cursor.execute(query, (pk_value,))
            conn.commit()
            messagebox.showinfo("Success", "Record deleted")
            self.clear_entries()
            self.refresh_table()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def clear_entries(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.set_status("Fields cleared")

    def search(self):
        """Search records"""
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.refresh_table()
            return
        
        self.set_status(f"Searching: '{keyword}'...")
        
        conn = connect_db()
        if not conn:
            return
        
        cursor = conn.cursor()
        text_columns = [col['name'] for col in self.columns if not col.get('pk')]
        
        if not text_columns:
            self.refresh_table()
            return
        
        conditions = " OR ".join([f"{col} LIKE %s" for col in text_columns])
        columns_names = [col['name'] for col in self.columns]
        query = f"SELECT {', '.join(columns_names)} FROM {self.table_name} WHERE {conditions}"
        
        try:
            cursor.execute(query, tuple([f"%{keyword}%"] * len(text_columns)))
            rows = cursor.fetchall()
            
            for row in self.tree.get_children():
                self.tree.delete(row)
            
            for row in rows:
                self.tree.insert("", tk.END, values=row)
            
            self.set_status(f"Found: {len(rows)} records")
        except Error as e:
            messagebox.showerror("Error", str(e))
        finally:
            cursor.close()
            conn.close()

# =====================================================
# TABLE CONFIGURATIONS (BASED ON YOUR DATABASE)
# =====================================================

# Armchairs table
ARMCHAIRS_COLUMNS = [
    {"name": "id_armchairs", "label": "ID", "pk": True, "auto_increment": True},
    {"name": "ranks", "label": "Row", "required": True},
    {"name": "place", "label": "Seat", "required": True},
]

# Buyers table
BUYERS_COLUMNS = [
    {"name": "id_buyer", "label": "ID", "pk": True, "auto_increment": True},
    {"name": "name", "label": "Name", "required": True},
    {"name": "telephone", "label": "Phone", "required": False},
]

# Halls table
HALLS_COLUMNS = [
    {"name": "id_hall", "label": "ID", "pk": True, "auto_increment": True},
    {"name": "number", "label": "Number", "required": True},
    {"name": "capacity", "label": "Capacity", "required": True},
    {"name": "type", "label": "Type", "required": False},
    {"name": "id_armchairs", "label": "Armchair ID", "required": False},
]

# Movies table
MOVIES_COLUMNS = [
    {"name": "id", "label": "ID", "pk": True, "auto_increment": True},
    {"name": "name", "label": "Title", "required": True},
    {"name": "director", "label": "Director", "required": False},
    {"name": "duration_min", "label": "Duration", "required": True},
    {"name": "age_rating", "label": "Rating", "required": False},
]

# Sessions table (based on your screenshot)
SESSIONS_COLUMNS = [
    {"name": "id_session", "label": "Session ID", "pk": True, "auto_increment": True},
    {"name": "date", "label": "Date", "required": True},
    {"name": "time", "label": "Time", "required": True},
    {"name": "price", "label": "Price", "required": True},
    {"name": "id_film", "label": "Film ID", "required": True},
    {"name": "id_hall", "label": "Hall ID", "required": True},
]

# Tickets table (based on typical structure - adjust if needed)
TICKETS_COLUMNS = [
    {"name": "id_ticket", "label": "Ticket ID", "pk": True, "auto_increment": True},
    {"name": "id_session", "label": "Session ID", "required": True},
    {"name": "id_armchair", "label": "Armchair ID", "required": True},
    {"name": "id_buyer", "label": "Buyer ID", "required": False},
    {"name": "price", "label": "Price", "required": True},
    {"name": "status", "label": "Status", "required": False},
]


# =====================================================
# RUN APPLICATION
# =====================================================
def main():
    root = tk.Tk()
    app = DatabaseApp(root, table_name="armchairs", columns=ARMCHAIRS_COLUMNS, table_label="Armchairs")
    root.mainloop()


if __name__ == "__main__":
    main()