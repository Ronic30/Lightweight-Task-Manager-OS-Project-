import tkinter as tk
from tkinter import ttk
import psutil

class TaskManagerApp(tk.Tk):
    """
    A lightweight, object-oriented Task Manager clone.
    Displays system statistics and the top 10 running processes sorted by CPU usage.
    """
    def __init__(self):
        super().__init__()
        self.title("Task Manager | OS Project")
        self.geometry("800x600")
        self.configure(bg="#FFFFFF")
        self.refresh_interval = 2000  # Refresh every 2 seconds

        # Build UI components
        self._build_stats_panel()
        self._build_process_table()

        # Start the refresh loop
        self.refresh()

    def _bytes_to_readable(self, byte_count):
        """Converts bytes to a human-readable format (KB, MB, GB, etc.)."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if byte_count < 1024:
                return f"{byte_count:.1f} {unit}"
            byte_count /= 1024
        return f"{byte_count:.1f} TB"

    def _build_stats_panel(self):
        """Constructs the system information cards (CPU, RAM, Disk)."""
        stats_frame = tk.Frame(self, bg="#FFFFFF", pady=10)
        stats_frame.pack(fill=tk.X, padx=20)

        tk.Label(
            stats_frame, text="SYSTEM INFORMATION", 
            font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#000000"
        ).pack(anchor=tk.W, pady=(0, 8))

        cards_row = tk.Frame(stats_frame, bg="#FFFFFF")
        cards_row.pack(fill=tk.X)

        self.cpu_val, self.cpu_det = self._make_card(cards_row, "CPU USAGE", "#000000")
        self.mem_val, self.mem_det = self._make_card(cards_row, "RAM (MEMORY)", "#000000")
        self.disk_val, self.disk_det = self._make_card(cards_row, "DISK", "#000000")

    def _make_card(self, parent, title, border_color):
        """Helper method to construct individual statistic cards."""
        card = tk.Frame(
            parent, bg="#FFFFFF", highlightbackground=border_color,
            highlightthickness=1, padx=14, pady=10
        )
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        tk.Label(card, text=title, font=("Arial", 9, "bold"), bg="#FFFFFF", fg=border_color).pack(anchor=tk.W)

        val_lbl = tk.Label(card, text="Loading...", font=("Arial", 14, "bold"), bg="#FFFFFF", fg="#000000")
        val_lbl.pack(anchor=tk.W, pady=(4, 2))

        det_lbl = tk.Label(card, text="", font=("Arial", 8), bg="#FFFFFF", fg="#555555")
        det_lbl.pack(anchor=tk.W)
        
        return val_lbl, det_lbl

    def _build_process_table(self):
        """Constructs the Treeview table to display the top 10 processes."""
        top_bar = tk.Frame(self, bg="#FFFFFF")
        top_bar.pack(fill=tk.X, padx=20, pady=(10, 6))

        tk.Label(
            top_bar, text="TOP 10 RUNNING PROCESSES (BY CPU)", 
            font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#000000"
        ).pack(side=tk.LEFT)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.Treeview", background="#FFFFFF", foreground="#000000",
            fieldbackground="#FFFFFF", rowheight=24, font=("Arial", 9)
        )
        style.configure(
            "Custom.Treeview.Heading", background="#F0F0F0", foreground="#000000",
            font=("Arial", 9, "bold"), relief="flat"
        )
        style.map("Custom.Treeview", background=[("selected", "#E0E0E0")], foreground=[("selected", "#000000")])

        columns = ("pid", "name", "cpu", "mem_pct", "mem_rss", "threads")
        headers = ("PID", "Process Name", "CPU %", "MEM %", "RAM Used", "Threads")
        widths = (60, 200, 70, 70, 100, 70)

        table_wrap = tk.Frame(self, bg="#000000", highlightthickness=1, highlightbackground="#000000")
        table_wrap.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings", style="Custom.Treeview")
        
        for col, header, width in zip(columns, headers, widths):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=width, anchor=tk.W)

        scrollbar = ttk.Scrollbar(table_wrap, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh(self):
        """Main loop callback to periodically update stats and processes."""
        self._update_system_info()
        self._update_processes()
        self.after(self.refresh_interval, self.refresh)

    def _update_system_info(self):
        """Fetches and updates CPU, RAM, and Disk metrics."""
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_cores = psutil.cpu_count(logical=True)
        freq = psutil.cpu_freq()
        cpu_freq_mhz = f"{freq.current:.0f} MHz" if freq else "N/A"

        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        self.cpu_val.config(text=f"{cpu_percent:.1f}%")
        self.cpu_det.config(text=f"{cpu_cores} cores | {cpu_freq_mhz}")

        self.mem_val.config(text=f"{ram.percent:.1f}%")
        self.mem_det.config(text=f"{self._bytes_to_readable(ram.used)} / {self._bytes_to_readable(ram.total)}")

        self.disk_val.config(text=f"{disk.percent:.1f}%")
        self.disk_det.config(text=f"{self._bytes_to_readable(disk.used)} / {self._bytes_to_readable(disk.total)}")

    def _update_processes(self):
        """Fetches process info, sorts by CPU, and populates the table with the top 10."""
        processes = []
        attrs = ["pid", "name", "cpu_percent", "memory_percent", "memory_info", "num_threads"]
        
        for p in psutil.process_iter(attrs=attrs):
            try:
                info = p.info
                ram_used = info["memory_info"].rss if info["memory_info"] else 0
                processes.append({
                    "pid": info["pid"],
                    "name": info["name"] or "Unknown",
                    "cpu": info["cpu_percent"] or 0.0,
                    "mem_pct": info["memory_percent"] or 0.0,
                    "mem_rss": ram_used,
                    "threads": info["num_threads"] or 0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Sort by CPU usage descending and take the top 10
        processes.sort(key=lambda p: p["cpu"], reverse=True)
        top_processes = processes[:10]

        # Clear existing rows
        for existing_row in self.tree.get_children():
            self.tree.delete(existing_row)

        # Insert new rows
        for p in top_processes:
            self.tree.insert("", tk.END, values=(
                p["pid"],
                p["name"][:35],
                f"{p['cpu']:.1f}",
                f"{p['mem_pct']:.1f}",
                self._bytes_to_readable(p["mem_rss"]),
                p["threads"]
            ))

if __name__ == "__main__":
    app = TaskManagerApp()
    app.mainloop()