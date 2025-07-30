import os
import cv2
import torch
import numpy as np
from pathlib import Path
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter, WordCompleter
import typer
from ultralytics import YOLO
from ultralytics.utils import LOGGER as ultralytics_logger # For more detailed logging
import logging # For suppressing ultralytics logs
from abc import ABC, abstractmethod


class YoloCropperBase(ABC):
    """Base class for YOLO-based image cropping functionality."""
    
    def __init__(self, margin_percentage: int = 3, model_size: int = 640, model: str = None, recursive: bool = False):
        self.margin_percentage = margin_percentage
        self.model_size = model_size
        self.recursive = recursive
        self.model = model # Will be validated and resolved to full path in setup_model
        self.yolo_model = None
        # Suppress less critical ultralytics logs, allow critical ones for errors
        ultralytics_logger.setLevel(logging.WARNING)
        
    def check_ultralytics_version(self):
        """Check ultralytics version and provide general advice."""
        try:
            import ultralytics
            version = ultralytics.__version__
            typer.echo(f"Ultralytics version: {version}")
            typer.echo("ℹ️  For YOLOv12 models, compatibility can vary. Ensure your Ultralytics version is recent.")
            typer.echo("   If you encounter issues like 'AttributeError' for model layers (e.g., AAttn, CKA, Focus):")
            typer.echo("   1. Try updating: pip install -U ultralytics")
            typer.echo("   2. Check the source of your YOLOv12 model for specific version recommendations.")
            typer.echo("   3. Consider using a stable YOLOv8 model as a fallback.")
        except Exception as e:
            typer.echo(f"Could not check ultralytics version: {e}")
        
    def get_available_models(self):
        """Get list of available YOLO models from ~/yolov12/ and ~/yolov8/."""
        home = Path.home()
        model_dirs = [home / "yolov12", home / "yolov8"]
        all_models = []
        found_dirs = False

        for yolo_dir in model_dirs:
            if yolo_dir.exists():
                found_dirs = True
                models = list(yolo_dir.glob("*.pt"))
                all_models.extend([model.name for model in models])
            else:
                typer.echo(f"Info: Directory not found, skipping: {yolo_dir}")
        
        if not found_dirs:
            typer.echo(f"Warning: Neither ~/yolov12/ nor ~/yolov8/ directories found.")
        elif not all_models:
            typer.echo(f"Warning: No .pt models found in existing ~/yolov12/ or ~/yolov8/ directories.")
        
        if not all_models:
             typer.echo("Please place YOLOv12 or YOLOv8 models in their respective directories (e.g., ~/yolov12/yolov12n.pt).")

        return sorted(list(set(all_models))) # Unique sorted models
        
    def get_default_model_path(self):
        """Get the default model path from ~/yolov12/ or ~/yolov8/."""
        available_models = self.get_available_models()
        if not available_models:
            typer.echo("No YOLO models found. Please add models to ~/yolov12/ or ~/yolov8/")
            raise typer.Exit(1)
        
        home = Path.home()
        # Prefer models in this order: x > l > m > s > n, check both dirs
        preferred_order = [
            "yolov12x.pt", "yolov8x.pt", "yolov12l.pt", "yolov8l.pt", 
            "yolov12m.pt", "yolov8m.pt", "yolov12s.pt", "yolov8s.pt", 
            "yolov12n.pt", "yolov8n.pt"
        ]
        
        for preferred_name in preferred_order:
            if preferred_name in available_models:
                path_v12 = home / "yolov12" / preferred_name
                path_v8 = home / "yolov8" / preferred_name
                if path_v12.exists(): return str(path_v12)
                if path_v8.exists(): return str(path_v8)
        
        # Fallback to the first model found in the list if no preferred one matches
        # This should use the actual found model name from available_models
        first_available_model_name = available_models[0]
        path_v12_fallback = home / "yolov12" / first_available_model_name
        path_v8_fallback = home / "yolov8" / first_available_model_name
        if path_v12_fallback.exists(): return str(path_v12_fallback)
        if path_v8_fallback.exists(): return str(path_v8_fallback)
        
        typer.echo("Error: Could not determine default model path even though models are listed as available.")
        typer.echo("Please check directory structures and permissions for ~/yolov12/ and ~/yolov8/")
        raise typer.Exit(1)

    def interactive_model_selection(self):
        available_models = self.get_available_models()
        if not available_models:
            typer.echo("No YOLO models found in ~/yolov12/ or ~/yolov8/. Please add some .pt files.")
            raise typer.Exit(1)
        
        typer.echo("\nAvailable YOLO models (from ~/yolov12/ and ~/yolov8/):")
        model_info = {
            "yolov12n.pt": "Nano (YOLOv12) - Fastest, basic accuracy",
            "yolov12s.pt": "Small (YOLOv12) - Fast, good accuracy", 
            "yolov12m.pt": "Medium (YOLOv12) - Balanced speed/accuracy",
            "yolov12l.pt": "Large (YOLOv12) - Slower, high accuracy",
            "yolov12x.pt": "Extra Large (YOLOv12) - Slowest, highest accuracy",
            "yolov8n.pt": "Nano (YOLOv8) - Very Fast, good for edge",
            "yolov8s.pt": "Small (YOLOv8) - Fast, efficient",
            "yolov8m.pt": "Medium (YOLOv8) - Balanced",
            "yolov8l.pt": "Large (YOLOv8) - Accurate, for general use",
            "yolov8x.pt": "Extra Large (YOLOv8) - Most accurate, resource-intensive"
        }
        
        for i, model_name in enumerate(available_models, 1):
            description = model_info.get(model_name, "Custom/Unknown model")
            typer.echo(f"  {i}. {model_name} ({('YOLOv12' if 'v12' in model_name else 'YOLOv8' if 'v8' in model_name else 'Unknown Type')}) - {description}")
        
        model_names_completion = [name.replace('.pt', '') for name in available_models] + available_models
        completer = WordCompleter(model_names_completion, ignore_case=True)
        
        while True:
            try:
                choice_str = prompt(f"\nSelect model (1-{len(available_models)} or name, e.g., yolov12n or 3): ", completer=completer).strip()
                selected_model_name = ""

                if choice_str.isdigit():
                    index = int(choice_str) - 1
                    if 0 <= index < len(available_models):
                        selected_model_name = available_models[index]
                    else:
                        typer.echo(f"Invalid number. Please choose between 1 and {len(available_models)}."); continue
                else:
                    temp_name = choice_str if choice_str.endswith('.pt') else choice_str + '.pt'
                    if temp_name in available_models:
                        selected_model_name = temp_name
                    else:
                        typer.echo(f"Model '{temp_name}' not found. Available: {', '.join(available_models)}"); continue
                
                home = Path.home()
                path_v12 = home / "yolov12" / selected_model_name
                path_v8 = home / "yolov8" / selected_model_name
                if path_v12.exists(): return str(path_v12)
                if path_v8.exists(): return str(path_v8)
                typer.echo(f"Error: Selected model '{selected_model_name}' path could not be resolved."); continue
            except KeyboardInterrupt:
                typer.echo("\nExiting..."); raise typer.Exit()
            except Exception: typer.echo("Invalid input. Please try again.")

    def validate_model_path(self, model_name_arg: str):
        model_full_name = model_name_arg if model_name_arg.endswith('.pt') else model_name_arg + '.pt'
        home = Path.home()
        paths_to_check = [home / "yolov12" / model_full_name, home / "yolov8" / model_full_name]
        for path in paths_to_check:
            if path.exists(): return str(path)
        
        available = self.get_available_models()
        typer.echo(f"Error: Model '{model_name_arg}' (resolved to '{model_full_name}') not found in ~/yolov12/ or ~/yolov8/")
        if available: typer.echo(f"Available models: {', '.join(available)}")
        raise typer.BadParameter(f"Model '{model_name_arg}' not found. Use --list-models to see available ones.")

    def model_callback(self, value: str):
        if value is None: return None
        return self.validate_model_path(value)

    def display_available_models(self):
        models = self.get_available_models()
        if models: typer.echo(f"Available models in ~/yolov12/ & ~/yolov8/: {', '.join(models)}")
        else: typer.echo("No models found in ~/yolov12/ or ~/yolov8/.")

    def setup_model(self):
        if self.model is None: # No --model argument passed
            typer.echo("No model specified via --model, prompting for interactive selection...")
            self.model = self.interactive_model_selection()
        else: # --model argument was passed, validate it (might be just name, not path)
            self.model = self.validate_model_path(self.model)
        typer.echo(f"Using model: {self.model}")

    def load_model(self):
        self.check_ultralytics_version()
        typer.echo(f"Attempting to load model: {Path(self.model).name}")
        try:
            self.yolo_model = YOLO(self.model, task='detect')
            typer.echo("Performing a quick test inference to check compatibility...")
            test_image = np.zeros((64, 64, 3), dtype=np.uint8)
            _ = self.yolo_model(test_image, imgsz=64, verbose=False)
            typer.echo("✓ Model loaded and basic inference test passed.")
        except Exception as e:
            typer.echo(f"✗ Failed to load or test model: {Path(self.model).name}")
            error_str = str(e).lower()
            known_compat_errors = [
                "'aattn' object has no attribute 'qkv'", 
                "'cka' object has no attribute 'conv_attention_list'",
                "'focus' object has no attribute 'conv'",
                "no attribute 'recompute_strict'" # Another common one
            ]
            is_known_compat_error = any(err_msg in error_str for err_msg in known_compat_errors)

            if is_known_compat_error:
                typer.echo("\nError appears to be a model architecture incompatibility with the current Ultralytics library version.")
                typer.echo("This is common with some YOLOv12 or other newer/custom YOLO variants.")
                typer.echo("\nTroubleshooting suggestions:")
                typer.echo("1. Update Ultralytics: pip install -U ultralytics")
                typer.echo("2. Try specific Ultralytics versions: pip install ultralytics==8.2.0 (or other known compatible versions for your specific model)")
                typer.echo("3. Verify your .pt model file is not corrupted and is from an official/trusted source for that YOLO variant.")
                typer.echo("4. Check the GitHub repository or source of your specific YOLOv12 model for recommended Ultralytics versions.")
                typer.echo("5. As a reliable fallback, try using a standard YOLOv8 model (e.g., yolov8n.pt) from ~/yolov8/.")
                typer.echo("6. Search for your error on Ultralytics GitHub Issues: https://github.com/ultralytics/ultralytics/issues")
            else:
                typer.echo(f"Error details: {e}")
                typer.echo("\nGeneral troubleshooting:")
                typer.echo("1. Ensure your .pt model file is valid and not corrupted.")
                typer.echo("2. Check for sufficient memory and correct CUDA/GPU driver setup if using GPU.")
            raise typer.Exit(1)

    def get_input_directory(self):
        input_dir_input = prompt("Select Input Directory: ", completer=PathCompleter(), default=str(Path.cwd()) + os.sep)
        if not input_dir_input: typer.echo("No directory selected, exiting..."); raise typer.Exit()
        return Path(input_dir_input)

    def setup_directories(self, input_dir: Path):
        output_dir = input_dir / "cropped_output"
        output_dir.mkdir(parents=True, exist_ok=True)
        return input_dir, output_dir

    def get_image_paths(self, input_dir: Path):
        patterns = ["*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp", "*.tif", "*.tiff", "*.heic", "*.heif"]
        images_paths = []
        search_method = input_dir.rglob if self.recursive else input_dir.glob
        for pattern in patterns:
            images_paths.extend(search_method(pattern.lower())) # search lowercase
            images_paths.extend(search_method(pattern.upper())) # search uppercase
        unique_paths = sorted(list(set(images_paths))) # Unique, sorted paths
        if not unique_paths:
             typer.echo(f"No supported image files found in {input_dir} (recursive={self.recursive}).")
        return unique_paths

    def load_and_detect(self, img_path: Path):
        image = cv2.imread(str(img_path))
        if image is None: 
            typer.echo(f"Warning: Failed to load image {img_path}, skipping.")
            return None, [] 
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        try:
            results = self.yolo_model(image_rgb, imgsz=self.model_size, verbose=False)
            if isinstance(results, list): results = results[0]
            if not hasattr(results, 'boxes') or results.boxes is None or len(results.boxes) == 0:
                return image, []
            # Ensure cls attribute exists and is tensor-like for comparison
            person_boxes = [box for box in results.boxes if hasattr(box, 'cls') and torch.is_tensor(box.cls) and int(box.cls[0]) == 0]
            return image, person_boxes
        except Exception as e:
            # Avoid spamming for known compatibility issues already warned about at load time
            error_str = str(e).lower()
            known_compat_errors = ["'aattn' object has no attribute 'qkv'", "'cka' object has no attribute 'conv_attention_list'", "'focus' object has no attribute 'conv'"]
            if not any(err_msg in error_str for err_msg in known_compat_errors):
                 typer.echo(f"Warning: Runtime detection error on {img_path}: {e}. Skipping detection for this image.")
            return image, []

    def calculate_cropping_coords(self, box, image_shape):
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        width, height = x2 - x1, y2 - y1
        margin_x = int(width * self.margin_percentage / 100)
        margin_y = int(height * self.margin_percentage / 100)
        x1 = max(0, x1 - margin_x); y1 = max(0, y1 - margin_y)
        x2 = min(image_shape[1], x2 + margin_x); y2 = min(image_shape[0], y2 + margin_y)
        return x1, y1, x2, y2

    def crop_image(self, image, x1, y1, x2, y2):
        return image[y1:y2, x1:x2]

    def save_no_person_image(self, image, img_path: Path, input_dir: Path, output_dir: Path):
        no_person_dir = output_dir / "no-person_or_error"
        no_person_dir.mkdir(parents=True, exist_ok=True)
        relative_path = img_path.relative_to(input_dir)
        output_path = no_person_dir / relative_path.name
        cv2.imwrite(str(output_path), image)

    @abstractmethod
    def process_person_boxes(self, person_boxes, image, img_path: Path, input_dir: Path, output_dir: Path): pass

    def process_image(self, img_path: Path, input_dir: Path, output_dir: Path):
        image, person_boxes = self.load_and_detect(img_path)
        if image is None: return False
        if person_boxes: 
            return self.process_person_boxes(person_boxes, image, img_path, input_dir, output_dir)
        else: 
            self.save_no_person_image(image, img_path, input_dir, output_dir)
            return False

    def run(self):
        self.setup_model()
        self.load_model() # This will exit if model is incompatible
        input_dir = self.get_input_directory()
        input_dir, output_dir = self.setup_directories(input_dir)
        images_paths = self.get_image_paths(input_dir)
        
        if not images_paths:
            raise typer.Exit()
            
        typer.echo(f"Found {len(images_paths)} images to process in '{input_dir}'. Output will be in '{output_dir}'.")
        processed_count, no_person_count = 0, 0
        
        # Determine label for progress bar based on subclass
        progress_label = "Processing images"
        if hasattr(self, 'run_with_progress'): # Check if it's SingleCropper
             for img_path in typer.progressbar(images_paths, label=progress_label, length=len(images_paths)):
                if self.process_image(img_path, input_dir, output_dir):
                    processed_count += 1
                else:
                    no_person_count += 1
        else: # For MultiCropper or other future direct YoloCropperBase users without specific progress
            for img_path in images_paths:
                if self.process_image(img_path, input_dir, output_dir):
                    processed_count += 1
                else:
                    no_person_count += 1
        
        typer.echo(f"\nProcessing finished!")
        typer.echo(f"  Successfully processed (persons detected and cropped): {processed_count}")
        typer.echo(f"  Images with no persons or errors during detection: {no_person_count}")
        if no_person_count > 0:
            typer.echo(f"  These original images are saved in: '{output_dir / 'no-person_or_error'}'") 