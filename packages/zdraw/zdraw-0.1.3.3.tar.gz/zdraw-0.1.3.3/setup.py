from setuptools import setup, find_packages

setup(
    name="zdraw",
    version="0.1.3.3",
    author="Zaid Aslam",
    author_email="zaidmughal46@gmail.com",
    description="A library for drawing custom bounding boxes with rounded corners and zones.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    # url="https://your-private-repo-url-or-none",  # Optional
    packages=find_packages(),
    install_requires=[
        "numpy",
        "opencv-python"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Update license if needed
        "Operating System :: OS Independent",
    ],
)

