import argparse
import json
from tqdm import tqdm
from vgrid.utils.rhealpixdggs.dggs import RHEALPixDGGS
from vgrid.utils.rhealpixdggs.utils import my_round
from vgrid.utils.rhealpixdggs.conversion import compress_order_cells, get_finest_containing_cell
from shapely.geometry import Polygon, box, Point, LineString
import os
from vgrid.generator.rhealpixgrid import fix_rhealpix_antimeridian_cells
from vgrid.generator.settings import geodesic_dggs_to_feature
from vgrid.conversion.dggscompact import rhealpix_compact 


# Function to convert cell vertices to a Shapely Polygon
def rhealpix_cell_to_polygon(cell):
    vertices = [tuple(my_round(coord, 14) for coord in vertex) for vertex in cell.vertices(plane=False)]
    if vertices[0] != vertices[-1]:
        vertices.append(vertices[0])
    vertices = fix_rhealpix_antimeridian_cells(vertices)
    return Polygon(vertices)

# Function to generate grid for Point
def point_to_grid(rhealpix_dggs, resolution, point,feature_properties):
    rhealpix_features = []
    # Convert point to the seed cell
    seed_cell = rhealpix_dggs.cell_from_point(resolution, (point.x, point.y), plane=False)    
    seed_cell_polygon = rhealpix_cell_to_polygon(seed_cell)    
    if seed_cell_polygon:
        seed_cell_id = str(seed_cell)  # Unique identifier for the current cell
        num_edges = 4
        if seed_cell.ellipsoidal_shape() == 'dart':
            num_edges = 3
        rhealpix_feature = geodesic_dggs_to_feature("rhealpix",seed_cell_id,resolution,seed_cell_polygon,num_edges)   
        rhealpix_feature["properties"].update(feature_properties)
        rhealpix_features.append(rhealpix_feature)

    return {
        "type": "FeatureCollection",
        "features": rhealpix_features
    }  
 

def poly_to_grid(rhealpix_dggs, resolution, geometry,feature_properties, compact = None):
    rhealpix_features = []
    if geometry.geom_type == 'LineString' or geometry.geom_type == 'Polygon' :
        polys = [geometry]
    elif geometry.geom_type == 'MultiLineString' or geometry.geom_type == 'MultiPolygon' :
        polys = list(geometry)

    for poly in polys:
        minx, miny, maxx, maxy = poly.bounds
        # Create a bounding box polygon
        bbox_polygon = box(minx, miny, maxx, maxy)

        bbox_center_lon = bbox_polygon.centroid.x
        bbox_center_lat = bbox_polygon.centroid.y
        seed_point = (bbox_center_lon, bbox_center_lat)

        seed_cell = rhealpix_dggs.cell_from_point(resolution, seed_point, plane=False)
        seed_cell_id = str(seed_cell)  # Unique identifier for the current cell
        seed_cell_polygon = rhealpix_cell_to_polygon(seed_cell)

        if seed_cell_polygon.contains(bbox_polygon):
            num_edges = 4
            if seed_cell.ellipsoidal_shape() == 'dart':
                num_edges = 3
            cell_resolution = resolution
            rhealpix_feature = geodesic_dggs_to_feature("rhealpix",seed_cell_id,cell_resolution,seed_cell_polygon,num_edges)   
            rhealpix_feature["properties"].update(feature_properties)
            rhealpix_features.append(rhealpix_feature)

            return {
                "type": "FeatureCollection",
                "features": rhealpix_features
            }  
       

        else:
            # Initialize sets and queue
            covered_cells = set()  # Cells that have been processed (by their unique ID)
            queue = [seed_cell]  # Queue for BFS exploration
            while queue:
                current_cell = queue.pop()
                current_cell_id = str(current_cell)  # Unique identifier for the current cell

                if current_cell_id in covered_cells:
                    continue

                # Add current cell to the covered set
                covered_cells.add(current_cell_id)

                # Convert current cell to polygon
                cell_polygon = rhealpix_cell_to_polygon(current_cell)

                # Skip cells that do not intersect the bounding box
                if not cell_polygon.intersects(bbox_polygon):
                    continue

                # Get neighbors and add to queue
                neighbors = current_cell.neighbors(plane=False)
                for _, neighbor in neighbors.items():
                    neighbor_id = str(neighbor)  # Unique identifier for the neighbor
                    if neighbor_id not in covered_cells:
                        queue.append(neighbor)
            if compact:
                # need to recheck
                covered_cells = rhealpix_compact(rhealpix_dggs,covered_cells)

            for cell_id in covered_cells:
                rhealpix_uids = (cell_id[0],) + tuple(map(int, cell_id[1:]))
                rhelpix_cell = rhealpix_dggs.cell(rhealpix_uids)   
                cell_resolution = rhelpix_cell.resolution
                cell_polygon = rhealpix_cell_to_polygon(rhelpix_cell)
                if cell_polygon.intersects(poly):
                    num_edges = 4
                    if seed_cell.ellipsoidal_shape() == 'dart':
                        num_edges = 3
                    rhealpix_feature = geodesic_dggs_to_feature("rhealpix",str(cell_id),cell_resolution, cell_polygon,num_edges)   
                    rhealpix_feature["properties"].update(feature_properties)
                    rhealpix_features.append(rhealpix_feature)                
    return {
        "type": "FeatureCollection",
        "features": rhealpix_features,
    }


# Main function to handle different GeoJSON shapes
def main():
    parser = argparse.ArgumentParser(description="Convert GeoJSON to rHEALPix DGGS")
    parser.add_argument('-r', '--resolution', type=int, required=True, help="Resolution [0..15]")
    parser.add_argument(
        '-geojson', '--geojson', type=str, required=True, help="GeoJSON file path (Point, Polyline or Polygon)"
    )
    parser.add_argument('-compact', action='store_true', help="Enable H3 compact mode - for polygon only")

    args = parser.parse_args()
    geojson = args.geojson
     # Initialize RHEALPix DGGS
    rhealpix_dggs = RHEALPixDGGS()
    resolution = args.resolution
    compact = args.compact  
    
    if resolution < 0 or resolution > 15:
        print(f"Please select a resolution in [0..15] range and try again ")
        return
    
    if not os.path.exists(geojson):
        print(f"Error: The file {geojson} does not exist.")
        return

    with open(geojson, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
    
    geojson_features = []

    for feature in tqdm(geojson_data['features'], desc="Processing GeoJSON features"):  
        feature_properties = feature['properties']   
        if feature['geometry']['type'] in ['Point', 'MultiPoint']:
            coordinates = feature['geometry']['coordinates']
            if feature['geometry']['type'] == 'Point':
                point = Point(coordinates)
                point_features = point_to_grid(rhealpix_dggs, resolution, point,feature_properties)
                geojson_features.extend(point_features['features'])

            elif feature['geometry']['type'] == 'MultiPoint':
                for point_coords in coordinates:
                    point = Point(point_coords)  # Create Point for each coordinate set
                    point_features = point_to_grid(rhealpix_dggs, resolution, point,feature_properties)
                    geojson_features.extend(point_features['features'])
        
        elif feature['geometry']['type'] in ['LineString', 'MultiLineString']:
            coordinates = feature['geometry']['coordinates']
            if feature['geometry']['type'] == 'LineString':
                # Directly process LineString geometry
                polyline = LineString(coordinates)
                polyline_features = poly_to_grid(rhealpix_dggs, resolution, polyline,feature_properties)
                geojson_features.extend(polyline_features['features'])

            elif feature['geometry']['type'] == 'MultiLineString':
                # Iterate through each line in MultiLineString geometry
                for line_coords in coordinates:
                    polyline = LineString(line_coords)  # Use each part's coordinates
                    polyline_features = poly_to_grid(rhealpix_dggs, resolution, polyline,feature_properties)
                    geojson_features.extend(polyline_features['features'])
            
        elif feature['geometry']['type'] in ['Polygon', 'MultiPolygon']:
            coordinates = feature['geometry']['coordinates']

            if feature['geometry']['type'] == 'Polygon':
                # Create Polygon with exterior and interior rings
                exterior_ring = coordinates[0]  # The first coordinate set is the exterior ring
                interior_rings = coordinates[1:]  # Remaining coordinate sets are interior rings (holes)
                polygon = Polygon(exterior_ring, interior_rings)
                polygon_features = poly_to_grid(rhealpix_dggs, resolution, polygon,feature_properties,compact)
                geojson_features.extend(polygon_features['features'])

            elif feature['geometry']['type'] == 'MultiPolygon':
                # Handle each sub-polygon in MultiPolygon geometry
                for sub_polygon_coords in coordinates:
                    exterior_ring = sub_polygon_coords[0]  # The first coordinate set is the exterior ring
                    interior_rings = sub_polygon_coords[1:]  # Remaining coordinate sets are interior rings (holes)
                    polygon = Polygon(exterior_ring, interior_rings)
                    polygon_features = poly_to_grid(rhealpix_dggs, resolution, polygon,feature_properties,compact)
                    geojson_features.extend(polygon_features['features'])

                    
    # Save the results to GeoJSON
    geojson_name = os.path.splitext(os.path.basename(geojson))[0]
    geojson_path = f"{geojson_name}2rhealpix_{resolution}.geojson"
    if compact:
        geojson_path = f"{geojson_name}2rhealpix_{resolution}_compacted.geojson"
        
    with open(geojson_path, 'w') as f:
        json.dump({"type": "FeatureCollection", "features": geojson_features}, f, indent=2)

    print(f"GeoJSON saved as {geojson_path}")



if __name__ == "__main__":
    main()
