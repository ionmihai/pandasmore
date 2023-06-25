# pandasmore

<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

The full documentation site is
[here](https://ionmihai.github.io/pandasmore/), and the GitHub page is
[here](https://github.com/ionmihai/pandasmore).

Here is a short description of some of the main functions (more details
below and in the
[documentation](https://ionmihai.github.io/pandasmore/core.html)):

- [`setup_tseries`](https://ionmihai.github.io/pandasmore/core.html#setup_tseries):
  cleans up dates and sets them as the index
- [`setup_panel`](https://ionmihai.github.io/pandasmore/core.html#setup_panel):
  cleans up dates and panel id’s and sets them as the index (panel id,
  period date)
- [`lag`](https://ionmihai.github.io/pandasmore/core.html#lag): robust
  lagging that accounts for panel structure, unsorted or duplicate
  dates, or gaps in the time-series

## Install

``` sh
pip install pandasmore
```

## How to use

First, we set up an example dataset to showcase the functions in this
module.

``` python
import pandas as pd
import numpy as np
import pandasmore as pdr
```

``` python
raw = pd.DataFrame(np.random.rand(15,2), 
                    columns=list('AB'), 
                    index=pd.MultiIndex.from_product(
                        [[1,2, np.nan],[np.nan,'2010-01','2010-02','2010-02','2010-04']],
                        names = ['firm_id','date'])
                      ).reset_index()
raw
```

<div>

|     | firm_id | date    | A        | B        |
|-----|---------|---------|----------|----------|
| 0   | 1.0     | NaN     | 0.943132 | 0.981995 |
| 1   | 1.0     | 2010-01 | 0.328816 | 0.473158 |
| 2   | 1.0     | 2010-02 | 0.177921 | 0.835497 |
| 3   | 1.0     | 2010-02 | 0.928199 | 0.743025 |
| 4   | 1.0     | 2010-04 | 0.857208 | 0.742693 |
| 5   | 2.0     | NaN     | 0.147470 | 0.357477 |
| 6   | 2.0     | 2010-01 | 0.172676 | 0.978518 |
| 7   | 2.0     | 2010-02 | 0.391758 | 0.574734 |
| 8   | 2.0     | 2010-02 | 0.824737 | 0.863340 |
| 9   | 2.0     | 2010-04 | 0.847638 | 0.293925 |
| 10  | NaN     | NaN     | 0.969513 | 0.842419 |
| 11  | NaN     | 2010-01 | 0.491236 | 0.194837 |
| 12  | NaN     | 2010-02 | 0.854151 | 0.267796 |
| 13  | NaN     | 2010-02 | 0.461259 | 0.010185 |
| 14  | NaN     | 2010-04 | 0.735704 | 0.601400 |

</div>

``` python
df = pdr.setup_tseries(raw.query('firm_id==1'),
                        time_var='date', time_var_format="%Y-%m",
                        freq='M')
df
```

<div>

|         | date    | dtdate     | firm_id | A        | B        |
|---------|---------|------------|---------|----------|----------|
| Mdate   |         |            |         |          |          |
| 2010-01 | 2010-01 | 2010-01-01 | 1.0     | 0.328816 | 0.473158 |
| 2010-02 | 2010-02 | 2010-02-01 | 1.0     | 0.928199 | 0.743025 |
| 2010-04 | 2010-04 | 2010-04-01 | 1.0     | 0.857208 | 0.742693 |

</div>

``` python
df = pdr.setup_panel(raw,
                        panel_ids='firm_id',
                        time_var='date', time_var_format="%Y-%m",
                        freq='M')
df
```

<div>

|         |         | date    | dtdate     | A        | B        |
|---------|---------|---------|------------|----------|----------|
| firm_id | Mdate   |         |            |          |          |
| 1       | 2010-01 | 2010-01 | 2010-01-01 | 0.328816 | 0.473158 |
|         | 2010-02 | 2010-02 | 2010-02-01 | 0.928199 | 0.743025 |
|         | 2010-04 | 2010-04 | 2010-04-01 | 0.857208 | 0.742693 |
| 2       | 2010-01 | 2010-01 | 2010-01-01 | 0.172676 | 0.978518 |
|         | 2010-02 | 2010-02 | 2010-02-01 | 0.824737 | 0.863340 |
|         | 2010-04 | 2010-04 | 2010-04-01 | 0.847638 | 0.293925 |

</div>

``` python
pdr.lag(df['A'])
```

    permno  Mdate  
    1       2010-01         NaN
            2010-02    0.698770
            2010-04         NaN
    2       2010-01         NaN
            2010-02    0.834091
            2010-04         NaN
    Name: A_lag1, dtype: float64
