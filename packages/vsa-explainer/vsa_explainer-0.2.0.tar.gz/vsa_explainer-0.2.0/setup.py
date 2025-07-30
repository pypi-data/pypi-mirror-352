from setuptools import setup, find_packages
import pathlib

# read the README file
here = pathlib.Path(__file__).parent
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="vsa_explainer",
    version="0.2.0",
    description="Visualize and explain RDKit VSA descriptor contributions",
    
    long_description=long_description,
    long_description_content_type="text/markdown",  # tells PyPI to render Markdown

    
    author="Srijit Seal",
    author_email="seal@understanding.bio",
    license="MIT",
    packages=find_packages(),  # finds vsa_explainer/
    
    install_requires=[
        "numpy>=1.18",
        "matplotlib>=3.0",
        "rdkit",            # see rdkit install instructions for your platform
        "ipython",          # for IPython.display.SVG
    ],

    extras_require={
       "dev": ["pytest"],
    },
    tests_require=["pytest"],
    
    entry_points={
        "console_scripts": [
            "vsa-explain=vsa_explainer.explainer:visualize_vsa_contributions",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    url='https://github.com/srijitseal/vsa_explainer',
)