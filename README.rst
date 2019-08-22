========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |requires|
        | |coveralls|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/tdam_api/badge/?style=flat
    :target: https://readthedocs.org/projects/tdam_api
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/jbasu/tdam_api.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/jbasu/tdam_api

.. |requires| image:: https://requires.io/github/jbasu/tdam_api/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/jbasu/tdam_api/requirements/?branch=master

.. |coveralls| image:: https://coveralls.io/repos/jbasu/tdam_api/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/jbasu/tdam_api

.. |version| image:: https://img.shields.io/pypi/v/tdam_api.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/tdam_api

.. |commits-since| image:: https://img.shields.io/github/commits-since/jbasu/tdam_api/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/jbasu/tdam_api/compare/v0.1.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/tdam_api.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/tdam_api

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/tdam_api.svg
    :alt: Supported versions
    :target: https://pypi.org/project/tdam_api

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/tdam_api.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/tdam_api


.. end-badges

A Python Client for the TDAmeritrade API

* Free software: MIT license

Installation
============

::

    pip install tdam_api

Documentation
=============


https://tdam_api.readthedocs.io/


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
