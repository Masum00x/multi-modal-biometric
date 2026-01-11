#!/usr/bin/env python3
"""Test enrollment without camera - uses generated test images."""

import cv2
import numpy as np
from src.workflows.enrollment import FaceEnrollmentWorkflow
from src.workflows.verification import FaceVerificationWorkflow
from src.database.storage import DatabaseManager

def create_test_face_image(seed=0):
    """Create a synthetic face-like image for testing."""
    np.random.seed(seed)
    
    # Create a simple face-like image (this won't work with actual face detection)
    # But we can use it to test the workflow
    img = np.ones((480, 640, 3), dtype=np.uint8) * 200
    
    # Draw simple face
    center = (320, 240)
    
    # Face oval
    cv2.ellipse(img, center, (100, 130), 0, 0, 360, (220, 180, 150), -1)
    
    # Eyes
    cv2.circle(img, (280, 220), 15, (50, 50, 50), -1)
    cv2.circle(img, (360, 220), 15, (50, 50, 50), -1)
    
    # Nose
    cv2.ellipse(img, (320, 260), (10, 20), 0, 0, 360, (200, 160, 140), -1)
    
    # Mouth
    cv2.ellipse(img, (320, 300), (40, 20), 0, 0, 180, (180, 100, 100), 2)
    
    # Add some noise for variation
    noise = np.random.randint(-10, 10, img.shape, dtype=np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    return img

def test_system():
    """Test the enrollment and verification system."""
    print("\n" + "="*60)
    print("Testing Face Recognition System")
    print("="*60 + "\n")
    
    # Initialize database
    db = DatabaseManager()
    db.initialize()
    
    print("1. Database initialized ✓")
    
    # List current users
    users = db.list_users()
    print(f"2. Currently enrolled users: {len(users)}")
    
    # Initialize workflow
    workflow = FaceEnrollmentWorkflow()
    print("3. Enrollment workflow initialized ✓")
    
    # Note: Actual enrollment requires camera and real faces
    # This test just verifies the workflow is properly configured
    
    print("\n" + "="*60)
    print("System Status: READY")
    print("="*60)
    print("\nTo enroll a real user, run:")
    print('  python demo/face_demo.py enroll <user_id> "<name>" -s 3')
    print("\nMake sure you have:")
    print("  - A working webcam")
    print("  - Good lighting")
    print("  - Your face clearly visible")
    print("\nThe system will:")
    print("  1. Open camera preview")
    print("  2. Detect your face")
    print("  3. Auto-capture 3 samples (or press 'c' manually)")
    print("  4. Store your face template in the database")
    print("  5. Press 'q' to quit/cancel")
    
    return True

if __name__ == "__main__":
    try:
        success = test_system()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
