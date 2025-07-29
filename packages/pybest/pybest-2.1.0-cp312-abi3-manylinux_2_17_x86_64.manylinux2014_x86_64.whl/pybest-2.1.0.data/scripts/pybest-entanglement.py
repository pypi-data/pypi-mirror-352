#!python
# PyBEST: Pythonic Black-box Electronic Structure Tool
# Copyright (C) 2016-- The PyBEST Development Team
#
# This file is part of PyBEST.
#
# PyBEST is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# PyBEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
# --
"""Script generating mutual information and single orbital entropy plots."""

import argparse
import pathlib
import sys

import matplotlib as mpl
import matplotlib.colors as colors
import matplotlib.patches as mpatches
import matplotlib.path as mpath
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from matplotlib.ticker import NullFormatter

try:
    from matplotlib._png import read_png
except ModuleNotFoundError:
    from matplotlib.image import imread as read_png

from pybest import __version__, filemanager
from pybest.exceptions import ArgumentError
from pybest.log import log


def ploti12(
    i12_ind_1,
    i12_ind_2,
    i12_val,
    indices,
    thresh,
    s1_index,
    s1_value,
    zoom=0.09,
):
    """Plot mutual information circular plot.

    **Arguments:**

    i12_ind_1, i12_ind_2 : iterable
        Iterables containing all orbital indices where zip(i12_ind_1, i12_ind_2)
        contains all non-redundant orbital pairs.

    i12_val : iterable
        Iterable containing all mutual entropy (i12) values corresponding
        to orbital pairs in zip(i12_ind_1, i12_ind_2).

    indices : iterable
        Indices of orbitals in the order we want to plot.

    thresh : float
        Mutual information values below threshold are not visible.

    s1_index : iterable
        Iterable containing all orbital indices.

    s1_value : iterable
        Iterable containing all single-orbital entropy values corresponding
        to indices in s1_index.

    zoom : float
        Zoom factor for orbital images.

    """
    plt.rcParams.update(
        {
            "text.usetex": 1,
        }
    )

    norb = len(indices)
    theta = 2 * np.pi * np.arange(1, norb + 1) / (norb)
    max_r = 150.0
    radius = np.ones(norb, int) * (max_r + 50.0)
    r = max_r * np.ones(norb, int) - 25.0 * (np.arange(0, norb) % 2)
    plt.figure(figsize=(10, 8))
    #
    # First subplot: mutual information
    #
    ax = plt.subplot(111, polar=True)
    ax.grid(False)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.spines["polar"].set_visible(False)

    for i in range(len(indices)):
        offset = -10
        if i % 2 == 0:
            offset = 10
        ax.annotate(
            indices[i],
            xy=(theta[i], r[i] + offset),
            xytext=(0, 0),
            textcoords="offset points",  # ha = 'center', va = 'bottom',
            fontsize=10,
            fontweight="bold",
            horizontalalignment="center",
            verticalalignment="center",
        )
        #
        # Plot orbitals if available.
        #
        filename = f"mo_{indices[i]!s}.png"
        try:
            offset = 50
            if i % 2 == 0:
                offset = 70
            arr_hand = read_png(filename)
            imagebox = OffsetImage(arr_hand, zoom=zoom)

            abox = AnnotationBbox(
                imagebox,
                (theta[i], r[i] + offset - 20),
                xycoords="data",
                frameon=False,
            )
            ax.add_artist(abox)
        except Exception:
            log.warn(f"Orbital image {filename} not found.")
            continue

    ax.yaxis.set_data_interval(0, 22.5)
    ax.xaxis.set_major_formatter(NullFormatter())
    ax.yaxis.set_major_formatter(NullFormatter())

    ax.plot(
        [theta[0], theta[0]],
        [radius[0], radius[0]],
        "",
        lw=2,
        color="w",
        zorder=0,
    )
    #
    # Sort i12 values
    #
    i12 = list(zip(i12_val, i12_ind_1, i12_ind_2))
    i12.sort(key=lambda x: x[0])  # The largest values are plotted on top.

    #
    # Define style and scale
    #
    color_map = mpl.colormaps.get_cmap("CMRmap_r")
    log_scale = colors.LogNorm(vmin=thresh, vmax=2 * np.log(2))

    for val, ind1, ind2 in i12:
        pos1 = np.where(indices == ind1)[0]
        pos2 = np.where(indices == ind2)[0]
        if not (len(pos1) == 1 and len(pos2) == 1):
            raise ValueError(f"Indices {ind1} [{pos1}] and {ind2} [{pos2}].")
        if val >= thresh:
            color = color_map(int(256 * log_scale(val / 2 / np.log(2))))
            linewidth = 4 * val / np.log(2)
        else:
            continue
        if linewidth < 1:
            linewidth = 1
        #
        # Plot quadratic Bezier curve
        #
        Path = mpath.Path
        start = np.array((*theta[pos1], *r[pos1]))
        end = np.array((*theta[pos2], *r[pos2]))
        middle = np.array((0, 0))
        bezier_curve = mpatches.PathPatch(
            Path(
                [start, middle, end], [Path.MOVETO, Path.CURVE3, Path.CURVE3]
            ),
            fc="none",
            lw=linewidth,
            color=color,
            transform=ax.transData,
        )
        ax.add_patch(bezier_curve)
    #
    # i_12 colormap legend
    #
    smc = plt.cm.ScalarMappable(cmap=color_map, norm=log_scale)
    plt.colorbar(smc, shrink=0.4, pad=0.05, ax=ax)

    #
    # Define size of circles in mutual information plot
    #
    positions = []
    for ind in indices:
        positions.append(int(np.where(s1_index == ind)[0][0]))
    areavalue = s1_value[positions]
    colorvalue = areavalue
    areavalue *= 200
    # Define own colormap:
    #
    endcolor = "#191970"
    midcolor2 = "#ff0000"
    midcolor1 = "#228b22"
    cmap2 = colors.LinearSegmentedColormap.from_list(
        "own2", [midcolor1, midcolor2, endcolor]
    )
    mpl.colormaps.register(cmap=cmap2)

    #
    # Plot circles of different size and color
    #
    ax.scatter(
        theta,
        r,
        s=areavalue,
        alpha=0.75,
        c=colorvalue,
        cmap=cmap2,
        norm=colors.LogNorm(vmin=thresh, vmax=np.log(2)),
        zorder=4,
    )

    ax.set_ylim(0, 225)
    plt.tight_layout()

    plt.savefig(f"{filemanager.result_path('i12.pdf')}", format="pdf", dpi=400)
    log(f"\nSuccess! Saved Iij plot in {filemanager.result_path('i12.pdf')}")


def plots1(orb_init, orb_final, s1_index, s1_value, smax=0.71):
    """Plot single orbital entropy.

    **Arguments:**

    orb_init : int
        Index of the first orbital in the plot.

    orb_final : int
        Index of the last orbital in the plot.

    s1_index : iterable
        Iterable containing all orbital indices.

    s1_value : iterable
        Iterable containing all single-orbital entropy values corresponding
        to indices in s1_index.

    smax : float
        Maximum value of single-orbital entropy in the plot.
    """
    plt.figure(figsize=(10, 5))
    ax2 = plt.subplot(111)
    ax2.axis([orb_init - 1, orb_final + 1, 0, smax])
    ax2.vlines(s1_index, [0], s1_value, color="r", linewidth=2, linestyle="-")
    plt.ylabel("single-orbital entropy")
    plt.xlabel("Orbital index")
    plt.plot(s1_index, s1_value, "ro", markersize=8)
    plt.savefig(f"{filemanager.result_path('s1.pdf')}", format="pdf", dpi=400)
    log(f"\nSuccess! Saved S1 plot in {filemanager.result_path('s1.pdf')}")


def read_i12_data(orb_init, orb_final, filename="i12.dat"):
    """Read mutual information data from file.

    **Arguments:**

    orb_init : int
        Index of the first orbital to be read.

    orb_final : int
        Index of the last orbital to be read.

    filename : string
        Name of the file with mutual information (i12) data.
    """
    index1 = np.array([], dtype=int)
    index2 = np.array([], dtype=int)
    value = np.array([])
    with open(filename) as file_in:
        for line in file_in:
            words = line.split()
            if (
                int(words[0]) >= orb_init
                and int(words[1]) >= orb_init
                and int(words[0]) <= orb_final
                and int(words[1]) <= orb_final
            ):
                index1 = np.append(index1, int(words[0]))
                index2 = np.append(index2, int(words[1]))
                value = np.append(value, float(words[2]))
    return index1, index2, value


def read_s1_data(orb_init, orb_final, filename="s1.dat"):
    """Read single orbital entropies from file.

    **Arguments:**

    orb_init : int
        Index of the first orbital to be read.

    orb_final : int
        Index of the last orbital to be read.

    filename : string
        Name of the file with single-orbital entropy (s1) data.
    """
    index = np.array([], dtype=int)
    value = np.array([])
    with open(filename) as file_in:
        for line in file_in:
            words = line.split()
            if len(words) != 2:
                raise ArgumentError(
                    f"Expecting 2 fields on each data line in {filename}"
                )
            index = np.append(index, int(words[0]))
            value = np.append(value, float(words[1]))
    if orb_final:
        newind = np.where(index >= (orb_init))
        index = index[newind]
        value = value[newind]
        newind2 = np.where(index <= orb_final)
        index = index[newind2]
        value = value[newind2]
    return index, value


def get_highest_s1_index(index, value, number):
    """Returns indices of orbitals with highest s1.

    **Arguments:**

    index : iterable
        Iterable containing all orbital indices.

    value : iterable
        Iterable containing all single-orbital entropy values corresponding
        to indices in s1_index.

    number : int
        Limits the number of single-orbital entropy (s1) values.
    """
    s1 = [(i, v) for i, v in zip(index, value)]
    s1.sort(key=lambda x: x[1], reverse=True)
    index_ = np.asarray([i[0] for i in s1])
    return sorted(index_[:number])


def get_highest_i12_index(index1, index2, value, number):
    """Returns indices of orbitals with highest i12.

    **Arguments:**

    index1, index2 : iterable
        Iterables containing all orbital indices where zip(index1, index2)
        contains all non-redundant orbital pairs.

    value : iterable
        Iterable containing all mutual entropy (i12) values corresponding
        to indices in s1_index.

    number : int
        Limits the number of mutual entropy (i12) values.
    """
    # Get all non-redundant indices of orbitals
    orbitals = set(index1).union(set(index2))
    omin = min(orbitals)  # the smallest index
    omax = max(orbitals)  # the largest index
    # Initialize a list containing orbital indices and associated highest i12
    i12 = [[i + omin, 0.0] for i, j in enumerate(range(omin, omax + 1))]
    # Find highest i12 for each orbital
    for i, j, v in zip(index1, index2, value):
        if i12[i - omin][1] < v:
            i12[i - omin][1] = v
        if i12[j - omin][1] < v:
            i12[j - omin][1] = v
    # Get indices of orbitals with highest i12
    i12.sort(key=lambda x: x[1], reverse=True)
    return sorted([i[0] for i in i12[:number]])


def parse_args(args):
    """Parse arguments.

    **Supported flags:**

    --version, -V
        Prints PyBEST version.

    --threshold <float>
        Lowest mutual information value in the plot.

    -i <int>
        Index of the first orbital in the plot.

    -f <int>
        Index of the last orbital in the plot.

    --zoom <float>
        Zoom factor for orbital pictures.

    --plot <string>
        "all", "s1", or "i12" - specifies the type of plot.

    --smax <float>
        The maximum value of single-orbital entropy (s1) in the plot.

    --iname <string>
        The name of the file with mutual information (i12) values.

    --sname <string>
        The name of the file with single-orbital entropy (s1) values.

    --order <int sequence>
        The order of orbitals shown in the graph.

    --largest-i <int>
        Specifies a number of mutual information values shown in the plot.

    --largest-s <int>
        Specifies a number of single-orbital entropy values shown in the plot.

    --indices <int sequence>
        Specifies a user-defined set of orbitals in the plot.

    """
    parser = argparse.ArgumentParser(
        prog="pybest-entanglement.py",
        description="This script makes an orbital entanglement plot. It "
        "assumes that the files s1.dat and i12.dat are present in "
        "the current directory. These two files will be used to "
        "create the figure orbital_entanglement.png.",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"{parser.prog} (PyBEST version) {__version__}",
    )
    parser.add_argument(
        "--threshold",
        default=0.001,
        type=float,
        nargs="?",
        help="orbitals with a mutual information below this threshold will not"
        " be connected by a line [default=%(default)s]",
    )
    parser.add_argument(
        "-i",
        default=1,
        type=int,
        nargs="?",
        help="the first orbital to be used for the plot "
        "(indexing from 1) [default=%(default)s]",
    )
    parser.add_argument(
        "-f",
        default=None,
        type=int,
        nargs="?",
        help="the last orbital to be used for the plot (inclusive) "
        "(indexing from 1) [default=last orbital]",
    )
    parser.add_argument(
        "--zoom",
        default=0.03,
        type=float,
        nargs="?",
        help="zoom factor for orbitals. [default=%(default)s]",
    )
    parser.add_argument(
        "--plot",
        default="all",
        type=str,
        nargs="?",
        help="Type of graph to be plotted. If not specified (None) both graphs "
        "will be generated. Possible values are None, i (mutual information), "
        "s (single-orbital entropy) [default=%(default)s]",
    )
    parser.add_argument(
        "--smax",
        default=0.71,
        type=float,
        nargs="?",
        help="the maximum of s1 scale [default=%(default)s]",
    )
    parser.add_argument(
        "--iname",
        default="i12.dat",
        type=str,
        nargs="?",
        help="file name to be read in for Iij [default=%(default)s]",
    )
    parser.add_argument(
        "--sname",
        default="s1.dat",
        type=str,
        nargs="?",
        help="file name to be read in for S1 [default=%(default)s]",
    )
    parser.add_argument(
        "--order",
        default=None,
        metavar="i",
        type=int,
        nargs="+",
        help="The order of the indices to be shown on each graph. "
        "Indexing starts from 1. [default=%(default)s]",
    )
    parser.add_argument(
        "--largest-i",
        default=0,
        type=int,
        nargs="?",
        help="select [LARGEST_I] orbitals with largest Iij values for Iij plot",
    )
    parser.add_argument(
        "--largest-s",
        default=0,
        type=int,
        nargs="?",
        help="select [LARGEST_S] orbitals with largest S1 values for Iij plot",
    )
    parser.add_argument(
        "--indices",
        default=None,
        type=int,
        nargs="+",
        help="user-specified orbital indices for Iij plot (indexing from 1)",
    )
    return parser.parse_args(args)


def main():
    """This is main of CLI app.

    The flow is following: the data and command
    line arguments are read and turned into pretty pictures in pdf format.
    """
    args = parse_args(sys.argv[1:])

    # Paths for data files
    iname = pathlib.Path(args.iname)
    sname = pathlib.Path(args.sname)
    # Orbitals which will be printed
    orb_init = args.i
    orb_final = args.f
    number_i = args.largest_i
    number_s = args.largest_s
    indices = args.indices
    order = args.order
    if order is not None:
        order = [i - 1 for i in order]
    # Plotting options
    plot_type = args.plot
    smax = args.smax
    zoom = args.zoom

    # Read single-orbital entropies from s1.dat
    s1_index, s1_value = read_s1_data(orb_init, orb_final, sname)

    # Check the index of last orbital
    if orb_final is None:
        orb_final = s1_index[-1]
    orb_init = min(s1_index)
    log("\nSelected options for S1 plot")
    log(f"  [x] set initial orbital to {orb_init}")
    log(f"  [x] set final orbital to {orb_final}")
    log(f"  [x] set maximal S1 value to {smax}")

    # Read mutual information values from i12.dat
    i12_index_1, i12_index_2, i12_value = read_i12_data(
        orb_init, orb_final, iname
    )

    # Get indices of orbitals which will be included in plot
    log("\nSelected options for Iij plot")
    log(f"  [x] set zoom factor for orbitals to {zoom}")
    log(f"  [x] set threshold for Iij values to {args.threshold}")
    if indices is not None:
        log("  [x] using the user-specified orbitals")
    elif number_i:
        log(f"  [x] using {number_i} orbitals with largest Iij values")
        indices = get_highest_i12_index(
            i12_index_1, i12_index_2, i12_value, number_i
        )
    elif number_s:
        log(f"  [x] using {number_s} orbitals with largest Iij values")
        indices = get_highest_s1_index(s1_index, s1_value, number_s)
    else:
        log(f"  [x] using orbitals from {orb_init} to {orb_final}")
        indices = list(range(orb_init, orb_final + 1))

    # Reorder
    if order and len(order) != len(indices):
        raise ArgumentError(
            "Number of orbitals and elements of order must be the same."
        )
    if order:
        indices = np.asarray(indices)[order]
        log("  [x] orbitals will be reordered")

    # Check if indices are read correctly
    log(f"\nThe Iij plot includes orbitals {', '.join(map(str, indices))}.")

    # Plot only selected graphs
    if plot_type not in ["i", "s", "all"]:
        raise ValueError(f"Unknown type {plot_type}")
    if plot_type in ["s", "all"]:
        plots1(orb_init, orb_final, s1_index, s1_value, smax)
    if plot_type in ["i", "all"]:
        # Filter the values which will be printed
        s_1 = [(i, v) for i, v in zip(s1_index, s1_value) if i in indices]
        s1_index = np.asarray([element[0] for element in s_1])
        s1_value = np.asarray([element[1] for element in s_1])
        _i_12 = zip(i12_index_1, i12_index_2, i12_value)
        i_12 = [
            (i, j, v) for i, j, v in _i_12 if i in indices and j in indices
        ]
        i12_index_1 = np.asarray([element[0] for element in i_12])
        i12_index_2 = np.asarray([element[1] for element in i_12])
        i12_value = np.asarray([element[2] for element in i_12])
        # Plot
        ploti12(
            i12_index_1,
            i12_index_2,
            i12_value,
            indices,
            args.threshold - 0.0005,
            s1_index,
            s1_value,
            zoom,
        )


if __name__ == "__main__":
    main()
