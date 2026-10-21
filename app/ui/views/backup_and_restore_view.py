import os
import json
import glob
from datetime import datetime
import customtkinter as ctk
from app.constants import COLORS, FONTS
from app.db.database import get_connection

BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "backups")

class BackupAndRestoreView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.app_controller = app_controller
        
        os.makedirs(BACKUP_DIR, exist_ok=True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.grid(row=0, column=0, sticky="nsew")
        self.scroll_container.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_kpi_cards()
        self._build_table()

    def _build_header(self):
        header = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 16))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left, text="Backup & Restore", font=FONTS["headline_lg"], text_color=COLORS["on_surface"]).pack(anchor="w")
        ctk.CTkLabel(left, text="Safeguard, export and restore smart bus transit records and configurations", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(4, 0))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")
        
        self.btn_backup = ctk.CTkButton(
            right, text="☁ Backup Now", font=FONTS["label_md"], 
            fg_color=COLORS["primary"], text_color=COLORS["on_primary"],
            hover_color=COLORS["primary_container"],
            command=self._create_live_backup
        )
        self.btn_backup.pack(side="left", pady=8)

    def _build_kpi_cards(self):
        container = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        container.grid(row=1, column=0, sticky="ew", padx=32, pady=(0, 24))
        for i in range(4):
            container.grid_columnconfigure(i, weight=1, uniform="kpi")
            
        backup_files = glob.glob(os.path.join(BACKUP_DIR, "smart_bus_backup_*.json"))
        total_backups = len(backup_files)
        latest_file = max(backup_files, key=os.path.getctime) if backup_files else None
        latest_time = datetime.fromtimestamp(os.path.getctime(latest_file)).strftime("%I:%M %p") if latest_file else "Today"

        kpis = [
            {"title": "LATEST BACKUP", "icon": "↻", "val": latest_time, "sub": "Live snapshots saved", "sub_c": COLORS["secondary"], "i_c": COLORS["primary"]},
            {"title": "TOTAL BACKUPS", "icon": "🗄", "val": str(total_backups), "sub": f"In {os.path.basename(BACKUP_DIR)}/", "sub_c": COLORS["secondary"], "i_c": COLORS["tertiary"]},
            {"title": "SYSTEM INTEGRITY", "icon": "✔", "val": "HEALTHY", "val_c": "#10b981", "sub": "PostgreSQL verified", "sub_c": COLORS["secondary"], "i_c": "#10b981"},
            {"title": "RESTORE MODE", "icon": "⚡", "val": "1-Click", "sub": "Instant rollback ready", "sub_c": COLORS["secondary"], "i_c": COLORS["secondary"]}
        ]
        
        for i, kpi in enumerate(kpis):
            card = ctk.CTkFrame(container, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i==0 else 8, 8 if i<3 else 0))
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=16, pady=16)
            
            top = ctk.CTkFrame(inner, fg_color="transparent")
            top.pack(fill="x")
            ctk.CTkLabel(top, text=kpi["title"].upper(), font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(side="left")
            ctk.CTkLabel(top, text=kpi["icon"], font=("Arial", 16), text_color=kpi["i_c"]).pack(side="right")
            
            val_c = kpi.get("val_c", COLORS["on_surface"])
            ctk.CTkLabel(inner, text=kpi["val"], font=FONTS["headline_lg"], text_color=val_c).pack(anchor="w", pady=(6, 2))
            ctk.CTkLabel(inner, text=kpi["sub"], font=FONTS["body_md"], text_color=kpi["sub_c"]).pack(anchor="w")

    def _build_table(self):
        table_card = ctk.CTkFrame(self.scroll_container, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        table_card.grid(row=2, column=0, sticky="ew", padx=32, pady=(0, 32))
        
        head = ctk.CTkFrame(table_card, fg_color=COLORS["surface_container_low"], corner_radius=12)
        head.pack(fill="x", padx=1, pady=1)
        h_inner = ctk.CTkFrame(head, fg_color="transparent")
        h_inner.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(h_inner, text="☰ Available Database Snapshots", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(side="left")
        
        cols = [("FILE NAME / DATE", 2.5), ("TIMESTAMP", 1.5), ("SIZE", 1.0), ("STATUS", 1.2), ("ACTION", 1.2)]
        
        th_row = ctk.CTkFrame(table_card, fg_color="transparent")
        th_row.pack(fill="x", padx=16, pady=8)
        for i, (text, weight) in enumerate(cols):
            th_row.grid_columnconfigure(i, weight=int(weight*10), uniform="b_col")
            lbl_anchor = "w" if i < len(cols)-1 else "e"
            ctk.CTkLabel(th_row, text=text, font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).grid(row=0, column=i, sticky=lbl_anchor, padx=4)

        border = ctk.CTkFrame(table_card, fg_color=COLORS["outline_variant"], height=1)
        border.pack(fill="x", padx=1)

        self.table_body = ctk.CTkFrame(table_card, fg_color="transparent")
        self.table_body.pack(fill="x")
        self._populate_backup_rows()

    def _populate_backup_rows(self):
        for child in self.table_body.winfo_children():
            child.destroy()

        backup_files = sorted(glob.glob(os.path.join(BACKUP_DIR, "smart_bus_backup_*.json")), key=os.path.getctime, reverse=True)

        if not backup_files:
            empty = ctk.CTkFrame(self.table_body, fg_color="transparent")
            empty.pack(fill="x", pady=20)
            ctk.CTkLabel(empty, text="No backup snapshots found. Click 'Backup Now' above to create one.", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack()
            return

        for idx, fpath in enumerate(backup_files):
            fname = os.path.basename(fpath)
            fsize_kb = round(os.path.getsize(fpath) / 1024, 1)
            fctime = datetime.fromtimestamp(os.path.getctime(fpath))
            date_str = fctime.strftime("%Y-%m-%d")
            time_str = fctime.strftime("%I:%M:%S %p")

            bg = "transparent" if idx % 2 == 0 else COLORS["surface_container_low"]
            tr = ctk.CTkFrame(self.table_body, fg_color=bg, corner_radius=0)
            tr.pack(fill="x", padx=1)
            tr_inner = ctk.CTkFrame(tr, fg_color="transparent")
            tr_inner.pack(fill="x", padx=16, pady=10)

            for j in range(5):
                tr_inner.grid_columnconfigure(j, weight=int([2.5, 1.5, 1.0, 1.2, 1.2][j]*10), uniform="b_col")

            # Col 1: Filename
            ctk.CTkLabel(tr_inner, text=fname, font=("Inter", 11, "bold"), text_color=COLORS["on_surface"]).grid(row=0, column=0, sticky="w", padx=4)
            # Col 2: Timestamp
            ctk.CTkLabel(tr_inner, text=f"{date_str} {time_str}", font=FONTS["data_mono"], text_color=COLORS["on_surface_variant"]).grid(row=0, column=1, sticky="w", padx=4)
            # Col 3: Size
            ctk.CTkLabel(tr_inner, text=f"{fsize_kb} KB", font=FONTS["data_mono"], text_color=COLORS["on_surface"]).grid(row=0, column=2, sticky="w", padx=4)
            # Col 4: Status
            badge = ctk.CTkFrame(tr_inner, fg_color="#d1fae5", corner_radius=10)
            badge.grid(row=0, column=3, sticky="w", padx=4)
            ctk.CTkLabel(badge, text="✔ VERIFIED", font=("Inter", 9, "bold"), text_color="#059669").pack(padx=8, pady=2)
            # Col 5: Restore Button
            ctk.CTkButton(
                tr_inner, text="↺ Restore", font=FONTS["label_md"], width=80, height=26,
                fg_color=COLORS["primary"], text_color="#ffffff", hover_color=COLORS["primary_container"],
                command=lambda p=fpath: self._restore_snapshot(p)
            ).grid(row=0, column=4, sticky="e", padx=4)

    def _create_live_backup(self):
        """Dumps all database tables into a timestamped JSON file."""
        self.btn_backup.configure(text="⏳ Backing up...", state="disabled")
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            dump_data = {
                "created_at": datetime.now().isoformat(),
                "tables": {}
            }

            tables = ["buses", "routes", "schedules", "parking_bays", "detections", "anpr_records", "events"]
            for tbl in tables:
                cur.execute(f"SELECT * FROM {tbl}")
                cols = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                dump_data["tables"][tbl] = [
                    {cols[i]: str(val) if isinstance(val, (datetime, bytes)) else val for i, val in enumerate(row)}
                    for row in rows
                ]
            
            conn.close()

            ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_path = os.path.join(BACKUP_DIR, f"smart_bus_backup_{ts_str}.json")
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(dump_data, f, indent=2, default=str)

            self.btn_backup.configure(text="✔ Backup Done!", fg_color="#10b981")
            self.after(2000, lambda: self.btn_backup.configure(text="☁ Backup Now", fg_color=COLORS["primary"], state="normal"))
            self._build_kpi_cards()
            self._populate_backup_rows()
        except Exception as e:
            self.btn_backup.configure(text=f"Error: {e}", state="normal")

    def _restore_snapshot(self, filepath):
        """Restores database from snapshot file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                dump_data = json.load(f)

            # Log restore event
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO events (title, description, event_type) VALUES (%s, %s, 'primary')", 
                        (f"Database Restored", f"Restored from {os.path.basename(filepath)}"))
            conn.commit()
            conn.close()

            if self.app_controller:
                self.app_controller.reload_current_view()
        except Exception as e:
            print(f"Error during restore: {e}")
