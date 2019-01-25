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
Data downloaded by the program is stored in a files. Each site has its own file (database).
<br>
Object used by the program are saved and loaded (with [Pickle](https://docs.python.org/3/library/pickle.html)), look into [source](./dokidokimd/core/manga_site.py) to see what is stored.
*Downloaded images are not stored in files - they are only present when downloaded, saving process gets rid of them*.

## TUI Controls
- Use <kbd>Shift</kbd>+<kbd>q</kbd> to quit.
- Use <kbd>Shift</kbd>+<kbd>s</kbd> to save all data (except chapter images) - it will be autoloaded next time.
- Use <kbd>←</kbd> and <kbd>→</kbd> to navigate between existing columns.
- <kbd>Enter</kbd>, <kbd>Space</kbd> selects highlighted element from current column.
- Use <kbd>Mouse</kbd> click to select elements from any visible column.
- Use chapter column buttons (Download, Save, Convert, Remove) or:
    - Use <kbd>Shift</kbd>+<kbd>d</kbd> to download content of highlighted column(not selected row in a column).
    - Use <kbd>Shift</kbd>+<kbd>w</kbd> to save pages from chapter as images.
    - Use <kbd>Shift</kbd>+<kbd>c</kbd> to converted downloaded pages into PDF.
    - Use <kbd>Shift</kbd>+<kbd>r</kbd> to remove downloaded images.
- Use <kbd>Home</kbd> to jump to first element in current column.
- Use <kbd>End</kbd> to jump to last element in current column.
- Use <kbd>PageUp</kbd> to jump full screen length up.
- Use <kbd>PageDown</kbd> to jump full screen length down.

+ Use <kbd>/</kbd> to start typing filter string (regular expression).
  - Use <kbd>Enter</kbd> to apply filter.
  - ### Example regex
    ```
    kiss.*      this regex will match all mangas starting with "kiss" folowed by any repeadted or none characters.
    .*kiss      this regex will match all mangas ending with "kiss".
    kiss.*ass   this regex will match all mangas starting with "kiss", ending with "ass" and with any or none characters between.
    ```
  - Refere to [this site](https://regex101.com/) if you want to learn more basics.
  
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
- [PyFPDF](https://github.com/reingart/pyfpdf)(custom)

## License
This project is licensed under the BSD-3 License - see the [LICENSE](LICENSE) file for details
