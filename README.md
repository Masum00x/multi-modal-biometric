# Multi-Modal Biometric Authentication System

A dual-factor biometric authentication system combining **face recognition** and **iris recognition** for secure access control.

## 🎯 Project Status

**Phase 1: Face Recognition** ✅ **COMPLETE**

- ✅ Face detection (CNN model)
- ✅ Face encoding (128-D embeddings)  
- ✅ Face matching & verification
- ✅ Database storage (SQLite)
- ✅ Enrollment workflow
- ✅ Verification (1:1) workflow
- ✅ Identification (1:N) workflow
- ✅ CLI demo interface

**Phase 2: Iris Recognition** 🔄 **NEXT**

- 🔲 Iris segmentation (open-iris)
- 🔲 Iris encoding
- 🔲 Iris matching
- 🔲 RGB webcam adaptation

**Phase 3: Dual-Factor Fusion** 🔲 **PLANNED**

- 🔲 Score-level fusion
- 🔲 Weighted combination (face: 0.7, iris: 0.3)
- 🔲 System unlock on authentication

## 🚀 Quick Start

### Installation

```bash
# Clone repository
cd multi-modal-biometric

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Enroll yourself
python demo/face_demo.py enroll sahil "Sahil" -s 3

# Verify your identity
python demo/face_demo.py verify sahil

# List enrolled users
python demo/face_demo.py list

# View all commands
python demo/face_demo.py --help
```

**📖 See [USAGE.md](USAGE.md) for detailed usage guide.**

## 🏗️ Architecture

```
src/
├── capture/        # Camera interface (OpenCV)
├── face/           # Face recognition (face_recognition library)
├── database/       # SQLite storage
├── workflows/      # Enrollment & verification workflows
└── utils/          # Configuration management

demo/
└── face_demo.py    # CLI interface

config/
└── settings.yaml   # System configuration

docs/
└── IMPLEMENTATION_DOCUMENT.md  # Detailed design & architecture
```

## 🔧 Technical Stack

| Component | Technology |
|-----------|-----------|
| Face Detection | face_recognition (dlib HOG/CNN) |
| Face Encoding | dlib ResNet model (128-D) |
| Iris Recognition | open-iris (planned) |
| Camera | OpenCV |
| Database | SQLite + SQLAlchemy |
| Config | YAML + Pydantic |

## 💻 Hardware

**Current Setup:**
- CPU: AMD Ryzen 5 5600H (6C/12T)
- GPU: NVIDIA GTX 1660 (6GB VRAM, 1408 CUDA cores)
- Camera: Built-in 720p RGB webcam

**Optimizations:**
- CNN face detection with GPU acceleration
- Batch processing for multiple faces
- Template caching for faster verification

## 📊 Performance

**Face Recognition:**
- Detection: ~50-100ms (CNN on GPU)
- Encoding: ~100-150ms per face
- Matching: <1ms
- Total verification: ~150-250ms

**Expected Dual-Factor:**
- Face: 99.38% accuracy (standard conditions)
- Iris (RGB): 70-95% accuracy (varies by eye color)
- Combined: Enhanced security with lower false acceptance

## 🎓 Key Features

### Enrollment
- Multi-sample capture (3-10 samples)
- Automatic face detection
- Quality assessment
- Pose diversity validation

### Verification (1:1)
- Fast template matching
- Configurable tolerance
- Multiple attempt support
- Timeout handling

### Identification (1:N)
- Search all enrolled users
- Best match selection
- Confidence scoring
- Template caching

### Database
- User management
- Template storage
- Verification logging
- Statistics tracking

## 🛠️ Configuration

Key settings in `config/settings.yaml`:

```yaml
face_recognition:
  detection_model: "cnn"     # CNN (GPU) or HOG (CPU)
  match_tolerance: 0.6       # 0.0-1.0, lower = stricter
  
enrollment:
  num_samples: 5             # Number of captures
  sample_interval: 0.5       # Seconds between captures
  
verification:
  max_attempts: 3            # Verification attempts
  timeout_seconds: 30        # Timeout
```

## 📝 Documentation

- **[USAGE.md](USAGE.md)** - Complete usage guide with examples
- **[docs/IMPLEMENTATION_DOCUMENT.md](docs/IMPLEMENTATION_DOCUMENT.md)** - Detailed technical documentation
- **Demo CLI** - Run `python demo/face_demo.py --help`

## 🔐 Security Notes

- Face templates stored as 128-D embeddings (not raw images)
- Local storage only (no cloud dependency)
- Configurable match tolerance
- Verification logging for audit trails
- Dual-factor increases security over single-factor

## 🚧 Limitations (RGB Webcam)

- **No NIR camera**: Iris recognition accuracy reduced
- **RGB iris**: 70-95% accuracy vs 99.9% with NIR
- **Lighting dependent**: Performance varies with conditions
- **Eye color impact**: Better accuracy with lighter eyes

## 📈 Roadmap

- [x] Face recognition system
- [ ] Iris recognition integration
- [ ] Dual-factor fusion algorithm
- [ ] Liveness detection
- [ ] Multi-user support
- [ ] Web interface
- [ ] Mobile app integration

## 🙏 Acknowledgments

Built using:
- [face_recognition](https://github.com/ageitgey/face_recognition) by Adam Geitgey
- [open-iris](https://github.com/worldcoin/open-iris) by Worldcoin
- [dlib](http://dlib.net/) by Davis King

## 📄 License

[Your License Here]

---

**Status**: Phase 1 Complete - Ready for Testing ✅
