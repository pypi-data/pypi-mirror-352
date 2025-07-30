json2tex - Convert JSON to LaTeX
================================

:mod:`json2tex` is a Python package to convert JSON to LaTeX.

What can it do?
+++++++++++++++

:mod:`json2tex` converts JSON so it can be accessed from within LaTeX:

.. code-block:: sh

   echo '["Anne","Bob","Alice",{"age":14,"hobbies":["football","games"]}]' | json2tex
   # \newcommand{\First}{Anne}
   # \newcommand{\Second}{Bob}
   # \newcommand{\Third}{Alice}
   # \newcommand{\FourthAge}{14}
   # \newcommand{\FourthHobbiesFirst}{football}
   # \newcommand{\FourthHobbiesSecond}{games}

Installation
++++++++++++

.. code-block:: sh

    # from PyPI
    pip install -U json2tex
    # latest development version from GitLab
    pip install -U git+https://gitlab.com/nobodyinperson/json2tex


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   examples
   api/modules
   changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
