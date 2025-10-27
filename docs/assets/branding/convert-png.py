from pathlib import Path

from cairosvg import svg2png

FOLDER_SVG = Path("./svg")
FOLDER_PNG = Path("./png")
DPI = 96  # default
DPI *= 3
FOLDER_PNG.mkdir(exist_ok=True)


def main():
    for file in FOLDER_SVG.glob("*.svg"):
        with open(file) as f:
            svg_content = f.read()

        output_file = FOLDER_PNG / (file.stem + ".png")
        svg2png(bytestring=svg_content, write_to=str(output_file), dpi=DPI)


if __name__ == "__main__":
    main()
