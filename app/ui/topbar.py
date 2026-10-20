import customtkinter as ctk
from app.constants import COLORS, FONTS

class Topbar(ctk.CTkFrame):
    def __init__(self, master, app_controller=None, **kwargs):
        super().__init__(master, fg_color=COLORS["surface_container_lowest"], height=64, corner_radius=0, **kwargs)
        self.app_controller = app_controller
        
        self.pack_propagate(False)
        self.grid_propagate(False)

        # Content container to center things vertically
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=24)

        # Left side - Search
        self.search_entry = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="Search buses, routes...",
            width=450,
            height=36,
            fg_color=COLORS["surface_container_low"],
            border_color=COLORS["outline_variant"],
            border_width=1,
            text_color=COLORS["on_surface"],
            font=FONTS["body_md"],
            corner_radius=18
        )
        self.search_entry.pack(side="left", pady=14, padx=24)

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

        self.notif_btn = ctk.CTkButton(
            self.right_frame,
            text="🔔", 
            width=36,
            height=36,
            fg_color="transparent",
            text_color=COLORS["outline"],
            hover_color=COLORS["surface_container_low"],
            corner_radius=18,
            font=("Segoe UI Emoji", 20),
            command=lambda: self.app_controller.show_view("AlertsNotifications") if self.app_controller else None
        )
        self.notif_btn.pack(side="left", padx=12)

        # Profile area
        self.profile_frame = ctk.CTkFrame(
            self.right_frame, 
            fg_color="transparent", 
            border_color=COLORS["outline_variant"],
            border_width=0
        )
        self.profile_frame.pack(side="left")
        
        # Add a subtle left border to profile frame to mimic Tailwind's border-l
        self.divider = ctk.CTkFrame(self.right_frame, width=1, height=32, fg_color=COLORS["outline_variant"])
        self.divider.pack(side="left", padx=8)

        self.avatar = ctk.CTkLabel(
            self.profile_frame,
            text="A", # Avatar placeholder
            width=32,
            height=32,
            fg_color=COLORS["primary"],
            text_color=COLORS["on_primary"],
            corner_radius=16,
            font=FONTS["label_md"]
        )
        self.avatar.pack(side="left", padx=(8, 8))

        self.admin_label = ctk.CTkLabel(
            self.profile_frame,
            text="Admin",
            font=FONTS["label_md"],
            text_color=COLORS["on_surface"]
        )
        self.admin_label.pack(side="left")
