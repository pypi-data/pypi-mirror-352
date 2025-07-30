from setuptools import setup

main_ns = {}
with open("dash_auth_plus/version.py", encoding="utf-8") as f:
    exec(f.read(), main_ns)

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="dash_auth_plus",
    version=main_ns["__version__"],
    author="Bryan Schroeder",
    author_email="bryan.ri.schroeder@gmail.com",
    packages=["dash_auth_plus"],
    license="MIT",
    description="Dash Authorization Package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "dash>=1.1.1",
        "flask",
        "werkzeug",
    ],
    extras_require={
        "oidc": ["authlib"],
    },
    python_requires=">=3.8",
    include_package_data=True,
    url="https://github.com/BSd3v",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database :: Front-Ends",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Widget Sets",
    ],
)
