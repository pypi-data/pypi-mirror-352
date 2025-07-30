from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

packages = ['ns_parental_controls']

setup(
    name="ns_parental_controls",

    version="2.0.0",  # updated version number of mobile app header
    # version="1.4.5",  # bug fix when adding minutes, need to account for time already played
    # version="1.4.4",  # bug fix when adding minutes, need to account for time already played
    # version="1.4.3",  # added get_allowed_playtime_today
    # version="1.4.2",  # added get_today_playtime_minutes to get the current amount of time the user has played on the device
    # version="1.4.1",  # bug fix in set_playtime method when minutes was 0
    # version="1.4.0",  # added method to add time to existing play time
    # version="1.3.2",  # changed name of method to set_playtime_minutes_for_today and added flag for disableself.print
    # version="1.3.0",  # new features, adding setting today playtime limits
    # version="1.2.0",  # bug fix, verification code logic is frustrating me
    # version="1.1.0",  # bug fix, dont reset verification code every time
    # version="1.0",

    packages=packages,
    install_requires=[
        'requests',
    ],

    author="Grant miller",
    author_email="grant@grant-miller.com",
    description="A simple interface to enable/disable your NS",
    long_description=long_description,
    license="PSF",
    keywords="grant miller ns parental controls",
    url="https://github.com/GrantGMiller/ns_parental_controls",  # project home page, if any
    project_urls={
        "Source Code": "https://github.com/GrantGMiller/ns_parental_controls",
    }

)
