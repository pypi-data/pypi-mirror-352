from pathlib import Path

from pdoc import pdoc, render

if __name__ == "__main__":
    with open("VERSION") as f:
        version = f.read()

    render.configure(
        footer_text=f"sfapp {version}",
        edit_url_map={"sfapp": "https://github.com/EtienneMR/sfapp/blob/main/sfapp/"},
    )

    pdoc(Path("sfapp"), output_directory=Path("docs/dist"))
