.. highlight:: rest

.. _installation:

Installation and Configuration
==============================

This chapter describes how to install, configure and uninstall CYMDISTPy.


Software requirements
^^^^^^^^^^^^^^^^^^^^^

To export CYMDIST as an FMU, CYMDISTPy needs:

1. Python 3.4.x. 32bit

2. jinja2

3. lxml

4. pandas

5. numpy

6. cython

7. Dymola


CYMDISTPy has been tested with:


- Windows 10 64 bit Professional.
- Dymola 2017.


.. _installation directory:

Installation
^^^^^^^^^^^^

To install CYMDISTPy, proceed as follows:

1. Download the installation file from the :doc:`download` page.

2. Unzip the installation file into any subdirectory (hereafter referred to as the "installation directory").
 

The installation directory should contain the following subdirectories:

- ``dev/``

  - ``parser/``
    (Python scripts, Modelica templates and xsd validator files)
    
  - ``cymdist/``
    (Python scripts for communicating with CYMDIST)

  - ``fmuChecker/``
    (fmuChecker binaries for running unit test)

  - ``bin/``
    (Scripts for running unit tests.)

  - ``fmus/``
    (FMUs folder.)

- ``models/``
  (Examples models)

  - ``modelica``

3. Add following folders to your system path: 

 - Python installation folder (e.g. ``C:\Python34``)
 - Python scripts folder (e.g. ``C:\Python34\Scripts``), 
 - Dymola executable folder (e.g. ``C:\Program Files(x86)\Dymola2017\bin``)

   
   You can add folders to your system path by performing following steps on Windows 8 or 10:

   - In Search, search for and then select: System (Control Panel)
     
   - Click the Advanced system settings link.
     
   - Click Environment Variables. In the section System Variables, find the PATH environment variable and select it. Click Edit. 
     
   - In the Edit System Variable (or New System Variable) window, specify the value of the PATH environment variable (e.g. ``C:\Python34``, ``C:\Python34\Scripts``). Click OK. Close all remaining windows by clicking OK.
     
   - Reopen Command prompt window for your changes to be active.
    
   To check if the variables have been correctly added to the system path, type ``python``
   into a command prompt to see if the right version of Python starts up.


4. Install Python dependencies by running

   .. code-block:: none
   
      pip install -r bin/cymdistpy-dependencies.txt


   .. note:: 
   
     ``lxml`` cannot be installed using ``pip``. Please download and install
     the executable (``lxml-3.4.4.win32-py3.4.exe``) from `PyPyi <https://pypi.python.org/pypi/lxml/3.4.4>`_. 
   


Uninstallation
^^^^^^^^^^^^^^

To uninstall CYMDISTPy, delete the `installation directory`_.
