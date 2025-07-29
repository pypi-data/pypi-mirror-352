from setuptools import setup, find_packages

setup(
    name='ai-data-prep',
    version='0.1.0',
    description='A lightweight data preprocessing tool for AI/ML projects',
    author='Your Name',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'scikit-learn'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
