# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% ../nbs/00_core.ipynb 4
from __future__ import annotations
from typing import List 
import pandas as pd
import numpy as np

# %% auto 0
__all__ = ['order_columns', 'process_dates', 'setup_panel', 'fast_lag', 'lag', 'add_lags', 'rpct_change', 'rdiff']

# %% ../nbs/00_core.ipynb 8
def order_columns(df: pd.DataFrame, these_first: List[str]) -> pd.DataFrame:
    """Returns `df` with reordered columns. Use as `df = order_columns(df,_)`"""
    remaining = [x for x in df.columns if x not in these_first]
    return df[these_first + remaining]

# %% ../nbs/00_core.ipynb 10
def process_dates(df: pd.DataFrame, # Function returns copy of this df with `dtdate_var` and `f'{freq}date'` cols added
                time_var: str='date', # This will be the date variable used to generate datetime var `dtdate_var`
                time_var_format: str='%Y-%m-%d', # Format of `time_var`; must be valid pandas `strftime`
                dtdate_var: str='dtdate', # Name of datetime var to be created from `time_var`
                freq: str=None, # Used to create `f'{freq}date'` period date; must be valid pandas offset string
                ) -> pd.DataFrame:
    """Makes datetime date `dtdate_var` from `time_var`; adds period date `f'{freq}date'`."""
    
    df = df.copy()
    df[dtdate_var] = pd.to_datetime(df[time_var], format=time_var_format)
    df[f'{freq}date'] = df['dtdate'].dt.to_period(freq)
    return order_columns(df, [time_var,dtdate_var,f'{freq}date'])

# %% ../nbs/00_core.ipynb 12
def setup_panel(df: pd.DataFrame, # Input DataFrame; a copy is returned
                panel_ids :str=None, # Name of variable that identifies panel entities
# Params passed to `process_dates`
                time_var: str='date', # This will be the date variable used to generate datetime var `dtdate_var`
                time_var_format: str='%Y-%m-%d', # Format of `time_var`; must be valid pandas `strftime`
                dtdate_var: str='dtdate', # Name of datetime var to be created from `time_var`
                freq: str=None, # Used to create `f'{freq}date'` period date; must be valid pandas offset string
# Params for cleaning                 
                drop_missing_index_vals: bool=True, # What to do with missing `panel_ids` or `f'{freq}date'`
                panel_ids_toint: str='Int64', # Converts `panel_ids` to int in place; use falsy value if not wanted
                drop_index_duplicates: bool=True, # What to do with duplicates in (`panel_ids`, `f'{freq}date'`) values
                duplicates_which_keep: str='last', # If duplicates in index, which to keep; must be 'first', 'last' or `False`
                ) -> pd.DataFrame:
    """Applies `process_dates` to `df`; cleans up (`panel_ids` ,`f'{freq}date'`) and sets it as index."""

    df = process_dates(df, time_var=time_var, time_var_format=time_var_format, dtdate_var=dtdate_var, freq=freq)
    if drop_missing_index_vals:
        df = df.dropna(subset=[panel_ids,time_var])
    if panel_ids_toint:
        df[panel_ids] = df[panel_ids].astype('Int64')
    df = df.set_index([panel_ids, f'{freq}date']).sort_index()
    if drop_index_duplicates:
        df = df[~df.index.duplicated(keep=duplicates_which_keep)]   
    return order_columns(df,[time_var,dtdate_var]) 

# %% ../nbs/00_core.ipynb 16
def fast_lag(df: pd.Series|pd.DataFrame, # Index (or level 1 of MultiIndex) must be period date
        n: int=1, # Number of periods to lag based on frequency of df.index; Negative values means lead.
        ) -> pd.Series: # Series with lagged values; Name is taken from `df`, with _lag{n} or _lead{n} added
    """Lag data in 'df' by 'n' periods. 
    ASSUMES DATA IS SORTED BY DATES AND HAS NO DUPLICATE OR MISSING DATES."""

    if isinstance(df,pd.Series): df = df.to_frame()
    if len(df.columns) > 1: raise ValueError("<df> must have a single column")
    dfl = df.copy()
    old_name = str(df.columns[0])
    new_varname = old_name + f'_lag{n}' if n>=0 else old_name + f'_lead{-n}'
    
    if isinstance(df.index, pd.MultiIndex):
        if f'{df.index.levels[1].dtype}'.startswith('period'):
            (panelvar, timevar) = dfl.index.names
            dfl = dfl.reset_index()
            dfl[['lag_panel','lag_time',new_varname]] = dfl[[panelvar, timevar, old_name]].shift(n)
            dfl[new_varname] = np.where((dfl[panelvar]==dfl['lag_panel']) & (dfl[timevar]==dfl['lag_time']+n),
                                        dfl[new_varname], np.nan)
            dfl = dfl.set_index([panelvar, timevar])
        else:
            raise ValueError('Dimension 1 of multiindex must be period date')
    else:
        if f'{df.index.dtype}'.startswith('period'):
            timevar = dfl.index.name
            dfl = dfl.reset_index()
            dfl[['lag_time',new_varname]] = dfl[[timevar, old_name]].shift(n)
            dfl[new_varname] = np.where((dfl[timevar]==dfl['lag_time']+n),
                                        dfl[new_varname], np.nan)
            dfl = dfl.set_index([timevar])
        else:
            raise ValueError('Index must be period date')
    return dfl[new_varname].squeeze()

# %% ../nbs/00_core.ipynb 17
def lag(df: pd.Series|pd.DataFrame, # Index (or level 1 of MultiIndex) must be period date with no missing values.
        n: int=1, # Number of periods to lag based on frequency of df.index; Negative values means lead.
        fast: bool=True, # Assumes data is sorted by date and no duplicate or missing dates
        ) -> pd.Series: # Series with lagged values; Name is taken from `df`, with _lag{n} or _lead{n} added
    """Lag data in 'df' by 'n' periods. ASSUMES NO MISSING DATES"""

    if fast: return fast_lag(df,n)

    if isinstance(df,pd.Series): df = df.to_frame()
    if len(df.columns) > 1: raise ValueError("'df' parameter must have a single column")
    dfl = df.copy()
    dfl.columns = [str(df.columns[0]) + f'_lag{n}'] if n>=0 else df.columns + f'_lead{-n}'

    if isinstance(df.index, pd.MultiIndex):
        if f'{df.index.levels[1].dtype}'.startswith('period'):
            dfl.index = dfl.index.set_levels(df.index.levels[1]+n, level=1)
        else:
            raise ValueError('Dimension 1 of multiindex must be period date')
    else:
        if f'{df.index.dtype}'.startswith('period'):
            dfl.index += n
        else:
            raise ValueError('Index must be period date')

    dfl = df.join(dfl).drop(columns=df.columns)
    return dfl.squeeze()

# %% ../nbs/00_core.ipynb 21
def add_lags(df: pd.Series|pd.DataFrame, # If series, it must have a name equal to 'vars' parameter
             vars: str|List[str], # Variables to be lagged; must be a subset of df.columns()
             lags: int|List[int]=1, # Which lags to be added
             lag_suffix: str='_lag',
             lead_suffix: str='_lead',
             fast: bool=True, # Weather to use fast_lag function
             ) -> pd.DataFrame:
    """Returns a copy of 'df' with all 'lags' of all 'vars' added to it"""

    df = df.copy()
    if isinstance(df, pd.Series): df = df.to_frame()  
    if isinstance(vars, str): vars = [vars]
    if isinstance(lags, int): lags = [lags]

    for var in vars:
        for n in lags:
            suffix = f'{lag_suffix}{n}' if n>=0 else f'{lead_suffix}{-n}'
            df[f'{var}{suffix}'] = lag(df[var], n, fast)
    return df

# %% ../nbs/00_core.ipynb 28
def rpct_change(df: pd.Series, n: int=1, fast=True):
    """Percentage change using robust lag function"""
    return df / lag(df, n, fast) - 1

# %% ../nbs/00_core.ipynb 30
def rdiff(df: pd.Series, n: int=1, fast=True):
    """Difference using robust lag function"""
    return df - lag(df, n, fast)
