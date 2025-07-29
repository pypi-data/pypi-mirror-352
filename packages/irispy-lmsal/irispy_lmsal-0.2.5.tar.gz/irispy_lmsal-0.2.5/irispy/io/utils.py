import tarfile
from pathlib import Path

from astropy.io import fits

from sunpy import log as logger

__all__ = ["fitsinfo", "read_files"]


def fitsinfo(filename):
    """
    Prints information about the extension of a raster or SJI level 2 data
    file.

    Parameters
    ----------
    filename : str
        Filename to load.
    """
    with fits.open(filename) as hdulist:
        hdulist.info()
        hdr = hdulist[0].header
        msg = f"Observation description: {hdr['OBS_DESC']}"
        logger.info(msg)
        modifier = ""
        for i in range(hdr["NWIN"]):
            msg = f"Extension No. {i + 1} stores data and header of {hdr[f'TDESC{i + 1}']}: "
            logger.info(msg)
            if "SJI" not in hdr[f"TDET{i + 1}"]:
                modifier = f" ({hdr[f'TDET{i + 1}'][:3]})"
            msg = f"{hdr[f'TWMIN{i + 1}']:.2f} - {hdr[f'TWMAX{i + 1}']:.2f} AA{modifier}"
            logger.info(msg)


def read_files(filename, *, spectral_windows=None, uncertainty=False, memmap=False, **kwargs):
    """
    A wrapper function to read a raster or SJI level 2 data file.

    You can provide one SJI image or a one raster image or a list of raster images.

    If you mix raster and SJI images, the function will raise an error.

    Parameters
    ----------
    filename : `list of `str`, `str`, `pathlib.Path`
        Filename(s) to load.
        If given a string, will load that file.
        If given a list of strings, it will check they are all raster files and load them.
    spectral_windows: iterable of `str` or `str`
        Spectral windows to extract from files. Default=None, implies, extract all
        spectral windows.
    uncertainty : `bool`, optional
        If `True` (not the default), will compute the uncertainty for the data (slower and
        uses more memory). If `memmap=True`, the uncertainty is never computed.
    memmap : `bool`, optional
        If `True` (not the default), will not load arrays into memory, and will only read from
        the file into memory when needed. This option is faster and uses a
        lot less memory. However, because FITS scaling is not done on-the-fly,
        the data units will be unscaled, not the usual data numbers (DN).
    kwargs : `dict`, optional
        Additional keyword arguments to pass to the reader functions.

    Returns
    -------
    The corresponding `irispy.sji.SJICube` or `irispy.spectrogram.SpectrogramCube`.
    """
    from irispy.io.sji import read_sji_lvl2
    from irispy.io.spectrograph import read_spectrograph_lvl2

    if isinstance(filename, Path):
        filename = str(filename)
    if isinstance(filename, str | Path):
        if tarfile.is_tarfile(filename):
            path = Path(filename.replace(".tar.gz", ""))
            path.mkdir(parents=True, exist_ok=True)
            with tarfile.open(filename, "r") as tar:
                tar.extractall(path, filter="data")
                filename = [path / file for file in tar.getnames()]
        else:
            filename = [filename]
    intrume = fits.getval(filename[0], "INSTRUME")
    all_instrume = [fits.getval(f, "INSTRUME") for f in filename]
    if any(intrume != i for i in all_instrume):
        msg = "You cannot mix raster and SJI files."
        raise ValueError(msg)
    if intrume == "SJI":
        if len(filename) > 1:
            msg = "You cannot load more than one SJI file at a time."
            raise ValueError(msg)
        return read_sji_lvl2(filename[0], memmap=memmap, uncertainty=uncertainty, **kwargs)
    if intrume == "SPEC":
        return read_spectrograph_lvl2(
            filename,
            spectral_windows=spectral_windows,
            memmap=memmap,
            uncertainty=uncertainty,
            **kwargs,
        )
    msg = f"Unsupported instrument: {intrume}"
    raise ValueError(msg)
