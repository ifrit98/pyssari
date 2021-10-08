## Pyssari 

Pyssari is a monolithic application (script) that utilizes a customized python API interface to interact with the Messari Web API 

### Usage
```{bash}
pyssari.py [-h] -a ASSETS [ASSETS ...] [-s START_DATE] [-e END_DATE] [-f]
```
### Help
```{bash}
python pyssari.py --help
```
```
usage: pyssari.py [-h] -a ASSETS [ASSETS ...] [-s START] [-e END] [-f]

optional arguments:
  -h, --help            show this help message and exit
  -a ASSETS [ASSETS ...], --assets ASSETS [ASSETS ...]
                        <Required> Set flag
  -s START, --start START

  -e END, --end END
  -f, --flatten_results
```

#### Example
Grab price history for BTC, ETH, and SOL from 01/01/2020 through 10/01/2021, returned as pandas dataframe.
```{bash}
python pyssari.py -a BTC ETH SOL -s '2020-01-01' -e '2021-10-01'
```

Result:
```
Parsed arguments:
 Namespace(assets=['BTC', 'ETH', 'SOL'], end='2021-10-06', flatten=True, start='2020-01-01')

Pandas DataFrame containing asset price history:
                      BTC          ETH         SOL
2019-12-31   7181.337264   130.327045    0.000000
2020-01-01   6947.972833   126.856802    0.000000
2020-01-02   7334.642937   134.203804    0.000000
2020-01-03   7342.932133   133.977728    0.000000
2020-01-04   7353.340005   135.297624    0.000000
...                  ...          ...         ...
2021-10-01  47660.801396  3389.156477  169.049729
2021-10-02  48228.374332  3419.656127  173.051778
2021-10-03  49245.049342  3386.956778  167.200909
2021-10-04  51496.073794  3516.424168  164.668520
2021-10-05  55333.011327  3575.722695  153.912387

[645 rows x 3 columns]

Pandas Dataframe of ALL Asset Metrics:
                                                  BTC           ETH           SOL
all_time_high_breakeven_multiple        1.444583e+00  1.433237e+00  1.361858e+00
all_time_high_days_since                1.250000e+02  9.700000e+01  2.800000e+01
all_time_high_percent_down              3.077586e+01  3.022787e+01  2.657090e+01
all_time_high_price                     6.465415e+04  4.337100e+03  2.151784e+02
blockchain_stats_24_hours_adjusted_nvt  4.539763e+01  3.739140e+01           NaN
...                                              ...           ...           ...
supply_supply_revived_90d               1.883746e+07  1.173644e+08           NaN
supply_y_2050                           2.098634e+07  1.351356e+08  9.450229e+08
supply_y_2050_issued_percent            8.980410e+01  8.584107e+01  5.248293e+01
supply_y_plus10                         2.064640e+07  1.224447e+08  7.408839e+08
supply_y_plus10_issued_percent          9.128271e+01  9.473816e+01  6.694378e+01
```
