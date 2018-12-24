# DokiDokiMD
Python manga downloader.

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

## TUI Controls
- Use <kbd>←</kbd> and <kbd>→</kbd> to navigate between existing columns.
- <kbd>Enter</kbd>, <kbd>Space</kbd> selects highlighted element from current column.
- Use <kbd>Mouse</kbd> click to select elements from any visible column.
- Use <kbd>Shift</kbd>+<kbd>d</kbd> to download content of highlighted column(not selected row in a column).
- Use <kbd>Shift</kbd>+<kbd>s</kbd> to save all data (except chapter images) - it will be autoloaded next time.
- Use <kbd>Home</kbd> to jump to first element in current column.
- Use <kbd>End</kbd> to jump to last element in current column.
- Use <kbd>PageUp</kbd> to jump full screen len up.
- Use <kbd>PageDown</kbd> to jump full screen len down.

+ Use <kbd>/</kbd> to start typing filter string.
  - Use <kbd>Enter</kbd> to apply filter.

### Example
```buildoutcfg


```

## Issue
To post any issue use available issue templates:
- [BUG](.github/ISSUE_TEMPLATE/bug_report.md)
- [FEATURE](.github/ISSUE_TEMPLATE/feature_request.md)

## Files Structure
- dokidokimd/
  - convert/
    - make_pdf.py
  - core/
    - controller.py
    - manga_site.py
  - img/
    - coder.py
  - logging/
    - logger.py
  - net/
    - crawler/
      - base_crawler.py
      - \*name\*.py
  - tui/
    - tui.py

## Dependencies
- [Urwid](https://github.com/urwid/urwid)
- [PyFPDF](https://github.com/reingart/pyfpdf)

## License
This project is licensed under the BSD-3 License - see the [LICENSE](LICENSE.md) file for details
