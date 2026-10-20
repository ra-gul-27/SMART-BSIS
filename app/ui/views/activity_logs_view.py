import customtkinter as ctk
import tkinter as tk
from app.constants import COLORS, FONTS

class ActivityLogsView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.app_controller = app_controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.grid(row=0, column=0, sticky="nsew")
        self.scroll_container.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_filters()
        self._build_table()

    def _build_header(self):
        header = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 16))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left, text="Activity Logs", font=FONTS["headline_lg"], text_color=COLORS["on_surface"]).pack(anchor="w")
        ctk.CTkLabel(left, text="Track system and administrator activities", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(4, 0))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")
        
        btn = ctk.CTkButton(right, text="📥 Export Logs", font=FONTS["label_md"], 
                           fg_color=COLORS["surface"], text_color=COLORS["primary"],
                           border_color=COLORS["outline_variant"], border_width=1,
                           hover_color=COLORS["surface_container_low"])
        btn.pack(pady=8)

    def _build_filters(self):
        # Bento style filter card
        card = ctk.CTkFrame(self.scroll_container, fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        card.grid(row=1, column=0, sticky="ew", padx=32, pady=(0, 24))
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=24)
        
        # 4 filter dropdowns + 1 button
        cols = [
            ("Date Range", "📅 Select Date"),
            ("Module", "All Modules ▾"),
            ("Action", "All Actions ▾"),
            ("Status", "All Statuses ▾")
        ]
        
        for i, (label, placeholder) in enumerate(cols):
            inner.grid_columnconfigure(i, weight=1, uniform="filter")
            f = ctk.CTkFrame(inner, fg_color="transparent")
            f.grid(row=0, column=i, sticky="ew", padx=(0, 16))
            
            ctk.CTkLabel(f, text=label, font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(0, 8))
            btn = ctk.CTkButton(f, text=placeholder, font=FONTS["body_md"], 
                               fg_color=COLORS["surface"], text_color=COLORS["on_surface"],
                               border_color=COLORS["outline_variant"], border_width=1,
                               hover_color=COLORS["surface_container_low"], anchor="w")
            btn.pack(fill="x")
            
        inner.grid_columnconfigure(4, weight=0)
        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.grid(row=0, column=4, sticky="sw")
        apply_btn = ctk.CTkButton(btn_frame, text="⚡ Apply", font=FONTS["label_md"],
                                 fg_color=COLORS["primary"], text_color=COLORS["on_primary"],
                                 hover_color=COLORS["surface_tint"], width=100)
        apply_btn.pack(fill="y", ipady=2)

    def _build_table(self):
        # Wrapper frame for exact table outline
        table_border = ctk.CTkFrame(self.scroll_container, fg_color="#94a3b8", corner_radius=12)
        table_border.grid(row=2, column=0, sticky="ew", padx=32, pady=(0, 32))
        
        # Inner card
        table_card = ctk.CTkFrame(table_border, fg_color=COLORS["surface_container_lowest"], corner_radius=11)
        table_card.pack(fill="both", expand=True, padx=1, pady=1)
        
        # table header
        th = ctk.CTkFrame(table_card, fg_color=COLORS["surface_container_low"], corner_radius=11)
        th.pack(fill="x")
        
        # Mask bottom corners to connect with the table body seamlessly
        bottom_mask = ctk.CTkFrame(th, fg_color=COLORS["surface_container_low"], height=12, corner_radius=0)
        bottom_mask.pack(side="bottom", fill="x")
        
        th_content = ctk.CTkFrame(th, fg_color="transparent")
        th_content.pack(fill="x", side="bottom")
        
        cols = [
            ("Timestamp", 1),
            ("Source", 1),
            ("Module", 1),
            ("Action", 2),
            ("Description", 3),
            ("Status", 1)
        ]
        
        for i, (text, weight) in enumerate(cols):
            th_content.grid_columnconfigure(i, weight=weight, uniform="col")
            # Perfectly aligned, exactly matching the deep blue requested earlier
            ctk.CTkLabel(th_content, text=text, font=("Segoe UI", 12, "bold"), text_color="#1e40af", anchor="w").grid(row=0, column=i, sticky="ew", padx=16, pady=10)
            
        # Heavy Border under table header for crisp separation
        ctk.CTkFrame(table_card, fg_color="#cbd5e1", height=2).pack(fill="x")
            
        data = [
            {"time": "10:42:15", "src_icon": "💻", "src": "SYSTEM", "src_bg": COLORS["surface_variant"], "src_c": COLORS["on_surface_variant"], "mod": "ANPR", "act": "Recognition", "desc": "TN 01 AB 1234 recognized", "desc_c": COLORS["on_surface"], "st": "SUCCESS", "st_bg": "#d1fae5", "st_c": "#059669"},
            {"time": "10:35:22", "src_icon": "👤", "src": "ADMIN", "src_bg": "#dbeafe", "src_c": COLORS["primary"], "mod": "Bus\nManagement", "act": "Update", "desc": "Updated Bus TN-02-C-5544 schedule", "desc_c": COLORS["on_surface"], "st": "SUCCESS", "st_bg": "#d1fae5", "st_c": "#059669", "bg": COLORS["surface"]},
            {"time": "10:15:05", "src_icon": "👤", "src": "ADMIN", "src_bg": "#dbeafe", "src_c": COLORS["primary"], "mod": "Bay\nManagement", "act": "Disable", "desc": "Disabled Bay B04 (Maintenance)", "desc_c": COLORS["on_surface"], "desc_font": ("Arial", 12, "bold"), "st": "WARNING", "st_bg": "#ffedd5", "st_c": "#b45309"},
            {"time": "09:58:41", "src_icon": "💻", "src": "SYSTEM", "src_bg": COLORS["surface_variant"], "src_c": COLORS["on_surface_variant"], "mod": "Hardware", "act": "Connection", "desc": "Camera Connection Lost (Bay A02)", "desc_c": COLORS["error"], "desc_font": ("Arial", 12, "bold"), "st": "ERROR", "st_bg": "#fee2e2", "st_c": "#b91c1c", "bg": COLORS["surface"]},
            {"time": "09:45:00", "src_icon": "💻", "src": "SYSTEM", "src_bg": COLORS["surface_variant"], "src_c": COLORS["on_surface_variant"], "mod": "Backup", "act": "Automated Task", "desc": "Daily DB snapshot completed", "desc_c": COLORS["on_surface"], "st": "SUCCESS", "st_bg": "#d1fae5", "st_c": "#059669"}
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
                    ctk.CTkLabel(cell, text=row["time"], font=FONTS["data_mono"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
                elif i == 1:
                    badge = ctk.CTkFrame(cell, fg_color=row["src_bg"], corner_radius=12)
                    badge.pack(anchor="w")
                    ctk.CTkLabel(badge, text=f'{row["src_icon"]} {row["src"]}', font=("Arial", 10, "bold"), text_color=row["src_c"]).pack(padx=8, pady=2)
                elif i == 2:
                    ctk.CTkLabel(cell, text=row["mod"], font=FONTS["data_mono"], text_color=COLORS["on_surface"], justify="left").pack(anchor="w")
                elif i == 3:
                    ctk.CTkLabel(cell, text=row["act"], font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(anchor="w")
                elif i == 4:
                    font = row.get("desc_font", FONTS["data_mono"])
                    ctk.CTkLabel(cell, text=row["desc"], font=font, text_color=row["desc_c"]).pack(anchor="w")
                elif i == 5:
                    badge = ctk.CTkFrame(cell, fg_color=row["st_bg"], corner_radius=12)
                    badge.pack(anchor="w")
                    ctk.CTkLabel(badge, text=f'● {row["st"]}', font=("Arial", 10, "bold"), text_color=row["st_c"]).pack(padx=8, pady=2)
                    
            if r_idx < len(data) - 1:
                # 2px divider between rows to guarantee visibility
                divider = ctk.CTkFrame(table_card, fg_color="#cbd5e1", height=2)
                divider.pack(fill="x")

        # Footer
        footer = ctk.CTkFrame(table_card, fg_color="transparent")
        footer.pack(fill="x", padx=16, pady=16)
        
        ctk.CTkLabel(footer, text="Showing 1 to 5 of 1,248 entries", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(side="left")
        
        pagination = ctk.CTkFrame(footer, fg_color="transparent")
        pagination.pack(side="right")
        
        ctk.CTkButton(pagination, text="<", width=30, fg_color="transparent", border_width=1, border_color=COLORS["outline_variant"], text_color=COLORS["on_surface_variant"]).pack(side="left", padx=2)
        ctk.CTkButton(pagination, text="1", width=30, fg_color=COLORS["primary"], text_color=COLORS["on_primary"]).pack(side="left", padx=2)
        ctk.CTkButton(pagination, text="2", width=30, fg_color="transparent", border_width=1, border_color=COLORS["outline_variant"], text_color=COLORS["on_surface_variant"]).pack(side="left", padx=2)
        ctk.CTkButton(pagination, text="3", width=30, fg_color="transparent", border_width=1, border_color=COLORS["outline_variant"], text_color=COLORS["on_surface_variant"]).pack(side="left", padx=2)
        ctk.CTkLabel(pagination, text="...", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(side="left", padx=4)
        ctk.CTkButton(pagination, text=">", width=30, fg_color="transparent", border_width=1, border_color=COLORS["outline_variant"], text_color=COLORS["on_surface_variant"]).pack(side="left", padx=2)
