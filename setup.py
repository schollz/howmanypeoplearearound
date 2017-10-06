from setuptools import setup

setup(
    name='howmanypeoplearearound',
    packages=['howmanypeoplearearound'],
    version='0.3.6',
    description='A tshark wrapper to count the number of cellphones in the vicinity',
    author='schollz',
    url='https://github.com/schollz/howmanypeoplearearound',
    author_email='hypercube.platforms@gmail.com',
    download_url='https://github.com/schollz/howmanypeoplearearound/archive/v0.3.5.tar.gz',
    keywords=['tshark', 'wifi', 'location'],
    classifiers=[],
    install_requires=[
        "click",
        "netifaces",
        "pick",
    ],
    setup_requires=[],
    tests_require=[],
    entry_points={'console_scripts': [
        'howmanypeoplearearound = howmanypeoplearearound.__main__:main',
    ], },
)
