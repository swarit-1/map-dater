"""
Setup script for Map Dater.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / 'README.md'
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ''

# Read requirements
requirements_path = Path(__file__).parent / 'requirements.txt'
requirements = []
if requirements_path.exists():
    with open(requirements_path) as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith('#')
        ]

setup(
    name='map-dater',
    version='0.1.0',
    description='Historical map dating system using computer vision and historical knowledge',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/map-dater',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=requirements,
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='maps historical-analysis computer-vision ocr dating cartography',
    entry_points={
        'console_scripts': [
            'map-dater=main:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
