from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="object_tracking",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20",
        "opencv-python>=4.5.0"
    ],
    author="Kuntal Pal",
    author_email="kuntal.pal7550@gmail.com",
    url="https://www.linkedin.com/in/kuntalpal?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="object tracking unique ID assignment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    zip_safe=False,
    description="A simple tracking package for assigning unique IDs to detected objects.",
)
