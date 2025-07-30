from setuptools import setup, find_packages

setup(
    name='AuthNex',
    version='1.0',
    packages=find_packages(),
    install_requires=[],
    author='Kuro__',
    author_email='sufyan532011@gmail.com',
    description='A short description of AuthNex package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Kuro__/AuthNex',  # Replace with your actual repo URL if available
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
