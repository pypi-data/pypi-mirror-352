def get_data():
    from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
    from ExoRM import get_exorm_filepath
    import os
    import pandas
    import numpy

    directory = get_exorm_filepath('ExoRM')
    if not os.path.exists(directory):
        os.makedirs(directory)

    MASS_FILTER = 0.25
    RADIUS_FILTER = 0.1

    MASS_FILTER_EDGE = 0.5
    RADIUS_FILTER_EDGE = 0.2

    table = NasaExoplanetArchive.query_criteria(
        table = 'PS',
        select = 'pl_name, pl_bmasse, pl_rade, disc_year, pl_controv_flag, pl_bmasseerr1, pl_bmasseerr2, pl_radeerr1, pl_radeerr2, soltype',
        where = '''soltype='Published Confirmed' AND pl_bmasse IS NOT NULL AND pl_rade IS NOT NULL AND disc_year > 2000 AND pl_controv_flag = 0'''
    )

    data = table.to_pandas()
    low_bound = numpy.percentile(data['pl_rade'], 10)
    high_bound = numpy.percentile(data['pl_rade'], 90)

    data = data[
        ((data['pl_rade'] < low_bound) | (data['pl_rade'] > high_bound)) &
        (abs(data['pl_bmasseerr1'] / data['pl_bmasse']) < MASS_FILTER_EDGE) &
        (abs(data['pl_bmasseerr2'] / data['pl_bmasse']) < MASS_FILTER_EDGE) &
        (abs(data['pl_radeerr1'] / data['pl_rade']) < RADIUS_FILTER_EDGE) &
        (abs(data['pl_radeerr2'] / data['pl_rade']) < RADIUS_FILTER_EDGE)
        |
        ((data['pl_rade'] >= 1) & (data['pl_rade'] <= 17.5)) &
        (abs(data['pl_bmasseerr1'] / data['pl_bmasse']) < MASS_FILTER) &
        (abs(data['pl_bmasseerr2'] / data['pl_bmasse']) < MASS_FILTER) &
        (abs(data['pl_radeerr1'] / data['pl_rade']) < RADIUS_FILTER) &
        (abs(data['pl_radeerr2'] / data['pl_rade']) < RADIUS_FILTER)
    ]

    data.to_csv(get_exorm_filepath('exoplanet_data.csv'), index = False)

    data['error'] = (
        abs(data['pl_bmasseerr1'] / data['pl_bmasse']) +
        abs(data['pl_bmasseerr2'] / data['pl_bmasse']) +
        abs(data['pl_radeerr1'] / data['pl_rade']) +
        abs(data['pl_radeerr2'] / data['pl_rade'])
    ) / 4

    data = data.groupby('pl_name', group_keys = False).apply(
        lambda g: g[g['disc_year'] > 2010].loc[g[g['disc_year'] > 2010]['error'].idxmin()]
        if (g['disc_year'] > 2010).any()
        else g.loc[g['error'].idxmin()]
    )

    # data = data.sort_values(by = ['pl_name', 'disc_year'], ascending = [True, False])
    # data = data.drop_duplicates(subset = 'pl_name').reset_index(drop = True)

    data['radius'] = data['pl_rade']
    data['mass'] = data['pl_bmasse']
    data['name'] = data['pl_name']
    rm = data[['name', 'radius', 'mass', 'error', 'disc_year']]
    rm.to_csv(get_exorm_filepath('exoplanet_rm.csv'), index = False)