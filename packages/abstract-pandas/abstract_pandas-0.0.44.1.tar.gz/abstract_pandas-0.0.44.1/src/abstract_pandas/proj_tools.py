from pyproj import CRS
import logging
import geopandas as gpd
def is_wkt_string(value: str) -> bool:
    """
    Check if the provided string is a valid WKT representation of a CRS.

    Args:
    - value (str): The string to be tested.

    Returns:
    - bool: True if the string is a valid WKT, False otherwise.
    """
    try:
        # Try to create a CRS object from the WKT string
        crs = CRS.from_wkt(value)
        logging.info("Valid WKT string for CRS.")
        return True
    except Exception as e:
        logging.error(f"Invalid WKT string: {e}")
        return False
def get_crs(crs):
    if crs is not None and isinstance(crs,str) and os.path.isfile(crs):
        crs = get_df(crs)
    if isinstance(crs, gpd.GeoDataFrame):
        try:
            crs = crs.crs
        except Exception as e:
            logging.warning(f"crs conversion failed: {e}")
    if is_wkt_string(crs):
        crs = CRS.from_wkt(crs)
    return crs
    
def get_wkt_string(crs):
    # Extract the CRS if provided as a GeoDataFrame
    if isinstance(crs, CRS):
        wkt_string = crs.to_wkt()
    else:
        # Assume the input is a WKT string and attempt to parse it
        wkt_string = CRS.from_wkt(crs).to_wkt()
    return wkt_string
def correct_prj(prj_path, default_epsg=4326):
    is_valid, crs = validate_prj(prj_path)
    if is_valid:
        return crs

    logging.warning(f"Attempting to set default EPSG code: {default_epsg}")
    corrected_crs = CRS.from_epsg(default_epsg)

    # Save the corrected CRS
    with open(prj_path, "w") as file:
        file.write(corrected_crs.to_wkt())

    return corrected_crs

def validate_prj(prj_path):
    try:
        logging.warning(f"validating .prj: {prj_path}")
        # Attempt to load the CRS
        with open(prj_path, "r") as file:
            prj_content = file.read()
        crs = CRS.from_wkt(prj_content)
        logging.info("CRS is valid.")
        return True, crs
    except Exception as e:
        logging.error(f"Invalid CRS: {e}")
        return False, None
def save_valid_crs(crs: CRS, file_path: str):
    """
    Save the CRS to a .prj file if it is valid.

    Args:
        crs: A valid pyproj CRS object, a GeoDataFrame, or WKT string.
        file_path: Path to save the .prj file.
    """
    try:
        crs = get_crs(crs)
        wkt_string = get_wkt_string(crs)
        # Write the WKT string to the specified file
        with open(file_path, "w") as file:
            file.write(wkt_string)

        # Validate by reading it back
        loaded_crs = CRS.from_wkt(wkt_string)
        logging.info(f"Successfully saved and verified CRS at {file_path}")

    except Exception as e:
        logging.error(f"Error saving CRS: {e}")

