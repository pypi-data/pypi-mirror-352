from setuptools import setup, find_packages

setup(
    name="snapbox-api",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "pillow>=11.2.0",
        "numpy>=2.0.0",
        "opencv-python>=4.11.0",
        "torch>=2.0.0",
        "transparent-background>=1.2.4",
        "fastapi>=0.100.0",
        "python-multipart>=0.0.6",
    ],
    extras_require={
        'dev': [
            'pytest',
            'black',
            'flake8',
        ],
    },
    entry_points={
        'console_scripts': [
            'snapbox-api=snapbox_api.cli:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A background removal CLI tool using InSPyReNet model",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vinacogroup/snapbox-effect-api.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 