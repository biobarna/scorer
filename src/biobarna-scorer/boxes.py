import shapely

"""
 shapely.Polygon that represent interesting regions

The polygons' coordinates are given in the EPSG:4326 coordinate system.
"""

southwest = shapely.geometry.box(-3.2177, 45.8170, 0.5390, 52.0071),
southeast = shapely.geometry.box(0.5390, 45.8170, 4.2956, 52.0071),
northwest = shapely.geometry.box(-3.2177, 52.0071, 0.5390, 55.8117),
northeast = shapely.geometry.box(0.5390, 52.0071, 4.2956, 55.8117),
scotland = shapely.geometry.box(-8.6494, 54.6331, -0.7659, 59.3607),
wales = shapely.geometry.box(-5.2670, 51.2409, -2.6494, 53.4308),
ireland = shapely.geometry.box(-10.6507, 51.2409, -5.2670, 55.8117),
england = shapely.geometry.box(-5.2670, 50.0642, 2.3291, 55.8117),
UK = shapely.geometry.box(-10.6507, 50.0642, 2.3291, 59.3607),
london = shapely.geometry.box(-0.5104, 51.2868, 0.3340, 51.6919),
