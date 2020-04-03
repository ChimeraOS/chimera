from setuptools import setup, find_packages
from glob import glob

setup(
    name="Steam-Buddy",
    version="0.4.5",
    packages=find_packages(exclude=['tests']),
    scripts=['steam-buddy'],

    data_files=[
        ('share/steam-buddy/images', glob('images/*.png')),
        ('share/steam-buddy/images/flathub', glob('images/flathub/*.png')),
        ('share/steam-buddy/views', glob('views/*.tpl')),
        ('share/steam-buddy/public', glob('public/*.js')),
        ('share/steam-buddy/public', glob('public/*.css')),
        ('share/steam-buddy/config', glob('config/*.cfg')),
        ('share/steam-buddy', ['launcher']),
        ('bin', glob('bin/*')),
        ('bin', ['toggle-steamos-compositor']),
        ('share/steam-buddy/bin', ['steam-buddy-authenticator', 'flatpak-wrapper']),
        ('share/doc/steam-buddy', ['README.md']),
        ('share/doc/steam-buddy', ['LICENSE']),
    ],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=[
        'bottle',
        'pyyaml',
        'requests',
        'beaker',
        'pygame',
        'psutil',
        'bcrypt',
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
