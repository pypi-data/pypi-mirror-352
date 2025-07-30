from setuptools import setup, find_packages

setup(
    name="quicklearnkit",  # Package name
    version="0.0.2",    # Initial version
    author="hazi", # Your name
    author_email="hajiafribaba@gmail.com",  # Your email
    description="A simplified interface for machine learning algorithms.",  # Short description
    long_description=open("README.md").read(),  # Long description from README
    long_description_content_type="text/markdown",  # Format of the long description
    url="https://github.com/Masterhazi/quicklearnkit",  # Project URL
    packages=find_packages(),  # Automatically find all packages
    install_requires=[  # List your dependencies here
        "scikit-learn",
        "pandas",
        "numpy",
    ],
    classifiers=[  # Metadata for PyPI
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Python version compatibility
)