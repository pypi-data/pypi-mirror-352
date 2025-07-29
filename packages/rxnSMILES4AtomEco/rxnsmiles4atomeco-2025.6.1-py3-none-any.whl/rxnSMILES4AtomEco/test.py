from atom_eco import get_atom_economy
reactions_smiles = "C.O>catalyst>{3}[HH]"
value = get_atom_economy(reactions_smiles)
print(value)