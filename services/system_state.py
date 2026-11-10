class SystemState:

    def __init__(self):

        # ==========================
        # Camera
        # ==========================
        self.camera_online = False

        # ==========================
        # Motion
        # ==========================
        self.motion_detected = False

        # ==========================
        # Countdown
        # ==========================
        self.countdown_running = False
        self.countdown_seconds = 5

        # ==========================
        # QR Scanner
        # ==========================
        self.scanner_enabled = False

        # ==========================
        # Siren
        # ==========================
        self.siren_on = False

        # ==========================
        # Scheduled System State
        # ==========================
        self.break_mode = False

        # True = system is currently
        # within its operating schedule
        self.system_active = True

        # ==========================
        # Last Scan
        # ==========================
        self.last_student = None

        # ==========================
        # Processing
        # ==========================
        self.processing = False

        # ==========================
        # Statistics
        # ==========================
        self.total_entries = 0
        self.total_exits = 0
        self.students_inside = 0

        # ==========================
        # Detection Zone
        # ==========================
        self.zone_x1 = 620
        self.zone_y1 = 140

        self.zone_x2 = 930
        self.zone_y2 = 610


system_state = SystemState()