from setuptools import setup, find_packages

setup(
    name="divami_lib",
    version="0.1",
    packages=find_packages(),
    # package_dir={"": "src"},
    install_requires=[],
    entry_points={
        "console_scripts": [
            "hello_world=divami_lib.y:hello_world",
        ],
    },
    python_requires=">=3.8",
    author="Yeshwanth",
    description="A command-line todo tracker application",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
