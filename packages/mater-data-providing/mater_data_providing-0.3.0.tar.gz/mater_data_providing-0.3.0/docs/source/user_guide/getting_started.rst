.. Copyright (C) 2025 @verzierf <francois.verzier@univ-grenoble-alpes.fr>

.. SPDX-License-Identifier: LGPL-3.0-or-later

.. _getting_started:

===============
Getting Started
===============

Here's a simple example to get you started with mater-data-providing:

This example shows how to:

1. Import the main functions
2. Create a basic dataset
3. Serialize it to JSON format
4. Save it locally

Project Structure
-----------------

First, create this project structure:

.. code-block:: text

   my-project/
   ├── main.py
   └── data/
       ├── variable_dimension/
       │   └── variable_dimension.json
       ├── dimension/
       │   └── dimension.json
       └── input_data/
           └── (output will be generated here)

Required Files
--------------

Create the following files in your project:

**Main Script**

.. literalinclude:: ../../../main.py
   :language: python
   :caption: main.py

**Dimension Configuration**

.. literalinclude:: ../../../data/dimension/dimension.json
   :language: json
   :caption: data/dimension/dimension.json

**Variable Dimension Configuration**

.. literalinclude:: ../../../data/variable_dimension/variable_dimension.json
   :language: json
   :caption: data/variable_dimension/variable_dimension.json

Running the Example
-------------------

To create the JSON dataset, execute:

.. code-block:: bash

   python main.py

Expected Output
---------------

This will create the following file:

.. literalinclude:: ../../../data/input_data/main.json
   :language: json
   :caption: data/input_data/main.json