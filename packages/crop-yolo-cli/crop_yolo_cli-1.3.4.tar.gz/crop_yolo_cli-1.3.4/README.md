# YOLOv8 Person Cropping Tool

This tool uses YOLOv8 to detect and crop persons from images. It's designed to process multiple images, optionally searching recursively through directories, and can crop either the largest detected person or all detected persons in each image.

## Features

- Uses YOLOv8 for accurate person detection
- Supports multiple YOLOv8 models (yolov8x.pt, yolov8m.pt, yolov8s.pt)
- Processes images in parallel for faster execution
- Allows recursive directory search
- Option to crop all detected persons or just the largest one
- Adds customizable margin to cropped images
- Saves images with no detected persons in a separate directory
- Option to remove small images after processing

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install ultralytics rich typer opencv-python
```

3. Ensure you have the YOLOv8 models in your home directory under a `yolov8` folder.

## Usage

Run the script using the following command:

```bash
python main.py [OPTIONS]
```

### Options

- `--margin-percentage INTEGER`: Margin percentage for bounding box (default: 3, recommended range: 0-10)
- `--model-size INTEGER`: Model size (default: 640, recommended: 320, 640, or 1280)
- `--model TEXT`: YOLOv8 model to use (options: yolov8x.pt, yolov8m.pt, yolov8s.pt)
- `--recursive / --no-recursive`: Search for images recursively (default: False)
- `--crop-all / --no-crop-all`: Crop all detected persons instead of just the largest (default: False)

## How it works

1. The script prompts you to select an input directory.
2. It processes all images in the selected directory (and subdirectories if recursive option is enabled).
3. Detected persons are cropped from the images with the specified margin.
4. Cropped images are saved in a 'cropped' subdirectory within the input directory.
5. Images with no detected persons are saved in a 'no-person' subdirectory.
6. After processing, you have the option to remove small images based on a size threshold.
