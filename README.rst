**dswell**
===========

::

      A CLI tool which will run a daemon process in backgroud to delete the file/directory
      after a specific time period
      
      
**Installation**
----------------

::

      python setup.py install
      
**General Info**

::
      
      dswell will run a deamon process in backgroud which will delete the file/directory after
      a specific time period.
      I have created this to automatally delete the file and directory after specified time as
      my disk usually filed with files and directory which i creates to test something and forget
      to delete it. 


**using**
---------

Type ``dswell --help`` in terminal This will guide you through the
process

::
      
      Usage: dswell [OPTIONS]

      Options:
            --dir BOOLEAN  Set this if you want to test something as a packge
            --name TEXT        Name of the file or package
            --time INTEGER     time till file will be deleted(in seconds)
            --help             Show this message and exit.

**Issues**
----------
Filled with issue. look at the log file in .dswell in homedir.
1 looking for a way to kill daemon processes created by dswell

**Contributing**
----------------

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.
