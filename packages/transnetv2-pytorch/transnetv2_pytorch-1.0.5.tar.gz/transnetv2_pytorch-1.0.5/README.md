# TransNet V2: Shot Boundary Detection Neural Network (PyTorch)

This repository contains a PyTorch implementation of [TransNet V2: An effective deep network architecture for fast shot transition detection](https://arxiv.org/abs/2008.04838).

This is a PyTorch reimplementation of the TransNetV2 model that produces identical results as the original TensorFlow version. The code is for inference only.

## Performance

Our reevaluation of other publicly available state-of-the-art shot boundary methods (F1 scores):

Model | ClipShots | BBC Planet Earth | RAI
--- | :---: | :---: | :---:
TransNet V2 | **77.9** | **96.2** | 93.9
[TransNet](https://arxiv.org/abs/1906.03363) [(github)](https://github.com/soCzech/TransNet) | 73.5 | 92.9 | **94.3**
[Hassanien et al.](https://arxiv.org/abs/1705.03281) [(github)](https://github.com/melgharib/DSBD) | 75.9 | 92.6 | 93.9
[Tang et al., ResNet baseline](https://arxiv.org/abs/1808.04234) [(github)](https://github.com/Tangshitao/ClipShots_basline) | 76.1 | 89.3 | 92.8

## Installation

```bash
pip install transnetv2-pytorch
```

Or install from source:
```bash
git clone https://github.com/allenday/transnetv2_pytorch.git
cd transnetv2_pytorch
pip install -e .
```

## Usage

### Command Line Interface

The package provides both a direct command and Python module execution:

```bash
# Direct command
transnetv2_pytorch path/to/video.mp4

# Python module execution
python -m transnetv2_pytorch path/to/video.mp4
```

#### CLI Arguments

```bash
# Basic usage
transnetv2_pytorch path/to/video.mp4

# Specify output file
transnetv2_pytorch path/to/video.mp4 --output predictions.txt

# Use specific device
transnetv2_pytorch path/to/video.mp4 --device cuda

# Set detection threshold
transnetv2_pytorch path/to/video.mp4 --threshold 0.3

# Get help for all options
transnetv2_pytorch --help
```

**Note**: See [Device Support](#device-support) section for detailed information about device selection and MPS considerations.

### Python API

#### High-Level Methods (Recommended)

```python
import torch
from transnetv2_pytorch import TransNetV2

# Initialize model
model = TransNetV2(device='auto')
model.eval()

# Load weights
state_dict = torch.load("transnetv2-pytorch-weights.pth", map_location=model.device)
model.load_state_dict(state_dict)

with torch.no_grad():
    # Primary method: Scene detection
    scenes = model.detect_scenes("video.mp4")
    
    print(f"Found {len(scenes)} scenes")
    for scene in scenes[:3]:
        print(f"Scene {scene['shot_id']}: {scene['start_time']}s - {scene['end_time']}s")
    
    # Convenience methods
    scene_count = model.get_scene_count("video.mp4")
    timestamps = model.get_scene_timestamps("video.mp4")
    
    # Custom threshold
    scenes = model.detect_scenes("video.mp4", threshold=0.3)
```

#### Mid-Level Methods (Advanced Users)

```python
# Comprehensive analysis with raw predictions
results = model.analyze_video("video.mp4")
print(f"Video FPS: {results['fps']}")
print(f"Total scenes: {results['total_scenes']}")
raw_predictions = results['single_frame_predictions']
scenes = results['scenes']

# Raw video predictions only
video_frames, single_frame_pred, all_frame_pred = model.predict_video("video.mp4")
```

#### Low-Level Methods (Expert Users)

```python
# Direct model inference
frames = load_frames_somehow()  # Your frame loading logic
single_frame_pred, all_frame_pred = model.predict_raw(frames)

# Manual scene conversion
import numpy as np
predictions = single_frame_pred.cpu().detach().numpy()
scenes = model.predictions_to_scenes(predictions, threshold=0.5)
scenes_with_data = model.predictions_to_scenes_with_data(predictions, fps=25.0, threshold=0.5)
```

#### API Consistency

The CLI tool uses the same methods as the programmatic API:
- CLI: `transnetv2_pytorch video.mp4 --threshold 0.5` 
- API: `model.detect_scenes("video.mp4", threshold=0.5)`

Both produce identical results.

## Device Support

This implementation supports multiple compute devices with intelligent auto-detection:

### Supported Devices

- **CPU**: Works on all systems (consistent, reliable)
- **CUDA**: For NVIDIA GPUs (fastest, consistent)  
- **MPS**: For Apple Silicon Macs (fast but with consistency limitations)

### Device Auto-Detection

By default (`--device auto`), the model uses this priority order:

**Priority: CUDA > CPU > MPS**

```bash
# Auto-detection (recommended)
transnetv2_pytorch video.mp4 --device auto
```

When MPS is available but auto-detection chooses CPU instead, you'll see:
```
ℹ️  MPS device detected but not used due to numerical inconsistency issues.
   Use --device mps to explicitly enable MPS (faster but inconsistent results).
```

### MPS Device Considerations

**⚠️ Important**: MPS has numerical inconsistency issues with this neural network architecture.

- **The Problem**: Some 3D convolution operations fall back to CPU inconsistently, causing different scene detection results compared to pure CPU execution
- **Impact**: Same video produces different scene counts (e.g., MPS: 66 scenes, CPU: 108 scenes)
- **Performance**: MPS is ~3x faster than CPU but less accurate

#### Using MPS Explicitly

If you prioritize speed over consistency, you can explicitly request MPS:

```bash
# Explicit MPS usage (faster but inconsistent)
transnetv2_pytorch video.mp4 --device mps
```

When explicitly using MPS, you'll see this warning:
```
⚠️  WARNING: MPS device has numerical inconsistency issues!
   This neural network architecture has operations that fall back to CPU
   inconsistently, causing different scene detection results vs. pure CPU.
```

#### Device Selection Examples

```bash
# Auto-detection (chooses best reliable device)
transnetv2_pytorch video.mp4 --device auto

# Force CPU (most reliable, slower)  
transnetv2_pytorch video.mp4 --device cpu

# Force MPS (fastest on Apple Silicon, less reliable)
transnetv2_pytorch video.mp4 --device mps

# Force CUDA (fastest + reliable on NVIDIA GPUs)
transnetv2_pytorch video.mp4 --device cuda
```

#### Python API Device Selection

```python
from transnetv2_pytorch import TransNetV2

# Auto-detection (recommended)
model = TransNetV2(device='auto')

# Explicit device selection
model = TransNetV2(device='cpu')    # Most reliable
model = TransNetV2(device='mps')    # Fast but inconsistent  
model = TransNetV2(device='cuda')   # Fast and reliable
```

### Recommendations

- **For Production/Research**: Use `--device auto` or `--device cpu` for consistent, reproducible results
- **For Quick Prototyping**: Use `--device mps` on Apple Silicon if speed is more important than precision
- **For GPU Systems**: Use `--device cuda` for optimal performance and consistency

## Memory Optimization

TransNetV2 includes transparent memory optimizations that work automatically without affecting the detection algorithm:

### Automatic Memory Management

The model automatically:
- **Performs periodic memory cleanup** to prevent accumulation
- **Uses efficient tensor management** during processing
- **Applies device-specific memory optimizations** (MPS, CUDA, CPU)

```python
# Memory optimization is automatic and transparent
model = TransNetV2(device='auto')  # All optimizations work behind the scenes
```

### Handling Memory Issues

The memory optimizations are built-in and transparent. For persistent memory issues with very large videos:

1. **Reduce video resolution** before processing
2. **Split longer videos** into shorter segments  
3. **Close other memory-intensive applications**

All optimizations preserve the original algorithm parameters and accuracy!

## Original Work & Training

This PyTorch implementation is based on the original TensorFlow version. For:
- **Training code and datasets**
- **TensorFlow implementation** 
- **Weight conversion utilities**
- **Research replication**

Please visit the original repository: **[soCzech/TransNetV2](https://github.com/soCzech/TransNetV2)**

## Credits

### Original Work

This PyTorch implementation is based on the original TensorFlow TransNet V2 by Tomáš Souček and Jakub Lokoč.

If found useful, please cite the original work:

```bibtex
@article{soucek2020transnetv2,
    title={TransNet V2: An effective deep network architecture for fast shot transition detection},
    author={Sou{\v{c}}ek, Tom{\'a}{\v{s}} and Loko{\v{c}}, Jakub},
    year={2020},
    journal={arXiv preprint arXiv:2008.04838},
}
```

### PyTorch Implementation

This production-ready PyTorch package was developed by [Your Name] with significant improvements including:
- Complete PyTorch reimplementation for inference
- Cross-platform device support (CPU, CUDA, MPS)
- Command-line interface
- Package distribution and installation
- Comprehensive testing and error handling

### Related Papers

- ACM Multimedia paper of the older version: [A Framework for Effective Known-item Search in Video](https://dl.acm.org/doi/abs/10.1145/3343031.3351046)
- The older version paper: [TransNet: A deep network for fast detection of common shot transitions](https://arxiv.org/abs/1906.03363)

## License

MIT License

Original work Copyright (c) 2020 Tomáš Souček, Jakub Lokoč  
PyTorch implementation Copyright (c) 2025 Allen Day

See the original [TransNetV2 repository](https://github.com/soCzech/TransNetV2) for the original license.
