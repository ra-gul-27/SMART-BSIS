import customtkinter as ctk
from app.constants import COLORS, FONTS
from app.db.database import get_connection

class Topbar(ctk.CTkFrame):
    def __init__(self, master, app_controller=None, **kwargs):
        super().__init__(master, fg_color=COLORS["surface_container_lowest"], height=64, corner_radius=0, **kwargs)
        self.app_controller = app_controller
        
        self.pack_propagate(False)
        self.grid_propagate(False)

        # Content container
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=24)

        # Left side - Global Search
        self.search_entry = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="🔍 Search buses, routes, bays or license plates...",
            width=460,
            height=36,
            fg_color=COLORS["surface_container_low"],
            border_color=COLORS["outline_variant"],
            border_width=1,
            text_color=COLORS["on_surface"],
            font=FONTS["body_md"],
            corner_radius=18
        )
        self.search_entry.pack(side="left", pady=14, padx=12)
        self.search_entry.bind("<KeyRelease>", self._on_global_search)

        # Right side - Profile & Notifications
        self.right_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.right_frame.pack(side="right", pady=14)

        # Refresh / Reload button
        self.reload_btn = ctk.CTkButton(
            self.right_frame,
            text="🔄", 
            width=36,
            height=36,
            fg_color="transparent",
            text_color=COLORS["outline"],
            hover_color=COLORS["surface_container_low"],
            corner_radius=18,
            font=("Segoe UI Emoji", 16),
            command=lambda: self.app_controller.reload_current_view() if self.app_controller else None
        )
        self.reload_btn.pack(side="left", padx=(0, 4))

        # Notification bell with alert badge
        notif_box = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        notif_box.pack(side="left", padx=8)

        self.notif_btn = ctk.CTkButton(
            notif_box,
            text="🔔", 
            width=36,
            height=36,
            fg_color="transparent",
            text_color=COLORS["outline"],
            hover_color=COLORS["surface_container_low"],
            corner_radius=18,
            font=("Segoe UI Emoji", 18),
            command=lambda: self.app_controller.show_view("AlertsNotifications") if self.app_controller else None
        )
        self.notif_btn.pack(side="left")

        # Query active alerts count
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM events WHERE event_type IN ('error', 'warning')")
            alert_count = cur.fetchone()[0]
            conn.close()
        except Exception:
            alert_count = 0

        if alert_count > 0:
            badge = ctk.CTkFrame(notif_box, fg_color=COLORS["error"], corner_radius=8, width=18, height=18)
            badge.place(relx=0.75, rely=0.1, anchor="center")
            badge.pack_propagate(False)
            ctk.CTkLabel(badge, text=str(alert_count), font=("Inter", 9, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        # Profile area
        self.profile_frame = ctk.CTkFrame(
            self.right_frame, 
            fg_color="transparent", 
            border_color=COLORS["outline_variant"],
            border_width=0
        )
        self.profile_frame.pack(side="left")
        
        self.divider = ctk.CTkFrame(self.right_frame, width=1, height=32, fg_color=COLORS["outline_variant"])
        self.divider.pack(side="left", padx=8)

        self.avatar = ctk.CTkLabel(
            self.profile_frame,
            text="ADM",
            width=34,
            height=34,
            fg_color=COLORS["primary"],
            text_color=COLORS["on_primary"],
            corner_radius=17,
            font=("Inter", 10, "bold")
        )
        self.avatar.pack(side="left", padx=(8, 8))

        self.admin_label = ctk.CTkLabel(
            self.profile_frame,
            text="Super Admin",
            font=FONTS["label_md"],
            text_color=COLORS["on_surface"]
        )
        self.admin_label.pack(side="left")

    def _on_global_search(self, event):
        query = self.search_entry.get().strip()
        if not self.app_controller or not hasattr(self.app_controller, "current_view"):
            return
        cv = self.app_controller.current_view
        # Forward search to active view if supported
        if hasattr(cv, "search_var"):
            cv.search_var.set(query)
            if hasattr(cv, "_populate_grid"):
                cv._populate_grid()
        elif hasattr(cv, "route_filter_var"):
            cv.route_filter_var.set(query)
            if hasattr(cv, "_populate_grid"):
                cv._populate_grid()
