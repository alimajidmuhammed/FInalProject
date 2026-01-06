"""
Face Service - Handles face detection and recognition.
Uses MediaPipe for detection and face_recognition for encoding/matching.
"""
import pickle
import uuid
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import numpy as np
import cv2

try:
    import mediapipe as mp
    # Check if the old solutions API is available
    if hasattr(mp, 'solutions'):
        MEDIAPIPE_AVAILABLE = True
    else:
        # New mediapipe API (0.10.31+) - fall back to OpenCV
        MEDIAPIPE_AVAILABLE = False
        print("Note: Using OpenCV for face detection (mediapipe API changed)")
except ImportError:
    MEDIAPIPE_AVAILABLE = False

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False

from config import FACE_MATCH_THRESHOLD, FACES_DIR
from services.encryption_service import encryption_service


class FaceService:
    """Manages face detection, encoding, and recognition."""
    
    def __init__(self):
        """Initialize face service with detection models."""
        self.mp_face_detection = None
        self.mp_draw = None
        self.detector = None
        
        if MEDIAPIPE_AVAILABLE:
            self.mp_face_detection = mp.solutions.face_detection
            self.mp_draw = mp.solutions.drawing_utils
            self.detector = self.mp_face_detection.FaceDetection(
                model_selection=1,  # 1 = full range model (better for distance)
                min_detection_confidence=0.5
            )
        
        # Cache for loaded face encodings (passenger_id -> encoding)
        self._encoding_cache: Dict[int, np.ndarray] = {}
    
    def detect_faces(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect faces in a frame using MediaPipe.
        Returns list of face detections with bounding boxes.
        """
        if not MEDIAPIPE_AVAILABLE or self.detector is None:
            return self._detect_faces_opencv(frame)
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.detector.process(rgb_frame)
        
        faces = []
        if results.detections:
            h, w = frame.shape[:2]
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                # Ensure bounds are within frame
                x = max(0, x)
                y = max(0, y)
                width = min(width, w - x)
                height = min(height, h - y)
                
                faces.append({
                    'bbox': (x, y, width, height),
                    'confidence': detection.score[0] if detection.score else 0.0
                })
        
        return faces
    
    def _detect_faces_opencv(self, frame: np.ndarray) -> List[Dict]:
        """Fallback face detection using OpenCV Haar Cascade."""
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        cascade = cv2.CascadeClassifier(cascade_path)
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detections = cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))
        
        faces = []
        for (x, y, w, h) in detections:
            faces.append({
                'bbox': (x, y, w, h),
                'confidence': 0.8  # Default confidence for Haar
            })
        
        return faces
    
    def draw_face_boxes(
        self, 
        frame: np.ndarray, 
        faces: List[Dict], 
        color: Tuple[int, int, int] = (0, 255, 0),
        label: str = None
    ) -> np.ndarray:
        """Draw bounding boxes around detected faces."""
        frame_copy = frame.copy()
        
        for face in faces:
            x, y, w, h = face['bbox']
            cv2.rectangle(frame_copy, (x, y), (x + w, y + h), color, 2)
            
            if label:
                cv2.putText(
                    frame_copy, label, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
                )
        
        return frame_copy
    
    def get_face_encoding(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Get face encoding from a frame.
        Returns numpy array encoding or None if no face found.
        """
        if not FACE_RECOGNITION_AVAILABLE:
            print("Warning: face_recognition not available")
            return None
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Get face locations and encodings
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if not face_locations:
            return None
        
        # Get encoding for first face
        encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        if encodings:
            return encodings[0]
        return None
    
    def save_face_encoding(
        self, 
        encoding: np.ndarray, 
        passenger_id: int
    ) -> str:
        """
        Save face encoding to encrypted file.
        Returns the filename (relative to FACES_DIR).
        """
        # Serialize encoding
        encoding_bytes = pickle.dumps(encoding)
        
        # Generate unique filename
        filename = f"face_{passenger_id}_{uuid.uuid4().hex[:8]}"
        
        # Encrypt and save
        filepath = encryption_service.encrypt_to_file(encoding_bytes, filename)
        
        # Update cache
        self._encoding_cache[passenger_id] = encoding
        
        return filepath.name
    
    def load_face_encoding(self, face_file: str) -> Optional[np.ndarray]:
        """Load and decrypt face encoding from file."""
        filepath = FACES_DIR / face_file
        
        encrypted_data = encryption_service.decrypt_from_file(filepath)
        if encrypted_data:
            return pickle.loads(encrypted_data)
        return None
    
    def load_all_encodings(self, passengers: List) -> Dict[int, np.ndarray]:
        """
        Load all face encodings for a list of passengers.
        Returns dict mapping passenger_id to encoding.
        """
        encodings = {}
        
        for passenger in passengers:
            if passenger.face_file:
                # Check cache first
                if passenger.id in self._encoding_cache:
                    encodings[passenger.id] = self._encoding_cache[passenger.id]
                else:
                    encoding = self.load_face_encoding(passenger.face_file)
                    if encoding is not None:
                        encodings[passenger.id] = encoding
                        self._encoding_cache[passenger.id] = encoding
        
        return encodings
    
    def recognize_face(
        self, 
        frame: np.ndarray, 
        known_encodings: Dict[int, np.ndarray]
    ) -> Optional[Tuple[int, float]]:
        """
        Recognize a face in frame against known encodings.
        Returns (passenger_id, confidence) or None if no match.
        """
        if not FACE_RECOGNITION_AVAILABLE or not known_encodings:
            return None
        
        # Get encoding of face in frame
        current_encoding = self.get_face_encoding(frame)
        if current_encoding is None:
            return None
        
        # Compare with all known encodings
        best_match_id = None
        best_distance = float('inf')
        
        for passenger_id, known_encoding in known_encodings.items():
            # Calculate face distance (lower = better match)
            distance = face_recognition.face_distance([known_encoding], current_encoding)[0]
            
            if distance < best_distance:
                best_distance = distance
                best_match_id = passenger_id
        
        # Check if best match is within threshold
        if best_distance <= FACE_MATCH_THRESHOLD:
            # Convert distance to confidence (0-100%)
            confidence = (1 - best_distance) * 100
            return (best_match_id, confidence)
        
        return None
    
    def is_face_centered(
        self, 
        face: Dict, 
        frame_width: int, 
        frame_height: int, 
        tolerance: float = 0.2
    ) -> bool:
        """Check if face is centered in frame."""
        x, y, w, h = face['bbox']
        face_center_x = x + w // 2
        face_center_y = y + h // 2
        
        frame_center_x = frame_width // 2
        frame_center_y = frame_height // 2
        
        # Calculate tolerance in pixels
        tol_x = frame_width * tolerance
        tol_y = frame_height * tolerance
        
        is_centered_x = abs(face_center_x - frame_center_x) < tol_x
        is_centered_y = abs(face_center_y - frame_center_y) < tol_y
        
        return is_centered_x and is_centered_y
    
    def clear_cache(self):
        """Clear the encoding cache."""
        self._encoding_cache.clear()


# Global face service instance
face_service = FaceService()
