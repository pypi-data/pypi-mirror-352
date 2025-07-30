import os
import cv2
import torch
import numpy as np
from pathlib import Path
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
import typer
from ultralytics import YOLO
from abc import ABC, abstractmethod


class YoloCropperBase(ABC):
    """Base class for YOLO-based image cropping functionality."""
    
    def __init__(self, margin_percentage: int = 3, model_size: int = 640, model: str = None, recursive: bool = False):
        self.margin_percentage = margin_percentage
        self.model_size = model_size
        self.recursive = recursive
        self.model = model or self.get_default_model_path()
        self.yolo_model = None
        
    def get_default_model_path(self):
        """Get the default model path from ~/yolov12 directory."""
        home = Path.home()
        yolo_dir = home / "yolov12"
        models = list(yolo_dir.glob("*.pt"))
        if models:
            return str(models[0])
        return "yolov12x.pt"  # fallback to default if no models found

    def model_callback(self, value: str):
        """Validate and return the full path to the model."""
        if value not in ["yolov12x.pt", "yolov12m.pt", "yolov12s.pt"]:
            raise typer.BadParameter("Invalid model choice")
        home = Path.home()
        return str(home / "yolov12" / value)

    def load_model(self):
        """Load the YOLO model."""
        self.yolo_model = YOLO(self.model)
        self.yolo_model.verbose = False  # Disable verbose output from YOLO

    def get_input_directory(self):
        """Prompt user to select input directory."""
        input_dir_input = prompt("Select Input Directory: ", completer=PathCompleter())
        if not input_dir_input:
            typer.echo("No directory selected, exiting...")
            raise typer.Exit()
        return Path(input_dir_input)

    def setup_directories(self, input_dir: Path):
        """Setup input and output directories."""
        output_dir = input_dir / "cropped"
        output_dir.mkdir(parents=True, exist_ok=True)
        return input_dir, output_dir

    def get_image_paths(self, input_dir: Path):
        """Get list of image paths based on recursive flag."""
        if self.recursive:
            images_paths = list(input_dir.rglob("*.jpg")) + list(input_dir.rglob("*.jpeg")) + list(input_dir.rglob("*.png"))
        else:
            images_paths = list(input_dir.glob("*.jpg")) + list(input_dir.glob("*.jpeg")) + list(input_dir.glob("*.png"))
        return images_paths

    def load_and_detect(self, img_path: Path):
        """Load image and run YOLO detection."""
        # Load the image
        image = cv2.imread(str(img_path))
        if image is None:
            typer.echo(f"Failed to load image: {img_path}")
            return None, None
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect objects in the image
        results = self.yolo_model(image_rgb, imgsz=self.model_size)
        
        # Check if results is a list and take the first item if so
        if isinstance(results, list):
            results = results[0]
        
        # Check if 'boxes' attribute exists
        if not hasattr(results, 'boxes'):
            typer.echo(f"No detection results for {img_path}")
            return image, None
        
        # Class 0 is typically person
        person_boxes = [box for box in results.boxes if box.cls == 0]
        return image, person_boxes

    def calculate_cropping_coords(self, box, image_shape):
        """Calculate cropping coordinates with margin."""
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        
        # Calculate the margin
        width = x2 - x1
        height = y2 - y1
        margin_x = int(width * self.margin_percentage / 100)
        margin_y = int(height * self.margin_percentage / 100)
        
        # Add the margin to the bounding box
        x1 = max(0, x1 - margin_x)
        y1 = max(0, y1 - margin_y)
        x2 = min(image_shape[1], x2 + margin_x)
        y2 = min(image_shape[0], y2 + margin_y)
        
        return x1, y1, x2, y2

    def crop_image(self, image, x1, y1, x2, y2):
        """Crop the image using the provided coordinates."""
        return image[y1:y2, x1:x2]

    def save_no_person_image(self, image, img_path: Path, input_dir: Path, output_dir: Path):
        """Save image when no person is detected."""
        typer.echo(f"No person detected in {img_path}")
        no_person_dir = output_dir / "no-person"
        no_person_dir.mkdir(parents=True, exist_ok=True)
        relative_path = img_path.relative_to(input_dir)
        output_path = no_person_dir / relative_path.name
        cv2.imwrite(str(output_path), image)

    @abstractmethod
    def process_person_boxes(self, person_boxes, image, img_path: Path, input_dir: Path, output_dir: Path):
        """Process detected person boxes. Must be implemented by subclasses."""
        pass

    def process_image(self, img_path: Path, input_dir: Path, output_dir: Path):
        """Process a single image."""
        image, person_boxes = self.load_and_detect(img_path)
        
        if image is None:
            return False
        
        if person_boxes:
            return self.process_person_boxes(person_boxes, image, img_path, input_dir, output_dir)
        else:
            self.save_no_person_image(image, img_path, input_dir, output_dir)
            return False

    def run(self):
        """Main execution method."""
        # Load the model
        self.load_model()
        
        # Get input directory
        input_dir = self.get_input_directory()
        
        # Setup directories
        input_dir, output_dir = self.setup_directories(input_dir)
        
        # Get image paths
        images_paths = self.get_image_paths(input_dir)
        
        typer.echo(f"Found {len(images_paths)} images to process.")
        
        # Process images
        processed_count = 0
        failed_count = 0
        
        for img_path in images_paths:
            if self.process_image(img_path, input_dir, output_dir):
                processed_count += 1
            else:
                failed_count += 1
        
        # Report results
        typer.echo(f"Processing finished! Successfully processed {processed_count} images. Failed to process {failed_count} images.")
        typer.echo(f"Images with no person detected: {failed_count}")
        typer.echo(f"These images have been saved in the 'no-person' subdirectory.") 