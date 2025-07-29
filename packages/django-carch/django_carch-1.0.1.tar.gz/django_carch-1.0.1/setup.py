from setuptools import setup, find_packages
import os

README = "README.md"
long_description = ""
if os.path.exists(README):
    with open(README, encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="django-carch",
    version="1.0.0",
    author="Jean Marie Daniel Vianney Guedegbe",
    description="Générateur de projet Django Clean Architecture avec support DevOps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/daniel10027/django-cleanarch-starter/",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "django-carch=django_carch.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    package_data={
    "django_carch": ["bootstrap.md"],
},
)
