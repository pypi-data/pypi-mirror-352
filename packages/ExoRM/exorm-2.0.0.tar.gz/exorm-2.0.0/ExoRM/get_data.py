def get_data():
    from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
    from ExoRM import get_exorm_filepath
    import os

    directory = get_exorm_filepath('ExoRM')
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Confirmed Exoplanet Query
    table = NasaExoplanetArchive.query_criteria(
        table = 'PS',
        select = 'pl_name, pl_bmasse, pl_rade, disc_year, pl_controv_flag'
    )

    data = table.to_pandas()

    data.to_csv(get_exorm_filepath('exoplanet_data.csv'), index = False)

    # Creating Radius and Mass Data
    data = data[data['pl_controv_flag'] == 0]
    data['radius'] = data['pl_rade']
    data['mass'] = data['pl_bmasse']
    data['name'] = data['pl_name']
    data = data[data['radius'].notna() & data['mass'].notna()]

    data = data.sort_values(by = ['pl_name', 'disc_year'], ascending = [True, False])
    data = data.drop_duplicates(subset = 'pl_name').reset_index(drop = True)

    rm = data[['name', 'radius', 'mass']]
    rm.to_csv(get_exorm_filepath('exoplanet_rm.csv'), index = False)