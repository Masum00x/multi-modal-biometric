# Face Recognition System - Usage Guide

## System Status: ✅ READY

All components are properly configured and working:
- ✅ Face detection (CNN model with GPU acceleration)
- ✅ Face encoding (128-D embeddings)
- ✅ Face matching (configurable tolerance)
- ✅ SQLite database storage
- ✅ Enrollment workflow
- ✅ Verification workflow
- ✅ Identification workflow

## Quick Start

### 1. Enroll Yourself

```bash
python demo/face_demo.py enroll sahil "Sahil" -s 3
```

**What happens:**
- Camera opens with live preview window
- System detects your face automatically
- Auto-captures 3 samples (moves every 0.5 seconds)
- Alternatively, press 'c' to capture manually
- Press 'q' to quit/cancel anytime

**Tips for good enrollment:**
- ✓ Face the camera directly
- ✓ Ensure good lighting
- ✓ Move slightly between captures (turn head slightly, tilt, etc.)
- ✓ Keep your face in the green box
- ✗ Don't wear sunglasses or masks
- ✗ Avoid extreme lighting conditions

### 2. List Enrolled Users

```bash
python demo/face_demo.py list
```

Shows all enrolled users with their enrollment details.

### 3. Verify Your Identity (1:1 Match)

```bash
python demo/face_demo.py verify sahil
```

**What happens:**
- Opens camera
- Tries to match your face against the stored template for "sahil"
- Shows success/failure with confidence score
- Maximum 3 attempts with 30 second timeout

### 4. Identify Who's at Camera (1:N Search)

```bash
python demo/face_demo.py identify
```

**What happens:**
- Opens camera
- Searches through ALL enrolled users
- Identifies the best match
- Shows the person's name and confidence score

### 5. View Verification Statistics

```bash
python demo/face_demo.py stats
```

Shows:
- Total verification attempts
- Success/failure counts
- Success rate percentage
- Average confidence scores

### 6. Continuous Monitoring

**Continuous Verification (Watch for specific person):**
```bash
python demo/face_demo.py continuous sahil
```

**Continuous Identification (Watch for any enrolled person):**
```bash
python demo/face_demo.py continuous
```

Press 'q' to stop monitoring.

### 7. Delete a User

```bash
python demo/face_demo.py delete sahil
```

Removes the user and their face template from the database.

## Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `enroll <user_id> "<name>" [-s NUM]` | Enroll new user | `enroll john "John Doe" -s 5` |
| `verify <user_id> [-t TIMEOUT]` | Verify identity | `verify john -t 60` |
| `identify [-t TIMEOUT]` | Identify person | `identify -t 30` |
| `list [-a]` | List users | `list --all` |
| `delete <user_id> [-f]` | Delete user | `delete john --force` |
| `stats [-u USER] [-d DAYS]` | View stats | `stats -u john -d 7` |
| `continuous [USER_ID]` | Live monitoring | `continuous john` |

## Configuration

Settings are in `config/settings.yaml`:

```yaml
face_recognition:
  detection_model: "cnn"        # Use CNN (GPU) or HOG (CPU)
  match_tolerance: 0.6          # Lower = stricter (0.0-1.0)
  min_face_size: 50            # Minimum face size in pixels
  
enrollment:
  num_samples: 5               # Number of face samples to capture
  sample_interval: 0.5         # Seconds between auto-captures
  
verification:
  max_attempts: 3              # Maximum verification attempts
  timeout_seconds: 30          # Timeout for verification
```

## Troubleshooting

### Camera won't open
```bash
# Check if camera is available
ls /dev/video*

# Try different camera ID
# Edit config/settings.yaml, change device_id: 0 to device_id: 1
```

### Face not detected
- Ensure good lighting
- Move closer to camera
- Remove glasses/masks
- Check camera focus

### Low accuracy
- Re-enroll with more samples: `-s 10`
- Adjust tolerance in config (lower = stricter)
- Ensure enrollment was done in similar lighting

### Database location
Default: `data/biometric.db`

To reset database:
```bash
rm data/biometric.db
```

## Architecture

```
┌─────────────┐
│   Camera    │
│  (OpenCV)   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Face Detection  │ ← face_recognition library
│   (CNN/HOG)     │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Face Encoding   │ ← 128-D embeddings
│  (dlib model)   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Face Matching  │ ← Euclidean distance
│  (tolerance)    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  SQLite DB      │ ← Store templates
│  (persistence)  │
└─────────────────┘
```

## Next Steps

After testing face recognition, the system will be extended with:
- 🔲 Iris recognition module (open-iris library)
- 🔲 Dual-factor fusion (face + iris)
- 🔲 Weighted score combination
- 🔲 System unlock on successful authentication

## Support

For issues or questions:
1. Check this guide
2. Review implementation document: `docs/IMPLEMENTATION_DOCUMENT.md`
3. Check logs in terminal output
