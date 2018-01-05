.. image:: etv_logo.png
   :align: left

Earth Time series Visualization
==============================

An application visualizing gridded geospatial time series data

A live demo can be viewed at:
http://etv.ryandillon.net


Requirements
------------

* Python3.4+
* An up-to-date web-browser that handles HTML5 and CSS Flexbox


Install
-------
It is best to use a Python virtual environment when running Etv, particularly
for ensuring the correct version of Django. A good place you virtual environment
could be where the directory where you put your processed JSON data:

.. code:: bash

    # Create a path for your Etv projects
    mkdir ~/etv_projects

    # Create your virtual environment for Python3
    cd ~/etv_projects
    virtualenv --python=python3 venv

Then just activate your virtual environment and install Etv via `pip`:

.. code:: bash

    source venv/bin/activate
    pip install etv


Quickstart
----------
After installation, use the Etv command-line-interface (CLI) to create sample
data and run the application. The first argument for all CLI commands is the
path to your processed JSON data.

First, create some sample data from the NOAA NCOM regional ocean model,
focussed on the waters off of Humboldt County, California:

.. note:: If you installed Etv in your virtual environment, you must activate
    it before runing the Etv CLI.

.. code:: bash

    mkdir json
    etv ./json create_sample_data

Then run the app via standard Django `manage.py` commands:

.. code:: bash

    etv ./json manage runserver

* The default location for the app is `http://localhost:8000`
* Type `Control-C` on the terminal to close the app.


Authors
-------
Ryan J. Dillon and Radovan Bast


Contributors
------------
Hans Kristian Djuve


License
-------
MPL 2.0 License. See the included license file.
