Installation
============

.. note::

    Wheels are provided for Linux, MacOS and Windows x86-64, as well
    as Linux and MacOS Aarch64, but other machines will have to build the wheel 
    from the source distribution. Building ``pyaragorn`` involves compiling 
    ARAGORN, which requires a C compiler to be available.


PyPi
^^^^

``pyaragorn`` is hosted on GitHub, but the easiest way to install it is to download
the latest release from its `PyPi repository <https://pypi.python.org/pypi/pyaragorn>`_.
It will install all dependencies then install ``pyaragorn`` either from a wheel if
one is available, or from source after compiling the Cython code :

.. code:: console

   $ pip install --user pyaragorn

.. Conda
.. ^^^^^

.. Pyrodigal is also available as a `recipe <https://anaconda.org/bioconda/pyaragorn>`_
.. in the `bioconda <https://bioconda.github.io/>`_ channel. To install, simply
.. use the ``conda`` installer:

.. .. code:: console

..    $ conda install -c bioconda pyaragorn


Arch User Repository
^^^^^^^^^^^^^^^^^^^^

A package recipe for Arch Linux can be found in the Arch User Repository
under the name `python-pyaragorn <https://aur.archlinux.org/packages/python-pyaragorn>`_.
It will always match the latest release from PyPI.

Steps to install on ArchLinux depend on your `AUR helper <https://wiki.archlinux.org/title/AUR_helpers>`_
(``yaourt``, ``aura``, ``yay``, etc.). For ``aura``, you'll need to run:

.. code:: console

    $ aura -A python-pyaragorn


.. Piwheels
.. ^^^^^^^^

.. Pyrodigal works on Raspberry Pi computers (with NEON vectorization enabled!), 
.. and pre-built wheels are compiled for `armv7l` platforms on piwheels.
.. Run the following command to install these instead of compiling from source:

.. .. code:: console

..    $ pip3 install pyaragorn --extra-index-url https://www.piwheels.org/simple

.. Check the `piwheels documentation <https://www.piwheels.org/faq.html>`_ for 
.. more information.


GitHub + ``pip``
^^^^^^^^^^^^^^^^

If, for any reason, you prefer to download the library from GitHub, you can clone
the repository and install the repository by running (with the admin rights):

.. code:: console

   $ pip install git+https://github.com/althonos/pyaragorn

.. caution::

    Keep in mind this will install always try to install the latest commit,
    which may not even build, so consider using a versioned release instead.


GitHub + ``build`` and ``installer``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you do not want to use ``pip``, you can still clone the repository and
run the install file manually, although you will need to install the
build dependencies (mainly `Cython <https://pypi.org/project/cython>`_):

.. code:: console

   $ git clone --recursive https://github.com/althonos/pyaragorn
   $ cd pyaragorn
   $ python -m build -w .
   # python -m installer dist/*.whl

.. Danger::

    Installing packages without ``pip`` is strongly discouraged, as they can
    only be uninstalled manually, and may damage your system.
