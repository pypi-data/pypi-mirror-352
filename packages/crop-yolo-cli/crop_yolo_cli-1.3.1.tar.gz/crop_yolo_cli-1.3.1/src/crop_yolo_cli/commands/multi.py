import typer
import cv2
from pathlib import Path
from crop_yolo_cli.core.base import YoloCropperBase

app = typer.Typer()

class MultiCropper(YoloCropperBase):
    """Multi person cropper - crops all detected persons in each image."""
    
    def process_person_boxes(self, person_boxes, image, img_path: Path, input_dir: Path, output_dir: Path):
        """Process person boxes by saving all detected persons."""
        for i, box in enumerate(person_boxes):
            # Calculate cropping coordinates
            x1, y1, x2, y2 = self.calculate_cropping_coords(box, image.shape)
            
            # Crop the image
            cropped_image = self.crop_image(image, x1, y1, x2, y2)
            
            # Save the cropped image
            relative_path = img_path.relative_to(input_dir)
            output_path = output_dir / relative_path.parent / f"{img_path.stem}_cropped_person_{i}{img_path.suffix}"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(output_path), cropped_image)
        return True

@app.command()
def multi(
    margin_percentage: int = typer.Option(3, help="Margin percentage for bounding box (default: 3, recommended range: 0-10)"),
    model_size: int = typer.Option(640, help="Model size (default: 640, recommended: 320, 640, or 1280)"),
    model: str = typer.Option(
        None,
        help="YOLOv12 model to use (e.g., yolov12n, yolov12s, yolov12m, yolov12l, yolov12x). If not specified, uses the best available model from ~/yolov12/"
    ),
    recursive: bool = typer.Option(False, help="Search for images recursively"),
    list_models: bool = typer.Option(False, "--list-models", help="List available models and exit")
):
    """Crop images with multi-person detection (all detected persons)."""
    
    # Create a cropper instance to access model methods
    cropper = MultiCropper()
    
    # If user wants to list models, show them and exit
    if list_models:
        cropper.display_available_models()
        return
    
    # If model is provided, validate it
    if model:
        model = cropper.validate_model_path(model)
    
    # Create the final cropper with all parameters
    cropper = MultiCropper(
        margin_percentage=margin_percentage,
        model_size=model_size,
        model=model,
        recursive=recursive
    )
    cropper.run()

if __name__ == "__main__":
    app()
