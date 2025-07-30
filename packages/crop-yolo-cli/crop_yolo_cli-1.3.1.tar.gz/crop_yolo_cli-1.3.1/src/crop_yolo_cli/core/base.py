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
        
    def get_available_models(self):
        """Get list of available YOLOv12 models."""
        home = Path.home()
        yolo_dir = home / "yolov12"
        
        if not yolo_dir.exists():
            typer.echo(f"Warning: YOLOv12 directory not found at {yolo_dir}")
            typer.echo("Please create ~/yolov12/ directory and place your YOLOv12 models there")
            return []
        
        models = list(yolo_dir.glob("*.pt"))
        return sorted([model.name for model in models])
        
    def get_default_model_path(self):
        """Get the default model path from ~/yolov12 directory."""
        available_models = self.get_available_models()
        
        if not available_models:
            typer.echo("No YOLOv12 models found in ~/yolov12/")
            typer.echo("Please download YOLOv12 models and place them in ~/yolov12/")
            typer.echo("Available models: yolov12n.pt, yolov12s.pt, yolov12m.pt, yolov12l.pt, yolov12x.pt")
            raise typer.Exit(1)
        
        home = Path.home()
        yolo_dir = home / "yolov12"
        
        # Prefer models in this order: x > l > m > s > n
        preferred_order = ["yolov12x.pt", "yolov12l.pt", "yolov12m.pt", "yolov12s.pt", "yolov12n.pt"]
        
        for preferred in preferred_order:
            if preferred in available_models:
                return str(yolo_dir / preferred)
        
        # If no preferred model found, use the first available
        return str(yolo_dir / available_models[0])

    def validate_model_path(self, model_name: str):
        """Validate and return the full path to the model."""
        if not model_name.endswith('.pt'):
            model_name += '.pt'
            
        home = Path.home()
        yolo_dir = home / "yolov12"
        model_path = yolo_dir / model_name
        
        if not model_path.exists():
            available_models = self.get_available_models()
            typer.echo(f"Error: Model '{model_name}' not found in {yolo_dir}")
            if available_models:
                typer.echo(f"Available models: {', '.join(available_models)}")
            else:
                typer.echo("No models found in ~/yolov12/")
            raise typer.BadParameter(f"Model '{model_name}' not found")
        
        return str(model_path)

    def model_callback(self, value: str):
        """Validate and return the full path to the model."""
        if value is None:
            return None
        return self.validate_model_path(value)

    def display_available_models(self):
        """Display available models to the user."""
        available_models = self.get_available_models()
        if available_models:
            typer.echo(f"Available YOLOv12 models in ~/yolov12/: {', '.join(available_models)}")
        else:
            typer.echo("No YOLOv12 models found in ~/yolov12/")

    def load_model(self):
        """Load the YOLO model."""
        typer.echo(f"Loading model: {Path(self.model).name}")
        try:
            self.yolo_model = YOLO(self.model)
            self.yolo_model.verbose = False  # Disable verbose output from YOLO
            typer.echo("✓ Model loaded successfully")
        except Exception as e:
            typer.echo(f"✗ Failed to load model: {e}")
            typer.echo("This might be due to:")
            typer.echo("1. Incompatible ultralytics version")
            typer.echo("2. Corrupted model file")
            typer.echo("3. Wrong model format")
            typer.echo("\nTry:")
            typer.echo("pip install ultralytics==8.3.149")
            typer.echo("Or download a fresh YOLOv12 model")
            raise typer.Exit(1)

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
        
        try:
            # Detect objects in the image
            results = self.yolo_model(image_rgb, imgsz=self.model_size)
            
            # Check if results is a list and take the first item if so
            if isinstance(results, list):
                results = results[0]
            
            # Check if 'boxes' attribute exists
            if not hasattr(results, 'boxes') or results.boxes is None:
                return image, []
            
            # Class 0 is typically person
            person_boxes = [box for box in results.boxes if box.cls == 0]
            return image, person_boxes
            
        except Exception as e:
            typer.echo(f"Detection failed for {img_path}: {e}")
            return image, []

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
        # Display available models
        self.display_available_models()
        
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