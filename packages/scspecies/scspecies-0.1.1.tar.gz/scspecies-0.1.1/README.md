# scspecies

**scSpecies** is a deep‐learning framework for aligning single‐cell RNA-seq datasets across species.  
Built on top of scVI and transfer-learning principles, it learns a shared embedding space that directly matches cell populations from different organisms.

## Installation

To install the latest stable release of scSpecies run one of the following commands.
scSpecies defines two extras required to run the tutorial notebooks, **plotting** and **notebooks**.

.. code-block:: bash

    # Without extras
    pip install scspecies

    # Installs visualization libraries
    pip install scspecies[plotting]

    # Notebook support. Installs Jupyter and related packages so you can run the example notebooks. Notebooks can be accessed via the package documentation or found in docs/source/tutorials via GitHub.
    pip install scspecies[notebooks]

    # All extras
    pip install scspecies[plotting,notebooks]


After installing,  confirm that scSpecies loads:

.. code-block:: bash

    python -c "import scspecies; print(scspecies.__version__)"
    
## Documentation 

Full API docs, tutorials, and examples are available at:
[scSpecies Documentation (Read the Docs)](https://scspecies.readthedocs.io/en/latest/)