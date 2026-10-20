import customtkinter as ctk
import tkinter as tk
from app.constants import COLORS, FONTS

class SettingsView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color=COLORS["surface_dim"], **kwargs)
        self.app_controller = app_controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.grid(row=0, column=0, sticky="nsew")
        self.scroll_container.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_settings_grid()
        self._build_action_bar()

    def _build_header(self):
        header = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 16))
        
        ctk.CTkLabel(header, text="System Settings", font=FONTS["headline_lg"], text_color=COLORS["on_surface"]).pack(anchor="w")
        ctk.CTkLabel(header, text="Configure transport management and AI parameters", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(4, 0))

    def _build_settings_grid(self):
        grid = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        grid.grid(row=1, column=0, sticky="ew", padx=32)
        grid.grid_columnconfigure((0, 1), weight=1, uniform="col")

        # Top Left: General Settings
        gen_card, gen_content = self._create_card(grid, "💻", "General")
        gen_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=8)
        self._build_general(gen_content)

        # Top Right: AI Settings
        ai_card, ai_content = self._create_card(grid, "🧠", "AI Detection Settings")
        ai_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=8)
        self._build_ai(ai_content)

        # Middle: Camera Config (Spans both)
        cam_card, cam_content = self._create_card(grid, "🎥", "Camera Configuration", right_widget=self._add_camera_btn)
        cam_card.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=8)
        self._build_cameras(cam_content)

        # Bottom Left: ANPR Settings
        anpr_card, anpr_content = self._create_card(grid, "🚗", "ANPR Settings")
        anpr_card.grid(row=2, column=0, sticky="nsew", padx=(0, 8), pady=8)
        self._build_anpr(anpr_content)

        # Bottom Right Stack: Parking and Database
        stack_right = ctk.CTkFrame(grid, fg_color="transparent")
        stack_right.grid(row=2, column=1, sticky="nsew", padx=(8, 0), pady=0)
        stack_right.grid_columnconfigure(0, weight=1)

        park_card, park_content = self._create_card(stack_right, "🅿", "Parking Bay Settings")
        park_card.grid(row=0, column=0, sticky="nsew", pady=(8, 16))
        self._build_parking(park_content)

        db_card, db_content = self._create_card(stack_right, "🗄", "Database", right_widget=self._db_status)
        db_card.grid(row=1, column=0, sticky="nsew", pady=(0, 8))
        self._build_database(db_content)

    def _create_card(self, parent, icon, title, right_widget=None):
        card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=16)
        
        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(left, text=icon, font=("Arial", 18), text_color=COLORS["primary"]).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(left, text=title, font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(side="left")
        
        if right_widget:
            right_widget(header).pack(side="right")
            
        ctk.CTkFrame(card, fg_color=COLORS["outline_variant"], height=1).pack(fill="x", padx=16)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=16, pady=16)
        return card, content
        
    def _add_camera_btn(self, parent):
        return ctk.CTkButton(parent, text="+ Add Camera", font=FONTS["label_md"], 
                           fg_color=COLORS["primary_container"], text_color=COLORS["on_primary_container"],
                           hover_color=COLORS["primary"])

    def _db_status(self, parent):
        badge = ctk.CTkFrame(parent, fg_color="#d1fae5", corner_radius=12)
        ctk.CTkLabel(badge, text="Connected", font=("Arial", 11, "bold"), text_color="#065f46").pack(padx=8, pady=2)
        return badge

    def _build_input(self, parent, label, val, is_combobox=False, opts=None):
        ctk.CTkLabel(parent, text=label, font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(0, 4))
        if is_combobox:
            cb = ctk.CTkComboBox(parent, values=opts, font=FONTS["body_md"], text_color=COLORS["on_surface"], 
                                fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], 
                                button_color=COLORS["surface"], button_hover_color=COLORS["surface_variant"])
            cb.set(val)
            cb.pack(fill="x", pady=(0, 16))
        else:
            ent = ctk.CTkEntry(parent, font=FONTS["body_md"], text_color=COLORS["on_surface"], 
                              fg_color=COLORS["surface"], border_color=COLORS["outline_variant"])
            ent.insert(0, val)
            ent.pack(fill="x", pady=(0, 16))

    def _build_general(self, parent):
        self._build_input(parent, "Terminal Name", "Central Station Terminal A")
        self._build_input(parent, "Location Coordinates", "40.7128° N, 74.0060° W")
        self._build_input(parent, "System Timezone", "UTC-05:00 Eastern Time (US & Canada)", True, 
                         ["UTC-05:00 Eastern Time (US & Canada)", "UTC+00:00 Greenwich Mean Time"])

    def _build_ai(self, parent):
        # slider
        ctk.CTkLabel(parent, text="YOLO Confidence Threshold (%)", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(0, 4))
        sl_row = ctk.CTkFrame(parent, fg_color="transparent")
        sl_row.pack(fill="x", pady=(0, 16))
        sl = ctk.CTkSlider(sl_row, from_=0, to=100, button_color=COLORS["primary"], progress_color=COLORS["primary"])
        sl.set(85)
        sl.pack(side="left", fill="x", expand=True, padx=(0, 16))
        ctk.CTkLabel(sl_row, text="85", font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(side="right")
        
        self._build_input(parent, "Detection Interval (ms)", "100")
        
        sw_row = ctk.CTkFrame(parent, fg_color="transparent")
        sw_row.pack(fill="x", pady=(8, 0))
        left = ctk.CTkFrame(sw_row, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(left, text="Enable GPU Acceleration", font=FONTS["label_md"], text_color=COLORS["on_surface"]).pack(anchor="w")
        ctk.CTkLabel(left, text="Uses TensorRT if available", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
        
        sw = ctk.CTkSwitch(sw_row, text="", progress_color=COLORS["primary"])
        sw.select()
        sw.pack(side="right")

    def _build_anpr(self, parent):
        self._build_input(parent, "OCR Confidence Threshold (%)", "92")
        self._build_input(parent, "Read Retry Attempts", "3 (Balanced)", True,
                         ["1 (Fastest)", "2", "3 (Balanced)", "5 (Highest Accuracy)"])

    def _build_parking(self, parent):
        self._build_input(parent, "Default Zone Mapping", "Zone A (Intercity)", True, 
                         ["Zone A (Intercity)", "Zone B (Local Transit)", "Dynamic Allocation"])

    def _build_database(self, parent):
        row1 = ctk.CTkFrame(parent, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(row1, text="Last Sync", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(side="left")
        ctk.CTkLabel(row1, text="2 mins ago", font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(side="right")
        
        row2 = ctk.CTkFrame(parent, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(row2, text="Sync Interval", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(side="left")
        ctk.CTkLabel(row2, text="5 minutes", font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(side="right")
        
        ctk.CTkButton(parent, text="Force Manual Sync", font=FONTS["label_md"], 
                           fg_color="transparent", text_color=COLORS["on_surface"],
                           border_color=COLORS["outline"], border_width=1,
                           hover_color=COLORS["surface_container_low"]).pack(fill="x", pady=(8, 0))

    def _build_cameras(self, parent):
        th_content = ctk.CTkFrame(parent, fg_color=COLORS["surface_container_low"], corner_radius=8)
        th_content.pack(fill="x", pady=(0, 0))
        
        cols = [
            ("ID", 1),
            ("Name", 2),
            ("IP Address", 2),
            ("FPS Target", 1),
            ("Status", 1),
            ("Actions", 1)
        ]
        
        for i, (text, weight) in enumerate(cols):
            th_content.grid_columnconfigure(i, weight=weight, uniform="col")
            lbl_anchor = "w" if i < len(cols)-1 else "e"
            ctk.CTkLabel(th_content, text=text.upper(), font=("Segoe UI", 12, "bold"), text_color="#1e40af", anchor=lbl_anchor).grid(row=0, column=i, sticky="ew", padx=16, pady=8)
            
        ctk.CTkFrame(parent, fg_color="#cbd5e1", height=2).pack(fill="x")
            
        data = [
            {"id": "CAM-01", "name": "Entry Gate North", "ip": "192.168.1.101", "fps": "30", "st": "Online"},
            {"id": "CAM-02", "name": "Bay Area A", "ip": "192.168.1.102", "fps": "24", "st": "Online"}
        ]
        
        for r_idx, row in enumerate(data):
            tr = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
            tr.pack(fill="x")
            
            for i, (text, weight) in enumerate(cols):
                tr.grid_columnconfigure(i, weight=weight, uniform="col")
                
                cell = ctk.CTkFrame(tr, fg_color="transparent")
                cell.grid(row=0, column=i, sticky="ew", padx=16, pady=8)
                
                if i == 0:
                    ctk.CTkLabel(cell, text=row["id"], font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(anchor="w")
                elif i == 1:
                    ctk.CTkLabel(cell, text=row["name"], font=FONTS["body_md"], text_color=COLORS["on_surface"]).pack(anchor="w")
                elif i == 2:
                    ctk.CTkLabel(cell, text=row["ip"], font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(anchor="w")
                elif i == 3:
                    ctk.CTkLabel(cell, text=row["fps"], font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(anchor="w")
                elif i == 4:
                    badge = ctk.CTkFrame(cell, fg_color="#dcfce7", corner_radius=12) # green-100
                    badge.pack(anchor="w")
                    ctk.CTkLabel(badge, text=row["st"], font=("Arial", 11, "bold"), text_color="#166534").pack(padx=8, pady=2) # green-800
                elif i == 5:
                    ctk.CTkButton(cell, text="✎ Edit", font=FONTS["label_md"], fg_color="transparent", text_color=COLORS["primary"], hover_color=COLORS["surface_container_low"], width=60).pack(anchor="e")
                    
            if r_idx < len(data) - 1:
                divider = ctk.CTkFrame(parent, fg_color="#e2e8f0", height=1)
                divider.pack(fill="x")

    def _build_action_bar(self):
        bar = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        bar.grid(row=2, column=0, sticky="ew", padx=32, pady=(16, 32))
        
        top_line = ctk.CTkFrame(bar, fg_color=COLORS["outline_variant"], height=1)
        top_line.pack(fill="x", pady=(0, 16))
        
        btn_container = ctk.CTkFrame(bar, fg_color="transparent")
        btn_container.pack(side="right")
        
        btn_discard = ctk.CTkButton(btn_container, text="Discard Changes", font=FONTS["label_md"], 
                           fg_color="transparent", text_color=COLORS["on_surface"],
                           border_color=COLORS["outline"], border_width=1,
                           hover_color=COLORS["surface_container_low"])
        btn_discard.pack(side="left", padx=(0, 16))
        
        btn_save = ctk.CTkButton(btn_container, text="Save Configuration", font=FONTS["label_md"], 
                           fg_color=COLORS["primary"], text_color=COLORS["on_primary"],
                           hover_color="#004e9c")
        btn_save.pack(side="left")
