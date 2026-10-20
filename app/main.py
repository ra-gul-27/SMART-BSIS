import customtkinter as ctk
import os
import sys

# Add the root project directory to Python Path so 'app' module can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.constants import COLORS
from app.db.database import init_db
from app.db.create_db import ensure_database_exists
from app.ui.sidebar import Sidebar
from app.ui.topbar import Topbar
from app.ui.views.dashboard_view import DashboardView

class SmartBusStandApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Ensure Database exists and then Initialize Tables
        ensure_database_exists()
        init_db()

        self.title("Smart Bus Stand - Management Portal")
        self.geometry("1440x900")
        
        # Configure grid for the main window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Apply Global Background
        self.configure(fg_color=COLORS["background"])

        # 1. Sidebar (Left Column)
        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # 2. Main Content Area (Right Column)
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)

        # 3. Topbar (Top row of Main Content)
        self.topbar = Topbar(self.main_container, self)
        self.topbar.grid(row=0, column=0, sticky="ew")

        # Views Dictionary
        self.views = {}
        self.current_view_name = "Dashboard"

        # Keyboard shortcuts for instant refresh during development
        self.bind("<Control-r>", lambda e: self.reload_current_view())
        self.bind("<Control-R>", lambda e: self.reload_current_view())
        self.bind("<F5>", lambda e: self.reload_current_view())

        # 4. Content View (Dashboard initially)
        self.show_view("Dashboard")

    def reload_current_view(self):
        view = getattr(self, "current_view_name", "Dashboard")
        self.show_view(view)

    def show_view(self, view_name):
        self.current_view_name = view_name
        if hasattr(self, "current_view") and self.current_view is not None:
            self.current_view.destroy()
            
        if view_name == "Dashboard":
            from app.ui.views.dashboard_view import DashboardView
            self.current_view = DashboardView(self.main_container, self)
        elif view_name == "LiveMonitoring1":
            from app.ui.views.live_monitoring_1_view import LiveMonitoring1View
            self.current_view = LiveMonitoring1View(self.main_container, self)
        elif view_name == "LiveMonitoring2":
            from app.ui.views.live_monitoring_2_view import LiveMonitoring2View
            self.current_view = LiveMonitoring2View(self.main_container, self)
        elif view_name == "BusManagement":
            from app.ui.views.bus_management_view import BusManagementView
            self.current_view = BusManagementView(self.main_container, self)
        elif view_name == "RouteManagement":
            from app.ui.views.route_management_view import RouteManagementView
            self.current_view = RouteManagementView(self.main_container, self)
        elif view_name == "ScheduleAndTimings":
            from app.ui.views.schedule_and_timings_view import ScheduleAndTimingsView
            self.current_view = ScheduleAndTimingsView(self.main_container, self)
        elif view_name == "ParkingBayManagement":
            from app.ui.views.parking_bay_management_view import ParkingBayManagementView
            self.current_view = ParkingBayManagementView(self.main_container, self)
        elif view_name == "ANPRRecords":
            from app.ui.views.anpr_records_view import ANPRRecordsView
            self.current_view = ANPRRecordsView(self.main_container, self)
        elif view_name == "AlertsNotifications":
            from app.ui.views.alerts_notifications_view import AlertsNotificationsView
            self.current_view = AlertsNotificationsView(self.main_container, self)
        elif view_name == "ReportsAnalytics":
            from app.ui.views.reports_analytics_view import ReportsAnalyticsView
            self.current_view = ReportsAnalyticsView(self.main_container, self)
        elif view_name == "SystemHealth":
            from app.ui.views.system_health_view import SystemHealthView
            self.current_view = SystemHealthView(self.main_container, self)
        elif view_name == "ActivityLogs":
            from app.ui.views.activity_logs_view import ActivityLogsView
            self.current_view = ActivityLogsView(self.main_container, self)
        elif view_name == "BackupAndRestore":
            from app.ui.views.backup_and_restore_view import BackupAndRestoreView
            self.current_view = BackupAndRestoreView(self.main_container, self)
        elif view_name == "Settings":
            from app.ui.views.settings_view import SettingsView
            self.current_view = SettingsView(self.main_container, self)
            
        self.current_view.grid(row=1, column=0, sticky="nsew")

if __name__ == "__main__":
    # Ensure customtkinter uses light mode since the Tailwind design is light mode
    ctk.set_appearance_mode("light")
    
    app = SmartBusStandApp()
    app.mainloop()
