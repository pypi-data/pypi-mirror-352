from setuptools import setup, find_packages

setup(
    name="cloey-orm",
    fullname="CloeyORM - The Python ORM for PostgreSQL",
    version="0.0.7",
    description="The Python ORM for PostgreSQL",
    long_description=f"{open('README.md').read()}\n\n{open('CHANGELOG.en.md').read()}\n{open('CHANGELOG.pt.md').read()}",
    long_description_content_type="text/markdown",
    author="Xindiri Inc.",
    author_email="info@xindiri.com",
    packages=find_packages(include=["cloey", "cloey.*"]),
    install_requires=[
        "psycopg2-binary",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
