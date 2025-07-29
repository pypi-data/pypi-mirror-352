from fontTools.subset import main as pyftsubset
from fontTools import ttLib
from string import Template
import hashlib
import base64
import click
import os

CSS_TEMPLATE = Template(
    """\
@font-face {
  font-family: "${font_family}";
  font-style: ${font_style};
  font-weight: ${font_weight};
  src: url(http://localhost:8080/output/${font_filename}) format("${font_format}");
  unicode-range: ${unicode_range};
}
"""
)


def get_font_info(fontPath: str) -> dict:
    font = ttLib.TTFont(fontPath)
    return {
        "font_family": font["name"].names[1],
        "font_weight": font["OS/2"].usWeightClass,
    }


def unique_filename(unicode_range: str) -> str:
    return (
        base64.urlsafe_b64encode(hashlib.sha1(unicode_range.encode()).digest())
        .decode("utf-8")
        .replace("=", "")
    )


def generate_subset_font(
    font_file: str, unicode_range: str, font_format: str, output_dir: str, force: bool
) -> str:
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    filename = ("{}.{}").format(unique_filename(unicode_range), font_format)
    output_file = ("{}/{}").format(output_dir, filename)

    if not force and os.path.exists(output_file):
        print("[INFO] skip: " + output_file)
        return filename

    pyftsubset(
        [
            font_file,
            "--unicodes=" + unicode_range,
            "--layout-features=*",
            "--flavor=" + font_format,
            "--output-file=" + output_file,
        ]
    )
    print("[INFO] generate: " + output_file)
    return filename


@click.command()
@click.argument("font_file", type=click.Path(exists=True))
@click.option(
    "--unicode_ranges_file", type=click.Path(exists=True), default="unicode_ranges.txt"
)
@click.option(
    "--css_template_file",
    type=click.Path(exists=True),
)
@click.option("--output_dir", type=click.Path(), default="output")
@click.option("--font_format", type=click.Choice(["woff2", "woff"]), default="woff2")
@click.option("--font_face_css", type=click.Path(), default="font-face.css")
@click.option("--force", is_flag=True, default=False)
def split(
    font_file: str,
    unicode_ranges_file: str,
    css_template_file: str,
    output_dir: str,
    font_format: str,
    font_face_css: str,
    force: bool,
):
    if not os.path.exists(font_file):
        print("[ERROR] font file not found: " + font_file)
        return

    if not os.path.exists(unicode_ranges_file):
        print("[ERROR] unicode ranges file not found: " + unicode_ranges_file)
        return

    with open(unicode_ranges_file, "r") as file:
        content = file.read()
        unicode_ranges = content.split("\n")

    if unicode_ranges == [""]:
        print("[ERROR] No unicode ranges found in the file")
        return

    print("[INFO] unicode-range: {} ranges found".format(len(unicode_ranges)))

    if css_template_file and os.path.exists(css_template_file):
        print("[INFO] Using custom css template: " + css_template_file)
        with open(css_template_file, "r") as file:
            css_template = Template(file.read())
    else:
        print("[INFO] Using default css template")
        css_template = CSS_TEMPLATE

    font_info = get_font_info(font_file)
    font_family = str(font_info["font_family"])
    font_weight = str(font_info["font_weight"])

    print("[INFO] font-family: " + font_family + ", font-weight: " + font_weight)

    font_faces = []
    for unicode_range in unicode_ranges:
        subset_font_filename = generate_subset_font(
            font_file, unicode_range, font_format, output_dir, force
        )

        font_faces.append(
            css_template.substitute(
                font_family=font_family,
                font_style="normal",
                font_weight=font_weight,
                font_filename=subset_font_filename,
                font_format=font_format,
                unicode_range=unicode_range,
            )
        )

    print("[INFO] generate CSS: " + output_dir + "/" + font_face_css)
    with open(output_dir + "/" + font_face_css, "w") as file:
        file.write("\n".join(font_faces))

    print("[INFO] success to generate")
