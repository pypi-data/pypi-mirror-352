def get_geo_location_master():
    return "/home/catalystRepository/distance_repository/filters/geo_location/zip_codes/sacramento_to_zipcodes_geo_locations.xlsx"
def get_geo_location_master_headers():
    return """COUNTY	COUNTY_closest_latitude	COUNTY_closest_longitude	ZIP	ZIP_closest_latitude	ZIP_closest_longitude	ZIP_COUNTY_closest_distance(mi)	ZIP_furthest_latitude	ZIP_furthest_longitude	ZIP_COUNTY_furthest_distance(mi)""".split('\t')
async def distance_within_range(distance,geo_location_refference=None):
    logging.info(f"distance = {distance}\n\geo_location_refference={geo_location_refference}")
    geo_location_refference = geo_location_refference or get_geo_location_master()
    # Ensure distance is a float
    distance = float(get_number(safe_get(distance, 0)))
    
    # Load geo location data
    df_geo_location = get_df(geo_location_refference)
    
    # Convert ZIP codes to integers, assuming all entries are valid zip codes
    df_geo_location['ZIP'] = df_geo_location['ZIP'].astype(str)
    
    # Convert distances to floats
    df_geo_location['ZIP_COUNTY_furthest_distance(mi)'] = df_geo_location['ZIP_COUNTY_furthest_distance(mi)'].astype(float)
    df_geo_location['ZIP_COUNTY_closest_distance(mi)'] = df_geo_location['ZIP_COUNTY_closest_distance(mi)'].astype(float)
    
    # Create a mask where the distance is within the specified range
    mask = (distance >= df_geo_location['ZIP_COUNTY_closest_distance(mi)']) | (distance >= df_geo_location['ZIP_COUNTY_furthest_distance(mi)'])
    logging.info(f"mask = {mask}")

    # Filter zip codes based on the mask
    good_zips = df_geo_location.loc[mask, 'ZIP'].tolist()
    good_zips=['00000'[:-len(zips)]+str(zips) for zips in good_zips]
    return good_zips
