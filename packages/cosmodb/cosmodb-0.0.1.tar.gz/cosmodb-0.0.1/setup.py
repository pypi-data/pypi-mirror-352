from setuptools import setup, find_packages

setup(
    name="cosmodb",
    version="0.0.1",
    author="Bhuvanesh M",
    author_email="contact@bhuvaneshm.in",
    description="A future-proof database library for Cosmotalker.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://bhuvaneshm.in",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    license="Non-Commercial Custom License",
    python_requires='>=3.6',
)
