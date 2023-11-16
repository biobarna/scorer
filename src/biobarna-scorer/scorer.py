import rasterio
import geopandas as gpd


def _open_cropped_density_dataset(cropped_density_dataset_path):
    # Open the TIFF file
    dataset = rasterio.open(cropped_density_dataset_path)
    return dataset


def _open_cropped_endangered_dataset(endangered_species_path):
    # Open the TIFF file
    dataset = rasterio.open(endangered_species_path)
    return dataset


def _get_value_from_coords(dataset, lon, lat):
    # Convert geographic coordinates to raster indices
    row, col = dataset.index(lon, lat)

    # Read the value at the indices
    value = dataset.read(1)[row, col]
    return value


def _find_centroid_from_polygon(polygon):
    return polygon.centroid.coords.xy[0][0], polygon.centroid.coords.xy[1][0]  # finds xy coordinates of centroid


def _biodiv_score(habitat, density, endangered1, endangered2, habitat_coeff=0.9, density_coeff=0.05,
                  endangered1_coeff=0.025, endangered2_coeff=0.025):
    return habitat_coeff * habitat + density_coeff * density + endangered1_coeff * endangered1 + endangered1_coeff * endangered2


def produce_scores(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    takes a rasterised geodataframe
    returns the same dataframe with a score column: 'biodiv_score'
    """
    # make dummy

    # open three datasets
    density_output_path = 'dataset/density_population/cropped_ppp_2020_1km_Aggregated.tif'
    cropped_dataset_density = _open_cropped_density_dataset(density_output_path)

    endangered1_path = 'dataset/Endangered_species/Theoretically_coordinate_changed_gifs/cropped_new_Combined_RWR_2022.tif'
    cropped_dataset_endangered1 = _open_cropped_endangered_dataset(endangered1_path)

    endangered2_path = 'dataset/Endangered_species/Theoretically_coordinate_changed_gifs/cropped_new_Combined_THR_RWR_2022.tif'
    cropped_dataset_endangered2 = _open_cropped_endangered_dataset(endangered2_path)

    # add columns from datasets
    gdf['centroid_coordinates'] = gdf['geometry'].apply(_find_centroid_from_polygon)
    gdf['density'] = gdf['centroid_coordinates'].apply(
        lambda x: _get_value_from_coords(cropped_dataset_density, x[0], x[1]))
    gdf['endangered1'] = gdf['centroid_coordinates'].apply(
        lambda x: _get_value_from_coords(cropped_dataset_endangered1, x[0], x[1]))
    gdf['endangered2'] = gdf['centroid_coordinates'].apply(
        lambda x: _get_value_from_coords(cropped_dataset_endangered2, x[0], x[1]))

    # scale score to 0-1 %TODO fix this
    gdf_scaled = gdf.copy()
    for col in ['density', 'endangered1', 'endangered2']:
        gdf_scaled[col] = (gdf_scaled[col] - gdf_scaled[col].min()) / (gdf_scaled[col].max() - gdf_scaled[col].min())

        # calculate score
    gdf_scaled['biodiv_score'] = gdf_scaled.apply(
        lambda row: _biodiv_score(row['biobarna_biodiv_scr'], row['density'], row['endangered1'], row['endangered2']),
        axis=1)
    gdf_selected_columns = gdf_scaled[['geometry', 'Code_18', 'Area_Ha', 'biodiv_score']]

    return gdf_selected_columns
