# Salient Predictions SDK

## Intended Use

The Salient SDK is a python convenience wrapper around Salient Predictions' customer-facing  
[web API](https://api.salientpredictions.com/v2/documentation/api/). It also contains utility functions for manipulating and analyzing the data delivered from the API.

## Installing the SDK

The Salient SDK is a Python package that depends on Python v3.11 and installs from [PyPI](https://pypi.org/project/salientsdk):

```bash
python3 --version | grep -q '3.11' && echo "Py OK" || echo "Need Py 3.11"
pip install salientsdk poetry --upgrade
pip show salientsdk
```

If you "need Py 3.11", follow the instructions in [Getting Python 3.11](#getting-python-311).

The `install` will also get `poetry`, which `salientsdk` uses to manage dependencies.

## Usage

### Command Line

The Salient SDK contains a full command line interface that can access each of the primary
API functions without even opening Python.

```bash
# Get the version number:
salientsdk version
# Show help for all available commands:
salientsdk --help
```

To verify that you can access Salient's API, use the limited `test*` credentials to log in. If you see errors or warnings relating to `VERIFY SSL` you may need to adjust your firewall settings.

```bash
salientsdk login -u testusr -p testpwd
# If successful, the command should return a Session object:
# <requests.sessions.Session object at 0x12cf45590>
```

To verify that you can download data from Salient, try these `testusr`/`testpwd` credentials to download historical data with the `data_timeseries` function. This will download a NetCDF file to your current directory and display its contents.

```bash
salientsdk data_timeseries -fld all \
-lat 42 -lon -73 \
--start 2020-01-01 --end 2020-12-31 \
-u testusr -p testpwd
```

To test that your specific Salient-issued credentials are functioning properly, try them with the `forecast_timeseries` function. Replace `username` and `password` in the example below with your credentials. Note that you may need to change the location (North America) and timescale (seasonal) if your license does not include them.

```bash
salientsdk forecast_timeseries --variable precip \
-lat 42 -lon -73 \
--timescale seasonal --date 2020-01-01 \
-u username -p "password"
```

### Example Notebooks

The package ships with examples that show `salientsdk` in action. You can list the file locations and copy them to a working directory for use. Let's work with the `hindcast_summary` notebook example:

```bash
mkdir salient_env && cd salient_env
# show all of the available examples:
salientsdk examples
# Copy the "hindcast_summary" example to the current directory:
salientsdk examples | grep "hindcast_summary" | xargs -I {} cp {} .
```

`salientsdk` uses the `poetry` dependency manager to set up a virtual environment with all the dependencies needed to run the examples:

```bash
# Clear out any poetry projects that may already exist
rm -f pyproject.toml
# Create a new poetry project
poetry init --no-interaction
# Get the latest version of the salient sdk
poetry add jupyter salientsdk@latest
# Create a virtual environment with the right dependencies
poetry run ipython kernel install --user --name="salient_env"
# Open the notebook and get it ready to run
poetry run jupyter notebook hindcast_summary.ipynb
```

Once the hindcast_summary notebook launches in your browser:

- If "salient env" is not already selected as a kernel:<br>
  Kernel > Change Kernel > salient_env > Select
- Add your username/password credentials to the "login" step in the first cell:<br>
  `sk.login(<username>, <password>, verbose=False)`
- The notebook assumes you are licenced for regions `north-america` and `europe`, and variables `temp` and `precip`. If you are not, change cell 2 to generate a request consistent with your licensing:<br>
  `loc=sk.Location(region=["<region1>", "<region2>"]),`<br>
  `variable=["<var1>", <var2>"],`
- Run > Run All Cells
- This will generate files in the `hindcast_summary_example` directory:<br>
  `hindcast_summary_<hash>.csv` the source validation files from the API.<br>
  `hindcast_summary_transposed.csv` a combined version of the results

### Via Python

In a python 3.11 script, this example code will login and request a historical ERA5 data timeseries.

```python
import salientsdk as sk
import xarray as xr
import netcdf4

session = sk.login("testusr","testpwd")
history = sk.data_timeseries(loc = Location(lat=42, lon=-73), field="all", variable="temp", session=session)
print(xr.open_dataset(history))
```

Note that this example uses the limited credentials `testusr` and `testpwd`. To access the full capabilities of your license, use your Salient-provided credentials.

See all available functions in the [API Reference](api.md).

## Installation Help

### Getting Python 3.11

The Salient SDK requires Python 3.11 to use. If you have Python installed, you can check your version with:

```bash
python3 --version
```

To get version 3.11:

```bash
# Ubuntu:
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11
```

```bash
# macOS:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew update
brew install python@3.11
```

## License

This SDK is licensed for use by Salient customers [details](https://salient-predictions.github.io/salientsdk/LICENSE/).

Copyright 2024 [Salient Predictions](https://www.salientpredictions.com/)
