"""
Booking View - Flight booking interface.
Handles airport selection, date picking, and passenger information entry.
"""
from datetime import datetime, date, time
from typing import Optional
import customtkinter as ctk
from tkcalendar import DateEntry

from gui.theme import COLORS, FONTS, RADIUS, SPACING
from gui.components.airport_selector import AirportSelector
from gui.components.camera_widget import CameraWidget
from database.db_manager import db
from services.face_service import face_service
from services.airport_service import airport_service
from services.sound_service import sound_service
from services.audit_service import audit_service


class BookingView(ctk.CTkFrame):
    """
    Flight booking view - multi-step booking process.
    Step 1: Select source and destination airports, date
    Step 2: Enter passenger details and capture face
    Step 3: Confirmation
    """
    
    def __init__(self, parent, on_booking_complete=None, **kwargs):
        super().__init__(parent, fg_color=COLORS['bg_primary'], **kwargs)
        
        self.on_booking_complete = on_booking_complete
        self.current_step = 1
        self.booking_data = {
            'source': None,
            'destination': None,
            'date': None,
            'time': None,
            'first_name': '',
            'last_name': '',
            'passport': '',
            'face_encoding': None,
        }
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the booking interface."""
        # Main container with scroll
        self.main_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        self.main_scroll.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['lg'])
        
        # Header
        header = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, SPACING['xl']))
        
        ctk.CTkLabel(
            header,
            text="✈ Book Your Flight",
            font=FONTS['heading'],
            text_color=COLORS['text_primary']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header,
            text="Search and book your next journey",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(SPACING['xs'], 0))
        
        # Steps indicator
        self._create_steps_indicator()
        
        # Content area (changes based on step)
        self.content_frame = ctk.CTkFrame(
            self.main_scroll,
            fg_color=COLORS['bg_secondary'],
            corner_radius=RADIUS['xl']
        )
        self.content_frame.pack(fill="both", expand=True, pady=SPACING['lg'])
        
        # Load step 1
        self._show_step_1()
    
    def _create_steps_indicator(self):
        """Create the step progress indicator."""
        steps_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        steps_frame.pack(fill="x", pady=SPACING['md'])
        
        self.step_indicators = []
        steps = ["Flight Details", "Passenger Info", "Confirmation"]
        
        for i, step_name in enumerate(steps, 1):
            step_container = ctk.CTkFrame(steps_frame, fg_color="transparent")
            step_container.pack(side="left", expand=True)
            
            # Circle
            is_active = i <= self.current_step
            color = COLORS['accent'] if is_active else COLORS['bg_card']
            text_color = COLORS['bg_primary'] if is_active else COLORS['text_muted']
            
            circle = ctk.CTkLabel(
                step_container,
                text=str(i),
                width=36,
                height=36,
                fg_color=color,
                corner_radius=18,
                font=FONTS['button'],
                text_color=text_color
            )
            circle.pack()
            
            # Label
            label = ctk.CTkLabel(
                step_container,
                text=step_name,
                font=FONTS['body_small'],
                text_color=COLORS['text_primary'] if is_active else COLORS['text_muted']
            )
            label.pack(pady=(SPACING['xs'], 0))
            
            self.step_indicators.append((circle, label))
    
    def _update_steps_indicator(self):
        """Update step indicators based on current step."""
        for i, (circle, label) in enumerate(self.step_indicators, 1):
            is_active = i <= self.current_step
            color = COLORS['accent'] if is_active else COLORS['bg_card']
            text_color = COLORS['bg_primary'] if is_active else COLORS['text_muted']
            
            circle.configure(fg_color=color, text_color=text_color)
            label.configure(text_color=COLORS['text_primary'] if is_active else COLORS['text_muted'])
    
    def _clear_content(self):
        """Clear the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def _show_step_1(self):
        """Show step 1: Flight details."""
        self._clear_content()
        self.current_step = 1
        self._update_steps_indicator()
        
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['xl'])
        
        # Source airport
        self.source_selector = AirportSelector(
            container,
            label="From (Departure Airport)",
            placeholder="Search origin city or airport...",
            on_select=lambda a: self._update_booking('source', a)
        )
        self.source_selector.pack(fill="x", pady=(0, SPACING['lg']))
        
        # Destination airport
        self.dest_selector = AirportSelector(
            container,
            label="To (Arrival Airport)",
            placeholder="Search destination city or airport...",
            on_select=lambda a: self._update_booking('destination', a)
        )
        self.dest_selector.pack(fill="x", pady=(0, SPACING['lg']))
        
        # Date and time row
        datetime_frame = ctk.CTkFrame(container, fg_color="transparent")
        datetime_frame.pack(fill="x", pady=(0, SPACING['lg']))
        
        # Date picker
        date_container = ctk.CTkFrame(datetime_frame, fg_color="transparent")
        date_container.pack(side="left", fill="x", expand=True, padx=(0, SPACING['md']))
        
        ctk.CTkLabel(
            date_container,
            text="Flight Date",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.date_entry = DateEntry(
            date_container,
            width=20,
            background=COLORS['accent'],
            foreground='white',
            borderwidth=0,
            font=('Segoe UI', 12),
            mindate=date.today(),
            date_pattern='yyyy-mm-dd'
        )
        self.date_entry.pack(fill="x")
        
        # Time picker
        time_container = ctk.CTkFrame(datetime_frame, fg_color="transparent")
        time_container.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            time_container,
            text="Departure Time",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.time_var = ctk.StringVar(value="08:00")
        time_options = [f"{h:02d}:00" for h in range(6, 24)]
        
        self.time_dropdown = ctk.CTkOptionMenu(
            time_container,
            values=time_options,
            variable=self.time_var,
            fg_color=COLORS['bg_input'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['accent_hover'],
            height=40
        )
        self.time_dropdown.pack(fill="x")
        
        # Error message label
        self.error_label = ctk.CTkLabel(
            container,
            text="",
            font=FONTS['body_small'],
            text_color=COLORS['error']
        )
        self.error_label.pack(pady=SPACING['sm'])
        
        # Next button
        ctk.CTkButton(
            container,
            text="Continue to Passenger Details →",
            font=FONTS['button'],
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_hover'],
            height=50,
            corner_radius=RADIUS['md'],
            command=self._validate_step_1
        ).pack(fill="x", pady=(SPACING['lg'], 0))
    
    def _show_step_2(self):
        """Show step 2: Passenger details and face capture."""
        self._clear_content()
        self.current_step = 2
        self._update_steps_indicator()
        
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['xl'])
        
        # Two column layout
        left_col = ctk.CTkFrame(container, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, SPACING['md']))
        
        right_col = ctk.CTkFrame(container, fg_color="transparent")
        right_col.pack(side="right", fill="both", expand=True, padx=(SPACING['md'], 0))
        
        # Left column: Passenger form
        ctk.CTkLabel(
            left_col,
            text="Passenger Details",
            font=FONTS['subheading'],
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(0, SPACING['md']))
        
        # First name
        ctk.CTkLabel(
            left_col,
            text="First Name",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.first_name_entry = ctk.CTkEntry(
            left_col,
            placeholder_text="Enter first name",
            font=FONTS['body'],
            height=45,
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border']
        )
        self.first_name_entry.pack(fill="x", pady=(0, SPACING['md']))
        
        # Last name
        ctk.CTkLabel(
            left_col,
            text="Last Name",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.last_name_entry = ctk.CTkEntry(
            left_col,
            placeholder_text="Enter last name",
            font=FONTS['body'],
            height=45,
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border']
        )
        self.last_name_entry.pack(fill="x", pady=(0, SPACING['md']))
        
        # Passport number
        ctk.CTkLabel(
            left_col,
            text="Passport Number",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0, SPACING['xs']))
        
        self.passport_entry = ctk.CTkEntry(
            left_col,
            placeholder_text="Enter passport number",
            font=FONTS['body'],
            height=45,
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border']
        )
        self.passport_entry.pack(fill="x", pady=(0, SPACING['md']))
        
        # Error label
        self.step2_error = ctk.CTkLabel(
            left_col,
            text="",
            font=FONTS['body_small'],
            text_color=COLORS['error']
        )
        self.step2_error.pack(pady=SPACING['xs'])
        
        # Right column: Face capture
        ctk.CTkLabel(
            right_col,
            text="Face Capture",
            font=FONTS['subheading'],
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(0, SPACING['sm']))
        
        ctk.CTkLabel(
            right_col,
            text="Click the button below to start face capture",
            font=FONTS['body_small'],
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0, SPACING['md']))
        
        # Camera widget (not started yet)
        self.camera = CameraWidget(
            right_col,
            width=400,
            height=300,
            auto_capture=True,
            auto_capture_delay=45,
            on_face_captured=self._on_face_captured
        )
        self.camera.pack()
        
        # Capture status
        self.capture_status = ctk.CTkLabel(
            right_col,
            text="● Camera not started",
            font=FONTS['body'],
            text_color=COLORS['text_muted']
        )
        self.capture_status.pack(pady=SPACING['sm'])
        
        # Start Capturing button
        self.start_capture_btn = ctk.CTkButton(
            right_col,
            text="📷 Start Capturing",
            font=FONTS['button'],
            fg_color=COLORS['success'],
            hover_color="#00aa44",
            height=45,
            width=200,
            command=self._start_face_capture
        )
        self.start_capture_btn.pack(pady=SPACING['sm'])
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(container, fg_color="transparent")
        nav_frame.pack(fill="x", pady=(SPACING['xl'], 0))
        
        ctk.CTkButton(
            nav_frame,
            text="← Back",
            font=FONTS['button'],
            fg_color="transparent",
            hover_color=COLORS['bg_hover'],
            border_width=1,
            border_color=COLORS['border'],
            text_color=COLORS['text_primary'],
            height=45,
            width=120,
            command=self._show_step_1
        ).pack(side="left")
        
        ctk.CTkButton(
            nav_frame,
            text="Complete Booking →",
            font=FONTS['button'],
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_hover'],
            height=45,
            command=self._validate_step_2
        ).pack(side="right")
    
    def _show_step_3(self, ticket):
        """Show step 3: Confirmation."""
        self._clear_content()
        self.current_step = 3
        self._update_steps_indicator()
        
        # Note: Camera is already stopped in _validate_step_2() before this is called
        
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=SPACING['xl'], pady=SPACING['xl'])
        
        # Success icon
        ctk.CTkLabel(
            container,
            text="✓",
            font=("Segoe UI", 64),
            text_color=COLORS['success']
        ).pack(pady=SPACING['lg'])
        
        ctk.CTkLabel(
            container,
            text="Booking Confirmed!",
            font=FONTS['heading'],
            text_color=COLORS['text_primary']
        ).pack()
        
        # Ticket number
        ctk.CTkLabel(
            container,
            text=f"Ticket Number: {ticket.ticket_number}",
            font=FONTS['subheading'],
            text_color=COLORS['accent']
        ).pack(pady=SPACING['md'])
        
        # Flight details summary
        details = ctk.CTkFrame(container, fg_color=COLORS['bg_card'], corner_radius=RADIUS['lg'])
        details.pack(fill="x", pady=SPACING['lg'], padx=SPACING['xxl'])
        
        details_content = ctk.CTkFrame(details, fg_color="transparent")
        details_content.pack(padx=SPACING['xl'], pady=SPACING['lg'])
        
        # Route
        route_text = f"{ticket.source_airport} → {ticket.destination_airport}"
        ctk.CTkLabel(
            details_content,
            text=route_text,
            font=("Segoe UI", 28, "bold"),
            text_color=COLORS['text_primary']
        ).pack()
        
        # Date and time
        flight_dt = f"{ticket.flight_date} at {ticket.flight_time.strftime('%H:%M')}"
        ctk.CTkLabel(
            details_content,
            text=flight_dt,
            font=FONTS['body_large'],
            text_color=COLORS['text_secondary']
        ).pack(pady=SPACING['sm'])
        
        # Passenger
        ctk.CTkLabel(
            details_content,
            text=f"Passenger: {self.booking_data['first_name']} {self.booking_data['last_name']}",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        ).pack()
        
        # Instructions
        ctk.CTkLabel(
            container,
            text="Please proceed to the Check-In kiosk for boarding pass",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        ).pack(pady=SPACING['xl'])
        
        # New booking button
        ctk.CTkButton(
            container,
            text="Book Another Flight",
            font=FONTS['button'],
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_hover'],
            height=50,
            width=250,
            corner_radius=RADIUS['md'],
            command=self._reset_booking
        ).pack()
    
    def _update_booking(self, key, value):
        """Update booking data."""
        self.booking_data[key] = value
    
    def _validate_step_1(self):
        """Validate step 1 and proceed."""
        self.error_label.configure(text="")
        
        if not self.booking_data['source']:
            self.error_label.configure(text="Please select a departure airport")
            return
        
        if not self.booking_data['destination']:
            self.error_label.configure(text="Please select a destination airport")
            return
        
        if self.booking_data['source']['iata'] == self.booking_data['destination']['iata']:
            self.error_label.configure(text="Source and destination cannot be the same")
            return
        
        # Store date and time
        self.booking_data['date'] = self.date_entry.get_date()
        time_str = self.time_var.get()
        hour = int(time_str.split(':')[0])
        self.booking_data['time'] = time(hour, 0)
        
        self._show_step_2()
    
    def _validate_step_2(self):
        """Validate step 2 and complete booking."""
        self.step2_error.configure(text="")
        
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        passport = self.passport_entry.get().strip()
        
        if not first_name:
            self.step2_error.configure(text="Please enter first name")
            return
        
        if not last_name:
            self.step2_error.configure(text="Please enter last name")
            return
        
        if not passport:
            self.step2_error.configure(text="Please enter passport number")
            return
        
        if len(passport) < 5:
            self.step2_error.configure(text="Invalid passport number")
            return
        
        if self.booking_data['face_encoding'] is None:
            self.step2_error.configure(text="Please capture your face")
            return
        
        # Store passenger details
        self.booking_data['first_name'] = first_name
        self.booking_data['last_name'] = last_name
        self.booking_data['passport'] = passport
        
        # Stop camera
        self.camera.stop()
        
        # Create booking
        try:
            ticket = self._create_booking()
            self._show_step_3(ticket)
            
            if self.on_booking_complete:
                self.on_booking_complete(ticket)
                
        except Exception as e:
            self.step2_error.configure(text=f"Booking failed: {str(e)}")
    
    def _start_face_capture(self):
        """Start the face capture process when button is clicked."""
        # Disable the button
        self.start_capture_btn.configure(state="disabled", text="📷 Capturing...")
        
        # Update status
        self.capture_status.configure(
            text="● Looking for face...",
            text_color=COLORS['warning']
        )
        
        # Start camera
        self.camera.start()
    
    def _on_face_captured(self, frame):
        """Handle face capture from camera."""
        # Get face encoding
        encoding = face_service.get_face_encoding(frame)
        
        if encoding is not None:
            self.booking_data['face_encoding'] = encoding
            sound_service.play_shutter()  # Camera shutter sound
            self.capture_status.configure(
                text="✓ Face captured successfully!",
                text_color=COLORS['success']
            )
        else:
            sound_service.play_error()
            self.capture_status.configure(
                text="× Failed to capture face, please try again",
                text_color=COLORS['error']
            )
    
    def _create_booking(self):
        """Create the actual booking in database."""
        # Check if passenger exists
        passenger = db.get_passenger_by_passport(self.booking_data['passport'])
        
        if not passenger:
            # Create new passenger
            passenger = db.create_passenger(
                first_name=self.booking_data['first_name'],
                last_name=self.booking_data['last_name'],
                passport_number=self.booking_data['passport']
            )
        
        # Save face encoding
        if self.booking_data['face_encoding'] is not None:
            face_file = face_service.save_face_encoding(
                self.booking_data['face_encoding'],
                passenger.id
            )
            db.update_passenger_face(passenger.id, face_file)
        
        # Create ticket
        source = self.booking_data['source']
        dest = self.booking_data['destination']
        
        ticket = db.create_ticket(
            passenger_id=passenger.id,
            source_airport=source['iata'],
            source_airport_name=source['name'],
            destination_airport=dest['iata'],
            destination_airport_name=dest['name'],
            flight_date=self.booking_data['date'],
            flight_time=self.booking_data['time']
        )
        
        # Log booking and play success sound
        audit_service.log_booking(
            ticket.ticket_number,
            passenger.full_name,
            f"{source['iata']}->{dest['iata']}"
        )
        sound_service.play_success()
        
        return ticket
    
    def _reset_booking(self):
        """Reset for new booking."""
        self.booking_data = {
            'source': None,
            'destination': None,
            'date': None,
            'time': None,
            'first_name': '',
            'last_name': '',
            'passport': '',
            'face_encoding': None,
        }
        self._show_step_1()
    
    def on_hide(self):
        """Called when view is hidden."""
        if hasattr(self, 'camera'):
            self.camera.stop()
