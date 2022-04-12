from config import *
import plotly.express as px
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

# Read csv as df
df_kfs = pd.read_csv('computed_kfs.csv', delimiter=',', index_col=0)

# Read excel for getting measurement depths
df_input = pd.read_excel('input-data.xlsx', usecols=['depth'], skiprows=[1])
df_kfs['depth'] = df_input

# Create array for subsequent loop
meas_array = df_kfs['sample'].unique().tolist()

# Create kf methods for susequent loop
cols = df_kfs.columns.values.tolist()
methods_list = cols[1:-1]

# Dict for assigining colors for each method
colors = ['green', 'violet', 'orange', 'blue']
color_dict = dict(zip(methods_list, colors))

# Dict for assigining markers for each method
symbols = ['*', 'o', 's', 'v']
marker_list = dict(zip(methods_list, symbols))

# Loop through measurement location
for meas in meas_array:
    df_toplot = df_kfs[df_kfs['sample'] == meas]
    fig, ax = plt.subplots(figsize=(6, 6))

    # for each measurement location loop through kf values computed with different qapproaches
    for method in methods_list:
        df_toplot.plot.scatter(x=method,
                               y='depth',
                               color=color_dict[method],
                               ax=ax,
                               label=method,
                               s=30,
                               marker=marker_list[method],
                               grid=True)
    ax.set_xlabel('kf [m/s]')
    ax.set_ylabel('Sediment depth [m]')
    ax.xaxis.set_label_position('top')  # axis label is located on the top, instead of on the bottom as usual
    ax.xaxis.tick_top()
    ax.set_ylim(bottom=0.6, top=0)
    ax.set_xscale('log')
    ax.xaxis.set_major_formatter(FormatStrFormatter('%1.0e'))
    ax.set_xlim(0.000003, 0.030)
    props = dict(boxstyle='Square', fill=False, alpha=1)
    ax.text(0.18, 0.95, meas, fontsize=20, transform=ax.transAxes, verticalalignment='top', bbox=props)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=7)
    plt.tight_layout()
    fig.savefig('SA-plots/' + meas + '.png', dpi=300)
