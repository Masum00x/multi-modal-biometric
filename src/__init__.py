"""
Multi-Modal Biometric Authentication System

A dual-factor biometric authentication system combining face and iris recognition.
"""

__version__ = "0.1.0"
__author__ = "Sahil"

# Re-export main components for convenience
from .capture.camera import Camera, CaptureResult, ImageQuality
from .face.recognition import (
    FaceRecognitionSystem,
    FaceDetector,
    FaceEncoder,
    FaceMatcher,
    DetectedFace,
    FaceTemplate,
)
from .database.storage import DatabaseManager, EnrollmentResult
from .workflows.enrollment import FaceEnrollmentWorkflow
from .workflows.verification import FaceVerificationWorkflow, VerificationResult

__all__ = [
    # Camera
    "Camera",
    "CaptureResult",
    "ImageQuality",
    # Face Recognition
    "FaceRecognitionSystem",
    "FaceDetector",
    "FaceEncoder",
    "FaceMatcher",
    "DetectedFace",
    "FaceTemplate",
    # Database
    "DatabaseManager",
    "EnrollmentResult",
    # Workflows
    "FaceEnrollmentWorkflow",
    "FaceVerificationWorkflow",
    "VerificationResult",
]
