from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit import RDLogger
import argparse
import re

# Ignore RDKit warnings
RDLogger.DisableLog('rdApp.*') 

def parse_smiles_with_coefficients(smiles_str):
    """
    Parse SMILES string with optional stoichiometric coefficients.

    Args:
        smiles_str (str): SMILES string with optional coefficients.

    Returns:
        parsed_smiles (list): List of (SMILES, coefficient) tuples.
    """
    pattern = re.compile(r'(\{(\d*\.?\d+)\})?([^{}.]+)')
    matches = pattern.findall(smiles_str)
    parsed_smiles = []
    
    for match in matches:
        coefficient = float(match[1]) if match[1] else 1.0
        smiles = match[2]
        entities = smiles.split('.')
        for entity in entities:
            parsed_smiles.append((entity, coefficient))
    
    return parsed_smiles

def formula_atom_economy(reactants, products):
    """
    Calculate the atom economy of a reaction.

    Args:
        reactants (list): List of (RDKit molecule object, coefficient) tuples for reactants.
        products (list): List of (RDKit molecule object, coefficient) tuples for products.

    Returns:
        atom_economy (float): The atom economy as a percentage.
    """
    reactant_mass = sum([Descriptors.MolWt(mol) * coeff for mol, coeff in reactants])
    product_mass = sum([Descriptors.MolWt(mol) * coeff for mol, coeff in products])
    atom_economy = (product_mass / reactant_mass) * 100
    return atom_economy

def print_molecule_info(molecules, title):
    """
    Print information about molecules.

    Args:
        molecules (list): List of (RDKit molecule object, coefficient) tuples.
        title (str): The title for the molecule group (e.g., "Reactants", "Products").
    """
    border = '-' * 50
    print(border)
    print(f"{title.upper():^50}")
    for mol, coeff in molecules:
        smiles = Chem.MolToSmiles(mol)
        mol_weight = f"{Descriptors.MolWt(mol):.2f} g/mol"
        mol_formula = Chem.rdMolDescriptors.CalcMolFormula(mol, False)  # False for not using Hill notation
        print(f"{'.' * 50}")
        print(f"{' SMILES:':<20} {smiles}")
        print(f"{' Molecular Formula:':<20} {mol_formula}")
        print(f"{' Molecular Weight:':<20} {mol_weight}")
        print(f"{' Coefficient:':<20} {coeff}")
        
    print(border)

def calculate_atom_economy(reactions_smiles, printout=True):
    """
    Calculate overall atom economy from a list of reaction SMILES.

    Args:
        reactions_smiles (str): Reaction SMILES for multiple reactions separated by newlines.
        printout (bool): Whether to print the atom economy information. Default is True.

    Returns:
        atom_economy (float): The atom economy as a percentage, if printout is False.
    """
    reactions = reactions_smiles.split('\n')  # Split reactions by newline character

    overall_reactants = []
    overall_products = []

    for reaction_smiles in reactions:
        reaction_parts = reaction_smiles.split('>')

        if len(reaction_parts) != 3:
            print("Error: Each reaction SMILES must be in the form 'reactants>agents>products'")
            continue

        reactants_smiles, agents_smiles, products_smiles = reaction_parts

        try:
            reactant_smiles_list = parse_smiles_with_coefficients(reactants_smiles)
            product_smiles_list = parse_smiles_with_coefficients(products_smiles)

            # Filter reactants on a SMILES basis
            filtered_reactants = [(reactant, coeff) for reactant, coeff in reactant_smiles_list if reactant not in [p[0] for p in overall_products]]

            # Accumulate reactants
            overall_reactants.extend(filtered_reactants)

            # Collect products for each reaction
            overall_products.extend(product_smiles_list)
        except ValueError as e:
            print(e)
            continue

    # Convert SMILES to RDKit molecule objects with coefficients
    overall_reactants_mols = [(Chem.MolFromSmiles(smiles), coeff) for smiles, coeff in overall_reactants]
    last_reaction_products_mols = [(Chem.MolFromSmiles(smiles), coeff) for smiles, coeff in product_smiles_list]

    # Calculate reactant and product masses
    reactant_mass = sum([Descriptors.MolWt(mol) * coeff for mol, coeff in overall_reactants_mols])
    product_mass = sum([Descriptors.MolWt(mol) * coeff for mol, coeff in last_reaction_products_mols])
    
    # Check if reactant mass is not zero
    if reactant_mass == 0:
        print("Error: No reactants specified.")
        return None

    # Calculate atom economy
    atom_economy = formula_atom_economy(overall_reactants_mols, last_reaction_products_mols)

    # Print atom economy if printout is True
    if printout:
        print("\n Atom Economy Calculation: \n")
        print_molecule_info(overall_reactants_mols, " Reactants")
        print_molecule_info(last_reaction_products_mols, " Products")
        atom_economy_str = f"{atom_economy:.1f}%"
        print(f"\n{' Atom Economy:':<20} {atom_economy_str:<30} \n")
    else:
        return round(atom_economy, 2)

def get_atom_economy(reactions_smiles):
    """
    Function to numerically calculate atom economy.

    Args:
        reactions_smiles (str): Reaction SMILES for multiple reactions separated by newlines.

    Returns:
        atom_economy (float): The atom economy as a percentage.
    """
    return calculate_atom_economy(reactions_smiles, printout=False)

def atom_economy(smiles_str):
    """
    Wrapper function to calculate atom economy from a SMILES string.

    Args:
        smiles_str (str): Reaction SMILES. For multiple reactions separate by newlines.

    Returns:
        None
    """
    atom_economy_value = calculate_atom_economy(smiles_str)
    if atom_economy_value is not None:
        print(f"Atom Economy: {atom_economy_value:.1f}%")

def main():
    """
    Main function to parse arguments and calculate overall atom economy.
    """
    parser = argparse.ArgumentParser(description='Calculate Atom Economy for reactions using Reaction SMILES.')
    parser.add_argument('reactions', type=str, help='Reaction SMILES for multiple reactions separate by newlines')
    parser.add_argument('--numeric', action='store_true', help='Flag to get only the numerical value of atom economy')
    args = parser.parse_args()

    if args.numeric:
        atom_economy_value = get_atom_economy(args.reactions)
        if atom_economy_value is not None:
            print(f"{atom_economy_value:.1f}")
    else:
        atom_economy(args.reactions)

if __name__ == '__main__':
    main()
