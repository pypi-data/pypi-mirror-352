.. _prima.install:

Installing Lino Prima
=====================

- Install Lino (the framework) as documented in
  :ref:`lino.dev.install`

- Go to your :xfile:`repositories` directory and download also a copy
  of the *Lino Prima* repository::

    cd ~/repositories
    git clone https://github.com/lino-framework/prima
    
- Use pip to install this as editable package::

    pip install -e prima

- Create a local Lino project as explained in
  :ref:`lino.tutorial.hello`.

- Change your project's :xfile:`settings.py` file so that it looks as
  follows:

  .. literalinclude:: settings.py

  The first line is Python way to specify encoding (:pep:`263`).
  That's needed because of the non-ascii **ì** of "Lino Noi" in
  line 3.

