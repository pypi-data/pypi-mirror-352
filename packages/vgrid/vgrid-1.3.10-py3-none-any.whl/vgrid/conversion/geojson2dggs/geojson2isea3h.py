import argparse, json, os
from tqdm import tqdm
from shapely.geometry import Polygon, box, Point, LineString
from vgrid.generator.settings import geodesic_dggs_to_feature
import platform

if (platform.system() == 'Windows'): 
    from vgrid.utils.eaggr.eaggr import Eaggr
    from vgrid.utils.eaggr.shapes.dggs_cell import DggsCell
    from vgrid.utils.eaggr.enums.model import Model
    from vgrid.utils.eaggr.enums.shape_string_format import ShapeStringFormat
    from vgrid.utils.eaggr.shapes.lat_long_point import LatLongPoint
    from vgrid.generator.isea3hgrid import isea3h_cell_to_polygon, isea3h_res_accuracy_dict, isea3h_accuracy_res_dict, get_isea3h_children_cells_within_bbox
    from vgrid.conversion.dggscompact import isea3h_compact
    
from pyproj import Geod
geod = Geod(ellps="WGS84")
from shapely.geometry import Polygon,mapping


# Function to generate grid for Point
def point_to_grid(isea3h_dggs,resolution, point,feature_properties):
    if (platform.system() == 'Windows'):
        isea3h_features = []   
        accuracy = isea3h_res_accuracy_dict.get(resolution)
        lat_long_point = LatLongPoint(point.y, point.x, accuracy)
        isea3h_cell = isea3h_dggs.convert_point_to_dggs_cell(lat_long_point)
        cell_polygon = isea3h_cell_to_polygon(isea3h_dggs,isea3h_cell)
        
        if cell_polygon:
            isea3h_id = isea3h_cell.get_cell_id() 
            cell_resolution = resolution
            num_edges = 3 if cell_resolution == 0 else 6       
            isea4t_feature = geodesic_dggs_to_feature("isea3h",isea3h_id,cell_resolution,cell_polygon,num_edges)   
            isea4t_feature["properties"].update(feature_properties)
            isea3h_features.append(isea4t_feature)
       
        return {
            "type": "FeatureCollection",
            "features": isea3h_features,
        }

def poly_to_grid(isea3h_dggs,resolution, geometry, feature_properties,compact):    
    if (platform.system() == 'Windows'):
        isea3h_features = []
        if geometry.geom_type == 'LineString' or geometry.geom_type == 'Polygon':
            polys = [geometry]
        elif geometry.geom_type == 'MultiLineString' or geometry.geom_type == 'MultiPolygon':
            polys = list(geometry)

        for poly in polys:
            accuracy = isea3h_res_accuracy_dict.get(resolution)
            bounding_box = box(*poly.bounds)
            bounding_box_wkt = bounding_box.wkt  # Create a bounding box polygon
            shapes = isea3h_dggs.convert_shape_string_to_dggs_shapes(bounding_box_wkt, ShapeStringFormat.WKT, accuracy)
            shape =  shapes[0]
            # for shape in shapes:
            bbox_cells = shape.get_shape().get_outer_ring().get_cells()
            bounding_cell = isea3h_dggs.get_bounding_dggs_cell(bbox_cells)
            bounding_child_cells = get_isea3h_children_cells_within_bbox(isea3h_dggs,bounding_cell.get_cell_id(), bounding_box,resolution)
            if compact:
                bounding_child_cells = isea3h_compact(isea3h_dggs,bounding_child_cells)

            for child in bounding_child_cells:
                isea3h_cell = DggsCell(child)
                cell_polygon = isea3h_cell_to_polygon(isea3h_dggs,isea3h_cell)
                if cell_polygon.intersects(poly):
                    isea3h_id = isea3h_cell.get_cell_id()
                    isea3h2point = isea3h_dggs.convert_dggs_cell_to_point(isea3h_cell)      
                    cell_accuracy = isea3h2point._accuracy        
                    cell_resolution  = isea3h_accuracy_res_dict.get(cell_accuracy)                    
                    num_edges = 3 if cell_resolution == 0 else 6  
                         
                    isea4t_feature = geodesic_dggs_to_feature("isea3h",isea3h_id,cell_resolution,cell_polygon,num_edges)   
                    isea4t_feature["properties"].update(feature_properties)
                    isea3h_features.append(isea4t_feature)
       
        return {
            "type": "FeatureCollection",
            "features": isea3h_features,
        }
            
def main():
    parser = argparse.ArgumentParser(description="Convert GeoJSON to Open-Eaggr ISEA3H DGGS")
    parser.add_argument('-r', '--resolution', type=int, required=True, help="Resolution [0..32]")
    # actual resolution range: [0..40]
    parser.add_argument(
        '-geojson', '--geojson', type=str, required=True, help="GeoJSON file path (Point, Polyline or Polygon)"
    )
    parser.add_argument('-compact', action='store_true', help="Enable ISEA4T compact mode")

    if (platform.system() == 'Windows'): 
        isea3h_dggs = Eaggr(Model.ISEA3H)
        args = parser.parse_args()
        geojson = args.geojson
        resolution = args.resolution
        compact = args.compact
        
        if resolution < 0 or resolution > 32:
            print(f"Please select a resolution in [0..32] range and try again ")
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
                    point_features = point_to_grid(isea3h_dggs,resolution, point,feature_properties)
                    geojson_features.extend(point_features['features'])

                elif feature['geometry']['type'] == 'MultiPoint':
                    for point_coords in coordinates:
                        point = Point(point_coords)  # Create Point for each coordinate set
                        point_features = point_to_grid(isea3h_dggs,resolution, point,feature_properties)
                        geojson_features.extend(point_features['features'])
            
            elif feature['geometry']['type'] in ['LineString', 'MultiLineString']:
                coordinates = feature['geometry']['coordinates']
                if feature['geometry']['type'] == 'LineString':
                    # Directly process LineString geometry
                    polyline = LineString(coordinates)
                    polyline_features = poly_to_grid(isea3h_dggs,resolution, polyline,feature_properties)
                    geojson_features.extend(polyline_features['features'])

                elif feature['geometry']['type'] == 'MultiLineString':
                    # Iterate through each line in MultiLineString geometry
                    for line_coords in coordinates:
                        polyline = LineString(line_coords)  # Use each part's coordinates
                        polyline_features = poly_to_grid(isea3h_dggs,resolution, polyline,feature_properties)
                        geojson_features.extend(polyline_features['features'])
                
            elif feature['geometry']['type'] in ['Polygon', 'MultiPolygon']:
                coordinates = feature['geometry']['coordinates']

                if feature['geometry']['type'] == 'Polygon':
                    # Create Polygon with exterior and interior rings
                    exterior_ring = coordinates[0]  # The first coordinate set is the exterior ring
                    interior_rings = coordinates[1:]  # Remaining coordinate sets are interior rings (holes)
                    polygon = Polygon(exterior_ring, interior_rings)
                    polygon_features = poly_to_grid(isea3h_dggs,resolution, polygon,feature_properties,compact)
                    geojson_features.extend(polygon_features['features'])

                elif feature['geometry']['type'] == 'MultiPolygon':
                    # Handle each sub-polygon in MultiPolygon geometry
                    for sub_polygon_coords in coordinates:
                        exterior_ring = sub_polygon_coords[0]  # The first coordinate set is the exterior ring
                        interior_rings = sub_polygon_coords[1:]  # Remaining coordinate sets are interior rings (holes)
                        polygon = Polygon(exterior_ring, interior_rings)
                        polygon_features = poly_to_grid(isea3h_dggs,resolution, polygon,feature_properties,compact)
                        geojson_features.extend(polygon_features['features'])

                        
        geojson_name = os.path.splitext(os.path.basename(geojson))[0]
        geojson_path = f"{geojson_name}2isea3h_{resolution}.geojson"
        if compact:
            geojson_path = f"{geojson_name}2isea3h_{resolution}_compacted.geojson"

        with open(geojson_path, 'w') as f:
            json.dump({"type": "FeatureCollection", "features": geojson_features}, f, indent=2)

        print(f"GeoJSON saved as {geojson_path}")


if __name__ == "__main__":
    main()