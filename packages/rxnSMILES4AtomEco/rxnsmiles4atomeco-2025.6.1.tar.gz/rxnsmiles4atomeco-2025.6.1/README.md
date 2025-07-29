
# rxnSMILES4AtomEco:

This package provides functions to calculate the atom economy of chemical reactions using reaction SMILES.
It utilizes the RDKit library to handle molecular structures and properties.

### Features:
- Calculation of atom economy for reactions
- Handling of multiple reactions in a single calculation
- Support for different types of reaction SMILES
- Programmatic output of atom economy numerical value: verbose- and numberic output.
    
### Usage:
To use the package, simply import the relevant functions and provide reaction SMILES as input.
    
### Example verbose output:

```python
from rxnSMILES4AtomEco import atom_economy
reactions_smiles = "C.O>catalyst>{3}[HH]"
atom_economy(reactions_smiles)

 Atom Economy Calculation:
 
--------------------------------------------------
                      REACTANTS
..................................................
 SMILES:             C
 Molecular Formula:  CH4
 Molecular Weight:   16.04 g/mol
 Coefficient:        1.0
..................................................
 SMILES:             O
 Molecular Formula:  H2O
 Molecular Weight:   18.02 g/mol
 Coefficient:        1.0
--------------------------------------------------
--------------------------------------------------
                     PRODUCTS
..................................................
 SMILES:             [HH]
 Molecular Formula:  H2
 Molecular Weight:   2.02 g/mol
 Coefficient:        3.0
--------------------------------------------------

 Atom Economy:       17.8%
```

### Example Numeric Output:

```python  
from rxnSMILES4AtomEco import get_atom_economy
reactions_smiles = "C.O>catalyst>{3}[HH]"
value = get_atom_economy(reactions_smiles)
print(value)

17.8
```



### More info...
For more information, please refer to the documentation at https://pypi.org/project/rxnSMILES4AtomEco/