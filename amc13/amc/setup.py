import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "OC Survey Automated Map Checking Tools",
    version = "1.4",
    author = "Dr. Kostas Alexandridis, OC Survey Geospatial Services",
    author_email = "Kostas.Alexandridis@ocpw.ocgov.com",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/ktalexan/OCAMC",
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
        ],
    python_requires = ">=3.6",
    )
