# DokiDokiMD
[![Build Status](https://travis-ci.org/Konrad-Ziarko/DokiDokiMD.svg?branch=master)](https://travis-ci.org/Konrad-Ziarko/DokiDokiMD)
![](https://img.shields.io/github/issues/Konrad-Ziarko/DokiDokiMD.svg)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/76fa5ed5e113414fbb2d7ae6b12d00e1)](https://app.codacy.com/app/Konrad-Ziarko/DokiDokiMD?utm_source=github.com&utm_medium=referral&utm_content=Konrad-Ziarko/DokiDokiMD&utm_campaign=Badge_Grade_Dashboard)
[![Documentation Status](https://readthedocs.org/projects/dokidokimd/badge/?version=latest)](https://dokidokimd.readthedocs.io/en/latest/?badge=latest)
![](https://img.shields.io/github/license/Konrad-Ziarko/DokiDokiMD.svg)

Python manga downloader.
Playground for my first tui project.

# Disclaimer
THIS TOOL HAS BEEN RELEASED JUST FOR TESTING PURPOSES.

# What is DDMD?
DokiDoki Manga Downloader is a software that helps you manage and download manga chapters.
<br>
It is able to convert downloaded images(regardles of orientation) into single pdf file, ready to read.

# What is required?
1. Python 3.6 or greater.
2. Linux based OS or Cygwin for Windows installation - this is required by Urwid library used for TUI.

## Overview
Data downloaded by the program is stored in a files. Each site has its own file (database).
<br>
Object used by the program are saved and loaded (with [Pickle](https://docs.python.org/3/library/pickle.html)), look into [source](dokidokimd/manga_site.py) to see what is stored.
*Downloaded images are not stored in files - they are only present when downloaded, saving process gets rid of them*.

## Issue
To post any issue use available issue templates:
- [BUG](.github/ISSUE_TEMPLATE/bug_report.md)
- [FEATURE](.github/ISSUE_TEMPLATE/feature_request.md)

## Dependencies
- [Urwid](https://github.com/urwid/urwid)
- [PyFPDF](https://github.com/reingart/pyfpdf)(custom)

## License
This project is licensed under the BSD-3 License - see the [LICENSE](LICENSE) file for details
