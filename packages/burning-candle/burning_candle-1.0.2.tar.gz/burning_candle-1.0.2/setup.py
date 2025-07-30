from setuptools import setup, find_packages
import pathlib

# Read the contents of README file
this_directory = pathlib.Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Get version from package
def get_version():
    with open('burning_candle/__init__.py', 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('"')[1]
    return "1.0.1"

setup(
    name="burning-candle",
    version=get_version(),
    author="Orhan Murat Tuncer",
    author_email="orancon11@gmail.com",
    description="🕯️ A beautiful ASCII candle timer for your terminal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Acenath/burning-candle",
    
    # Package configuration
    packages=find_packages() + find_packages(where="src"),
    package_dir={"": ".", "Timer": "src/Timer"},
    include_package_data=True,
    
    # Dependencies
    python_requires=">=3.6",
    install_requires=[
        # No external dependencies needed
    ],
    
    # Entry points for CLI
    entry_points={
        "console_scripts": [
            "burning-candle=burning_candle.cli:main",
            "candle-timer=burning_candle.cli:main",  # Alternative name
        ],
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    
    keywords="timer, candle, terminal, cli, ascii, animation, productivity",
)