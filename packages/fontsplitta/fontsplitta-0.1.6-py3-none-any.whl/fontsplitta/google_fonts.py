import re
import urllib.request
import click


def extract_unicode_ranges(text):
    pattern = r"^\s*unicode-range:\s+([^;]+);"
    matches = re.findall(pattern, text, flags=re.MULTILINE)
    matches = [i.upper() for i in matches]
    return matches


@click.command()
@click.option("--output_file", type=click.Path(), default="unicode_ranges.txt")
@click.option(
    "--css_url",
    type=str,
    default="https://fonts.googleapis.com/css2?family=Noto+Sans+JP",
)
@click.option(
    "--user_agent",
    type=str,
    default="Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0",
)
def get_unicode_ranges_from_google_fonts(
    output_file: str, css_url: str, user_agent: str
):
    print(f"Download: {css_url}")
    req = urllib.request.Request(css_url, headers={"User-Agent": user_agent})

    with urllib.request.urlopen(req) as response:
        if response.getcode() != 200:
            raise (f"Failed to download: {css_url}")
        text = response.read().decode("utf-8")

    unicode_ranges = extract_unicode_ranges(text)
    with open(output_file, "w") as file:
        file.write("\n".join(unicode_ranges))
        print(f"Success to generate: {output_file}")
