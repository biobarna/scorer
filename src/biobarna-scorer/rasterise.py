import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from scorer import produce_scores


# rasterization to squares
def create_grid(
        _gdf: gpd.GeoDataFrame = None,
        bounds=None,
        n_cells=10,
        overlap=False,
        crs="EPSG:29902",
) -> gpd.GeoDataFrame:
    """Create square grid that covers a geodataframe area
    or a fixed boundary with x-y coords
    clip: is a list of four coordinate tuples (xmin, ymin, xmax, ymax)
    returns: a GeoDataFrame of grid polygons
    see https://james-brennan.github.io/posts/fast_gridding_geopandas/
    """
    gdf = _gdf
    import geopandas as gpd
    import shapely

    if bounds != None:
        xmin, ymin, xmax, ymax = bounds
    else:
        xmin, ymin, xmax, ymax = gdf.total_bounds

    # get cell size
    cell_size = (xmax - xmin) / n_cells
    # create the cells in a loop
    grid_cells = []
    for x0 in np.arange(xmin, xmax + cell_size, cell_size):
        for y0 in np.arange(ymin, ymax + cell_size, cell_size):
            x1 = x0 - cell_size
            y1 = y0 + cell_size
            poly = shapely.geometry.box(x0, y0, x1, y1)
            # print (gdf.overlay(poly, how='intersection'))
            grid_cells.append(poly)

    cells = gpd.GeoDataFrame(grid_cells, columns=['geometry'],
                             crs=crs)
    if overlap:
        cols = ['grid_id', 'geometry', 'grid_area']
        cells = cells.sjoin(gdf, how='inner').drop_duplicates('geometry')
    return cells


def simplify_habitats(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    gdf = gdf.to_crs("EPSG:4326")  # convert to map coordinates
    # Load metadata
    metadata = pd.read_csv('dataset/corine_biobarna.csv')
    # Create dictionary to replace old labels for new labels
    category_dict = {row['code']: row['level_2_annotations'] for index, row in metadata.iterrows()}
    category_dict = {str(k): v for k, v in category_dict.items()}
    # Replace numeric codes for new categories
    gdf['Code_18'] = gdf['Code_18'].replace(category_dict)
    category_dict_2 = {row['level_2_annotations']: row['biodiversity_score'] for index, row in metadata.iterrows()}
    # Create dictionary to add a new column with the biobarna scores
    gdf['biobarna_biodiv_scr'] = gdf['Code_18'].map(category_dict_2)
    return gdf


# eg: load_rasterised(boxes,southwest], n_cells=90)
# map is a vector GeoDataFrame
def load_rasterised(map: gpd.GeoDataFrame, crop: shapely.geometry.Polygon, n_cells=90) -> gpd.GeoDataFrame:
    vector = map.clip(crop)
    raster = create_grid(vector, n_cells=n_cells, overlap=True, crs="EPSG:4326")
    return raster


def get_scored(box: shapely.geometry.Polygon, n_cells=90) -> gpd.GeoDataFrame:
    raster = load_rasterised(box, n_cells=n_cells)
    return produce_scores(raster)
