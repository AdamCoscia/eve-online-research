# -*- coding: utf-8 -*-
"""Data Presentation Script.

Utilizes the pandas library -
See https://pandas.pydata.org/pandas-docs/stable/api.html

Utilizes the matplotlib library -
See https://matplotlib.org/

Created by: Adam Coscia

Created on: 08/02/2018

Last Updated: 02/27/2019

"""
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar


class ScrollableWindow(QtWidgets.QMainWindow):
    """Found online, not my own creation. Thank you to whoever wrote this!

    """
    def __init__(self, fig):
        self.qapp = QtWidgets.QApplication([])

        QtWidgets.QMainWindow.__init__(self)
        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget)
        self.widget.setLayout(QtWidgets.QVBoxLayout())
        self.widget.layout().setContentsMargins(0, 0, 0, 0)
        self.widget.layout().setSpacing(0)

        self.fig = fig
        self.canvas = FigureCanvas(self.fig)
        self.canvas.draw()
        self.scroll = QtWidgets.QScrollArea(self.widget)
        self.scroll.setWidget(self.canvas)

        self.nav = NavigationToolbar(self.canvas, self.widget)
        self.widget.layout().addWidget(self.nav)
        self.widget.layout().addWidget(self.scroll)

        self.show()
        exit(self.qapp.exec_())


def multiple_plots_scrollable(groups, nplots=5, layout=None):
    """Plots groups.

    :param groups:
    :param nplots:
    :param layout:
    :return:
    """
    cids = iter(list(groups.groups.keys()))  # Iterable list of Group keys
    fig, axes = plt.subplots(nrows=nplots,
                             ncols=1,
                             figsize=(16, nplots * 5),
                             gridspec_kw=layout)
    for ax in axes:
        cid = next(cids)
        group = groups.get_group(cid)
        # deltas = group.index.to_series().diff().dt.days.values[1:]
        ax.set_title(f'Character ID: {cid}')
        ax.plot(group.index, group.kd_ratio)

    fig.text(x=0.5, y=0.01, s='Killmail Date (year-month)', ha='center',
             fontsize=14)
    fig.text(x=0.015, y=0.5, s='Kill/Death Ratio',
             va='center', rotation='vertical', fontsize=14)
    fig.suptitle('Investment and Performance Series Using Combat-Based Frigate',
                 fontsize=16, y=0.99)

    a = ScrollableWindow(fig)  # Pass the figure to the custom window


def create_poster_graphic(groups, cids, layout=None):
    """Poster graphic for BI&A Conference, Fall 2018, Stevens Inst. of Tech.

    :param groups:
    :param cids:
    :param layout:
    :return:
    """
    from matplotlib.font_manager import FontProperties

    def plot(groups, cid, layout=None):
        """TODO

        :param groups:
        :param cid:
        :param layout:
        :return:
        """
        # Create Unique Fonts for Title, Labels, and Legend
        title_font = FontProperties(family='Arial', style='italic',
                                    variant='small-caps', weight='roman',
                                    size=42)
        xlabel_font = FontProperties(family='Arial', weight='demi', size=32)
        ylabel_font = FontProperties(family='Arial', weight='demi', size=32)
        legend_font = FontProperties(family='Arial', weight='medium', size=24)

        # Get data
        df = groups.get_group(cid)[['kd_ratio', 'hi_slot', 'mid_slot',
                                    'lo_slot', 'od_prct']]

        # Plot each axis
        ax1 = df['kd_ratio'].plot(c='#00bbff', ls='--', lw=3, marker='.',
                                  mfc='#0033ff', ms=10, mew=0)

        ax2 = ax1.twinx()
        # Only fill if the next y value is the same sign as the current y value
        # mask = (abs(df['od_prct'] + df['od_prct'].shift(-1)) ==
        #         abs(df['od_prct']) + abs(df['od_prct'].shift(-1)))
        ax2.fill_between(df.index, 0, df['od_prct'], where=None,
                         step='post', alpha=0.5, color='#00c900')

        # ax3 = ax1.twinx()
        # df[['slot_hi', 'slot_mid', 'slot_lo']].plot(ax=ax3)

        # Adjust axes spines to include tertiary plot
        # ax2.spines['right'].set_position(('axes', 1.0))
        # ax3.spines['right'].set_position(('axes', 1.1))

        # Add a legend and a grid
        lns1 = ax1.get_lines()
        lns2 = mpatches.Patch(color='#00c900', alpha=0.5)
        # lns3 = ax3.get_lines()
        hndls = lns1
        hndls.append(lns2)
        # hndls.extend(lns3)
        lbls = ['K/D Ratio', 'Offensive Investment']
        # lbls.extend([l.get_label() for l in lns3])

        ax1.legend(handles=hndls, labels=lbls, loc=4, framealpha=0.7,
                   prop=legend_font
                   )
        ax1.grid(True)

        # Style the axes
        ax1.set_title(f'CHARACTER ID: {cid}', pad=30,
                      font_properties=title_font
                      )
        ax1.set_xlabel('Date (Year-Month)', labelpad=30,
                       font_properties=xlabel_font
                       )
        ax1.set_ylabel('Kill-to-Death Ratio (Kills/Deaths)', labelpad=30,
                       font_properties=ylabel_font
                       )
        ax1.tick_params(length=8, width=2, labelsize=18, grid_color='#00bbff',
                        grid_alpha=0.3, grid_linestyle=':'
                        )

        ax2.set_ylabel('% Investment in Offense', labelpad=30,
                       font_properties=ylabel_font
                       )
        ax2.set_yticklabels([f'{x/100:.0%}' for x in ax2.get_yticks()],
                            fontsize=18)
        ax2.tick_params(length=8, width=2, labelsize=18)

        # ax3.set_ylabel('Slot Value (ISK)', fontsize=16)

        # Set the figure size
        ax1.figure.set_size_inches(15, 15)

        if layout is not None:
            plt.subplots_adjust(left=layout['left'],
                                bottom=layout['bottom'],
                                right=layout['right'],
                                top=layout['top'],
                                wspace=layout['wspace'],
                                hspace=layout['hspace'])

        plt.savefig(f'../docs/graphs/player_strategy_graphs/cid-{cid}.png')

    if type(cids) is np.ndarray:
        for cid in cids:
            plot(groups, cid, layout)
            plt.clf()
    else:
        plot(groups, cids, layout)


def plot_investment_area_performance(groups, cids, layout=None):
    """Plots to examine relationship b/w investment and performance.

    :param groups:
    :param cids:
    :param layout:
    :return:
    """
    from matplotlib.font_manager import FontProperties
    title_font = FontProperties(family='Arial',
                                variant='small-caps', weight='roman',
                                size=54)
    xlabel_font = FontProperties(family='Arial', weight='demi', size=40)
    ylabel_font = FontProperties(family='Arial', weight='demi', size=40)
    legend_font = FontProperties(family='Arial', weight='medium', size=24)

    gp = groups.get_group(cid)[['kd_ratio', 'kd_prct', 'hi_slot', 'mid_slot',
                                'lo_slot']]

    hi, mid, lo = gp.hi_slot, gp.mid_slot, gp.lo_slot

    total = hi + mid + lo
    hi_slot = (hi / total) * 100
    mid_slot = (mid / total) * 100
    lo_slot = (lo / total) * 100
    percentages = pd.concat([hi_slot, mid_slot, lo_slot], axis=1)

    ax1 = percentages.plot(kind='area')
    # ax1 = gp[['hi_slot', 'mid_slot', 'lo_slot']].plot(kind='area')

    ax2 = ax1.twinx()
    ax2.plot(gp.index, gp.kd_ratio, c='white', linewidth=4)

    colors = [line.get_color() for line in ax1.get_lines()]
    lns1 = [mpatches.Patch(color=color, alpha=0.5) for color in colors]
    lns1.reverse()
    lns2 = mpatches.Patch(color='#ffffff', alpha=0.5)
    hndls = lns1
    hndls.append(lns2)
    lbls = ['High Slot', 'Mid Slot', 'Low Slot', 'Performance (K/D)']

    ax1.legend(handles=hndls, labels=lbls, loc=4, framealpha=0.7,
               prop=legend_font
               )

    # Style the axes
    ax1.set_title(f'Comparing Trajectory and Success of Sample Player', pad=30,
                  font_properties=title_font
                  )
    ax1.set_xlabel('Datetime', labelpad=30,
                   font_properties=xlabel_font
                   )
    ax1.set_ylabel('Percent of Total Investment', labelpad=30,
                   font_properties=ylabel_font
                   )
    ax1.tick_params(length=8, width=2, labelsize=18, grid_color='#00bbff',
                    grid_alpha=0.3, grid_linestyle=':'
                    )
    ax1.set_yticklabels([f'{x/100:.0%}' for x in ax1.get_yticks()],
                        fontsize=18)
    ax1.margins(0)

    ax2.set_ylabel('Performance (K/D Ratio)', labelpad=30,
                   font_properties=ylabel_font
                   )
    ax2.tick_params(length=8, width=2, labelsize=18)

    ax1.figure.set_size_inches(19.2, 10.8)

    if layout is not None:
        plt.subplots_adjust(left=layout['left'],
                            bottom=layout['bottom'],
                            right=layout['right'],
                            top=layout['top'],
                            wspace=layout['wspace'],
                            hspace=layout['hspace'])

    plt.savefig(f'../visuals/graphs/filled_cid{cid}.png')


def plot_correlation_distributions(dfc: pd.DataFrame, sharey=True, layout=None):
    """Frequency plot of r values for BI&A Conference, Fall 2018, Stevens Inst.
    of Tech.

    :param dfc:
    :param sharey:
    :param layout:
    :return:
    """
    from matplotlib.font_manager import FontProperties
    title_font = FontProperties(family='Arial', style='italic',
                                variant='small-caps', weight='roman',
                                size=54)
    xlabel_font = FontProperties(family='Arial', weight='demi', size=40)
    ylabel_font = FontProperties(family='Arial', weight='demi', size=40)

    fig, axes = plt.subplots(nrows=1,
                             ncols=2,
                             sharey=sharey,
                             figsize=(32, 16),
                             gridspec_kw=layout)

    columns = iter(['kd_od_ratio_corr', 'kd_od_prct_corr'])
    measures = iter(['Ratios', 'Percentage'])
    for ax in axes:
        col = next(columns)
        measure = next(measures)
        dfc[col].hist(ax=ax, alpha=0.9, color='blue', bins=50)

        # Style the axes
        ax.grid(False)
        ax.set_title(f'Correlations Between {measure}', pad=30,
                     font_properties=title_font
                     )
        ax.set_xlabel('Pearson Correlation Coefficient (r)', labelpad=30,
                      font_properties=xlabel_font
                      )
        ax.set_ylabel('Frequency', labelpad=30,
                      font_properties=ylabel_font
                      )
        ax.tick_params(length=8, width=2, labelsize=18, grid_color='#00bbff',
                       grid_alpha=0.3, grid_linestyle=':'
                       )

    a = ScrollableWindow(fig)  # Pass the figure to the custom window


def plot_tseries(groups: pd.DataFrame, cid, layout=None):
    """Plots 3x3 graphic of 8 series specific to a single character id (cid).

    :param groups:
    :param layout:
    :return:
    """
    group = groups.get_group(cid)
    fig, axes = plt.subplots(nrows=3, ncols=3,
                             figsize=(18, 20),
                             gridspec_kw=layout)

    group.kd_ratio.plot(ax=axes[0][0], title='KD_RATIO')
    group.kd_prct.plot(ax=axes[1][0], title='KD_PRCT')
    group.kd_diff.plot(ax=axes[2][0], title='KD_DIFF')

    group.hi_slot.plot(ax=axes[0][1], title='HI_SLOT')
    group.mid_slot.plot(ax=axes[1][1], title='MID_SLOT')
    group.lo_slot.plot(ax=axes[2][1], title='LO_SLOT')

    group[['hi_slot', 'mid_slot', 'lo_slot']].plot(ax=axes[0][2],
                                                   title='ALL_SLOTS')
    group.od_ratio.plot(ax=axes[1][2], title='OD_RATIO')
    group.od_prct.plot(ax=axes[2][2], title='OD_PRCT')

    a = ScrollableWindow(fig)


# ============================================================================ #
# Use the Command Line or a Terminal to do basic pre-filtering!
dfpd = pd.read_csv('../data/Series/players_frig_actv_ts-prd.csv', header=0)

grouped = dfpd.set_index(pd.to_datetime(dfpd.datetime)).groupby('character_id')

plot_layout = {'top': 0.88, 'bottom': 0.2, 'left': 0.11,
               'right': 0.87, 'hspace': 0.4, 'wspace': 0.4}

cids = dfpd['character_id'].unique()
cid = 90001332

plot_tseries(grouped, cid, layout=plot_layout)

# create_poster_graphic(grouped, cids=cids, layout=plot_layout)
# plot_investment_area_performance(grouped, cids=cid)

# df = df.set_index('character_id')
# plot_correlation_distributions(df, sharey=True)
