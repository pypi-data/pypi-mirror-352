from math import sin, cos, asin, atan2, radians, degrees, pi,atan2, sqrt
def earth_radius(metric='miles'):
    return {"miles":3958.756,"KM":6371}.get(metric,3958.756)
def get_coordinates(lat_center,lon_center,metric='miles'):
    # Constants
    earth_radius = get_metric(metric=metric)  # Earth's radius in kilometers

    # Convert central point to radians
    lat_center_rad = radians(lat_center)
    lon_center_rad = radians(lon_center)

    # Calculate coordinates at intervals of 45 degrees around the circumference
    coordinates = []
    for angle in range(0, 360, 45):
        theta = radians(angle)  # Convert angle to radians
        d_over_r = radius_km / earth_radius_km  # Distance over Earth's radius

        # Calculate latitude of the point
        lat_rad = asin(sin(lat_center_rad) * cos(d_over_r) + cos(lat_center_rad) * sin(d_over_r) * cos(theta))
        # Calculate longitude of the point
        lon_rad = lon_center_rad + atan2(sin(theta) * sin(d_over_r) * cos(lat_center_rad), cos(d_over_r) - sin(lat_center_rad) * sin(lat_rad))

        # Convert back to degrees
        lat_deg = degrees(lat_rad)
        lon_deg = degrees(lon_rad)

        coordinates.append((lat_deg, lon_deg))

    return coordinates
def point_of_origin(src_longitude,src_latitude,dest_longitude,lat_center,lon_center,radius,dest_latitude,metric='miles'):
   

    # Placeholder outside point (using an example, please replace with the actual point)
    # Constants
    earth_radius = earth_radius(metric='miles')  # Earth's radius in kilometers

    # Convert central point to radians
    lat_center_rad = radians(lat_center)
    lon_center_rad = radians(lon_center)
    # Convert to radians
    lat_p_rad = radians(lat_p)
    lon_p_rad = radians(lon_p)

    # Calculate delta longitude
    delta_lon = lon_p_rad - lon_center_rad

    # Calculate bearing from center to outside point
    bearing = atan2(sin(delta_lon) * cos(lat_p_rad), cos(lat_center_rad) * sin(lat_p_rad) - sin(lat_center_rad) * cos(lat_p_rad) * cos(delta_lon))

    # Normalize bearing to be between 0 and 2π
    bearing = (bearing + 2 * pi) % (2 * pi)

    # Calculate coordinates on the circumference using the bearing and the formula from the previous explanation
    lat_x_rad = asin(sin(lat_center_rad) * cos(radius / earth_radius) + cos(lat_center_rad) * sin(radius / earth_radius) * cos(bearing))
    lon_x_rad = lon_center_rad + atan2(sin(bearing) * sin(radius / earth_radius) * cos(lat_center_rad), cos(radius / earth_radius) - sin(lat_center_rad) * sin(lat_x_rad))

    # Convert back to degrees
    lat_x_deg = degrees(lat_x_rad)
    lon_x_deg = degrees(lon_x_rad)

    return lat_x_deg, lon_x_deg
def haversine(lat1, lon1, lat2, lon2,metric='miles'):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    
    # Convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula 
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a)) 
    distance = earth_radius(metric='miles') * c  # Earth's radius in kilometers
    return distance

def get_closest_boudary(D_lat, D_lon, boundary_polygon=None):
    boundary_polygon = get_bp(boundary_polygon)
    # Assuming read_excel_as_dicts is meant to read Excel file and convert it into a list of dictionaries
    # Assuming each dict has 'lat' and 'lon' keys
    closest_point = None
    shortest_distance = float('inf')
    for i,dist in enumerate(boundary_polygon):
        lat, lon = dist[0], dist[1]

        distance = haversine(D_lat, D_lon, lat, lon)
        if distance < shortest_distance:
            shortest_distance = distance
            closest_point = (lat, lon)
    
    return shortest_distance, closest_point
def get_furthest_boundary(D_lat, D_lon, polygon,shortest_distance):
    # Assuming read_excel_as_dicts is meant to read Excel file and convert it into a list of dictionaries
    # Assuming each dict has 'lat' and 'lon' keys
    closest_point = None
    shortest_distance = shortest_distance
    for i,dist in enumerate(polygon):
        lat, lon = dist[0], dist[1]
        distance = haversine(D_lat, D_lon, lat, lon)
        if distance > shortest_distance:
            shortest_distance = distance
            closest_point = (lat, lon)

    return shortest_distance, closest_point
def is_point_inside_polygon(point_lat, point_lon, polygon):
    """
    Determine if a point is inside a given polygon or not.
    
    Polygon is a list of (latitude, longitude) tuples, and point is defined by (point_lat, point_lon).
    """
    num = len(polygon)
    inside = False

    x, y = point_lon, point_lat
    if None not in [x,y]:
        p1x, p1y = polygon[0]
        for i in range(num+1):
            p2x, p2y = polygon[i % num]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
            p1x, p1y = p2x, p2y

    return inside

def calculate_shortest_distance_points(polygon1, polygon2):
    """
    Calculate the shortest distance between two polygons and return the points on each
    polygon that are closest to each other.
    
    Args:
    polygon1 (list): A list of (lat, lon) tuples for the first polygon.
    polygon2 (list): A list of (lat, lon) tuples for the second polygon.
    
    Returns:
    tuple: The closest points on each polygon and the distance between them.
    """
    
    # Convert the list of points to Shapely Polygons
    poly1 = Polygon(polygon1)
    poly2 = Polygon(polygon2)
    
    # Initialize variables to store the closest points and minimum distance
    min_distance = float('inf')
    closest_point_poly1 = None
    closest_point_poly2 = None
    
    # Compare each point in polygon1 to each point in polygon2
    for point1 in poly1.exterior.coords:
        for point2 in poly2.exterior.coords:
            # Create Shapely Points for each point
            spoint1 = Point(point1)
            spoint2 = Point(point2)
            # Calculate the distance between the points
            distance = spoint1.distance(spoint2)
            # If this is the shortest distance so far, update the minimum distance and points
            if distance < min_distance:
                min_distance = distance
                closest_point_poly1 = spoint1
                closest_point_poly2 = spoint2
    
    # Return the closest points and the distance between them
    return (closest_point_poly1, closest_point_poly2, min_distance)
# Pseudocode for Determining Polygon Relationship to a Static Reference Polygon Based on Driving Distance

def calculate_polygon_relationship(static_polygon, input_polygon, driving_distance_threshold):
    # Step 1: Find the shortest distance point in static polygon to any point in input polygon
    shortest_distance, closest_point_static = get_closest_boundary(D_lat, D_lon, static_polygon)

    # Step 2: Find the farthest distance point in static polygon to the same point in input polygon
    farthest_distance, farthest_point_static = get_farthest_boundary(D_lat, D_lon, static_polygon)

    # Step 3: Calculate driving distance for the shortest distance points
    driving_distance_closest = async_calculate_driving_distance(closest_point_static, input_polygon)

    # Step 4: If driving distance for the closest points is within the threshold, classify as "within"
    if driving_distance_closest <= driving_distance_threshold:
        return "within"

    # Step 5: If not within, calculate driving distance for the farthest distance points
    driving_distance_farthest = async_calculate_driving_distance(farthest_point_static, input_polygon)

    # Step 6: Classify the relationship based on driving distances
    if driving_distance_closest < driving_distance_threshold < driving_distance_farthest:
        return "partially within"
    else:
        return "outside"



