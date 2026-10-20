import customtkinter as ctk
import tkinter as tk
from app.constants import COLORS, FONTS

class BackupAndRestoreView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.app_controller = app_controller
        
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
        ctk.CTkLabel(left, text="Protect and recover transport system data", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(4, 0))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")
        
        btn_restore = ctk.CTkButton(right, text="↺ Restore Backup", font=FONTS["label_md"], 
                           fg_color=COLORS["surface_container"], text_color=COLORS["primary"],
                           border_color=COLORS["outline_variant"], border_width=1,
                           hover_color=COLORS["surface_variant"])
        btn_restore.pack(side="left", padx=(0, 16), pady=8)
        
        btn_backup = ctk.CTkButton(right, text="☁ Backup Now", font=FONTS["label_md"], 
                           fg_color=COLORS["primary"], text_color=COLORS["on_primary"],
                           hover_color="#004e9c") # slightly darker primary
        btn_backup.pack(side="left", pady=8)

    def _build_kpi_cards(self):
        container = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        container.grid(row=1, column=0, sticky="ew", padx=32, pady=(0, 24))
        for i in range(4):
            container.grid_columnconfigure(i, weight=1, uniform="kpi")
            
        kpis = [
            {"title": "Last Backup", "icon": "↻", "val": "Today", "sub": "09:30 AM", "sub_c": COLORS["secondary"], "i_c": COLORS["primary"]},
            {"title": "Database Size", "icon": "🗄", "val": "2.4 GB", "sub": "📈 +0.1 GB this week", "sub_c": COLORS["secondary"], "i_c": COLORS["tertiary"]},
            {"title": "Backup Status", "icon": "✔", "val": "SUCCESS", "val_c": "#10b981", "sub": "All systems secured", "sub_c": COLORS["secondary"], "i_c": "#10b981"},
            {"title": "Frequency", "icon": "📅", "val": "Daily", "sub": "Automated via CRON", "sub_c": COLORS["secondary"], "i_c": COLORS["secondary"]}
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
            ctk.CTkLabel(inner, text=kpi["val"], font=FONTS["headline_lg"], text_color=val_c).pack(anchor="w", pady=(8, 4))
            ctk.CTkLabel(inner, text=kpi["sub"], font=FONTS["body_md"], text_color=kpi["sub_c"]).pack(anchor="w")

    def _build_table(self):
        # Wrapper frame for exact table outline
        table_border = ctk.CTkFrame(self.scroll_container, fg_color="#94a3b8", corner_radius=12)
        table_border.grid(row=2, column=0, sticky="ew", padx=32, pady=(0, 32))
        
        # Inner card
        table_card = ctk.CTkFrame(table_border, fg_color=COLORS["surface_container_lowest"], corner_radius=11)
        table_card.pack(fill="both", expand=True, padx=1, pady=1)
        
        # table header top (with title and filter)
        header = ctk.CTkFrame(table_card, fg_color=COLORS["surface_container_low"], corner_radius=11)
        header.pack(fill="x")
        
        title_row = ctk.CTkFrame(header, fg_color="transparent")
        title_row.pack(fill="x", padx=16, pady=(12, 0))
        ctk.CTkLabel(title_row, text="☰ Backup History", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(side="left")
        ctk.CTkButton(title_row, text="Last 30 Days ▾", font=FONTS["label_md"], fg_color=COLORS["surface_container_lowest"], text_color=COLORS["on_surface"], border_width=1, border_color=COLORS["outline_variant"], hover_color=COLORS["surface_container_low"], width=120).pack(side="right")
        
        # Mask bottom corners
        bottom_mask = ctk.CTkFrame(header, fg_color=COLORS["surface_container_low"], height=12, corner_radius=0)
        bottom_mask.pack(side="bottom", fill="x")
        
        th_content = ctk.CTkFrame(header, fg_color="transparent")
        th_content.pack(fill="x", side="bottom")
        
        cols = [
            ("Date", 2),
            ("Time", 2),
            ("Type", 1),
            ("Size", 1),
            ("Status", 1),
            ("Action", 1)
        ]
        
        for i, (text, weight) in enumerate(cols):
            th_content.grid_columnconfigure(i, weight=weight, uniform="col")
            lbl_anchor = "w" if i < len(cols)-1 else "e"
            ctk.CTkLabel(th_content, text=text.upper(), font=("Segoe UI", 12, "bold"), text_color="#1e40af", anchor=lbl_anchor).grid(row=0, column=i, sticky="ew", padx=16, pady=10)
            
        # Heavy Border under table header for crisp separation
        ctk.CTkFrame(table_card, fg_color="#cbd5e1", height=2).pack(fill="x")
            
        data = [
            {"date": "2023-10-27", "time": "09:30:00 AM", "type": "AUTO", "type_bg": "#dbeafe", "type_c": COLORS["primary"], "size": "2.41 GB", "st": "SUCCESS", "st_bg": "#d1fae5", "st_c": "#059669"},
            {"date": "2023-10-26", "time": "09:30:00 AM", "type": "AUTO", "type_bg": "#dbeafe", "type_c": COLORS["primary"], "size": "2.39 GB", "st": "SUCCESS", "st_bg": "#d1fae5", "st_c": "#059669", "bg": COLORS["surface"]},
            {"date": "2023-10-25", "time": "14:15:22 PM", "type": "MANUAL", "type_bg": "#ffedd5", "type_c": "#b45309", "size": "2.38 GB", "st": "SUCCESS", "st_bg": "#d1fae5", "st_c": "#059669"},
            {"date": "2023-10-25", "time": "09:30:00 AM", "type": "AUTO", "type_bg": "#dbeafe", "type_c": COLORS["primary"], "size": "2.38 GB", "st": "FAILED", "st_bg": "#fee2e2", "st_c": "#b91c1c", "bg": COLORS["surface"]},
            {"date": "2023-10-24", "time": "09:30:00 AM", "type": "AUTO", "type_bg": "#dbeafe", "type_c": COLORS["primary"], "size": "2.36 GB", "st": "SUCCESS", "st_bg": "#d1fae5", "st_c": "#059669"}
        ]
        
        for r_idx, row in enumerate(data):
            bg = row.get("bg", "transparent")
            tr = ctk.CTkFrame(table_card, fg_color=bg, corner_radius=0)
            tr.pack(fill="x")
            
            for i, (text, weight) in enumerate(cols):
                tr.grid_columnconfigure(i, weight=weight, uniform="col")
                
                cell = ctk.CTkFrame(tr, fg_color="transparent")
                cell.grid(row=0, column=i, sticky="ew", padx=16, pady=12)
                
                if i == 0:
                    ctk.CTkLabel(cell, text=row["date"], font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(anchor="w")
                elif i == 1:
                    ctk.CTkLabel(cell, text=row["time"], font=FONTS["data_mono"], text_color=COLORS["secondary"]).pack(anchor="w")
                elif i == 2:
                    badge = ctk.CTkFrame(cell, fg_color=row["type_bg"], corner_radius=4)
                    badge.pack(anchor="w")
                    ctk.CTkLabel(badge, text=row["type"], font=("Arial", 11, "bold"), text_color=row["type_c"]).pack(padx=8, pady=2)
                elif i == 3:
                    ctk.CTkLabel(cell, text=row["size"], font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(anchor="w")
                elif i == 4:
                    badge = ctk.CTkFrame(cell, fg_color=row["st_bg"], corner_radius=12)
                    badge.pack(anchor="w")
                    st_icon = "✔" if row["st"] == "SUCCESS" else "✖"
                    ctk.CTkLabel(badge, text=f'{st_icon} {row["st"]}', font=("Arial", 10, "bold"), text_color=row["st_c"]).pack(padx=8, pady=2)
                elif i == 5:
                    if row["st"] == "SUCCESS":
                        ctk.CTkButton(cell, text="📥 Restore", font=FONTS["label_md"], fg_color="transparent", text_color=COLORS["primary"], hover_color=COLORS["surface_container"], width=80).pack(anchor="e")
                    else:
                        ctk.CTkButton(cell, text="🚫 N/A", font=FONTS["label_md"], fg_color="transparent", text_color=COLORS["outline"], width=80, state="disabled").pack(anchor="e")
                    
            if r_idx < len(data) - 1:
                divider = ctk.CTkFrame(table_card, fg_color="#cbd5e1", height=2)
                divider.pack(fill="x")

        # Footer
        footer = ctk.CTkFrame(table_card, fg_color="transparent")
        footer.pack(fill="x", padx=16, pady=16)
        
        ctk.CTkLabel(footer, text="Showing 5 of 124 backups", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(side="left")
        
        pagination = ctk.CTkFrame(footer, fg_color="transparent")
        pagination.pack(side="right")
        
        ctk.CTkButton(pagination, text="<", width=30, fg_color="transparent", border_width=1, border_color=COLORS["outline_variant"], text_color=COLORS["on_surface_variant"]).pack(side="left", padx=2)
        ctk.CTkButton(pagination, text=">", width=30, fg_color="transparent", border_width=1, border_color=COLORS["outline_variant"], text_color=COLORS["on_surface_variant"]).pack(side="left", padx=2)
