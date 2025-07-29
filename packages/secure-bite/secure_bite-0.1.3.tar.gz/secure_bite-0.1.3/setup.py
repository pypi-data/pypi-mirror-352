from setuptools import setup, find_packages

setup(
    name="secure_bite",
    version="0.1.4",
    author="Mbulelo Peyi",
    author_email="notseenyet013@gmail.com",
    description="A secure authentication and session management system for Django",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Mbulelo-Peyi/secure_bite",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "Django>=3.2",
        "djangorestframework",
        "djangorestframework-simplejwt",
        "django-cors-headers",
    ],
    python_requires=">=3.8",
)
