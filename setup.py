"Setup chimera app"
from glob import glob
from setuptools import setup, find_packages

setup(
    name="Chimera",
    version="0.24.4",
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': ['chimera = chimera_app.__main__:main']
                  },
    data_files=[
        ('bin', glob('bin/*')),
        ('lib/systemd/system', glob('lib/systemd/system/*')),
        ('lib/systemd/user', glob('lib/systemd/user/*')),
        ('lib/udev/rules.d', glob('lib/udev/rules.d/*')),
        ('libexec/chimera', glob('libexec/*')),
        ('share/applications', ['org.chimeraos.app.desktop']),
        ('share/chimera/images', glob('images/*.png')),
        ('share/chimera/images/flathub', glob('images/flathub/*.png')),
        ('share/chimera/images/splash', glob('images/splash/*.png')),
        ('share/chimera/images/cart-loader', glob('images/cart-loader/*.png')),
        ('share/chimera/shortcuts', glob('shortcuts/*.yaml')),
        ('share/chimera/views', glob('views/*.tpl')),
        ('share/chimera/public', glob('public/*.js')),
        ('share/chimera/public', glob('public/*.css')),
        ('share/chimera/public', glob('public/*.webp')),
        ('share/chimera/config', glob('config/*.cfg')),
        ('share/chimera/config', glob('config/*.conf')),
        ('share/chimera/migrations', glob('migrations/*')),
        ('share/doc/chimera', ['README.md']),
        ('share/doc/chimera', ['LICENSE']),
        ('share/polkit-1/rules.d', glob('polkit-1/rules.d/*')),
    ],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=[
        'bottle',
        'pyyaml',
        'requests',
        'beaker',
        'pyglet',
        'psutil',
        'bcrypt',
        'vdf',
        'inotify_simple',
        'pyudev',
        'plyvel',
        'waitress',
    ],

    # metadata to display on PyPI
    author="Alesh Slovak",
    author_email="aleshslovak@gmail.com",
    description=("Chimera is a web based tool for installing non-Steam "
                 "software to your Linux based couch gaming system. It "
                 "was primarily developed for ChimeraOS."),
    keywords=("steam steamos couch emulation flatpak flathub chimera app "
              "chimeraos gamer gaming"),
    url="https://github.com/chimeraos/chimera",   # project home page, if any
    project_urls={
        "Bug Tracker": "https://github.com/chimeraos/chimera/issues",
        "Documentation": ("https://github.com/chimeraos/chimera/"
                          "blob/master/README.md"),
        "Source Code": "https://github.com/chimeraos/chimera",
    },
    classifiers=[
        'License :: OSI Approved :: MIT License'
    ]
)
