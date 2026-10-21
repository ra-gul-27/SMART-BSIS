import os
import customtkinter as ctk
from PIL import Image
from app.constants import COLORS, FONTS
from app.models.anpr_record_model import ANPRRecordModel

class ANPRRecordsView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.app_controller = app_controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) 

        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.grid(row=0, column=0, sticky="nsew")
        self.scroll_container.grid_columnconfigure(0, weight=1)

        self.search_var = ctk.StringVar(value="")
        self.cam_filter_var = ctk.StringVar(value="All Cameras")
        self.selected_record = None

        self._build_header()
        
        self.content_grid = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.content_grid.grid(row=1, column=0, sticky="nsew", padx=32, pady=16)
        self.content_grid.grid_columnconfigure(0, weight=2)
        self.content_grid.grid_columnconfigure(1, weight=1)
        
        self._build_table_panel(self.content_grid)
        self._build_sidebar(self.content_grid)

    def _build_header(self):
        header = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 16))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left, text="ANPR Records & License Plate Log", font=FONTS["headline_lg"], text_color=COLORS["on_surface"]).pack(anchor="w")
        ctk.CTkLabel(left, text="Monitor, verify and audit automated number plate recognition captures", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e", pady=(16, 0))

        # Search plate entry
        self.search_entry = ctk.CTkEntry(
            right, placeholder_text="🔍 Search Plate / Cam...", textvariable=self.search_var,
            font=FONTS["body_md"], fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], width=170, height=38
        )
        self.search_entry.pack(side="left", padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", lambda e: self._populate_grid())

        # Camera dropdown filter
        self.cam_dropdown = ctk.CTkOptionMenu(
            right, values=["All Cameras", "CAM-01 (Bay B02)", "CAM-02 (Entry)", "CAM-03 (Exit)"],
            variable=self.cam_filter_var, font=FONTS["body_md"], fg_color=COLORS["surface_container_lowest"],
            button_color=COLORS["surface_container"], button_hover_color=COLORS["outline_variant"],
            text_color=COLORS["on_surface"], height=38, command=lambda e: self._populate_grid()
        )
        self.cam_dropdown.pack(side="left", padx=(0, 8))

        # Export CSV Button
        self.export_btn = ctk.CTkButton(
            right, text="📥 Export CSV", font=FONTS["label_md"], height=38,
            fg_color=COLORS["primary"], text_color=COLORS["on_primary"], hover_color=COLORS["primary_container"],
            command=self._export_csv_action
        )
        self.export_btn.pack(side="left")

    def _export_csv_action(self):
        try:
            count = ANPRRecordModel.export_csv("anpr_records_export.csv")
            self.export_btn.configure(text=f"✔ Exported ({count})", fg_color="#10b981")
            self.after(3000, lambda: self.export_btn.configure(text="📥 Export CSV", fg_color=COLORS["primary"]))
        except Exception as e:
            self.export_btn.configure(text=f"Error: {e}")

    def _build_table_panel(self, parent):
        table_card = ctk.CTkFrame(parent, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        table_card.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        
        # Header Row
        thead = ctk.CTkFrame(table_card, fg_color=COLORS["surface_container_low"], corner_radius=12)
        thead.pack(fill="x", padx=1, pady=1)
        th_row = ctk.CTkFrame(thead, fg_color="transparent")
        th_row.pack(fill="x", padx=16, pady=12)

        self.cols = [
            ("TIMESTAMP", 1.2), ("CAMERA", 1.2), ("REGISTRATION", 1.6), 
            ("CONFIDENCE", 1.1), ("BAY", 0.7), ("STATUS", 1.2)
        ]
        
        for i, (c, w) in enumerate(self.cols):
            th_row.grid_columnconfigure(i, weight=int(w*10), uniform="col")
            anchor = "w" if i < len(self.cols) - 1 else "e"
            sticky = "w" if anchor == "w" else "e"
            ctk.CTkLabel(th_row, text=c, font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).grid(row=0, column=i, sticky=sticky, padx=4)

        border1 = ctk.CTkFrame(table_card, fg_color=COLORS["outline_variant"], height=1)
        border1.pack(fill="x", padx=1)

        # Table Body Container
        self.grid_container = ctk.CTkFrame(table_card, fg_color="transparent")
        self.grid_container.pack(fill="x")
        self.table_card = table_card

        self._populate_grid()

        # Pagination Footer
        border_footer = ctk.CTkFrame(table_card, fg_color=COLORS["outline_variant"], height=1)
        border_footer.pack(fill="x", padx=1)
        
        tfoot = ctk.CTkFrame(table_card, fg_color=COLORS["surface_container_lowest"], corner_radius=12)
        tfoot.pack(fill="x", padx=1, pady=(0, 1))
        tfoot_mask = ctk.CTkFrame(tfoot, fg_color=COLORS["surface_container_lowest"], height=8, corner_radius=0)
        tfoot_mask.pack(side="top", fill="x")

        tfoot_content = ctk.CTkFrame(tfoot, fg_color="transparent")
        tfoot_content.pack(fill="x", padx=16, pady=(4, 12))

        self.footer_count = ctk.CTkLabel(tfoot_content, text="Loading entries...", font=("Inter", 12), text_color=COLORS["on_surface_variant"])
        self.footer_count.pack(side="left")

    def _populate_grid(self):
        for widget in self.grid_container.winfo_children():
            widget.destroy()

        cam_f = self.cam_filter_var.get()
        search_f = self.search_var.get().strip()
        records = ANPRRecordModel.get_all_records(camera_filter=cam_f, search_term=search_f)

        if hasattr(self, "footer_count"):
            self.footer_count.configure(text=f"Showing {len(records)} verified license plate captures")

        if records and self.selected_record is None:
            self.selected_record = records[0]

        for i, row in enumerate(records):
            is_verified = (row["match_status"] == "Verified")
            s_bg = "#d1fae5" if is_verified else "#fee2e2"
            s_fg = "#059669" if is_verified else COLORS["error"]
            reg_col = "#0284c7" if is_verified else COLORS["error"]
            
            is_selected = self.selected_record and self.selected_record["id"] == row["id"]
            bg_color = "#f0f9ff" if is_selected else ("transparent" if i % 2 == 0 else COLORS["surface_container_low"])
            
            tr = ctk.CTkFrame(self.grid_container, fg_color=bg_color, corner_radius=0, cursor="hand2")
            tr.pack(fill="x", padx=1)
            
            tr_content = ctk.CTkFrame(tr, fg_color="transparent")
            tr_content.pack(fill="x", padx=16, pady=10)
            
            for j, (c, w) in enumerate(self.cols):
                tr_content.grid_columnconfigure(j, weight=int(w*10), uniform="col")

            # Col 1: Timestamp
            c1 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c1.grid(row=0, column=0, sticky="ew", padx=4)
            ui_time = row["timestamp"].split(" ")[1] if " " in row["timestamp"] else row["timestamp"]
            ctk.CTkLabel(c1, text=ui_time, font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(anchor="w")

            # Col 2: Camera
            c2 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c2.grid(row=0, column=1, sticky="ew", padx=4)
            ctk.CTkLabel(c2, text=row["camera_loc"], font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")

            # Col 3: Registration
            c3 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c3.grid(row=0, column=2, sticky="ew", padx=4)
            ctk.CTkLabel(c3, text=row["plate_number"], font=("Inter", 13, "bold"), text_color=reg_col).pack(anchor="w")

            # Col 4: Confidence
            c4 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c4.grid(row=0, column=3, sticky="ew", padx=4)
            ctk.CTkLabel(c4, text=f"{row['confidence']}%", font=FONTS["data_mono"], text_color="#10b981" if is_verified else "#f59e0b").pack(anchor="w")

            # Col 5: Bay
            c5 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c5.grid(row=0, column=4, sticky="ew", padx=4)
            ctk.CTkLabel(c5, text=row["bay"], font=FONTS["data_mono"], text_color=COLORS["primary"]).pack(anchor="w")

            # Col 6: Status
            c6 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c6.grid(row=0, column=5, sticky="ew", padx=4)
            s_badge = ctk.CTkFrame(c6, fg_color=s_bg, border_color=s_bg, border_width=1, corner_radius=12)
            s_badge.pack(anchor="e")
            icon = "✓" if is_verified else "⚠"
            ctk.CTkLabel(s_badge, text=f"{icon} {row['match_status']}", text_color=s_fg, font=("Inter", 10, "bold")).pack(padx=8, pady=2)

            # Bind row click to inspect
            def on_row_click(e, rec=row):
                self.selected_record = rec
                self._populate_grid()
                self._build_sidebar(self.content_grid)

            tr.bind("<Button-1>", on_row_click)
            tr_content.bind("<Button-1>", on_row_click)
            for child in tr_content.winfo_children():
                child.bind("<Button-1>", on_row_click)
                for grandchild in child.winfo_children():
                    grandchild.bind("<Button-1>", on_row_click)

            if i < len(records) - 1:
                border = ctk.CTkFrame(self.grid_container, fg_color=COLORS["outline_variant"], height=1)
                border.pack(fill="x", padx=1)

    def _build_sidebar(self, parent):
        if hasattr(self, "side_panel_frame") and self.side_panel_frame is not None:
            self.side_panel_frame.destroy()

        self.side_panel_frame = ctk.CTkFrame(parent, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        self.side_panel_frame.grid(row=0, column=1, sticky="nsew")

        rec = self.selected_record
        plate = rec["plate_number"] if rec else "TN 01 AN 2345"
        rec_id = f"ANP-{rec['id']}" if rec else "ANP-101"
        conf = rec["confidence"] if rec else 94.2
        camera = rec["camera_loc"] if rec else "CAM-01 (Bay B02)"
        bay = rec["bay"] if rec else "B02"
        b_type = rec["bus_type"] if rec else "AC Volvo Express"
        driver = rec["driver"] if rec else "Kannan P"
        dest = rec["dest"] if rec else "Bangalore Shantinagar"

        # Header
        head = ctk.CTkFrame(self.side_panel_frame, fg_color=COLORS["surface_container_low"], corner_radius=12)
        head.pack(fill="x", padx=1, pady=1)
        h_inner = ctk.CTkFrame(head, fg_color="transparent")
        h_inner.pack(fill="x", padx=16, pady=14)
        ctk.CTkLabel(h_inner, text="Capture Telemetry & Plate", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(side="left")
        
        badge = ctk.CTkFrame(h_inner, fg_color="#e0f2fe", corner_radius=4)
        badge.pack(side="right")
        ctk.CTkLabel(badge, text=rec_id, text_color="#0284c7", font=("Inter", 11, "bold")).pack(padx=8, pady=2)

        # Scrollable Content
        body = ctk.CTkScrollableFrame(self.side_panel_frame, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=16)

        # Image Container
        img_box = ctk.CTkFrame(body, fg_color="#090d16", border_color=COLORS["outline_variant"], border_width=1, corner_radius=8, height=180)
        img_box.pack(fill="x", pady=(0, 16))
        img_box.pack_propagate(False)
        
        img_lbl = ctk.CTkLabel(img_box, text="")
        img_lbl.place(relx=0.5, rely=0.45, anchor="center")

        img_cand = "live_cctv_annotated.jpg" if os.path.exists("live_cctv_annotated.jpg") else "real_bus_sample.jpg"
        if os.path.exists(img_cand):
            try:
                pil_img = Image.open(img_cand)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(280, 150))
                img_lbl.configure(image=ctk_img)
            except Exception:
                img_lbl.configure(text="[ CCTV Image Preview ]", text_color="#94a3b8")

        # Plate High-Contrast Badge
        ocr_box = ctk.CTkFrame(body, fg_color="#0284c7", corner_radius=6)
        ocr_box.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(ocr_box, text=plate, font=("Inter", 16, "bold"), text_color="#ffffff").pack(pady=8)

        # Analysis Grid
        grid = ctk.CTkFrame(body, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 16))
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        a1 = ctk.CTkFrame(grid, fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=8)
        a1.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        a1_inner = ctk.CTkFrame(a1, fg_color="transparent")
        a1_inner.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(a1_inner, text="OCR CONFIDENCE", font=("Inter", 9, "bold"), text_color=COLORS["on_surface_variant"]).pack(anchor="w")
        ctk.CTkLabel(a1_inner, text=f"{conf}%", font=("Inter", 16, "bold"), text_color="#10b981").pack(anchor="w", pady=(2, 0))

        a2 = ctk.CTkFrame(grid, fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=8)
        a2.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        a2_inner = ctk.CTkFrame(a2, fg_color="transparent")
        a2_inner.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(a2_inner, text="CAMERA LOCATION", font=("Inter", 9, "bold"), text_color=COLORS["on_surface_variant"]).pack(anchor="w")
        ctk.CTkLabel(a2_inner, text=f"Bay {bay}", font=("Inter", 16, "bold"), text_color="#0284c7").pack(anchor="w", pady=(2, 0))

        # Matched Bus Record Info
        ctk.CTkLabel(body, text="RESOLVED BUS TELEMETRY", font=("Inter", 10, "bold"), text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(8, 8))
        
        info = [
            ("Model / Type", b_type),
            ("Destination", dest),
            ("Assigned Driver", driver),
            ("Sensor Feed", camera)
        ]

        for k, v in info:
            row = ctk.CTkFrame(body, fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=6)
            row.pack(fill="x", pady=3)
            r_inner = ctk.CTkFrame(row, fg_color="transparent")
            r_inner.pack(fill="x", padx=10, pady=6)
            ctk.CTkLabel(r_inner, text=k, font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(side="left")
            ctk.CTkLabel(r_inner, text=v, font=("Inter", 11, "bold"), text_color=COLORS["on_surface"]).pack(side="right")

        # Action Footer
        foot = ctk.CTkFrame(self.side_panel_frame, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        foot.pack(fill="x", side="bottom")
        
        f_inner = ctk.CTkFrame(foot, fg_color="transparent")
        f_inner.pack(fill="x", padx=16, pady=14)
        
        def flag_review():
            if self.selected_record:
                ANPRRecordModel.update_record_status(self.selected_record["id"], "Flagged")
                self.selected_record["match_status"] = "Flagged"
                self._populate_grid()
                self._build_sidebar(self.content_grid)

        def confirm_match():
            if self.selected_record:
                ANPRRecordModel.update_record_status(self.selected_record["id"], "Verified")
                self.selected_record["match_status"] = "Verified"
                self._populate_grid()
                self._build_sidebar(self.content_grid)

        ctk.CTkButton(f_inner, text="Flag Review", font=FONTS["body_md"], text_color=COLORS["error"], fg_color="#fee2e2", hover_color="#fecaca", height=36, command=flag_review).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(f_inner, text="Confirm Match", font=FONTS["body_md"], text_color="#ffffff", fg_color=COLORS["primary"], hover_color=COLORS["primary_container"], height=36, command=confirm_match).pack(side="right", fill="x", expand=True, padx=(6, 0))
