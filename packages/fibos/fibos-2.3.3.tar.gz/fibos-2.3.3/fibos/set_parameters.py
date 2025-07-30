import pandas as pd
import re
import pkgutil
import os
import io
import shutil

def get_radii():
    """
    Load Radii Values

    Loads the atomic radii values used for surface-occlusion calculations.
    The returned values correspond to the configuration currently in use
    during the execution of the algorithm.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing atomic radii used for occlusion calculations.
        Typically includes atom types and their corresponding radii.

    See Also
    --------
    set_radii : Set custom radii values.
    reset_radii : Reset radii values to the default configuration.

    Authors
    -------
    - Carlos Henrique da Silveira (carlos.silveira@unifei.edu.br)
    - Herson Hebert Mendes Soares (hersonhebert@hotmail.com)
    - Joao Paulo Roquim Romanelli (joaoromanelli@unifei.edu.br)
    - Patrick Fleming (Pat.Fleming@jhu.edu)

    Examples
    --------
    >>> from fibos import get_radii
    >>> radii = get_radii()
    >>> print(radii.head(3))
    """

    name_pack = "fibos"
    path_pack = pkgutil.get_loader(name_pack).get_filename()
    path_pack = os.path.dirname(path_pack)
    path_abs = os.path.abspath(path_pack)
    path_abs = path_abs+"/radii"
    larguras_colunas = [11, 4] # Largura do campo 1, Largura do campo 2
    nomes_colunas = ['ATOM', 'RAY']
    try:
        radii_value = pd.read_fwf(path_abs, widths=larguras_colunas, header=None, names=nomes_colunas)

    except FileNotFoundError:
        print(f"Err: radii file not found.")
        exit()
    except Exception as e:
        print(f"Err to read file: {e}")
        exit()
    return(radii_value)

def set_radii(radii_value):
        """
        Change Radii Values

        Updates the atomic radii values used in occluded surface calculations by
        passing a new table (typically a pandas DataFrame) of values.

        Parameters
        ----------
        radii_values : pandas.DataFrame
            A DataFrame containing atomic radii values. It must follow the same
            structure as the one returned by `get_radii()`.

        See Also
        --------
        get_radii : Retrieve the currently used radii values.
        reset_radii : Reset the radii values to the default configuration.

        Authors
        -------
        - Carlos Henrique da Silveira (carlos.silveira@unifei.edu.br)
        - Herson Hebert Mendes Soares (hersonhebert@hotmail.com)
        - Joao Paulo Roquim Romanelli (joaoromanelli@unifei.edu.br)
        - Patrick Fleming (Pat.Fleming@jhu.edu)

        Examples
        --------
        >>> from fibos import get_radii, set_radii
        >>> radii = get_radii()
        >>> print(radii.head(3))
        >>> radii.at[0, "RAY"] = 2.15  # Modify radius of first atom
        >>> set_radii(radii)
        >>> print(get_radii().head(3))  # Confirm the update
        """
        name_pack = "fibos"
        path_pack = pkgutil.get_loader(name_pack).get_filename()
        path_pack = os.path.dirname(path_pack)
        path_abs = os.path.abspath(path_pack)
        path_radii = path_abs+"/radii"
        try:
            with open(path_radii, 'w') as f:
                for index, row in radii_value.iterrows():
                    linha_formatada = f"{str(row['ATOM']):<11s}{row['RAY']:.2f}\n"
                    f.write(linha_formatada)#

        except Exception as e:
            print(e)
   
def reset_radii():

    """
    Reset Radii Values

    Reloads the default atomic radii values used in occluded surface (OS)
    calculations. This will discard any custom radii previously set using
    `set_radii()` and restore the original default values.

    See Also
    --------
    get_radii : Retrieve the currently used radii values.
    set_radii : Set new atomic radii values from a custom table.

    Authors
    -------
    - Carlos Henrique da Silveira (carlos.silveira@unifei.edu.br)
    - Herson Hebert Mendes Soares (hersonhebert@hotmail.com)
    - Joao Paulo Roquim Romanelli (joaoromanelli@unifei.edu.br)
    - Patrick Fleming (Pat.Fleming@jhu.edu)

    Examples
    --------
    >>> from fibos import get_radii, set_radii, reset_radii
    >>> radii = get_radii()
    >>> print(radii.head(3))  # View current radii
    >>> radii.at[0, "RAY"] = 2.15  # Modify one value
    >>> set_radii(radii)
    >>> print(get_radii().head(3))  # Confirm modification
    >>> reset_radii()
    >>> print(get_radii().head(3))  # Back to default values
    """
    name_pack = "fibos"
    path_pack = pkgutil.get_loader(name_pack).get_filename()
    path_pack = os.path.dirname(path_pack)
    path_abs = os.path.abspath(path_pack)
    path_radii = path_abs+"/radii"
    path_pattern = path_abs+"/pattern"
    os.remove(path_radii)
    shutil.copy(path_pattern,path_radii)
