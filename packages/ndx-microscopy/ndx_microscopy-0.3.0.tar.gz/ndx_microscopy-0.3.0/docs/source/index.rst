.. ndx-microscopy documentation master file

ndx-microscopy: NWB Extension for Microscopy Data
*********************************************

The ndx-microscopy extension provides a standardized way to store and organize microscopy data in the Neurodata Without Borders (NWB) format. This extension integrates with  `ndx-ophys-devices <https://github.com/catalystneuro/ndx-ophys-devices>`_ to provide comprehensive optical component specifications.

Key Features
-----------

- **Device Components**: MicroscopeModel, Microscope instances, and MicroscopyRig for organizing optical components
- **Illumination Patterns**: Support for various scanning and acquisition methods
- **Imaging Spaces**: Support for 2D/3D imaging with precise coordinate systems
- **Data Series**: Time series data with multi-plane and variable depth support
- **ROI Management**: Segmentation and response data storage

Documentation
-----------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   description
   getting_started
   user_guide
   examples
   format
   api
   release_notes
   credits

Installation
-----------

Python Installation
^^^^^^^^^^^^^^^^^

.. code-block:: bash

   pip install ndx-microscopy


Contributing
-----------

Contributions are welcome! Please see our `GitHub repository <https://github.com/catalystneuro/ndx-microscopy>`_ for:

- Source code and documentation
- Issue tracking and feature requests
- Development guidelines
- Contributing instructions

Indices and Tables
---------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
