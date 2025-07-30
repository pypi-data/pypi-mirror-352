====================================
sphinxcontrib-jsontable Examples
====================================

This page demonstrates how to use the .. jsontable:: directive.
It works in both “.rst” files and (if you have myst_parser enabled) “.md” files.

Sample Data Files
----------------------

We will use the following sample JSON files.

**``data/sample_users.json`` (array of objects)**:

.. literalinclude:: data/sample_users.json
   :language: json
   :caption: data/sample_users.json

**``data/sample_products.json`` (2D array)**:

.. literalinclude:: data/sample_products.json
   :language: json
   :caption: data/sample_products.json

External File (Array of Objects)
-----------------------------------

| A table is generated from ``data/sample_users.json``.
| Because it’s an array of objects, keys are used automatically as headers.
| Use the ``:header:`` option to display the header row.

.. jsontable:: data/sample_users.json
   :header:

| Use the ``:limit:`` option to limit the number of items displayed.

.. jsontable:: data/sample_users.json
   :header:
   :limit: 1

External File (2D Array + Header)
-------------------------------------

| Generate a table from ``data/sample_products.json``.
| When the first row is a header, use the ``:header:`` option.

.. jsontable:: data/sample_products.json
   :header:

Inline JSON (Array of Objects)
----------------------------------

You can also embed JSON directly in your document:

.. jsontable::

   [
       {"name": "Alice", "age": 30, "city": "New York"},
       {"name": "Bob", "age": 25, "city": "Los Angeles"},
       {"name": "Charlie", "age": 35, "city": "Chicago"}
   ]

External File (2D Array + Header)
-----------------------------------

Generate a table from ``data/sample_products.json``.
Since the first row contains column names, use the :header: option.

.. jsontable::

   [
       ["A1", "B1", "C1"],
       ["A2", "B2", "C2"],
       ["A3", "B3", "C3"]
   ]
