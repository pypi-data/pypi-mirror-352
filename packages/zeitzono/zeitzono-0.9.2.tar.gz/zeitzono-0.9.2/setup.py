from setuptools import setup

setup(
    name="zeitzono",
    version="v0.9.2",
    packages=["Zeitzono"],

    entry_points={
        "console_scripts": [
            "zeitzono = Zeitzono.ZeitzonoMain:main"
        ]
    },

    install_requires=["python-dateutil", "parsedatetime", "pytz", "tzlocal", "urwid", "xdg"],
    zip_safe=False,
    package_data={"Zeitzono": ["data/*"]},
    license="BSD",
    data_files=[
        ("share/man/man1", ["man/zeitzono.1"]),
        ("share/doc/zeitzono", ["README", "LICENSE", "LICENSE-geonames-db"]),
    ],
    python_requires=">3.8.0",
    author="N.J. Thomas",
    author_email="info@zeitzono.org",
    platforms="POSIX",
    description="city based timezone converter with a curses (TUI) interface",
    long_description=open("README").read(),
    long_description_content_type="text/plain",
    keywords="""console curses time zone timezone
                convert conversion city cities""".split(),
    url="https://zeitzono.org/",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Console :: Curses",
        "Intended Audience :: Other Audience",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Utilities",
    ],
)
