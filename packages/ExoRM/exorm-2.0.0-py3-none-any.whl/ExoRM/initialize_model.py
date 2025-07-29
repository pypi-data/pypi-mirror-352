def initialize_model():
    DEGREE = 1

    import matplotlib.pyplot as plot
    import numpy
    plot.style.use('seaborn-v0_8-whitegrid')

    from scipy.interpolate import UnivariateSpline
    from ExoRM import get_exorm_filepath, ExoRM, unique_radius, read_rm_data, preprocess_data, ForecasterRM

    data = read_rm_data()
    data = unique_radius(data)
    data = preprocess_data(data)

    recommended = round((len(data) / 1500) * 287)
    SMOOTHING = int(input(f'Recommended value: {recommended}. Enter smoothing amount (see README): '))

    x = data['radius']
    y = data['mass']

    x = numpy.log10(x)
    y = numpy.log10(y)

    model = UnivariateSpline(x, y, k = DEGREE, s = SMOOTHING)
    model = ExoRM(model, x, y)
    model.create_error_model(k = DEGREE, s = SMOOTHING / 2)

    x_smooth = numpy.linspace(-0.5, 2.5, 10000)
    y_smooth = model(x_smooth)

    min_crossing = x_smooth[numpy.argmin(numpy.abs(y_smooth - ForecasterRM.terran(x_smooth)))]
    max_crossing = x_smooth[numpy.argmin(numpy.abs(y_smooth - ForecasterRM.stellar(x_smooth)))]

    # model.override_min(min_crossing, model(min_crossing))
    # model.override_max(max_crossing, model(max_crossing))

    y_smooth = model(x_smooth)
    e_smooth = model.error(x_smooth)

    plot.scatter(x, y, s = 1)
    plot.plot(x_smooth, y_smooth, color = 'C1')
    plot.plot(x_smooth, y_smooth + e_smooth, color = 'C2')
    plot.plot(x_smooth, y_smooth - e_smooth, color = 'C2')
    plot.show()

    model.save(get_exorm_filepath('radius_mass_model.pkl'))