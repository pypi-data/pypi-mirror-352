import os
from . import cleaner
from . import main_intermediary
import pkgutil
import shutil
import tempfile
from pathlib import Path
from Bio.PDB import PDBParser
from Bio import PDB
from .read_os import read_prot
from .folders_manipulate import create_folder
from .folders_manipulate import change_files
from .utils import _load_library

respak75 = _load_library("respak75")

MAX_RES = 10000
MAX_AT = 50000
IRESF = 1


def occluded_surface(pdb,method = "FIBOS", density_dots = 5.0):
    """
    Occluded Surface (OS)

    The Occluded Surface (OS) algorithm is a widely used approach for analyzing atomic packing in biomolecules.
    This function is part of the FIBOS package, which extends the OS methodology with enhancements.
    The `occluded_surface` function calculates OS per atom.

    Parameters
    ----------
    pdb : str
        Either a 4-character PDB ID (the structure will be fetched from the RCSB repository)
        or a path to a local PDB file.
    method : str, optional
        Method to be used for dot distribution:
        - 'OS': Classic approach, radial coverage with a fixed axis reference.
        - 'FIBOS' (default): Uses Fibonacci spirals for distributing the dots, reducing axial anisotropy
          and providing more uniform point distribution over the sphere.
    density_dots : float, optional
        Density of dots used for surface occlusion calculation. Higher values produce more detailed surfaces.

    Returns
    -------
    pandas.DataFrame
        A table with the following columns:
        
        - 'ATOM': Atomic contacts for each atom.
        - 'NUMBER OF POINTS': Number of dots (surface patches) on each atom.
        - 'AREA': Total area of all dots.
        - 'RAYLENGTH': Average length of normals normalized by 2.8 Å (diameter of water). Values close to 1 indicate poor packing.
        - 'DISTANCE': Average distance of atomic contacts in Å.

    Notes
    -----
    The OS method (Pattabiraman et al., 1995) distributes dots across atomic surfaces. Each dot has a normal vector
    that either contacts a neighboring atom's van der Waals surface (occluded) or extends into solvent (non-occluded).
    Only occluded dots are considered when calculating surface metrics. This allows inference of local packing density
    at atomic, residue, and molecular levels.

    For more information, see:
        - Fleming et al. (2000)
        - Soares et al. (2024)

    References
    ----------
    Fleming PJ, Richards FM (2000). Protein packing: Dependence on protein size, secondary structure
    and amino acid composition. https://doi.org/10.1006/jmbi.2000.3750

    Pattabiraman N, Ward KB, Fleming PJ (1995). Occluded molecular surface: Analysis of protein packing.
    https://doi.org/10.1002/jmr.300080603

    Soares HHM, Romanelli JPR, Fleming PJ, da Silveira CH (2024). bioRxiv. https://doi.org/10.1101/2024.11.01.621530

    Examples
    --------
    >>> from fibos import occluded_surface, osp
    >>> df = occluded_surface("1ptx", method="FIBOS", density_dots=5.0)
    >>> osp_data = osp("fibos_files/prot_1ptx.srf")  # optional: analyze per residue
    """

    remove_files()
    #create_folder(pdb)
    source_path = os.getcwd()
    change = False
    name_pdb = pdb
    if not os.path.exists("fibos_files"):
        try:
            os.makedirs("fibos_files")
        except FileExistsError:
            pass

    if not (pdb.endswith(".pdb")):
            arq_aux = pdb + ".pdb"
            if os.path.exists(arq_aux):
                os.remove(arq_aux)
    else:
            change = True
            name_pdb = name_pdb[-8:]
            if (os.path.exists(pdb) == False):
                raise FileNotFoundError(f"File not Found: {pdb}")
            #parser = PDB.PDBParser()
            #estrutura = parser.get_structure("protein", pdb)
    with tempfile.TemporaryDirectory() as temp_dir:
        if(change == True):
            #io = PDB.PDBIO()
            #io.set_structure(estrutura)
            #output_pdb = os.path.join(temp_dir, os.path.basename(name_pdb))
            #io.save(output_pdb)
            shutil.copy(pdb,temp_dir)
        os.chdir(temp_dir)
        pdb = pdb.lower()
        name_pack = "fibos"
        path_pack = pkgutil.get_loader(name_pack).get_filename()
        path_pack = os.path.dirname(path_pack)
        path_abs = os.path.abspath(path_pack)
        path_abs = path_abs+"/radii"
        shutil.copy(path_abs,".")
        iresl = cleaner.get_file(name_pdb)
        method = method.upper()
        meth = 0
        if method == "OS":
            meth = 1
        elif method == "FIBOS":
            meth = 2
        else:
            print("Wrong Method")
        file_remove = pdb
        if pdb.endswith(".pdb"):
            file_remove = pdb.replace(".pdb","")
        ray_remove = "raydist_"+file_remove+".lst"
        pack_remove = "prot_"+file_remove+".pak"
        file_remove = "prot_"+file_remove+".srf"
        if os.path.exists(file_remove):
            os.remove(file_remove)
        if os.path.exists(ray_remove):
            os.remove(ray_remove)
        if os.path.exists(pack_remove):
            os.remove(pack_remove)
        main_intermediary.call_main(IRESF,iresl,MAX_RES,MAX_AT,meth, density_dots)
        remove_files()
        file_name = change_files(pdb)
        from_path = source_path+"/fibos_files"
        for arquivo in os.listdir(temp_dir):
            caminho_arquivo = os.path.join(temp_dir,arquivo)
            if os.path.isfile(caminho_arquivo) and not arquivo.endswith(".pdb") and "radii" not in arquivo:
                shutil.copy2(caminho_arquivo,from_path)
        os.chdir(source_path)
    #file_name = "fibos_files/"+file_name
    return read_prot(os.path.join("fibos_files", file_name))


def remove_files():
    path = os.getcwd()
    extensions = ['.ms','.txt','.inp']
    files = [file for file in os.listdir(path) if any(file.endswith(ext) for ext in extensions)]
    if len(files)>0:
        for file in files:
            os.remove(os.path.join(path, file))
    if os.path.exists(os.path.join(path,"fort.6")):
        os.remove(os.path.join(path,"fort.6"))
    if os.path.exists(os.path.join(path, "part_i.pdb")):
        os.remove(os.path.join(path, "part_i.pdb"))
    if os.path.exists(os.path.join(path, "part_v.pdb")):
        os.remove(os.path.join(path, "part_v.pdb"))
    #os.remove("temp.pdb")
    if os.path.exists("temp.cln"):
        os.remove("temp.cln")
