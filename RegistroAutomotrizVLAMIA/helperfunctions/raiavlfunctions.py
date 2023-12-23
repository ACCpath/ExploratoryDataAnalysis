#!/usr/bin/env python3
# raiavlfunctions.py
"""raiavlfunctions is a module that contains functions to help made some tasks in the treatment of
   the data of the administrative registration of the automotive industry of light vehicles,
   corresponding to the sale, production and export of cars and light trucks in Mexico.   
"""
__version__ = '1.0'

import os
import pandas as pd
import seaborn as sns
import scipy.stats as scistat

def formatter(x, pos):
    """Format the values of the marks on the axes of a graph.
    """
    return str(round(x / 1e6, 1))

def concat_files_csv(path):
    """Join similar csv files located in the provided path.
    """
    df = pd.DataFrame()
    for filename in sorted(os.listdir(path)):
        if filename.endswith('.csv'):
            fileloc = os.path.join(path, filename)
            #open the next file
            with open(fileloc, 'rt', encoding='utf-8') as f:
                df_new = pd.read_csv(fileloc, encoding='utf-8')
                print(filename + ' has ' + str(df_new.shape[0]) + ' rows.')
                df = pd.concat([df, df_new])
                # check for difference in columns
                columndiff = df.columns.symmetric_difference(df_new.columns)
                if (not columndiff.empty):
                    print('', 'Different column names for:', filename, columndiff, '', sep='\n')
    return df

def check_merge(dfleft, dfright, mergebyleft, mergebyright):
    """Check merged values per column in one file but not another.
    """

    dfleft['inleft'] = 'Y'
    dfright['inright'] = 'Y'
    dfboth = pd.merge(dfleft[[mergebyleft, 'inleft']],
                      dfright[[mergebyright, 'inright']],
                      left_on=[mergebyleft], right_on=[mergebyright],
                      how='outer')
    dfboth.fillna('N', inplace=True)
    print(pd.crosstab(dfboth.inleft, dfboth.inright))
    print(dfboth.loc[(dfboth.inleft=='N') | (dfboth.inright=='N')].head(20))

def make_frequencies(df, outfile):
    """Return a file with the calculate frequencies from all categorical variables.
    """
    freqout = open(outfile, 'w', encoding='utf-8')
    for col in df.select_dtypes(include=['category']):
        print(col, '-----------------------------------',
              'frequencies',
              df[col].value_counts(),
              'percentages',
              df[col].value_counts(normalize=True),
             sep='\n\n', end='\n\n\n', file=freqout)
    freqout.close()
def make_hist(seriestoplot, title, xlabel, ax, bins):
    """Make a histogram at the marked ax.
    """
    ax.hist(seriestoplot, bins=bins)
    ax.axvline(seriestoplot.mean(), color='red', linestyle='dashed', linewidth=1)
    ax.set_title(title, fontsize=10)
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel('Frequency', fontsize=9)

def get_outliers(dfinput, iqrvar, othervars):
    """Determines outlier thresholds for iqrvar, setting this at 1.5 times the
       interquartile range(the distance between the first and third quartile) below
       the first quartile or above the third quartile.
    """
    dfinput = dfinput.loc[:,othervars + [iqrvar]]
    dfinput.rename(columns={iqrvar:'quantity'}, inplace=True)
    thirdq = dfinput['quantity'].quantile(0.75)
    firstq = dfinput['quantity'].quantile(0.25)
    interquartilerange = 1.5 * (thirdq-firstq)
    outlierhigh = interquartilerange + thirdq
    outlierlow = firstq - interquartilerange
    dfoutput = dfinput.loc[(dfinput['quantity']>outlierhigh)|(dfinput['quantity']<outlierlow)]
    dfoutput = dfoutput.assign(varname = iqrvar,
                               threshold_low = outlierlow,
                               threshold_high = outlierhigh)
    return dfoutput
def get_analysisdf(dfinput, variable, carsvars, typecar):
    """Change the unit of the analysis of the Production, Export,
       and Sale of light vehicles grouping by model and type vehicle.
    """
    dfanalysis = dfinput.loc[(dfinput.year.between(2005,2023))&(dfinput.type==typecar)].\
        groupby(carsvars, as_index=False)[variable].sum()
    dfanalysis = dfanalysis.loc[dfanalysis[variable]>0]
    return dfanalysis

def testnorm(var, df):
    """Formal test of normality Shapiro-Wilk
    """
    stat, p = scistat.shapiro(df[var])
    return p

def make_lineplot(data, valuex, valuey, ax, xlima, xlimb, hue, xlabel='', ylabel='', fmillion=True):
    """Make a lineplot at the marked ax.
    """
    f = sns.lineplot(data=data, x=valuex, y=valuey, ax=ax, hue=hue)
    if fmillion:
        f.axes.yaxis.set_major_formatter(formatter)
    f.axes.xaxis.set_major_formatter('{x:.0f}')
    f.axes.set_ylabel(ylabel, fontdict={'fontsize':10})
    f.axes.set_xlabel(xlabel, fontdict={'fontsize':10})
    f.set_xticks(f.get_xticks().tolist())
    f.set_xticklabels(f.axes.get_xticklabels(), rotation=45)
    f.axes.set_xlim(xlima,xlimb)
