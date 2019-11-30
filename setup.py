from setuptools import setup, find_packages
setup(
    name="Steam-Buddy",
    version="0.1.5",
    packages=find_packages(),
    scripts=['steam-buddy'],

    data_file=[
        ('share/steam-buddy', ['views', 'images']),
        ('bin', ['bin/gb', 'bin/gba', 'bin/gbc', 'bin/genesis', 'bin/nes', 'bin/sgg', 'bin/sms', 'bin/snes']),
        ('share/doc/steam-buddy', ['README.md']),
    ],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=[
        'bottle',
        'pyyaml',
        'requests',
    ],

    # metadata to display on PyPI
    author="Alesh Slovak",
    author_email="aleshslovak@gmail.com",
    description="Steam Buddy is a web based tool for installing non-Steam software to your Linux based couch gaming system. It was primarily developed for GamerOS.",
    keywords="steam steamos couch emulation flatpak flathub steam-buddy buddy gameros gamer gaming",
    url="https://github.com/gamer-os/steam-buddy",   # project home page, if any
    project_urls={
        "Bug Tracker": "https://github.com/gamer-os/steam-buddy/issues",
        "Documentation": "https://github.com/gamer-os/steam-buddy/blob/master/README.md",
        "Source Code": "https://github.com/gamer-os/steam-buddy",
    },
    classifiers=[
        'License :: OSI Approved :: MIT License'
    ]
)
