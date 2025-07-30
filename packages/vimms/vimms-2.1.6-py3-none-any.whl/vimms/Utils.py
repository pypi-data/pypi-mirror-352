# Utils.py - some general utilities
import os
from pathlib import Path

import pysmiles
from mass_spec_utils.library_matching.gnps import load_mgf

from vimms.Chemicals import KnownChemical, UnknownChemical, DatabaseCompound
from vimms.Common import create_if_not_exist, ATOM_MASSES, POSITIVE, ADDUCT_TERMS
from vimms.MassSpecUtils import adduct_transformation

# Constants for write_msp
COLLISION_ENERGY = "25"
IONIZATION = "Positive"
SKIP_RT = False


def packline(outln, packme):
    outln.append(packme + "\n")
    return outln


def decimal_to_string(fnum, no_dec=0):
    """
    Convert a decimal to a string with no_dec decimal places
    """
    res = ""
    if no_dec == 0:
        res = str(int(fnum))
    else:
        res = str(round(fnum, no_dec))
    return res


# flake8: noqa: C901
def write_msp(
    chemical_list,
    msp_filename,
    out_dir=None,
    skip_rt=False,
    all_isotopes=False,
    ion_mode=[POSITIVE],
):
    """
    Turn a chemical list into an msp file
    """

    # buffer for msp lines
    outln = []
    outln.clear
    pos = 0

    for chem in chemical_list:
        if all_isotopes:
            use_isotopes = range(len(chem.isotopes))
        else:
            use_isotopes = [0]
        for which_isotope in use_isotopes:
            for ionisation_mode in ion_mode:
                for which_adduct in range(len(chem.adducts[ionisation_mode])):
                    if isinstance(chem, KnownChemical):
                        name = (
                            "NAME: "
                            + "KnowChemical"
                            + "_"
                            + chem.formula.formula_string
                            + "_iso"
                            + str(which_isotope)
                            + "_num"
                            + str(pos)
                        )
                    elif isinstance(chem, UnknownChemical):
                        name = (
                            "NAME: "
                            + "UnKnowChemical"
                            + "_"
                            + str(chem.mass)
                            + "_iso"
                            + str(which_isotope)
                            + "_num"
                            + str(pos)
                        )
                    else:
                        raise NotImplementedError()
                    outln = packline(outln, name)

                    mz = chem.isotopes[which_isotope][0]
                    adduct = chem.adducts[ionisation_mode][which_adduct][0]
                    mul, add = ADDUCT_TERMS[adduct]
                    mz = adduct_transformation(mz, mul, add)
                    outln = packline(outln, "PRECURSORMZ: " + decimal_to_string(mz, 2))
                    outln = packline(
                        outln,
                        "PRECURSORTYPE: "
                        + "["
                        + chem.adducts[ionisation_mode][which_adduct][0]
                        + "]+",
                    )
                    if isinstance(chem, KnownChemical):
                        outln = packline(outln, "FORMULA: " + chem.formula.formula_string)
                    if not skip_rt:
                        rt = chem.rt + chem.chromatogram.get_apex_rt()
                        outln = packline(
                            outln, "RETENTIONTIME: " + decimal_to_string(rt / 60, 2)
                        )  # in minutes
                    outln = packline(
                        outln,
                        "INTENSITY: "
                        + decimal_to_string(
                            chem.isotopes[which_isotope][1]
                            * chem.adducts[ionisation_mode][which_adduct][1]
                            * chem.max_intensity
                        ),
                    )
                    outln = packline(outln, "IONMODE: " + IONIZATION)
                    outln = packline(outln, "COLLISIONENERGY: " + COLLISION_ENERGY)
                    outln = packline(outln, "Num Peaks: " + str(len(chem.children)))
                    for msn in chem.children:
                        mz = msn.isotopes[0][0]
                        adduct = chem.adducts[ionisation_mode][which_adduct][0]
                        mul, add = ADDUCT_TERMS[adduct]
                        msn_mz = adduct_transformation(mz, mul, add)
                        msn_peak = (
                            chem.isotopes[which_isotope][1]
                            * chem.adducts[ionisation_mode][which_adduct][1]
                            * chem.max_intensity
                            * 1
                            * msn.prop_ms2_mass
                        )
                        if decimal_to_string(msn_peak) != "0":
                            temp = decimal_to_string(msn_mz, 5) + " " + decimal_to_string(msn_peak)
                            outln = packline(outln, temp)
                    outln = packline(outln, "")
                    pos += 1

    if out_dir is not None:
        msp_filename = Path(out_dir, msp_filename)

    out_dir = os.path.dirname(msp_filename)
    create_if_not_exist(out_dir)

    f = open(msp_filename, "w")
    f.writelines(outln)
    f.close()


def smiles_to_formula(smiles_string):
    """Safely convert a SMILES string into a chemical formula."""
    try:
        mol = pysmiles.read_smiles(smiles_string, explicit_hydrogen=True)
    except Exception:
        # Some of the example spectra contain non-standard or
        # malformed SMILES (e.g. dangling E/Z isomer tokens).  In these
        # cases ``pysmiles`` will raise an error.  For the purposes of
        # the unit tests we simply return ``None`` if the SMILES cannot
        # be parsed.
        return None

    atom_counts = {g: 0 for g in ATOM_MASSES}
    for node in mol.nodes(data="element"):
        atom = node[1]
        if atom not in atom_counts:
            return None
        atom_counts[atom] += 1

    chem_formula = ""
    for atom, count in atom_counts.items():
        if count == 0:
            continue
        if count == 1:
            chem_formula += atom
        else:
            chem_formula += f"{atom}{count}"
    return chem_formula


def mgf_to_database(mgf_file, id_field="SPECTRUMID"):
    """
    Load spectra from an mgf file and save as a list of DatabaseCompounds
    Computes chemimcal formula from SMILES
    """
    records = load_mgf(mgf_file, id_field=id_field)
    database = []
    for key, record in records.items():
        chemical_formula = smiles_to_formula(record.metadata["SMILES"])
        record.metadata["CHEMICAL_FORMULA"] = chemical_formula
        if chemical_formula is None:
            # Skip entries with unparseable SMILES strings.  They are not
            # useful for formula based sampling and would cause errors later
            # when converting to :class:`Formula` objects.
            continue
        database.append(
            DatabaseCompound(
                record.spectrum_id, record.metadata["CHEMICAL_FORMULA"], None, None, None, key
            )
        )
    return database
