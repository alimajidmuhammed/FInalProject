"""
Check-In View - Face recognition and QR code based check-in.
Automatically recognizes faces or scans QR codes and generates boarding passes.
"""
from typing import Optional, Dict
import customtkinter as ctk
import logging

from gui.theme import COLORS, FONTS, RADIUS, SPACING
from gui.components.camera_widget import CameraWidget
from database.db_manager import db
from database.models import TicketStatus
from services.face_service import face_service
from services.voice_service import voice_service
from services.boarding_pass_service import boarding_pass_service
from services.esp_service import esp_service
from services.sound_service import sound_service
from services.audit_service import audit_service
from services.qr_service import qr_service

logger = logging.getLogger(__name__)


class CheckInView(ctk.CTkFrame):
    """
    Check-in view with face recognition.
    Detects faces, matches against booked passengers, generates boarding pass.
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS['bg_primary'], **kwargs)
        
        self.known_encodings: Dict = {}
        self.passenger_lookup: Dict = {}  # passenger_id -> passenger
        self.last_recognized_id: Optional[int] = None
        self.is_processing = False
        self._last_led_state = None  # Track state to avoid spamming serial
        
        # Check-in mode: 'face' or 'qr'
        self.checkin_mode = 'face'
        self._qr_scanning = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the check-in interface."""
        # Two column layout
        left_panel = ctk.CTkFrame(self, fg_color="transparent")
        left_panel.pack(side="left", fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        right_panel = ctk.CTkFrame(
            self, 
            fg_color=COLORS['bg_secondary'],
            corner_radius=RADIUS['xl'],
            width=400
        )
        right_panel.pack(side="right", fill="y", padx=SPACING['lg'], pady=SPACING['lg'])
        right_panel.pack_propagate(False)
        
        # Left panel: Camera and controls
        self._setup_camera_panel(left_panel)
        
        # Right panel: Status and boarding pass
        self._setup_status_panel(right_panel)
    
    def _setup_camera_panel(self, parent):
        """Setup the camera panel."""
        # Header
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, SPACING['lg']))
        
        self.header_title = ctk.CTkLabel(
            header,
            text="🛂 Self Check-In",
            font=FONTS['heading'],
            text_color=COLORS['text_primary']
        )
        self.header_title.pack(anchor="w")
        
        self.header_subtitle = ctk.CTkLabel(
            header,
            text="Look at the camera for automatic check-in",
            font=FONTS['body'],
            text_color=COLORS['text_secondary']
        )
        self.header_subtitle.pack(anchor="w", pady=(SPACING['xs'], 0))
        
        # Mode toggle frame
        mode_frame = ctk.CTkFrame(header, fg_color="transparent")
        mode_frame.pack(anchor="w", pady=SPACING['md'])
        
        self.face_mode_btn = ctk.CTkButton(
            mode_frame,
            text="👤 Face Recognition",
            font=FONTS['body'],
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_hover'],
            text_color=COLORS['bg_primary'],
            corner_radius=RADIUS['md'],
            width=180,
            height=40,
            command=lambda: self._set_mode('face')
        )
        self.face_mode_btn.pack(side="left", padx=(0, SPACING['sm']))
        
        self.qr_mode_btn = ctk.CTkButton(
            mode_frame,
            text="📱 QR Code",
            font=FONTS['body'],
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['bg_hover'],
            text_color=COLORS['text_primary'],
            corner_radius=RADIUS['md'],
            width=180,
            height=40,
            command=lambda: self._set_mode('qr')
        )
        self.qr_mode_btn.pack(side="left")
        
        # Camera frame
        camera_container = ctk.CTkFrame(
            parent,
            fg_color=COLORS['bg_card'],
            corner_radius=RADIUS['xl']
        )
        camera_container.pack(fill="both", expand=True)
        
        # Camera widget
        self.camera = CameraWidget(
            camera_container,
            width=640,
            height=480,
            auto_capture=False,
            on_face_detected=self._on_faces_detected
        )
        self.camera.pack(padx=SPACING['md'], pady=SPACING['md'])
        
        # Recognition status
        self.recognition_label = ctk.CTkLabel(
            camera_container,
            text="● Scanning for registered faces...",
            font=FONTS['body_large'],
            text_color=COLORS['warning']
        )
        self.recognition_label.pack(pady=SPACING['md'])
        
        # Manual check-in button
        manual_frame = ctk.CTkFrame(parent, fg_color="transparent")
        manual_frame.pack(fill="x", pady=SPACING['md'])
        
        self.manual_label = ctk.CTkLabel(
            manual_frame,
            text="Or check in with ticket number:",
            font=FONTS['body_small'],
            text_color=COLORS['text_secondary']
        )
        self.manual_label.pack(side="left")
        
        self.ticket_entry = ctk.CTkEntry(
            manual_frame,
            placeholder_text="TK-XXXXXX",
            font=FONTS['body_large'],
            width=300,
            height=55,
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border'],
            border_width=2,
            corner_radius=RADIUS['full']
        )
        self.ticket_entry.pack(side="left", padx=SPACING['md'])
        
        self.manual_checkin_btn = ctk.CTkButton(
            manual_frame,
            text="Check In",
            font=FONTS['button'],
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_hover'],
            height=40,
            width=100,
            command=self._manual_checkin
        )
        self.manual_checkin_btn.pack(side="left")
    
    def _set_mode(self, mode: str):
        """Switch between face recognition and QR code mode."""
        self.checkin_mode = mode
        
        if mode == 'face':
            self.face_mode_btn.configure(
                fg_color=COLORS['accent'],
                text_color=COLORS['bg_primary']
            )
            self.qr_mode_btn.configure(
                fg_color=COLORS['bg_card'],
                text_color=COLORS['text_primary']
            )
            self.recognition_label.configure(
                text="● Scanning for registered faces...",
                text_color=COLORS['warning']
            )
            self._qr_scanning = False
            self.camera.set_qr_mode(False)
        else:  # qr mode
            self.qr_mode_btn.configure(
                fg_color=COLORS['accent'],
                text_color=COLORS['bg_primary']
            )
            self.face_mode_btn.configure(
                fg_color=COLORS['bg_card'],
                text_color=COLORS['text_primary']
            )
            self.recognition_label.configure(
                text="● Hold QR code in front of camera",
                text_color=COLORS['info']
            )
            self._qr_scanning = True
            self.camera.set_qr_mode(True)
        
        logger.info(f"Check-in mode changed to: {mode}")
    
    def _setup_status_panel(self, parent):
        """Setup the status/boarding pass panel."""
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=SPACING['lg'], pady=SPACING['lg'])
        
        # Title
        ctk.CTkLabel(
            content,
            text="Boarding Status",
            font=FONTS['subheading'],
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(0, SPACING['lg']))
        
        # Status icon area
        self.status_icon_label = ctk.CTkLabel(
            content,
            text="👤",
            font=("Segoe UI", 80)
        )
        self.status_icon_label.pack(pady=SPACING['lg'])
        
        # Status message
        self.status_message = ctk.CTkLabel(
            content,
            text="Waiting for\nface recognition...",
            font=FONTS['body_large'],
            text_color=COLORS['text_secondary'],
            justify="center"
        )
        self.status_message.pack(pady=SPACING['md'])
        
        # Boarding pass preview frame (hidden initially)
        self.boarding_frame = ctk.CTkFrame(
            content,
            fg_color=COLORS['bg_card'],
            corner_radius=RADIUS['lg']
        )
        
        # Passenger name
        self.bp_name = ctk.CTkLabel(
            self.boarding_frame,
            text="",
            font=FONTS['subheading'],
            text_color=COLORS['text_primary']
        )
        self.bp_name.pack(pady=(SPACING['md'], SPACING['xs']))
        
        # Route
        self.bp_route = ctk.CTkLabel(
            self.boarding_frame,
            text="",
            font=("Segoe UI", 24, "bold"),
            text_color=COLORS['accent']
        )
        self.bp_route.pack()
        
        # Details grid
        self.bp_details = ctk.CTkFrame(self.boarding_frame, fg_color="transparent")
        self.bp_details.pack(pady=SPACING['md'])
        
        # Print button
        self.print_btn = ctk.CTkButton(
            content,
            text="🖨 Print Boarding Pass",
            font=FONTS['button'],
            fg_color=COLORS['success'],
            hover_color="#00b862",
            height=45,
            command=self._print_boarding_pass
        )
        
        # ESP status
        self.esp_status = ctk.CTkLabel(
            content,
            text="",
            font=FONTS['caption'],
            text_color=COLORS['text_muted']
        )
        self.esp_status.pack(side="bottom", pady=SPACING['sm'])
        
        # Store current ticket for printing
        self.current_ticket = None
        self.current_pdf_path = None
    
    def _load_face_encodings(self):
        """Load all face encodings from booked passengers."""
        passengers = db.get_all_passengers()
        self.known_encodings = face_service.load_all_encodings(passengers)
        
        # Build lookup
        self.passenger_lookup = {p.id: p for p in passengers if p.face_file}
        
        print(f"Loaded {len(self.known_encodings)} face encodings")
    
    def _on_faces_detected(self, faces):
        """Handle face detection - try to recognize or scan QR."""
        if self.is_processing:
            return
        
        # Get current frame for recognition/QR scanning
        frame = self.camera.capture_now()
        if frame is None:
            return
        
        # QR Mode - scan for QR codes
        if self._qr_scanning:
            self._scan_qr_code(frame)
            return
            
        if not faces:
            # No face -> LED Off
            if self._last_led_state != "off":
                esp_service.led_off()
                self._last_led_state = "off"
            return
        
        # Face detected -> Blue (Scanning)
        if self._last_led_state != "scanning":
            esp_service.led_scanning()
            self._last_led_state = "scanning"
        
        # Try to recognize
        result = face_service.recognize_face(frame, self.known_encodings)
        
        if result:
            passenger_id, confidence = result
            
            # Avoid repeated triggers for same person
            if passenger_id == self.last_recognized_id:
                return
            
            self.last_recognized_id = passenger_id
            self._on_passenger_recognized(passenger_id, confidence)
        else:
            # Face found but not recognized -> Red (Error/Unknown)
            # Only trigger red if we haven't just triggered it (to avoid flickering)
            if self._last_led_state != "error":
                esp_service.on_checkin_failure()
                self._last_led_state = "error"
                
                # Optional: Show unknown message on UI
                self.recognition_label.configure(
                    text="● Face not recognized",
                    text_color=COLORS['error']
                )
    
    def _scan_qr_code(self, frame):
        """Scan frame for QR codes."""
        try:
            # Update bounds for visual feedback
            bounds = qr_service.get_qr_bounds(frame)
            self.camera.set_qr_detections(bounds)
            
            qr_data = qr_service.decode_qr_from_image(frame)
            
            if qr_data and qr_data.get('type') == 'flight_ticket':
                ticket_number = qr_data.get('ticket')
                
                if ticket_number:
                    # Avoid repeated triggers
                    if hasattr(self, '_last_qr_ticket') and self._last_qr_ticket == ticket_number:
                        return
                    
                    self._last_qr_ticket = ticket_number
                    logger.info(f"QR Code detected: {ticket_number}")
                    
                    # Show scanning indicator and turn box green
                    self.camera.set_qr_detections(self.camera.qr_detections, success=True)
                    self.recognition_label.configure(
                        text="● Processing check-in...",
                        text_color=COLORS['accent']
                    )
                    
                    # Process check-in
                    self.after(100, lambda: self._process_qr_checkin(ticket_number))
        except Exception as e:
            logger.error(f"QR scan error: {e}")
    
    def _process_qr_checkin(self, ticket_number: str):
        """Process check-in from QR code."""
        ticket = db.get_ticket_by_number(ticket_number)
        
        if not ticket:
            self.recognition_label.configure(
                text="● Ticket not found",
                text_color=COLORS['error']
            )
            sound_service.play_warning()
            self.after(3000, lambda: self._reset_qr_state())
            return
        
        if ticket.status != TicketStatus.BOOKED:
            self.recognition_label.configure(
                text=f"● Ticket already {ticket.status.value}",
                text_color=COLORS['warning']
            )
            self.after(3000, lambda: self._reset_qr_state())
            return
        
        # Get passenger and process check-in
        passenger = db.get_passenger_by_id(ticket.passenger_id)
        
        if passenger:
            self.is_processing = True
            checked_ticket = db.check_in_ticket(ticket.id)
            if checked_ticket:
                sound_service.play_success()
                audit_service.log_checkin(checked_ticket.ticket_number, passenger.full_name, True)
                self._show_boarding_pass(passenger, checked_ticket)
            self.after(5000, self._reset_recognition)
    
    def _reset_qr_state(self):
        """Reset QR scanning state."""
        self._last_qr_ticket = None
        self.camera.set_qr_detections(None, success=False)
        self.recognition_label.configure(
            text="● Hold QR code in front of camera",
            text_color=COLORS['info']
        )
    
    def _on_passenger_recognized(self, passenger_id: int, confidence: float):
        """Handle successful passenger recognition."""
        self.is_processing = True
        
        try:
            passenger = self.passenger_lookup.get(passenger_id)
            if not passenger:
                return
            
            # Update recognition label
            self.recognition_label.configure(
                text=f"✓ Recognized: {passenger.full_name} ({confidence:.1f}%)",
                text_color=COLORS['success']
            )
            
            # Find booked ticket for this passenger
            tickets = db.get_tickets_by_passenger(passenger_id)
            booked_ticket = None
            
            for ticket in tickets:
                if ticket.status == TicketStatus.BOOKED:
                    booked_ticket = ticket
                    break
            
            if not booked_ticket:
                self._show_no_booking(passenger)
                return
            
            # Check in the ticket
            checked_ticket = db.check_in_ticket(booked_ticket.id)
            
            if checked_ticket:
                sound_service.play_success()
                audit_service.log_checkin(checked_ticket.ticket_number, passenger.full_name, True)
                self._show_boarding_pass(passenger, checked_ticket)
                
        finally:
            # Allow new recognition after delay
            self.after(5000, self._reset_recognition)
    
    def _show_boarding_pass(self, passenger, ticket):
        """Display boarding pass and trigger announcements."""
        self.current_ticket = ticket
        
        # Update status
        self.status_icon_label.configure(text="✈")
        self.status_message.configure(
            text="Check-In Successful!",
            text_color=COLORS['success']
        )
        
        # Show boarding pass frame
        self.boarding_frame.pack(fill="x", pady=SPACING['md'])
        
        # Update boarding pass details
        self.bp_name.configure(text=passenger.full_name)
        self.bp_route.configure(text=f"{ticket.source_airport} → {ticket.destination_airport}")
        
        # Clear and add details
        for widget in self.bp_details.winfo_children():
            widget.destroy()
        
        details = [
            ("SEAT", ticket.seat_number, True),
            ("GATE", ticket.gate, True),
            ("TIME", ticket.flight_time.strftime("%H:%M"), False),
            ("DATE", str(ticket.flight_date), False),
        ]
        
        for label, value, highlight in details:
            item = ctk.CTkFrame(self.bp_details, fg_color="transparent")
            item.pack(side="left", padx=SPACING['md'])
            
            ctk.CTkLabel(
                item,
                text=label,
                font=FONTS['caption'],
                text_color=COLORS['text_muted']
            ).pack()
            
            ctk.CTkLabel(
                item,
                text=value,
                font=FONTS['subheading'] if highlight else FONTS['body'],
                text_color=COLORS['accent'] if highlight else COLORS['text_primary']
            ).pack()
        
        # Show print button
        self.print_btn.pack(fill="x", pady=SPACING['md'])
        
        # Generate PDF
        self.current_pdf_path = boarding_pass_service.generate(
            ticket_number=ticket.ticket_number,
            passenger_name=passenger.full_name,
            source_airport=ticket.source_airport,
            source_city=ticket.source_airport_name.split(' ')[0] if ticket.source_airport_name else "",
            destination_airport=ticket.destination_airport,
            destination_city=ticket.destination_airport_name.split(' ')[0] if ticket.destination_airport_name else "",
            flight_date=str(ticket.flight_date),
            flight_time=ticket.flight_time.strftime("%H:%M"),
            seat=ticket.seat_number,
            gate=ticket.gate,
            passport_number=""
        )
        
        # Voice announcement
        voice_service.announce_boarding(
            passenger_name=passenger.full_name,
            seat=ticket.seat_number,
            gate=ticket.gate,
            flight_time=ticket.flight_time.strftime("%H:%M")
        )
        
        # ESP32 signal
        if esp_service.is_connected:
            esp_service.on_checkin_success()
            self.esp_status.configure(text="✓ Gate signal sent")
        else:
            self.esp_status.configure(text="ESP32 not connected")
    
    def _show_no_booking(self, passenger):
        """Show message when no booking found."""
        sound_service.play_warning()
        self.status_icon_label.configure(text="❓")
        self.status_message.configure(
            text=f"No booking found for\n{passenger.full_name}",
            text_color=COLORS['warning']
        )
    
    def _reset_recognition(self):
        """Reset recognition state."""
        self.is_processing = False
        self.last_recognized_id = None
        self._last_led_state = None
        esp_service.led_off()
        
        # Reset UI after delay
        self.after(10000, self._reset_ui)
    
    def _reset_ui(self):
        """Reset the UI to initial state."""
        self.status_icon_label.configure(text="👤")
        self.status_message.configure(
            text="Waiting for\nface recognition...",
            text_color=COLORS['text_secondary']
        )
        self.boarding_frame.pack_forget()
        self.print_btn.pack_forget()
        self.esp_status.configure(text="")
        self.current_ticket = None
        self.current_pdf_path = None
        
        self.recognition_label.configure(
            text="● Scanning for registered faces...",
            text_color=COLORS['warning']
        )
    
    def _manual_checkin(self):
        """Handle manual check-in by ticket number."""
        ticket_number = self.ticket_entry.get().strip().upper()
        
        if not ticket_number:
            return
        
        ticket = db.get_ticket_by_number(ticket_number)
        
        if not ticket:
            self.status_message.configure(
                text="Ticket not found",
                text_color=COLORS['error']
            )
            return
        
        if ticket.status != TicketStatus.BOOKED:
            self.status_message.configure(
                text=f"Ticket already {ticket.status.value}",
                text_color=COLORS['warning']
            )
            return
        
        # Get passenger
        passenger = db.get_passenger_by_id(ticket.passenger_id)
        
        if passenger:
            self.is_processing = True
            checked_ticket = db.check_in_ticket(ticket.id)
            if checked_ticket:
                self._show_boarding_pass(passenger, checked_ticket)
            self.is_processing = False
    
    def _print_boarding_pass(self):
        """Print the current boarding pass."""
        if self.current_pdf_path:
            # Open PDF for user to print
            boarding_pass_service.open_pdf(self.current_pdf_path)
    
    def on_show(self):
        """Called when view is shown."""
        self._load_face_encodings()
        self._reset_ui()
        self.camera.start()
        self._last_led_state = None
        
        # Try to connect ESP
        if not esp_service.is_connected:
            esp_service.auto_connect()
    
    def on_hide(self):
        """Called when view is hidden."""
        self.camera.stop()
        voice_service.stop()
