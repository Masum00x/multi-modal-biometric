"""Face enrollment workflow module.

Provides functionality to enroll new users into the biometric system
by capturing multiple face samples and creating a template.
"""

import time
from dataclasses import dataclass
from typing import Optional
import cv2
import numpy as np

from ..capture.camera import Camera, CaptureResult
from ..face.recognition import (
    FaceRecognitionSystem,
    DetectedFace,
)
from ..database.storage import DatabaseManager, EnrollmentResult
from ..utils.config import get_config


@dataclass
class EnrollmentSession:
    """Tracks the state of an enrollment session."""
    
    user_id: str
    name: str
    target_samples: int
    captured_samples: list[DetectedFace]
    quality_scores: list[float]
    start_time: float
    
    @property
    def samples_collected(self) -> int:
        return len(self.captured_samples)
    
    @property
    def is_complete(self) -> bool:
        return self.samples_collected >= self.target_samples
    
    @property
    def progress_percent(self) -> float:
        return (self.samples_collected / self.target_samples) * 100


class FaceEnrollmentWorkflow:
    """Handles the face enrollment process.
    
    This class manages the complete enrollment workflow:
    1. Capture multiple face samples from the camera
    2. Validate face detection and quality
    3. Generate face encodings
    4. Store template in database
    
    Usage:
        workflow = FaceEnrollmentWorkflow()
        
        # Interactive enrollment
        result = workflow.enroll_interactive("user123", "John Doe")
        
        # Or with pre-captured images
        result = workflow.enroll_from_images("user123", "John Doe", images)
    """
    
    def __init__(
        self,
        camera: Optional[Camera] = None,
        face_system: Optional[FaceRecognitionSystem] = None,
        db_manager: Optional[DatabaseManager] = None
    ):
        """Initialize enrollment workflow.
        
        Args:
            camera: Camera instance (creates new if None)
            face_system: Face recognition system (creates new if None)
            db_manager: Database manager (creates new if None)
        """
        self.config = get_config()
        
        self.camera = camera or Camera()
        self.face_system = face_system or FaceRecognitionSystem()
        self.db = db_manager or DatabaseManager()
        
        # Ensure database is initialized
        self.db.initialize()
        
        # Enrollment parameters from config
        self.num_samples = self.config.enrollment.num_samples
        self.sample_interval = self.config.enrollment.sample_interval
        self.min_quality = self.config.quality.min_brightness
    
    def start_session(
        self,
        user_id: str,
        name: str,
        num_samples: Optional[int] = None
    ) -> EnrollmentSession:
        """Start a new enrollment session.
        
        Args:
            user_id: Unique user identifier
            name: User's display name
            num_samples: Number of samples to capture (default from config)
            
        Returns:
            EnrollmentSession object
        """
        target = num_samples or self.num_samples
        target = max(3, min(target, 10))  # Clamp between 3 and 10 samples
        
        return EnrollmentSession(
            user_id=user_id,
            name=name,
            target_samples=target,
            captured_samples=[],
            quality_scores=[],
            start_time=time.time()
        )
    
    def capture_sample(
        self,
        session: EnrollmentSession,
        frame: np.ndarray
    ) -> tuple[bool, str, Optional[DetectedFace]]:
        """Attempt to capture a face sample from a frame.
        
        Args:
            session: Current enrollment session
            frame: BGR image frame
            
        Returns:
            Tuple of (success, message, detected_face)
        """
        # Detect and encode face
        result = self.face_system.detect_and_encode(frame)
        
        if result is None:
            return False, "No face detected", None
        
        detected_face, quality = result
        
        # Check quality
        if quality < self.min_quality:
            return False, f"Low quality image ({quality:.1f})", None
        
        # Check for duplicate/similar samples
        if session.captured_samples:
            # Compare with existing samples to ensure diversity
            for existing in session.captured_samples:
                similarity = self.face_system.matcher.get_similarity_score(
                    detected_face.encoding,
                    existing.encoding
                )
                # If too similar (>0.95), it's probably the same pose
                if similarity > 0.95:
                    return False, "Too similar to existing sample, move slightly", None
        
        # Valid sample
        session.captured_samples.append(detected_face)
        session.quality_scores.append(quality)
        
        return True, f"Sample {session.samples_collected}/{session.target_samples} captured", detected_face
    
    def finalize_enrollment(
        self,
        session: EnrollmentSession,
        metadata: Optional[dict] = None
    ) -> EnrollmentResult:
        """Finalize enrollment session and store template.
        
        Args:
            session: Completed enrollment session
            metadata: Optional user metadata
            
        Returns:
            EnrollmentResult with status and details
        """
        if not session.captured_samples:
            return EnrollmentResult(
                success=False,
                message="No samples captured"
            )
        
        if session.samples_collected < 3:  # Minimum 3 samples
            return EnrollmentResult(
                success=False,
                message=f"Insufficient samples: {session.samples_collected}/3 minimum"
            )
        
        # Extract encodings from samples
        encodings = [sample.encoding for sample in session.captured_samples]
        
        # Enroll in database
        result = self.db.enroll_user(
            user_id=session.user_id,
            name=session.name,
            face_encodings=encodings,
            quality_scores=session.quality_scores,
            metadata=metadata
        )
        
        return result
    
    def enroll_interactive(
        self,
        user_id: str,
        name: str,
        num_samples: Optional[int] = None,
        show_preview: bool = True,
        timeout: float = 60.0
    ) -> EnrollmentResult:
        """Run interactive enrollment with live camera preview.
        
        Args:
            user_id: Unique user identifier
            name: User's display name
            num_samples: Number of samples to capture
            show_preview: Whether to show camera preview window
            timeout: Maximum time for enrollment in seconds
            
        Returns:
            EnrollmentResult with status and details
        """
        # Check if user already exists
        existing = self.db.get_user(user_id)
        if existing:
            return EnrollmentResult(
                success=False,
                user_id=user_id,
                message=f"User '{user_id}' already enrolled"
            )
        
        session = self.start_session(user_id, name, num_samples)
        last_capture_time = 0.0
        
        try:
            if not self.camera.open():
                return EnrollmentResult(
                    success=False,
                    message="Failed to open camera"
                )
            
            print(f"\n{'='*50}")
            print(f"Face Enrollment for: {name} ({user_id})")
            print(f"{'='*50}")
            print(f"Please look at the camera and hold still.")
            print(f"Move slightly between captures for sample diversity.")
            print(f"Press 'q' to cancel, 'c' to capture manually.")
            print(f"{'='*50}\n")
            
            while not session.is_complete:
                # Check timeout
                elapsed = time.time() - session.start_time
                if elapsed > timeout:
                    return EnrollmentResult(
                        success=False,
                        message=f"Enrollment timeout ({timeout}s)"
                    )
                
                # Read frame
                result = self.camera.read_frame()
                if not result.success or result.frame is None:
                    print("Failed to read frame from camera")
                    continue
                
                frame = result.frame
                current_time = time.time()
                auto_capture = (current_time - last_capture_time) >= self.sample_interval
                
                # Try to detect face for preview
                result = self.face_system.detect_and_encode(frame)
                
                if result is not None:
                    detected_face, quality = result
                    
                    # Draw detection on preview
                    preview_frame = self.face_system.draw_detections(
                        frame,
                        [detected_face]
                    )
                    
                    # Add quality indicator
                    color = (0, 255, 0) if quality >= self.min_quality else (0, 165, 255)
                    cv2.putText(
                        preview_frame,
                        f"Quality: {quality:.1f}%",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        color,
                        2
                    )
                    
                    # Auto-capture if interval passed and quality is good
                    if auto_capture and quality >= self.min_quality:
                        captured, msg, _ = self.capture_sample(session, frame)
                        if captured:
                            last_capture_time = current_time
                            print(f"✓ {msg}")
                        else:
                            print(f"  {msg}")
                else:
                    preview_frame = frame.copy()
                    cv2.putText(
                        preview_frame,
                        "No face detected",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )
                
                # Add progress bar
                progress = session.progress_percent
                bar_width = 200
                bar_height = 20
                bar_x, bar_y = 10, preview_frame.shape[0] - 40
                
                cv2.rectangle(
                    preview_frame,
                    (bar_x, bar_y),
                    (bar_x + bar_width, bar_y + bar_height),
                    (100, 100, 100),
                    -1
                )
                cv2.rectangle(
                    preview_frame,
                    (bar_x, bar_y),
                    (bar_x + int(bar_width * progress / 100), bar_y + bar_height),
                    (0, 255, 0),
                    -1
                )
                cv2.putText(
                    preview_frame,
                    f"{session.samples_collected}/{session.target_samples}",
                    (bar_x + bar_width + 10, bar_y + 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1
                )
                
                if show_preview:
                    cv2.imshow("Face Enrollment", preview_frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        return EnrollmentResult(
                            success=False,
                            message="Enrollment cancelled by user"
                        )
                    elif key == ord('c'):
                        # Manual capture
                        captured, msg, _ = self.capture_sample(session, frame)
                        if captured:
                            last_capture_time = current_time
                            print(f"✓ {msg}")
                        else:
                            print(f"✗ {msg}")
            
            # Finalize enrollment
            print(f"\n✓ Captured {session.samples_collected} samples")
            print("Finalizing enrollment...")
            
            result = self.finalize_enrollment(session)
            
            if result.success:
                print(f"✓ {result.message}")
            else:
                print(f"✗ {result.message}")
            
            return result
            
        finally:
            self.camera.close()
            cv2.destroyAllWindows()
    
    def enroll_from_images(
        self,
        user_id: str,
        name: str,
        images: list[np.ndarray],
        metadata: Optional[dict] = None
    ) -> EnrollmentResult:
        """Enroll user from pre-captured images.
        
        Args:
            user_id: Unique user identifier
            name: User's display name
            images: List of BGR image frames
            metadata: Optional user metadata
            
        Returns:
            EnrollmentResult with status and details
        """
        # Check if user already exists
        existing = self.db.get_user(user_id)
        if existing:
            return EnrollmentResult(
                success=False,
                user_id=user_id,
                message=f"User '{user_id}' already enrolled"
            )
        
        session = self.start_session(user_id, name, len(images))
        
        for i, image in enumerate(images):
            captured, msg, _ = self.capture_sample(session, image)
            if captured:
                print(f"✓ Image {i+1}: {msg}")
            else:
                print(f"✗ Image {i+1}: {msg}")
        
        return self.finalize_enrollment(session, metadata)
    
    def re_enroll(
        self,
        user_id: str,
        num_samples: Optional[int] = None,
        show_preview: bool = True
    ) -> EnrollmentResult:
        """Re-enroll an existing user with new face samples.
        
        Args:
            user_id: Existing user ID
            num_samples: Number of new samples
            show_preview: Whether to show preview
            
        Returns:
            EnrollmentResult with status
        """
        # Get existing user
        user = self.db.get_user(user_id)
        if not user:
            return EnrollmentResult(
                success=False,
                message=f"User '{user_id}' not found"
            )
        
        # Delete existing template
        self.db.delete_face_template(user_id)
        self.db.delete_user(user_id)
        
        # Re-enroll
        return self.enroll_interactive(
            user_id=user_id,
            name=user.name,
            num_samples=num_samples,
            show_preview=show_preview
        )
