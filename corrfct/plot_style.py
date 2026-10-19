import matplotlib.pyplot as plt

STATIONS_COLOR = "#0072B2"
RANDOMS_COLOR = "#E69F00"
PAIR_COLOR = "#D55E00"

plt_params = {
    "figure.figsize": [7.5, 4.5],
    "figure.dpi": 100,
    "text.usetex": False,
    "font.family": "serif",
    "font.serif": ["cmr10"],
    "axes.formatter.use_mathtext": True,
    "mathtext.fontset": "cm",
    "font.size": 16,
    "axes.labelsize": 16,
    "axes.titlesize": 18,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.fontsize": 16,
    "legend.title_fontsize": 12,
    "axes.linewidth": 1.0,
    "xtick.major.width": 1.0,
    "ytick.major.width": 1.0,
    "xtick.minor.width": 0.8,
    "ytick.minor.width": 0.8,
    "xtick.major.size": 5,
    "ytick.major.size": 5,
    "xtick.minor.size": 3,
    "ytick.minor.size": 3,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "ytick.color": "black",
    "axes.labelcolor": "black",
    "axes.edgecolor": "black",
    "xtick.color": "black",
    "axes.prop_cycle": plt.cycler('color', ['#E69F00', '#56B4E9', '#009E73', '#0072B2', '#D55E00', '#CC79A7', '#F0E442', '#000000']),
    "legend.frameon": False,
    "savefig.bbox": "tight",
    "savefig.dpi": 150,
}


def apply():
    plt.rcParams.update(plt_params)
