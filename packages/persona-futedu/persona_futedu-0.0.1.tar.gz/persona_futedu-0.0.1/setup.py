from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='persona-futedu',
    version='0.0.1',
    description='Persona of students from chat.',
    author='Ibrahim',
    author_email='string2025@gmail.com',
    packages=find_packages(),
    install_requires=[
        'google-genai',
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    zip_safe=False,
)