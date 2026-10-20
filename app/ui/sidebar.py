import customtkinter as ctk
from app.constants import COLORS, FONTS

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS["surface_bright"], width=280, corner_radius=0, **kwargs)
        
        # Prevent the frame from shrinking to fit its contents
        self.pack_propagate(False)
        self.grid_propagate(False)

        # App Logo / Title
        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.pack(fill="x", padx=16, pady=(16, 24))
        
        self.title_label = ctk.CTkLabel(
            self.title_frame, 
            text="Smart Bus Stand", 
            font=FONTS["headline_md"],
            text_color=COLORS["primary"]
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = ctk.CTkLabel(
            self.title_frame, 
            text="Management Portal", 
            font=FONTS["label_md"],
            text_color=COLORS["on_surface_variant"]
        )
        self.subtitle_label.pack(anchor="w")

        # Scrollable container for nav items
        self.nav_container = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.nav_container.pack(fill="both", expand=True, padx=8)

        # Navigation Items
        nav_items = [
            "Dashboard",
            "Live Monitoring",
            "Bus Management",
            "Route Management",
            "Schedule & Timings",
            "Parking Bay Management",
            "ANPR Records",
            "Alerts & Notifications",
            "Reports & Analytics",
            "System Health",
            "Activity Logs",
            "Backup & Restore",
            "Settings"
        ]

        self.nav_buttons = []
        for i, item in enumerate(nav_items):
            is_active = (i == 0) # Make Dashboard active initially
            
            if item == "Dashboard":
                cmd = lambda name="Dashboard": self.on_nav_click(name)
            elif item == "Live Monitoring":
                cmd = lambda name="Live Monitoring": self.on_nav_click(name)
            elif item == "Bus Management":
                cmd = lambda name="Bus Management": self.on_nav_click(name)
            elif item == "Route Management":
                cmd = lambda name="Route Management": self.on_nav_click(name)
            elif item == "Schedule & Timings":
                cmd = lambda name="Schedule & Timings": self.on_nav_click(name)
            elif item == "Parking Bay Management":
                cmd = lambda name="Parking Bay Management": self.on_nav_click(name)
            elif item == "ANPR Records":
                cmd = lambda name="ANPR Records": self.on_nav_click(name)
            elif item == "Alerts & Notifications":
                cmd = lambda name="Alerts & Notifications": self.on_nav_click(name)
            elif item == "Reports & Analytics":
                cmd = lambda name="Reports & Analytics": self.on_nav_click(name)
            elif item == "System Health":
                cmd = lambda name="System Health": self.on_nav_click(name)
            elif item == "Activity Logs":
                cmd = lambda name="Activity Logs": self.on_nav_click(name)
            elif item == "Backup & Restore":
                cmd = lambda name="Backup & Restore": self.on_nav_click(name)
            elif item == "Settings":
                cmd = lambda name="Settings": self.on_nav_click(name)
            else:
                cmd = None
            
            btn = ctk.CTkButton(
                self.nav_container,
                text=item,
                font=FONTS["body_md"],
                fg_color=COLORS["secondary_container"] if is_active else "transparent",
                text_color=COLORS["primary"] if is_active else COLORS["on_surface_variant"],
                hover_color=COLORS["secondary_container"],
                anchor="w",
                height=40,
                corner_radius=8,
                command=cmd
            )
            btn.pack(fill="x", pady=2, padx=4)
            self.nav_buttons.append(btn)



    def on_nav_click(self, item_name):
        for btn in self.nav_buttons:
            is_active = (btn.cget("text") == item_name)
            btn.configure(
                fg_color=COLORS["secondary_container"] if is_active else "transparent",
                text_color=COLORS["primary"] if is_active else COLORS["on_surface_variant"]
            )
            
        if item_name == "Dashboard":
            self.master.show_view("Dashboard")
        elif item_name == "Live Monitoring":
            self.master.show_view("LiveMonitoring1")
        elif item_name == "Bus Management":
            self.master.show_view("BusManagement")
        elif item_name == "Route Management":
            self.master.show_view("RouteManagement")
        elif item_name == "Schedule & Timings":
            self.master.show_view("ScheduleAndTimings")
        elif item_name == "Parking Bay Management":
            self.master.show_view("ParkingBayManagement")
        elif item_name == "ANPR Records":
            self.master.show_view("ANPRRecords")
        elif item_name == "Alerts & Notifications":
            self.master.show_view("AlertsNotifications")
        elif item_name == "Reports & Analytics":
            self.master.show_view("ReportsAnalytics")
        elif item_name == "System Health":
            self.master.show_view("SystemHealth")
        elif item_name == "Activity Logs":
            self.master.show_view("ActivityLogs")
        elif item_name == "Backup & Restore":
            self.master.show_view("BackupAndRestore")
        elif item_name == "Settings":
            self.master.show_view("Settings")
