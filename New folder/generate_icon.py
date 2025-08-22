from PIL import Image


def create_ico_from_png(png_path: str, ico_path: str) -> None:
    image = Image.open(png_path).convert("RGBA")
    # Generate multiple sizes for best Windows icon quality
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    image.save(ico_path, sizes=sizes)


if __name__ == "__main__":
    create_ico_from_png("images_chess/wK.png", "chess.ico")


