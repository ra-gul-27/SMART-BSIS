import customtkinter as ctk
from app.constants import COLORS, FONTS
from app.models.bus_model import BusModel

class BusManagementView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.app_controller = app_controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # The table should expand, or just scrollable main

        # Create a main scrollable container for the page
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.grid(row=0, column=0, sticky="nsew", rowspan=2)
        self.scroll_container.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_table()
        
        # Drawer is built but hidden initially
        self._build_drawer()

    def _build_header(self):
        header = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 16))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left, text="Bus Management", font=FONTS["headline_lg"], text_color=COLORS["on_surface"]).pack(anchor="w")
        ctk.CTkLabel(left, text="Manage fleet, monitor status, and assign routes.", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")

        self.search_var = ctk.StringVar(value="")
        self.status_filter_var = ctk.StringVar(value="All Status")

        # Search Box
        search_box = ctk.CTkEntry(
            right, placeholder_text="🔍 Filter buses, drivers...", textvariable=self.search_var,
            font=FONTS["body_md"], fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], width=180, height=36
        )
        search_box.pack(side="left", padx=(0, 8))
        search_box.bind("<KeyRelease>", lambda e: self._populate_grid())

        # Status OptionMenu
        status_menu = ctk.CTkOptionMenu(
            right, values=["All Status", "Active", "Maintenance"], variable=self.status_filter_var,
            font=FONTS["body_md"], fg_color=COLORS["surface_container_lowest"], text_color=COLORS["on_surface"],
            button_color=COLORS["surface_container"], button_hover_color=COLORS["outline_variant"],
            height=36, width=125, command=lambda e: self._populate_grid()
        )
        status_menu.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            right, text="+ Add New Bus", font=FONTS["label_md"], height=36,
            fg_color=COLORS["primary"], text_color=COLORS["on_primary"], hover_color=COLORS["primary_container"],
            command=self.open_drawer
        ).pack(side="left")

    def _build_table(self):
        # Table card with strong, well-defined 2px stroke
        table_card = ctk.CTkFrame(
            self.scroll_container, 
            fg_color=COLORS["surface_container_lowest"], 
            border_color="#64748b", 
            border_width=2, 
            corner_radius=12
        )
        table_card.grid(row=1, column=0, sticky="nsew", padx=32, pady=16)
        table_card.grid_columnconfigure(0, weight=1)

        # Table Header
        thead = ctk.CTkFrame(table_card, fg_color="#dbe8f8", corner_radius=10)
        thead.pack(fill="x", padx=2, pady=(2, 0))
        # Mask bottom corners
        thead_mask = ctk.CTkFrame(thead, fg_color="#dbe8f8", height=8, corner_radius=0)
        thead_mask.pack(side="bottom", fill="x")

        th_row = ctk.CTkFrame(thead, fg_color="transparent")
        th_row.pack(fill="x", padx=16, pady=12)

        self.cols = [
            ("Bus Reg No", 2), ("Type", 1.5), ("Capacity", 1), 
            ("Driver Name", 2), ("Status", 1.3), ("Maintenance", 1.5), ("Actions", 1.2)
        ]
        
        for i, (c, w) in enumerate(self.cols):
            th_row.grid_columnconfigure(i, weight=int(w*10), uniform="col")
            anchor = "w" if i < len(self.cols) - 1 else "e"
            th = ctk.CTkLabel(th_row, text=c, font=("Inter", 12, "bold"), text_color="#0f172a")
            sticky = "w" if anchor == "w" else "e"
            th.grid(row=0, column=i, sticky=sticky, padx=8)

        # Strong dividing stroke under the header
        header_divider = ctk.CTkFrame(table_card, fg_color="#64748b", height=2)
        header_divider.pack(fill="x", padx=2)

        # Table Body Container
        self.grid_container = ctk.CTkFrame(table_card, fg_color="transparent")
        self.grid_container.pack(fill="x")
        self.table_card = table_card

        # Populate Data from DB
        self._populate_grid()

        # Strong dividing stroke above the footer
        border_footer = ctk.CTkFrame(table_card, fg_color="#64748b", height=2)
        border_footer.pack(fill="x", padx=2)
        
        tfoot = ctk.CTkFrame(table_card, fg_color="#f8fafc", corner_radius=10)
        tfoot.pack(fill="x", padx=2, pady=(0, 2))
        tfoot_mask = ctk.CTkFrame(tfoot, fg_color="#f8fafc", height=8, corner_radius=0)
        tfoot_mask.pack(side="top", fill="x")

        tfoot_content = ctk.CTkFrame(tfoot, fg_color="transparent")
        tfoot_content.pack(fill="x", padx=16, pady=(6, 12))

        self.footer_count_lbl = ctk.CTkLabel(tfoot_content, text="Showing entries", font=("Inter", 12), text_color="#475569")
        self.footer_count_lbl.pack(side="left")
        
        pag_wrapper = ctk.CTkFrame(tfoot_content, fg_color="transparent")
        pag_wrapper.pack(side="right")
        
        for p in ["Prev", "1", "2", "3", "Next"]:
            is_active = (p == "1")
            fg = COLORS["primary"] if is_active else "#ffffff"
            tc = "#ffffff" if is_active else "#334155"
            border = 0 if is_active else 1
            ctk.CTkButton(
                pag_wrapper, text=p, width=32, height=28, font=("Inter", 12), 
                fg_color=fg, text_color=tc, border_color="#cbd5e1", border_width=border,
                hover_color=COLORS["surface_container"]
            ).pack(side="left", padx=2)

    def _populate_grid(self):
        # Clear existing rows
        for widget in self.grid_container.winfo_children():
            widget.destroy()
            
        s_term = self.search_var.get().strip() if hasattr(self, "search_var") else None
        st_filter = self.status_filter_var.get() if hasattr(self, "status_filter_var") else None
        buses = BusModel.get_all_buses(search_term=s_term, status_filter=st_filter)
        if hasattr(self, "footer_count_lbl"):
            self.footer_count_lbl.configure(text=f"Showing 1 to {len(buses)} of {len(buses)} entries")
        
        for i, row in enumerate(buses):
            # Alternating clean row background (zebra striping)
            row_bg = "#ffffff" if i % 2 == 0 else "#f8fbfe"
            tr = ctk.CTkFrame(self.grid_container, fg_color=row_bg, corner_radius=0)
            tr.pack(fill="x", padx=2)

            tr_content = ctk.CTkFrame(tr, fg_color="transparent")
            tr_content.pack(fill="x", padx=16, pady=10)
            
            for j, (c, w) in enumerate(self.cols):
                tr_content.grid_columnconfigure(j, weight=int(w*10), uniform="col")

            # Col 1: Bus Reg No
            c1 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c1.grid(row=0, column=0, sticky="ew", padx=8)
            ctk.CTkLabel(c1, text=row["reg"], font=("Inter", 14, "bold"), text_color=COLORS["primary"]).pack(anchor="w")

            # Col 2: Type
            c2 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c2.grid(row=0, column=1, sticky="ew", padx=8)
            ctk.CTkLabel(c2, text=row["type"], font=FONTS["body_md"], text_color="#0f172a").pack(anchor="w")

            # Col 3: Capacity
            c3 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c3.grid(row=0, column=2, sticky="ew", padx=8)
            ctk.CTkLabel(c3, text=f"{row['capacity']} seats", font=("Inter", 12), text_color="#475569").pack(anchor="w")

            # Col 4: Driver Name
            c4 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c4.grid(row=0, column=3, sticky="ew", padx=8)
            ctk.CTkLabel(c4, text=row["driver"] if row["driver"] else "-", font=("Inter", 13), text_color="#0f172a").pack(anchor="w")

            # Col 5: Status Badge
            c5 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c5.grid(row=0, column=4, sticky="ew", padx=8)
            is_active = (row["status"].lower() == "active")
            s_bg = "#dcfce7" if is_active else "#fef3c7"
            s_fg = "#15803d" if is_active else "#b45309"
            s_border = "#86efac" if is_active else "#fde68a"
            s_dot = "#16a34a" if is_active else "#d97706"
            
            s_badge = ctk.CTkFrame(c5, fg_color=s_bg, border_color=s_border, border_width=1, corner_radius=12)
            s_badge.pack(anchor="w")
            ctk.CTkLabel(s_badge, text="●", text_color=s_dot, font=("Arial", 10)).pack(side="left", padx=(8, 4), pady=3)
            ctk.CTkLabel(s_badge, text=row["status"].upper(), text_color=s_fg, font=("Inter", 11, "bold")).pack(side="left", padx=(0, 10), pady=3)

            # Col 6: Last Maintenance
            c6 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c6.grid(row=0, column=5, sticky="ew", padx=8)
            ctk.CTkLabel(c6, text=row["last_maintenance"], font=("Inter", 12), text_color="#475569").pack(anchor="w")

            # Col 7: Actions Buttons (Well-defined micro buttons)
            c7 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c7.grid(row=0, column=6, sticky="ew", padx=8)
            c7_wrapper = ctk.CTkFrame(c7, fg_color="transparent")
            c7_wrapper.pack(anchor="e")

            # View Icon Button
            ctk.CTkButton(
                c7_wrapper, text="👁", width=30, height=30, 
                fg_color="#e0eaf7", hover_color="#cbdff7", 
                text_color="#0058be", corner_radius=6,
                command=lambda b=row: self._open_edit_drawer(b)
            ).pack(side="left", padx=2)

            # Edit Icon Button
            ctk.CTkButton(
                c7_wrapper, text="✎", width=30, height=30, 
                fg_color="#e0f2fe", hover_color="#bae6fd", 
                text_color="#0284c7", corner_radius=6,
                command=lambda b=row: self._open_edit_drawer(b)
            ).pack(side="left", padx=2)

            # Power/Status Toggle Button
            ctk.CTkButton(
                c7_wrapper, text="⏻", width=30, height=30, 
                fg_color="#fee2e2", hover_color="#fca5a5", 
                text_color="#dc2626", corner_radius=6,
                command=lambda reg=row['reg']: self._toggle_status(reg)
            ).pack(side="left", padx=2)

            # Horizontal divider line under every row (except last)
            if i < len(buses) - 1:
                divider = ctk.CTkFrame(self.grid_container, fg_color="#cbd5e1", height=1)
                divider.pack(fill="x", padx=2)

    def _open_edit_drawer(self, bus_data):
        self.drawer_title_label.configure(text=f"Edit Bus: {bus_data['reg']}")
        self.entry_reg.delete(0, 'end')
        self.entry_reg.insert(0, bus_data['reg'])
        self.entry_type.delete(0, 'end')
        self.entry_type.insert(0, bus_data['type'])
        self.entry_cap.delete(0, 'end')
        self.entry_cap.insert(0, bus_data['capacity'])
        self.entry_status.delete(0, 'end')
        self.entry_status.insert(0, bus_data['status'])
        self.entry_driver.delete(0, 'end')
        self.entry_driver.insert(0, bus_data['driver'] if bus_data['driver'] else "")
        self.entry_maint.delete(0, 'end')
        self.entry_maint.insert(0, bus_data['last_maintenance'] if bus_data['last_maintenance'] != '-' else "")
        self.open_drawer()

    def _toggle_status(self, reg):
        BusModel.toggle_bus_status(reg)
        self._populate_grid()

    def _build_drawer(self):
        # The drawer sits exactly on top of the right side.
        # It's a Frame placed with relx=1.0. We toggle it by showing/hiding it.
        self.drawer_overlay = ctk.CTkFrame(self, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=0, width=400)
        # Prevent shrinking
        self.drawer_overlay.pack_propagate(False)

        # Drawer Header
        d_header = ctk.CTkFrame(self.drawer_overlay, fg_color=COLORS["surface_bright"], corner_radius=0, height=64)
        d_header.pack(fill="x")
        d_header.pack_propagate(False)
        
        self.drawer_title_label = ctk.CTkLabel(d_header, text="Add New Bus", font=FONTS["headline_md"], text_color=COLORS["on_surface"])
        self.drawer_title_label.pack(side="left", padx=24, pady=16)
        close_btn = ctk.CTkButton(d_header, text="✕", width=32, height=32, fg_color="transparent", text_color=COLORS["on_surface_variant"], hover_color=COLORS["surface_container"], command=self.close_drawer)
        close_btn.pack(side="right", padx=16, pady=16)

        d_border = ctk.CTkFrame(self.drawer_overlay, fg_color=COLORS["outline_variant"], height=1)
        d_border.pack(fill="x")

        # Drawer Scrollable Form
        d_form = ctk.CTkScrollableFrame(self.drawer_overlay, fg_color="transparent", corner_radius=0)
        d_form.pack(fill="both", expand=True, padx=24, pady=16)

        self.entry_reg = self._add_form_field(d_form, "Registration Number *", "e.g., TN 01 AN 2345")
        self.entry_type = self._add_form_field(d_form, "Bus Type", "AC Semi-Sleeper", is_dropdown=True)
        self.entry_cap = self._add_form_field(d_form, "Capacity (Seats) *", "e.g., 45")
        self.entry_status = self._add_form_field(d_form, "Initial Status", "Active", is_dropdown=True)
        
        ctk.CTkLabel(d_form, text="ASSIGNMENTS & MAINTENANCE", font=("Inter", 11, "bold"), text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(24, 8))
        self.entry_driver = self._add_form_field(d_form, "Driver Name", "e.g., Rajesh Kumar")
        self.entry_maint = self._add_form_field(d_form, "Last Maintenance (YYYY-MM-DD)", "2024-01-15")

        # Drawer Footer
        d_footer_border = ctk.CTkFrame(self.drawer_overlay, fg_color=COLORS["outline_variant"], height=1)
        d_footer_border.pack(fill="x")
        
        d_footer = ctk.CTkFrame(self.drawer_overlay, fg_color=COLORS["surface_bright"], corner_radius=0, height=72)
        d_footer.pack(fill="x")
        d_footer.pack_propagate(False)

        btn_wrapper = ctk.CTkFrame(d_footer, fg_color="transparent")
        btn_wrapper.pack(side="right", padx=24, pady=16)

        ctk.CTkButton(btn_wrapper, text="Cancel", font=FONTS["label_md"], fg_color="transparent", text_color=COLORS["on_surface"], border_color=COLORS["outline_variant"], border_width=1, hover_color=COLORS["surface_container"], command=self.close_drawer).pack(side="left", padx=8)
        ctk.CTkButton(btn_wrapper, text="Save Bus Record", font=FONTS["label_md"], fg_color=COLORS["primary"], text_color=COLORS["on_primary"], hover_color=COLORS["primary_container"], command=self._save_bus).pack(side="left")

    def _add_form_field(self, parent, label_text, placeholder, is_dropdown=False, disabled=False):
        wrapper = ctk.CTkFrame(parent, fg_color="transparent")
        wrapper.pack(fill="x", pady=8)
        ctk.CTkLabel(wrapper, text=label_text, font=FONTS["label_md"], text_color=COLORS["on_surface"]).pack(anchor="w", pady=(0, 4))
        
        bg = COLORS["surface_variant"] if disabled else COLORS["surface_container_lowest"]
        tc = COLORS["on_surface_variant"] if disabled else COLORS["on_surface"]
        
        entry = ctk.CTkEntry(wrapper, font=FONTS["body_md"], fg_color=bg, text_color=tc, border_color=COLORS["outline_variant"], placeholder_text=placeholder, height=36)
        entry.pack(fill="x")
        if disabled:
            entry.insert(0, placeholder)
            entry.configure(state="disabled")
        elif is_dropdown:
            entry.insert(0, placeholder)
            
        return entry

    def _save_bus(self):
        reg = self.entry_reg.get().strip()
        b_type = self.entry_type.get().strip()
        cap_str = self.entry_cap.get().strip()
        cap = int(cap_str) if cap_str.isdigit() else 45
        status = self.entry_status.get().strip()
        driver = self.entry_driver.get().strip()
        maint = self.entry_maint.get().strip()
        
        if not maint:
            maint = None
            
        if reg:
            try:
                BusModel.add_bus(reg, b_type, cap, status, driver, maint)
                # Refresh table
                self._populate_grid()
                
                # Reset fields
                self.entry_reg.delete(0, 'end')
                self.entry_cap.delete(0, 'end')
                self.entry_driver.delete(0, 'end')
                self.entry_maint.delete(0, 'end')
                
                self.close_drawer()
            except Exception as e:
                print(f"Error saving bus: {e}")

    def open_drawer(self):
        # Slide in or place on top right
        self.drawer_overlay.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")

    def close_drawer(self):
        self.drawer_overlay.place_forget()
