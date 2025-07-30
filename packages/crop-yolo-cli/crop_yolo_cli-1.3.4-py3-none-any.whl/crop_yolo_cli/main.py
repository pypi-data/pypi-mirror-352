import typer
from crop_yolo_cli.commands.single import app as single_app
from crop_yolo_cli.commands.multi import app as multi_app

app = typer.Typer(help="YOLO-based image cropping tool for person detection")

app.add_typer(single_app, name="single", help="Crop single person (largest) from images")
app.add_typer(multi_app, name="multi", help="Crop all detected persons from images")


if __name__ == "__main__":
    app()
