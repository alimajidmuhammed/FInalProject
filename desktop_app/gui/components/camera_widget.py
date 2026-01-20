"""
Camera Widget - Reusable camera feed component with face detection.
"""
import cv2
import threading
from typing import Callable, Optional, List, Dict
import customtkinter as ctk
from PIL import Image, ImageTk

from gui.theme import COLORS, RADIUS
from services.face_service import face_service


class CameraWidget(ctk.CTkFrame):
    """
    A reusable camera widget that displays live feed with face detection.
    """
    
    def __init__(
        self,
        parent,
        width: int = 640,
        height: int = 480,
        on_face_detected: Optional[Callable] = None,
        on_face_captured: Optional[Callable] = None,
        auto_capture: bool = False,
        auto_capture_delay: int = 30,  # frames
        **kwargs
    ):
        super().__init__(parent, fg_color=COLORS['bg_card'], corner_radius=RADIUS['lg'], **kwargs)
        
        self.cam_width = width
        self.cam_height = height
        self.on_face_detected = on_face_detected
        self.on_face_captured = on_face_captured
        self.auto_capture = auto_capture
        self.auto_capture_delay = auto_capture_delay
        
        self.camera: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.current_frame = None
        self.detected_faces: List[Dict] = []
        self._stable_face_frames = 0
        self._capture_thread: Optional[threading.Thread] = None
        
        # QR Mode attributes
        self.qr_mode = False
        self.qr_detections: Optional[tuple] = None  # (x, y, w, h)
        self.qr_success = False  # To turn box green
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the camera display UI."""
        # Camera display label
        self.display_label = ctk.CTkLabel(
            self,
            text="Camera Initializing...",
            width=self.cam_width,
            height=self.cam_height,
            fg_color=COLORS['bg_secondary'],
            corner_radius=RADIUS['md']
        )
        self.display_label.pack(padx=10, pady=10)
        
        # Status bar
        self.status_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.status_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="● Camera Off",
            text_color=COLORS['text_secondary'],
            font=("Segoe UI", 12)
        )
        self.status_label.pack(side="left")
        
        self.face_count_label = ctk.CTkLabel(
            self.status_frame,
            text="Faces: 0",
            text_color=COLORS['text_secondary'],
            font=("Segoe UI", 12)
        )
        self.face_count_label.pack(side="right")
    
    def start(self):
        """Start the camera feed."""
        if self.is_running:
            return
        
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                self._show_error("Camera not available")
                return
            
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_height)
            
            self.is_running = True
            self._stable_face_frames = 0
            
            self.status_label.configure(text="● Camera Active", text_color=COLORS['success'])
            
            self._capture_loop()
            
        except Exception as e:
            self._show_error(f"Camera error: {e}")
    
    def stop(self):
        """Stop the camera feed."""
        self.is_running = False
        
        if self.camera:
            self.camera.release()
            self.camera = None
        
        # Only update UI if widgets still exist (prevents TclError on destroyed widgets)
        try:
            if self.winfo_exists() and self.status_label.winfo_exists():
                self.status_label.configure(text="● Camera Off", text_color=COLORS['text_secondary'])
            if self.winfo_exists() and self.display_label.winfo_exists():
                self.display_label.configure(image=None, text="Camera Stopped")
        except Exception:
            pass  # Widget was already destroyed
    
    def _capture_loop(self):
        """Main capture loop."""
        if not self.is_running:
            return
        
        try:
            ret, frame = self.camera.read()
            
            if ret:
                self.current_frame = frame.copy()
                
                # Detect faces
                self.detected_faces = face_service.detect_faces(frame)
                
                # Update face count display
                face_count = len(self.detected_faces)
                self.face_count_label.configure(text=f"Faces: {face_count}")
                
                # Draw QR box if in QR mode
                if self.qr_mode:
                    display_frame = frame.copy()
                    
                    # Calculate center square
                    size = 300
                    x = (self.cam_width - size) // 2
                    y = (self.cam_height - size) // 2
                    
                    # Yellow by default, Green if successful detection
                    color = (0, 255, 0) if self.qr_success else (0, 255, 255)
                    
                    # Draw corners of the aiming square for a modern look
                    thick = 2
                    cv2.rectangle(display_frame, (x, y), (x + size, y + size), color, thick)
                    
                    # Add "Aim QR Code Here" text
                    text = "AIM QR CODE HERE"
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    text_size = cv2.getTextSize(text, font, 0.6, 2)[0]
                    tx = (self.cam_width - text_size[0]) // 2
                    cv2.putText(display_frame, text, (tx, y - 15), font, 0.6, color, 2)
                
                # Draw face boxes if detection enabled and not in QR mode
                elif self.detected_faces:
                    display_frame = face_service.draw_face_boxes(
                        frame, 
                        self.detected_faces,
                        color=(0, 212, 255)  # Cyan
                    )
                    
                    # Callback for face detection
                    if self.on_face_detected:
                        self.on_face_detected(self.detected_faces)
                    
                    # Auto-capture logic
                    if self.auto_capture and len(self.detected_faces) == 1:
                        face = self.detected_faces[0]
                        if face_service.is_face_centered(face, self.cam_width, self.cam_height):
                            self._stable_face_frames += 1
                            
                            # Show countdown
                            remaining = self.auto_capture_delay - self._stable_face_frames
                            if remaining > 0:
                                self.status_label.configure(
                                    text=f"● Hold still... {remaining // 10 + 1}s",
                                    text_color=COLORS['warning']
                                )
                            
                            if self._stable_face_frames >= self.auto_capture_delay:
                                self._trigger_capture()
                        else:
                            self._stable_face_frames = 0
                            self.status_label.configure(
                                text="● Center your face",
                                text_color=COLORS['accent']
                            )
                    else:
                        self._stable_face_frames = 0
                else:
                    display_frame = frame
                    self._stable_face_frames = 0
                    if self.auto_capture and not self.qr_mode:
                        self.status_label.configure(
                            text="● Looking for face...",
                            text_color=COLORS['warning']
                        )
                
                # Display frame
                self._display_frame(display_frame)
            
            # Schedule next frame
            if self.is_running:
                self.after(30, self._capture_loop)
                
        except Exception as e:
            print(f"Capture error: {e}")
            if self.is_running:
                self.after(100, self._capture_loop)
    
    def _display_frame(self, frame):
        """Convert and display frame in the label."""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize to fit
        rgb_frame = cv2.resize(rgb_frame, (self.cam_width, self.cam_height))
        
        # Convert to PIL Image
        pil_image = Image.fromarray(rgb_frame)
        
        # Convert to CTk Image
        ctk_image = ctk.CTkImage(
            light_image=pil_image,
            dark_image=pil_image,
            size=(self.cam_width, self.cam_height)
        )
        
        # Update label
        self.display_label.configure(image=ctk_image, text="")
        self.display_label.image = ctk_image  # Keep reference
    
    def _trigger_capture(self):
        """Trigger a face capture."""
        if self.current_frame is not None and self.on_face_captured:
            self.status_label.configure(
                text="● Face Captured!",
                text_color=COLORS['success']
            )
            self.on_face_captured(self.current_frame.copy())
            self._stable_face_frames = 0
    
    def capture_now(self) -> Optional:
        """Manually capture current frame."""
        if self.current_frame is not None:
            return self.current_frame.copy()
        return None
    
    def _show_error(self, message: str):
        """Display error message."""
        self.display_label.configure(
            text=message,
            text_color=COLORS['error']
        )
        self.status_label.configure(
            text="● Error",
            text_color=COLORS['error']
        )
    
    def get_current_faces(self) -> List[Dict]:
        """Get currently detected faces."""
        return self.detected_faces.copy()
    
    def has_face(self) -> bool:
        """Check if at least one face is detected."""
        return len(self.detected_faces) > 0

    def set_qr_mode(self, enabled: bool):
        """Set QR scanning mode."""
        self.qr_mode = enabled
        self.qr_detections = None
        self.qr_success = False

    def set_qr_detections(self, detections: Optional[tuple], success: bool = False):
        """Update QR code bounding box and status."""
        self.qr_detections = detections
        self.qr_success = success
