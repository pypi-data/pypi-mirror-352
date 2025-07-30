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

    recommended = round((len(data) / 1000) * 115)
    SMOOTHING = int(input(f'Recommended value: {recommended}. Enter smoothing amount (see README): '))

    x = data['radius']
    y = data['mass']

    x = numpy.log10(x)
    y = numpy.log10(y)

    w = numpy.diff(x)
    w = numpy.append(w, w[-1])
    w = numpy.sqrt(w)
    w /= numpy.mean(w)
    w *= 1 - data['error']
    # w = numpy.where((x > 0.75) & (x < 1.25), w * 0.1, w)

    model = UnivariateSpline(x, y, k = DEGREE, s = SMOOTHING, w = w)
    model = ExoRM(model, x, y)
    model.create_error_model()

    x_smooth = numpy.linspace(-0.5, 2, 10000)
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
    # plot.plot(x_smooth, e_smooth)
    plot.show()

    model.save(get_exorm_filepath('radius_mass_model.pkl'))