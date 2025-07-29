# RemoveBG CLI

A Python command-line tool for background removal from images and videos.

## Installation

```bash
pip install snapbox-api
```

## Usage

1. Process a single image:
```bash
snapbox-api image -i "input.jpg" -o "output.png"
```

2. Process a video:
```bash
snapbox-api video -i "input.mp4" -o "output.mp4"
```

3. Extract video mask only:
```bash
snapbox-api video -i "input.mp4" -mk -o "output.mp4"
```

## Requirements

- Python 3.8 or higher
- Dependencies are automatically installed with the package:
  - Pillow (for image processing)
  - rembg (for background removal)
  - OpenCV (for video processing)
  - NumPy (for array operations)

## License

MIT License 