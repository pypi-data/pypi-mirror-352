import reciprocalspaceship as rs


def fancy_read_mtz(mtzfile):
    """
    Read an mtz using `reciprocalspaceship` and also compute resolution

    Parameters
    ----------
    mtzfile : str
        File path to input mtz

    Returns
    -------
    rs.DataSet
        Data set, including resolution
    """

    mtz = rs.read_mtz(mtzfile)

    mtz.compute_dHKL(inplace=True)

    return mtz


def fancy_read_cif(ciffile):
    """
    Read a cif using `reciprocalspaceship` and also compute resolution

    Parameters
    ----------
    ciffile : str
        File path to input cif

    Returns
    -------
    rs.DataSet
        Data set, including resolution
    """

    cif = rs.read_cif(ciffile)

    cif.compute_dHKL(inplace=True)

    return cif
