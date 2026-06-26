"""
GUI application for managing ALL tables in Cinema Database
Variant 11: Cinema
Tables: armchairs, buyers, halls, movies, sessions, tickets
Full CRUD operations for each table
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
    def __init__(self, root):
        self.root = root
        self.current_table = "armchairs"
        
        self.root.title("Cinema Database Manager - Full CRUD Application")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')
        
        # Current table configuration (will be updated when switching)
        self.table_name = "armchairs"
        self.columns = ARMCHAIRS_COLUMNS
        self.table_label = "Armchairs"
        
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        """Create all interface elements"""
        
        # Title
        title_label = tk.Label(
            self.root, 
            text="🎬 CINEMA DATABASE MANAGEMENT SYSTEM 🎬", 
            font=("Arial", 18, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=10)
        
        # ========== TOP PANEL - TABLE SELECTION ==========
        top_frame = tk.Frame(self.root, bg='#f0f0f0', relief=tk.RAISED, bd=2)
        top_frame.pack(pady=10, padx=10, fill='x')
        
        tk.Label(top_frame, text="Select Table:", font=("Arial", 12, "bold"), bg='#f0f0f0').pack(side=tk.LEFT, padx=10)
        
        self.table_var = tk.StringVar(value="Armchairs")
        table_choice = ttk.Combobox(top_frame, textvariable=self.table_var, 
                                     values=["Armchairs", "Buyers", "Halls", "Movies", "Sessions", "Tickets"],
                                     width=20, font=("Arial", 11), state="readonly")
        table_choice.pack(side=tk.LEFT, padx=10)
        table_choice.bind("<<ComboboxSelected>>", self.on_table_change)
        
        # Current table info
        self.current_table_label = tk.Label(
            top_frame, 
            text="📋 Current Table: Armchairs", 
            font=("Arial", 11, "italic"),
            bg='#f0f0f0',
            fg='#2980b9'
        )
        self.current_table_label.pack(side=tk.RIGHT, padx=20)
        
        # ========== MAIN TITLE ==========
        self.main_title = tk.Label(
            self.root, 
            text="MANAGE TABLE: ARMCHAIRS", 
            font=("Arial", 16, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        self.main_title.pack(pady=10)
        
        # ========== INPUT FIELDS FRAME ==========
        input_frame_container = tk.LabelFrame(
            self.root, 
            text="📝 RECORD DATA", 
            font=("Arial", 12, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50',
            padx=15, 
            pady=15
        )
        input_frame_container.pack(pady=10, padx=10, fill="x")
        
        self.input_frame = tk.Frame(input_frame_container, bg='#f0f0f0')
        self.input_frame.pack()
        
        self.entries = {}
        self.create_input_fields()
        
        # ========== BUTTONS FRAME ==========
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=15)
        
        buttons = [
            ("➕ ADD", self.add_record, "#27ae60", "#ffffff"),
            ("✏️ UPDATE", self.update_record, "#f39c12", "#ffffff"),
            ("🗑️ DELETE", self.delete_record, "#e74c3c", "#ffffff"),
            ("🧹 CLEAR", self.clear_entries, "#95a5a6", "#ffffff"),
            ("🔄 REFRESH", self.refresh_table, "#3498db", "#ffffff"),
        ]
        
        for i, (text, command, bg_color, fg_color) in enumerate(buttons):
            btn = tk.Button(
                button_frame, 
                text=text, 
                command=command,
                bg=bg_color,
                fg=fg_color,
                width=12,
                height=1,
                font=("Arial", 11, "bold"),
                relief=tk.RAISED,
                bd=2,
                cursor="hand2"
            )
            btn.grid(row=0, column=i, padx=8, pady=5)
        
        # ========== SEARCH FRAME ==========
        search_frame = tk.Frame(self.root, bg='#f0f0f0')
        search_frame.pack(pady=10)
        
        search_bg = tk.Frame(search_frame, bg='#ecf0f1', relief=tk.SUNKEN, bd=1)
        search_bg.pack()
        
        tk.Label(search_bg, text="🔍 SEARCH:", font=("Arial", 11, "bold"), bg='#ecf0f1', fg='#2c3e50').pack(side=tk.LEFT, padx=10, pady=5)
        
        self.search_entry = tk.Entry(search_bg, width=50, font=("Arial", 11), relief=tk.FLAT)
        self.search_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        tk.Button(
            search_bg, 
            text="FIND", 
            command=self.search,
            bg="#2980b9",
            fg="white",
            width=10,
            font=("Arial", 10, "bold"),
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        tk.Button(
            search_bg, 
            text="SHOW ALL", 
            command=self.refresh_table,
            bg="#8e44ad",
            fg="white",
            width=12,
            font=("Arial", 10, "bold"),
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        
        # ========== TREEVIEW TABLE ==========
        tree_frame = tk.Frame(self.root, bg='#f0f0f0')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbars
        scroll_y = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scroll_x = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns_display = [col['name'] for col in self.columns]
        self.tree = ttk.Treeview(
            tree_frame, 
            columns=columns_display, 
            show="headings",
            yscrollcommand=scroll_y.set, 
            xscrollcommand=scroll_x.set,
            height=18
        )
        
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        # Configure headings
        for col in self.columns:
            self.tree.heading(col['name'], text=col['label'])
            self.tree.column(col['name'], width=130, anchor="center")
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # ========== STATUS BAR ==========
        self.status_bar = tk.Label(
            self.root, 
            text="✅ Ready", 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            font=("Arial", 9),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_input_fields(self):
        """Create input fields based on current table"""
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        
        self.entries = {}
        
        # Create two columns for better layout
        row = 0
        col = 0
        for col_info in self.columns:
            if col_info.get('pk') and col_info.get('auto_increment'):
                continue
            
            # Label
            label = tk.Label(
                self.input_frame, 
                text=f"{col_info['label']}:", 
                font=("Arial", 10, "bold"),
                bg='#f0f0f0',
                width=15,
                anchor='e'
            )
            label.grid(row=row, column=col*2, padx=10, pady=8, sticky="e")
            
            # Entry
            entry = tk.Entry(self.input_frame, width=30, font=("Arial", 10), relief=tk.SUNKEN, bd=1)
            entry.grid(row=row, column=col*2+1, padx=10, pady=8, sticky="w")
            self.entries[col_info['name']] = entry
            
            col += 1
            if col >= 2:  # Two columns of inputs
                col = 0
                row += 1

    def on_table_change(self, event):
        """Switch table when selection changes"""
        table = self.table_var.get()
        
        if table == "Armchairs":
            self.columns = ARMCHAIRS_COLUMNS
            self.table_name = "armchairs"
            self.table_label = "Armchairs"
        elif table == "Buyers":
            self.columns = BUYERS_COLUMNS
            self.table_name = "buyers"
            self.table_label = "Buyers"
        elif table == "Halls":
            self.columns = HALLS_COLUMNS
            self.table_name = "halls"
            self.table_label = "Halls"
        elif table == "Movies":
            self.columns = MOVIES_COLUMNS
            self.table_name = "movies"
            self.table_label = "Movies"
        elif table == "Sessions":
            self.columns = SESSIONS_COLUMNS
            self.table_name = "sessions"
            self.table_label = "Sessions"
        elif table == "Tickets":
            self.columns = TICKETS_COLUMNS
            self.table_name = "tickets"
            self.table_label = "Tickets"
        
        # Update UI
        self.current_table_label.config(text=f"📋 Current Table: {self.table_label}")
        self.main_title.config(text=f"MANAGE TABLE: {self.table_label.upper()}")
        
        # Recreate input fields
        self.create_input_fields()
        
        # Update Treeview columns
        columns_display = [col['name'] for col in self.columns]
        self.tree.config(columns=columns_display)
        
        for col in self.columns:
            self.tree.heading(col['name'], text=col['label'])
            self.tree.column(col['name'], width=130, anchor="center")
        
        # Refresh data
        self.refresh_table()

    def set_status(self, message, is_error=False):
        """Set status bar message"""
        if is_error:
            self.status_bar.config(text=f"❌ {message}", fg='#e74c3c')
        else:
            self.status_bar.config(text=f"✅ {message}", fg='#2c3e50')
        self.root.update_idletasks()

    def refresh_table(self):
        """Refresh data in Treeview"""
        self.set_status(f"Loading data from {self.table_label}...")
        
        # Clear current data
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        conn = connect_db()
        if not conn:
            self.set_status("Database connection error", True)
            return
        
        cursor = conn.cursor()
        columns_names = [col['name'] for col in self.columns]
        query = f"SELECT {', '.join(columns_names)} FROM {self.table_name}"
        
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                self.tree.insert("", tk.END, values=row)
            self.set_status(f"Loaded {len(rows)} records from {self.table_label}")
        except Error as e:
            self.set_status(f"Load error: {str(e)[:50]}", True)
            messagebox.showerror("Error", f"Failed to load data: {e}")
        finally:
            cursor.close()
            conn.close()

    def on_select(self, event):
        """Fill input fields when row selected"""
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0])['values']
        
        # Fill input fields
        for i, col in enumerate(self.columns):
            col_name = col['name']
            if col_name in self.entries:
                self.entries[col_name].delete(0, tk.END)
                if values[i] is not None and i < len(values):
                    self.entries[col_name].insert(0, str(values[i]))
        
        self.set_status("Record selected for editing")

    def get_pk_name(self):
        """Return primary key name"""
        for col in self.columns:
            if col.get('pk'):
                return col['name']
        return None

    def get_pk_value_from_selected(self):
        """Get PK value from selected row"""
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
        self.set_status(f"Adding new record to {self.table_label}...")
        
        # Collect values
        values = {}
        for col_name, entry in self.entries.items():
            values[col_name] = entry.get().strip()
        
        # Check required fields
        for col in self.columns:
            col_name = col['name']
            if col.get('required') and col_name in self.entries and not values[col_name]:
                messagebox.showwarning("Warning", f"Field '{col['label']}' is required")
                self.set_status("Missing required fields", True)
                return
        
        conn = connect_db()
        if not conn:
            self.set_status("Database connection error", True)
            return
        
        cursor = conn.cursor()
        columns_names = list(values.keys())
        placeholders = ", ".join(["%s"] * len(columns_names))
        query = f"INSERT INTO {self.table_name} ({', '.join(columns_names)}) VALUES ({placeholders})"
        
        try:
            cursor.execute(query, list(values.values()))
            conn.commit()
            messagebox.showinfo("Success", f"Record added to {self.table_label}")
            self.clear_entries()
            self.refresh_table()
            self.set_status(f"Record successfully added to {self.table_label}")
        except Error as e:
            self.set_status(f"Add error: {str(e)[:50]}", True)
            messagebox.showerror("DB Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def update_record(self):
        """Update selected record"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to update")
            return
        
        pk_name = self.get_pk_name()
        if not pk_name:
            messagebox.showwarning("Warning", "Primary key not found")
            return
        
        pk_value = self.get_pk_value_from_selected()
        
        self.set_status(f"Updating record in {self.table_label}...")
        
        # Collect new values
        new_values = {}
        for col_name, entry in self.entries.items():
            new_values[col_name] = entry.get().strip()
        
        conn = connect_db()
        if not conn:
            self.set_status("Database connection error", True)
            return
        
        cursor = conn.cursor()
        set_clause = ", ".join([f"{col} = %s" for col in new_values.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {pk_name} = %s"
        
        try:
            params = list(new_values.values()) + [pk_value]
            cursor.execute(query, params)
            conn.commit()
            messagebox.showinfo("Success", f"Record updated in {self.table_label}")
            self.refresh_table()
            self.set_status(f"Record successfully updated in {self.table_label}")
        except Error as e:
            self.set_status(f"Update error: {str(e)[:50]}", True)
            messagebox.showerror("DB Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def delete_record(self):
        """Delete selected record"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to delete")
            return
        
        pk_value = self.get_pk_value_from_selected()
        
        if not messagebox.askyesno("Confirm", f"Are you sure you want to delete this record from {self.table_label}?"):
            return
        
        self.set_status(f"Deleting record from {self.table_label}...")
        
        pk_name = self.get_pk_name()
        if not pk_name:
            return
        
        conn = connect_db()
        if not conn:
            self.set_status("Database connection error", True)
            return
        
        cursor = conn.cursor()
        query = f"DELETE FROM {self.table_name} WHERE {pk_name} = %s"
        
        try:
            cursor.execute(query, (pk_value,))
            conn.commit()
            messagebox.showinfo("Success", f"Record deleted from {self.table_label}")
            self.clear_entries()
            self.refresh_table()
            self.set_status(f"Record successfully deleted from {self.table_label}")
        except Error as e:
            self.set_status(f"Delete error: {str(e)[:50]}", True)
            messagebox.showerror("DB Error", str(e))
        finally:
            cursor.close()
            conn.close()

    def clear_entries(self):
        """Clear all input fields"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.set_status("Input fields cleared")

    def search(self):
        """Search records in current table"""
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.refresh_table()
            return
        
        self.set_status(f"Searching for '{keyword}' in {self.table_label}...")
        
        conn = connect_db()
        if not conn:
            self.set_status("Database connection error", True)
            return
        
        cursor = conn.cursor()
        
        # Get text columns (non-PK)
        text_columns = [col['name'] for col in self.columns if not col.get('pk')]
        
        if not text_columns:
            self.refresh_table()
            return
        
        # Build LIKE condition
        conditions = " OR ".join([f"{col} LIKE %s" for col in text_columns])
        columns_names = [col['name'] for col in self.columns]
        query = f"SELECT {', '.join(columns_names)} FROM {self.table_name} WHERE {conditions}"
        
        try:
            cursor.execute(query, tuple([f"%{keyword}%"] * len(text_columns)))
            rows = cursor.fetchall()
            
            # Clear and fill tree
            for row in self.tree.get_children():
                self.tree.delete(row)
            
            for row in rows:
                self.tree.insert("", tk.END, values=row)
            
            self.set_status(f"Found {len(rows)} records matching '{keyword}'")
        except Error as e:
            self.set_status(f"Search error: {str(e)[:50]}", True)
            messagebox.showerror("Error", str(e))
        finally:
            cursor.close()
            conn.close()


# =====================================================
# TABLE CONFIGURATIONS (ALL 6 TABLES)
# =====================================================

# 1. Armchairs table (кресла)
ARMCHAIRS_COLUMNS = [
    {"name": "id_armchairs", "label": "🪑 ID", "pk": True, "auto_increment": True},
    {"name": "ranks", "label": "Row", "required": True},
    {"name": "place", "label": "Seat", "required": True},
]

# 2. Buyers table (покупатели)
BUYERS_COLUMNS = [
    {"name": "id_buyer", "label": "👤 ID", "pk": True, "auto_increment": True},
    {"name": "name", "label": "Full Name", "required": True},
    {"name": "telephone", "label": "Phone", "required": False},
]

# 3. Halls table (залы)
HALLS_COLUMNS = [
    {"name": "id_hall", "label": "🏢 ID", "pk": True, "auto_increment": True},
    {"name": "number", "label": "Hall Number", "required": True},
    {"name": "capacity", "label": "Capacity", "required": True},
    {"name": "type", "label": "Type", "required": False},
    {"name": "id_armchairs", "label": "Armchair ID", "required": False},
]

# 4. Movies table (фильмы)
MOVIES_COLUMNS = [
    {"name": "id", "label": "🎬 ID", "pk": True, "auto_increment": True},
    {"name": "name", "label": "Title", "required": True},
    {"name": "director", "label": "Director", "required": False},
    {"name": "duration_min", "label": "Duration (min)", "required": True},
    {"name": "age_rating", "label": "Age Rating", "required": False},
]

# 5. Sessions table (сеансы)
SESSIONS_COLUMNS = [
    {"name": "id_session", "label": "🎟️ ID", "pk": True, "auto_increment": True},
    {"name": "date", "label": "Date", "required": True},
    {"name": "time", "label": "Time", "required": True},
    {"name": "price", "label": "Price", "required": True},
    {"name": "id_film", "label": "Film ID", "required": True},
    {"name": "id_hall", "label": "Hall ID", "required": True},
]

# 6. Tickets table (билеты)
TICKETS_COLUMNS = [
    {"name": "id_ticket", "label": "🎫 ID", "pk": True, "auto_increment": True},
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
    app = DatabaseApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
