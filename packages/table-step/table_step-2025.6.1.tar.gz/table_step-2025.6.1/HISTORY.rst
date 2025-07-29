=======
History
=======
2025.6.1 -- Enhancement to allow paths with directories.
    * As in reading/writing structures, paths beginning with '/' are relative to the
      root of the job, and relative paths are relative to the directory where the table
      step is invoked.

2023.11.10 -- Bugfix: title of edit dialog was wrong

2023.10.30 -- Cleaned up output
    * Nothing large, just made the output properly indented, etc.

2023.7.25 -- Bug fix and Enhancements
    * Fixed bug with reading table using a variable for the filename, but asking for the
      type from the extension.
    * Add ability to save tables with a frequency of other than ever call.
      
2023.2.15 -- Bugs fixes and documentation
    * Restructured documentation and moved to new theme
    * Fixed bug with access rows of tables with non-integer indexes as well as "current"
      index 
    * Added support for lists of tables in pulldowns in the GUI
      
2021.12.22 -- Improved the handling of index columns, added formats.
    * Improved the handling of the index column
    * Added Save as
    * Added Excel and JSON formats.

2021.10.14 -- Updated for Python
    * Now supporting Python 3.8 and 3.9
      
2021.2.12 (12 February 2021)
----------------------------

* Updated the README file to give a better description.
* Updated the short description in setup.py to work with the new installer.
* Added keywords for better searchability.

2020.12.5 (5 December 2020)
---------------------------

* Internal: switching CI from TravisCI to GitHub Actions, and in the
  process moving documentation from ReadTheDocs to GitHub Pages where
  it is consolidated with the main SEAMM documentation.
* Updated to be compatible with the new command-line argument
  handling.

0.9 (15 April 2020)
-------------------

* General bug fixing and code cleanup.
* Part of release of all modules.

0.7.0 (17 December 2019)
------------------------

* General clean-up of code and output.
* Part of release of all modules.


0.3.0 (20 August 2019)
----------------------

* First release on PyPI.
