import typer
import cv2
from pathlib import Path
from loguru import logger
from prompt_toolkit.shortcuts import ProgressBar
from crop_yolo_cli.core.base import YoloCropperBase

app = typer.Typer()


class SingleCropper(YoloCropperBase):
    """Single person cropper - crops only the largest person in each image."""
    
    def process_person_boxes(self, person_boxes, image, img_path: Path, input_dir: Path, output_dir: Path):
        """Process person boxes by selecting the largest one."""
        # Get the box with the largest area
        largest_box = max(person_boxes, key=lambda box: (
            box.xyxy[0][2] - box.xyxy[0][0]) * (box.xyxy[0][3] - box.xyxy[0][1]))
        
        # Calculate cropping coordinates
        x1, y1, x2, y2 = self.calculate_cropping_coords(largest_box, image.shape)
        
        # Crop the image
        cropped_image = self.crop_image(image, x1, y1, x2, y2)
        
        # Save the cropped image
        relative_path = img_path.relative_to(input_dir)
        output_path = output_dir / relative_path.parent / f"{img_path.stem}_cropped{img_path.suffix}"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), cropped_image)
        return True

    def run_with_progress(self):
        """Run with progress bar for single processing."""
        # Load the model
        self.load_model()
        
        # Get input directory
        input_dir = self.get_input_directory()
        
        # Setup directories
        input_dir, output_dir = self.setup_directories(input_dir)
        
        # Get image paths
        images_paths = self.get_image_paths(input_dir)
        
        typer.echo(f"Found {len(images_paths)} images to process.")
        
        # Set up logging
        logger.add("detection.log", rotation="1 MB")
        
        # Process images with progress bar
        processed_count = 0
        failed_count = 0
        
        with ProgressBar() as pb:
            for img_path in pb(images_paths, label="Processing images"):
                if self.process_image(img_path, input_dir, output_dir):
                    processed_count += 1
                else:
                    failed_count += 1
        
        # Report results
        typer.echo(f"Processing finished! Successfully processed {processed_count} images. Failed to process {failed_count} images.")
        typer.echo(f"Images with no person detected: {failed_count}")
        typer.echo(f"These images have been saved in the 'no-person' subdirectory.")


@app.command()
def single(
    margin_percentage: int = typer.Option(3, help="Margin percentage for bounding box (default: 3, recommended range: 0-10)"),
    model_size: int = typer.Option(640, help="Model size (default: 640, recommended: 320, 640, or 1280)"),
    model: str = typer.Option(
        None,
        help="yolov12 model to use (options: yolov12x.pt, yolov12m.pt, yolov12s.pt). If not specified, uses first model found in ~/yolov12/"
    ),
    recursive: bool = typer.Option(False, help="Search for images recursively")
):
    """Crop images with single person detection (largest person only)."""
    # Create a dummy cropper instance to access the model_callback method
    dummy_cropper = SingleCropper()
    
    # If model is provided, validate it
    if model:
        model = dummy_cropper.model_callback(model)
    
    cropper = SingleCropper(
        margin_percentage=margin_percentage,
        model_size=model_size,
        model=model,
        recursive=recursive
    )
    cropper.run_with_progress()


if __name__ == "__main__":
    app()
