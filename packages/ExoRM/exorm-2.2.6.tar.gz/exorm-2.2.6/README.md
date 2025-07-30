# ExoRM

- HomePage: https://github.com/kzhu2099/ExoRM
- Issues: https://github.com/kzhu2099/ExoRM/issues

[![PyPI Downloads](https://static.pepy.tech/badge/ExoRM)](https://pepy.tech/projects/ExoRM)

Author: Kevin Zhu

NOTE: As of June 2, 2025, the optimal SMOOTHING parameter is ~108, and it will only increase.
A rough estimate you may use is:
(Length of dataset / 1000) * 110, which is what the recommended value is.
Feel free to change this number if you find it is not smooth / too smooth.

## Features

- continuous radius-mass relationship
- smooth with lower residuals
- simple usage, log10 and linear
- best-fit for Terran, Neptunian, and Jovian

## Installation

To install ExoRM, use pip: ```pip install ExoRM```.

However, many prefer to use a virtual environment.

macOS / Linux:

```sh
# make your desired directory
mkdir /path/to/your/directory
cd /path/to/your/directory

# setup the .venv (or whatever you want to name it)
pip install virtualenv
python3 -m venv .venv

# install ExoRM
source .venv/bin/activate
pip install ExoRM

deactivate # when you are completely done
```

Windows CMD:

```sh
# make your desired directory
mkdir C:path\to\your\directory
cd C:path\to\your\directory

# setup the .venv (or whatever you want to name it)
pip install virtualenv
python3 -m venv .venv

# install ExoRM
.venv\Scripts\activate
pip install ExoRM

deactivate # when you are completely done
```

## Usage

To first begin using ExoRM, the data and model must be initialized. This is due to the constant discovery of new exoplanets, adding to the data.

Furthermore, this requires periodic updating to include the most recent information.

Simply run `get_data()` and `initialize_model()`. Note: import those by using `from ExoRM.get_data import get_data()` and `from ExoRM.initialize_model() import initialize_model()`. initialization requires a smoothing amount, which is set to 280 (SEE NOTE) but should be increased when there is more data. A plot of the model will be shown for you to see. Both are stored in your OS's Application Data for ExoRM. ExoRM provides built in functions to retrieve from this folder.

To use the model, call `ExoRM.load_model()` which returns the model from the filepath. If you wish, you may use `model.save(...)` to save it to your own directory.

Note that all files saved are located in `/Users/<username>/Library/Application Support/ExoRM` for macOS and `C:\Users\<username>\AppData\Local\ExoRM\ExoRM` for windows.

The model supports log10 and linear scale in earth radii. When using the `model([...]), .__call__([...]), or .predict([...])`, the log10 scale is used. Linear predictions are used in `.predict_linear([...])`.

The high amount of uncertainty can be accessed from ExoRM. We used another Univariate spline to calculate error (abs(residuals)). Also, this spline has the same degree as what you input at the beginning but half the smoothing. Because there is high overfitting near the edges of the data, the top 99th percentile is removed. Generally, the log error increase as the log radius increases. Estimate the error by using `model.error([...])` and `model.linear_error([...])`. Note that this values is the second standard deviation at a point, calculated by multiplying the spline error by the sqrt of pi / 2.

ExoRM's data limitations required overrides for certain areas. By default, `override_min()` and `override_max()` are set to the inverse power law relationship found by Chen and kipping (2017). The transition points to those are smooth and are calculated to be the closest intersection between the model and the relationship.

An example is seen in the `example.ipynb`.

## License

The License is an MIT License found in the LICENSE file.