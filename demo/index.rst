Diagram Examples
================

This document shows how to generate figures and diagrams with
``sphinxcontrib-texfigure`` extension.

Hello, World!
-------------

.. texfigure:: hello-world.tex

This image is rendered using ``texfigure`` directive:

.. sourcecode:: rst

   .. texfigure:: hello-world.tex

File ``hello-world.tex`` contains the following LaTeX document:

.. literalinclude:: hello-world.tex

Database Schema
---------------

.. texfigure:: database-schema.tex
   :align: center
   :alt: Database schema for HTSQL regression tests

This diagram was rendered using the following directive:

.. sourcecode:: rst

   .. texfigure:: database-schema.tex
      :align: center
      :alt: Database schema for HTSQL regression tests

The LaTeX document is split into two files.  File ``preamble.tex`` contains
common definitions:

.. literalinclude:: preamble.tex

File ``database-schema.tex`` contains the diagram itself:

.. literalinclude:: database-schema.tex

