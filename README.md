# DokiDokiMD
[![Build Status](https://travis-ci.org/Konrad-Ziarko/DokiDokiMD.svg?branch=master)](https://travis-ci.org/Konrad-Ziarko/DokiDokiMD)
![](https://img.shields.io/github/issues/Konrad-Ziarko/DokiDokiMD.svg)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/76fa5ed5e113414fbb2d7ae6b12d00e1)](https://app.codacy.com/app/Konrad-Ziarko/DokiDokiMD?utm_source=github.com&utm_medium=referral&utm_content=Konrad-Ziarko/DokiDokiMD&utm_campaign=Badge_Grade_Dashboard)
[![Documentation Status](https://readthedocs.org/projects/dokidokimd/badge/?version=latest)](https://dokidokimd.readthedocs.io/en/latest/?badge=latest)
![](https://img.shields.io/github/license/Konrad-Ziarko/DokiDokiMD.svg)

Python manga downloader.

# Disclaimer
THIS TOOL HAS BEEN RELEASED JUST FOR TESTING PURPOSES.

# What is DDMD?
DokiDoki Manga Downloader is a software that helps you manage and download manga chapters.
<br>
It is able to convert downloaded images(regardles of orientation) into single pdf file, ready to read.

# What is required?
Python 3.5 or greater.

## Overview
Data downloaded by the program is stored in a files. Each site has its own file (database).
<br>
Object used by the program are saved and loaded (with [Pickle](https://docs.python.org/3/library/pickle.html)), look into [source](dokidokimd/models.py) to see what is stored.

## Issues
To post any issue use available issue templates:
- [BUG](.github/ISSUE_TEMPLATE/bug_report.md)
- [FEATURE](.github/ISSUE_TEMPLATE/feature_request.md)

## [Dependencies](requirements.txt)
- [Selenium](https://github.com/SeleniumHQ/selenium)
- [reportlab](https://pypi.org/project/reportlab/)
- [PyQt5](https://pypi.org/project/PyQt5/)
- [configobj](https://pypi.org/project/configobj/)
- [six](https://pypi.org/project/six/)
- [Pillow](https://pypi.org/project/Pillow/)
- [lxml](https://pypi.org/project/lxml/)
- [requests](https://pypi.org/project/requests/)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
