#!/usr/bin/env python
# Copyright Salient Predictions 2024

"""Observed data timeseries.

This module acquires observed station meteorological data and converts it into a format
compatible with the `data_timeseries` function.
"""

from collections.abc import Iterable

import numpy as np
import pandas as pd
import xarray as xr


def make_observed_ds(
    obs_df: pd.DataFrame | str | Iterable[pd.DataFrame | str],
    name: str | Iterable[str],
    variable: str | Iterable[str],
    time_col: str = "time",
) -> xr.Dataset:
    """Convert weather observation DataFrame(s) to xarray Dataset.

    This function converts tabular meteorological data into a format identical to
    `data_timeseries(..., frequency='daily') suitable for use with the `crps` function.

    Args:
        obs_df: Single DataFrame or a filename to a CSV that can be read as a dataframe.
            May also be an iterable vector of filenames or `DataFrame`s.
            Each DataFrame should have columns for `time` and the `variable` of interest.
            If the dataframe contains lat, lon, and elev metadata the function will
            preserve thse as coordinates. Function `get_ghcnd` will provide a compatible
            dataset, or you can provide your own.
        name: Station name(s) corresponding to the DataFrame(s). Must be a string if obs_df
            is a single DataFrame, or an iterable of strings matching the length of obs_df
            if multiple DataFrames are provided.
        variable: Name(s) of the column(s) in obs_df to extract the met data
            (e.g. 'temp', 'precip') or ['temp','precip']
        time_col: Name of the column in obs_df containing the time (default `time`)

    Returns:
        xarray Dataset containing the variable data and station metadata. Has dimensions
        'time' and 'location', with coordinates for station lat/lon/elevation.
    """

    def get_attrs(var_name):
        """Helper to collect attributes from a dataframe column."""
        attrs = {"short_name": var_name}
        if hasattr(obs_df[var_name], "attrs"):
            for attr in ["units", "long_name"]:
                if attr in obs_df[var_name].attrs:
                    attrs[attr] = obs_df[var_name].attrs[attr]
        return attrs

    if isinstance(obs_df, Iterable) and not isinstance(obs_df, pd.DataFrame):
        if name is None or isinstance(name, str):
            raise ValueError(
                "When obs_df is a list of DataFrames, name must be an iterable of strings"
            )

        assert len(obs_df) == len(
            name
        ), f"Length mismatch: got {len(obs_df)} DataFrames but {len(name)} names"

        ds = [
            make_observed_ds(obs_df=df, name=n, variable=variable, time_col=time_col)
            for df, n in zip(obs_df, name)
        ]
        return xr.concat(ds, dim="location")

    if isinstance(obs_df, str):
        obs_df = pd.read_csv(obs_df)

    name = str(name)
    attrs = {}

    if isinstance(variable, str):
        data_vars = {"vals": (("time", "location"), obs_df[variable].values[:, np.newaxis])}
        attrs = get_attrs(variable)
    else:
        data_vars = {}
        for var in variable:
            data_vars[var] = (
                ("time", "location"),
                obs_df[var].values[:, np.newaxis],
                get_attrs(var),
            )

    ds = xr.Dataset(
        data_vars=data_vars,
        coords={
            "time": pd.to_datetime(obs_df[time_col]),
            "location": [name],
        },
        attrs=attrs,
    )

    # Preserve station geo-coordinates if they exist as a column
    for coord in ["lat", "lon", "elev"]:
        if coord in obs_df.columns:
            ds = ds.assign_coords({f"{coord}_station": ("location", [obs_df[coord].mean()])})

    return ds
