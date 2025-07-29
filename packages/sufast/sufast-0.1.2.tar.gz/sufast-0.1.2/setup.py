from setuptools import setup, find_packages

# Load long description from README.md
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="sufast",  # Your package name on PyPI
    version="0.1.2",  # Update for each release
    author="Shohan",
    author_email="shohan.dev.cse@gmail.com",  # Replace with your email
    description="A blazing-fast Python web framework powered by Rust 🚀",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Important for README.md rendering
    url="https://github.com/shohan-dev/sufast",  # Replace with your GitHub repo
    project_urls={
        "Bug Tracker": "https://github.com/shohan-dev/sufast/issues",
        "Documentation": "https://github.com/shohan-dev/sufast",  # Can update later
    },
    license="MIT",
    packages=find_packages(),
    include_package_data=True,  # Include README, LICENSE, etc.
    install_requires=[],  # Add any dependencies if needed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",  # Optional, for familiarity
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Development Status :: 3 - Alpha",  # Update later: 4-Beta, 5-Stable
    ],
    python_requires=">=3.8",
)
