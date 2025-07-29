from setuptools import setup, find_packages

setup(
    name='thenewallinone',  # Package name, use something simple for testing
    version='3.0.1',  # Version of your library, start with 0.1.0
    author='Agamjot Lamba',  # Replace with your name
    author_email='agamjotlamba55@gmail.com',  # Replace with your email
    description='A simple test library for PyPI',  # Short description
    long_description=open('README.md').read(),  # Reads from README.md for long description
    long_description_content_type='text/markdown',  # Tells PyPI the format of the description
    packages=find_packages(),  # Automatically include all Python packages in your project folder
    install_requires=[  # Specify your dependencies here
        'huggingface_hub',
        'transformers',
        'pillow',
        'torch'
    ],
    classifiers=[  # Classifiers help users find your package
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Define the minimum Python version required
)
