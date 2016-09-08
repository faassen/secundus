Install Secundus for development
================================

.. highlight:: console

Clone Secundus from github::

  $ git clone git@github.com:faassen/secundus.git

If this doesn't work and you get an error 'Permission denied
(publickey)', you need to upload your ssh public key to github.

Then go to the secundus directory::

  $ cd secundus

Make sure you have virtualenv installed.

Create a new virtualenv for Python 3 inside the secundus directory::

  $ virtualenv -p python3 env/py3

Activate the virtualenv::

  $ source env/py3/bin/activate

Make sure you have recent setuptools and pip installed::

  $ pip install -U setuptools pip

Install the various dependencies and development tools from
develop_requirements.txt::

  $ pip install -Ur develop_requirements.txt

Running the tests
-----------------

You can run the tests using `py.test`::

  $ py.test
