from setuptools import setup, find_packages

setup(
    name="deplace-cli",
    version="0.1.54",
    packages=find_packages(),
    install_requires=[
        "azure-storage-blob",
        "opencv-python",
        "numpy",
        "pycocotools",
        "tqdm"
    ],
    entry_points={
        "console_scripts": [
            "deplace=deplacecli.cli:main"
        ],
    },
    author="Deplace AI",
    description="A CLI tool to access Deplace Datasets.",
)