from setuptools import setup, find_packages

# Read the requirements from the requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='tracllm_kit',  # Replace with your package name
    version='0.1.1',  # Replace with your package version
    author='Yanting Wang',  # Replace with your name
    author_email='ykw5450@psu.com',  # Replace with your email
    description='A context traceback tool for LLM',  # Replace with your package description
    long_description=open('README.md').read(),  # Ensure you have a README.md file
    long_description_content_type='text/markdown',
    url='https://github.com/WYT8506/tracllm_kit',  # Replace with your package URL
    packages=find_packages(),  # Specify the source directory
    install_requires=requirements,  # Use the requirements from the file
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Replace with your license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',  # Specify the minimum Python version
)