import pathlib
import sys
import tomllib

from setuptools import setup

WORK_DIR = pathlib.Path(__file__).parent

# Check python version
MINIMAL_PY_VERSION = (3, 10, 8)
if sys.version_info < MINIMAL_PY_VERSION:
    raise RuntimeError(
        "aiogram works only with Python {}+".format(
            ".".join(map(str, MINIMAL_PY_VERSION))
        )
    )


def get_description() -> str:
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()


def get_meta_info() -> dict:
    try:
        with open("pyproject.toml", "rb") as f:
            return tomllib.load(f)
    except IndexError:
        raise RuntimeError("Unable to determine version.")


project_meta = get_meta_info()
project_dir = project_meta["project"]["name"]

setup(
    license="MIT",
    name=project_meta["project"]["name"],
    version=project_meta["tool"]["commitizen"]["version"],
    author=project_meta["project"]["authors"][0]["name"],
    author_email=project_meta["project"]["authors"][0]["email"],
    description=project_meta["project"]["description"],
    long_description=get_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Frndz-org/rekonify-python-sdk",
    download_url=(
        "https://github.com/Frndz-org/rekonify-python-sdk/archive/refs/tags/"
        f"{project_meta["tool"]["commitizen"]["version"]}.tar.gz"
    ),
    project_urls={
        "Documentation": "https://github.com/Frndz-org/rekonify-python-sdk/README.md",
        "Source": "https://github.com/Frndz-org/rekonify-python-sdk",
        "Bug Tracker": "https://github.com/Frndz-org/rekonify-python-sdk/issues",
    },
    keywords=project_meta["project"]["keywords"],
    classifiers=project_meta["project"]["classifiers"],
    include_package_data=False,
    python_requires=">=3.10.8",
    install_requires=project_meta["project"]["dependencies"],
)
