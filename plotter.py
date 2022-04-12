from config import *

# Read csv as df
df_kfs = pd.read_csv('computed_kfs.csv', delimiter=',', index_col=0)

# Read excel for getting measurement depths
df_input = pd.read_excel('input-data.xlsx', usecols=['depth'], skiprows=[1])
df_kfs['depth'] = df_input

# Create array for subsequent loop
meas_array = df_kfs['sample'].unique().tolist()

nested_colors_locations = {
    'before': {'1': 'blue', '2': 'lightblue', None: 'blue'},
    'after': {'1': 'green', '2': 'lightgreen', None: 'green'}
}

df_kfs[['location', 'campaign']] = df_kfs['sample'].str.split(' ', expand=True)
df_kfs[['site', 'up or downstream']] = df_kfs['location'].str.split('-', expand=True)

# Loop through measurement location
for site in df_kfs['site'].unique().tolist():
    fig, ax = plt.subplots(figsize=(6, 6))
    meas_array_site = df_kfs[df_kfs['site'] == site]
    meas_array_site_list = meas_array_site['sample'].unique().tolist()
    # for each measurement location loop through kf values computed with different qapproaches
    for meas in meas_array_site_list:
        df_toplot = df_kfs[df_kfs['sample'] == meas]
        campaign, up_or_down = df_toplot['campaign'].iloc[0], df_toplot['up or downstream'].iloc[0]
        df_toplot.plot(x='Wooster et al. (2008) [Estimated kf]',
                       y='depth',
                       color=nested_colors_locations[campaign][up_or_down],
                       ax=ax,
                       label=meas,
                       grid=True,
                       marker='o')
    ax.set_xlabel('kf [m/s]')
    ax.set_ylabel('Streambed depth [m]')
    ax.xaxis.set_label_position('top')  # axis label is located on the top, instead of on the bottom as usual
    ax.xaxis.tick_top()
    ax.set_ylim(bottom=0.6, top=0)
    ax.set_xscale('log')
    ax.xaxis.set_major_formatter(FormatStrFormatter('%1.0e'))
    ax.set_xlim(0.000001, 0.030)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=7)
    plt.tight_layout()
    fig.savefig('final-plots/' + site + '.png', dpi=300)
