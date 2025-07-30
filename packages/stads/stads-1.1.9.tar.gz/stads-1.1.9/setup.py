from setuptools import setup, find_packages
import os

def parse_requirements(filename):
    here = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(here, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

modules = [
    "config",
    "evaluation",
    "image_processing",
    "interpolator",
    "microscope",
    "random_sampler",
    "read_images",
    "stads",
    "stads_helpers",
    "stratified_sampler",
    "stratified_sampler_helpers",
    "utility_functions",
]

setup(
    name="stads",
    version='1.1.9',
    author='Akarsh Bharadwaj',
    author_email="akarsh_sudheendra.bharadwaj@dfki.de",
    description='a spatiotemporal statistics-based adaptive sampling algorithm',
    package_dir={"": "src"},
    py_modules=modules,
    packages=find_packages(where="src"),
    package_data={
        "stads.ground_truth": ["*.mp4"],
    },
    include_package_data=True,
    url="https://github.com/bharadwajakarsh/stads_adaptive_sampler",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    install_requires=parse_requirements("requirements.txt"),
    python_requires=">=3.8"
)
