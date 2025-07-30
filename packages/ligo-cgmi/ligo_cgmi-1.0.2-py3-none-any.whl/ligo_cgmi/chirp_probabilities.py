import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import h5py
import argparse
import json
from astropy import units as u
from configparser import ConfigParser
from pathlib import Path

from astropy.coordinates import Distance
from astropy.cosmology import Planck18
from ligo.skymap import distance
from ligo.skymap import moc
from ligo.skymap.postprocess.cosmology import cosmo
from ligo.skymap.io import read_sky_map

from ligo_cgmi.fetch_data_products import fetch_event


def get_parser():

    parser = argparse.ArgumentParser(
        description=""
    )
    parser.add_argument(
        "--event", type=str, required=True, help="name of event or superevent"
    )
    parser.add_argument(
        "--type", type=str, default="both", help="cgmi estimate to produce for CBC event: both, PE, or LL",  # noqa E501
    )

    parser.add_argument(
        "--plot", type=bool, default=False, help="plot a cgmi histogram",
    )
    parser.add_argument(
        "--plot_det_mc", type=bool, default=False, help="whether to include detector chirp mass point estimate in the plot",  # noqa E501
    )
    parser.add_argument(
        "--PE_filename", type=str, default='Bilby.posterior_samples.hdf5', help="parameter estimation filename",  # noqa E501
    )
    parser.add_argument(
        "--skymap_filename", type=str, default='bayestar.multiorder.fits', help="skymap filename",  # noqa E501
    )
    parser.add_argument(
        "--save_path", type=str, default='PE', help="folder to save PE and plots",  # noqa E501
    )
    parser.add_argument(
        "--MDC", type=bool, default=False, help="True if running on MDC event from playground",  # noqa E501
    )
    parser.add_argument(
        "--json", type=bool, default=False, help="save to json",  # noqa E501
    )

    return parser


def chirp_mass_histogram_LL(sky_map, mchirp_det, bin_edges, cosmo,
                            save_path=None, plot_det_mc=False):
    """
    Provided by Leo Singer
    Calculate a binned probability distribution for the source-frame
    chirp mass of a compact binary using a low-latency point estimate.

    Parameters
    ----------
    sky_map : astropy.table.Table
        Multi-resolution sky map as returned by
        :meth:ligo.skymap.io.read_sky_map`.
    mchirp_det : float
        Point estimate of detector-frame chirp mass.
    bin_edges : numpy.ndarray
        Array of source-frame chirp mass bin edges, **not**
        including the implied leftmost edge at 0 and rightmost
        edge at +infinity.
    cosmo : astropy.cosmology.Cosmology
        The cosmological model to use to calculate luminosity distance
        from redshift.
    save_path : string
        Path to save plot to, None means the plot is not saved
    plot_det_mc : bool
        Whether or not to include detector mchirp in plot

    Returns
    -------
    probs : numpy.ndarray
        Array of source-frame chirp mass probabilities.
        This array has a length that is one less than the length
        of ``bin_edges``. The value of ``prob[i]`` is the probability
        that the source-frame chirp mass is between ``bin_edges[i]``
        and ``bin_edges[i] + 1``.
    """

    # CBC, estimate will be source frame
    if sky_map:
        with np.errstate(divide='ignore'):
            z = np.maximum(mchirp_det / bin_edges - 1, 0)
        DL = cosmo.luminosity_distance(z).to_value(u.Mpc)
        prob = sky_map['PROBDENSITY'] * moc.uniq2pixarea(sky_map['UNIQ'])
        cdf = distance.marginal_cdf(DL, prob, sky_map['DISTMU'],
                                    sky_map['DISTSIGMA'], sky_map['DISTNORM'])
        probs = np.diff(-cdf)

        if save_path:
            with plt.style.context('seaborn-v0_8-white'):
                plt.figure(figsize=(7, 2))
                plt.subplots_adjust(bottom=0.25)
                plt.bar(range(len(bin_edges)-1), probs, alpha=1, align='edge',
                        label='Low-Latency estimate', width=1, edgecolor='w')

                if plot_det_mc:
                    plt.axvline(mchirp_det, color='k',
                                label='Detector Frame point estimate')

                # remove hanging .0 on integer bins for labels
                bin_labels = [int(e) if e % 1 == 0 else e for e in bin_edges]
                plt.xticks(range(len(bin_edges)), labels=bin_labels)
                plt.tick_params(axis='x', direction='out', length=3, width=1)
                plt.xlabel(r'Source Frame Chirp Mass Bin ($M_{\odot}$)')
                plt.ylabel('Probability')
                plt.legend()
                plt.savefig(save_path)
                plt.close()

    # cWB BBH, estimate will be single bin in detector frame
    else:
        probs, bin_edges, _ = plt.hist(mchirp_det, bins=bin_edges,
                                       linewidth=2, edgecolor='blue',
                                       alpha=.7, histtype='stepfilled')

        # normalize
        probs = probs/np.sum(probs)

        if save_path:
            with plt.style.context('seaborn-v0_8-white'):
                plt.figure(figsize=(7, 2))
                plt.subplots_adjust(bottom=0.25)
                plt.bar(range(len(bin_edges)-1), probs, alpha=1, align='edge',
                        label='Low-Latency estimate', width=1, edgecolor='w')

                # remove hanging .0 on integer bins for labels
                bin_labels = [int(e) if e % 1 == 0 else e for e in bin_edges]
                plt.xticks(range(len(bin_edges)), labels=bin_labels)
                plt.tick_params(axis='x', direction='out', length=3, width=1)
                plt.xlabel(r'Source Frame Chirp Mass Bin ($M_{\odot}$)')
                plt.ylabel('Probability')
                plt.legend()
                plt.savefig(save_path)
                plt.close()

    # round for readability and to avoid floating point issues
    probs = np.round(probs, decimals=3)
    return probs


def chirp_mass_histogram_PE(mchirp_source, mchirp_det, bin_edges,
                            save_path=None, plot_det_mc=False):
    """
    Calculate a binned probability distribution for the source-frame
    chirp mass of a compact binary using parameter estimation samples.

    Parameters
    ----------
    mchirp_source : numpy.ndarray
        PE posterior samples of source-frame chirp mass.
    mchirp_det : float
        Point estimate of detector-frame chirp mass.
    bin_edges : numpy.ndarray
        Array of source-frame chirp mass bin edges, **not**
        including the implied leftmost edge at 0 and rightmost
        edge at +infinity.
    save_path : string
        Path to save plot to, None means the plot is not saved
    plot_det_mc : bool
        Whether or not to include detector mchirp in plot

    Returns
    -------
    probs : numpy.ndarray
        Array of source-frame chirp mass probabilities.
        This array has a length that is one less than the length
        of ``bin_edges``. The value of ``prob[i]`` is the probability
        that the source-frame chirp mass is between ``bin_edges[i]``
        and ``bin_edges[i] + 1``.
    """

    probs, bin_edges, _ = plt.hist(mchirp_source, bins=bin_edges,
                                   linewidth=2, edgecolor='blue',
                                   alpha=.7, histtype='stepfilled')
    # normalize
    probs = probs/np.sum(probs)

    if save_path:
        with plt.style.context('seaborn-v0_8-white'):
            plt.figure(figsize=(7, 2))
            plt.subplots_adjust(bottom=0.25)
            plt.bar(range(len(bin_edges)-1), probs, alpha=1, align='edge',
                    label='PE estimate', width=1, edgecolor='w')

            if plot_det_mc:
                plt.axvline(mchirp_det, color='k',
                            label='Detector Frame point estimate')

            # remove hanging .0 on integer bins for labels
            bin_labels = [int(e) if e % 1 == 0 else e for e in bin_edges]
            plt.xticks(range(len(bin_edges)), labels=bin_labels)
            plt.tick_params(axis='x', direction='out', length=3, width=1)
            plt.xlabel(r'Source Frame Chirp Mass Bin ($M_{\odot}$)')
            plt.ylabel('Probability')
            plt.legend()
            plt.savefig(save_path)
            plt.close()

    # round for readability and to avoid floating point issues
    probs = np.round(probs, decimals=3)

    return probs


def load_posterior_samples(filename):
    """
    Read in posterior samples and shift masses to source frame if needed

    Parameters
    ----------
    filename : string
        path to file

    Returns
    -------
    PE_data : pandas DataFrame
        posterior samples
    """
    PE_data = pd.DataFrame(np.array(h5py.File(filename)['posterior_samples']))
    if 'chirp_mass_source' in PE_data.keys() or \
            ('mass_1_source' and 'mass_2_source') in PE_data.keys():
        return PE_data
    # compute source frame information using distance and cosmology
    distances = Distance(PE_data['luminosity_distance'].values, u.Mpc)
    one_plus_z = 1 + distances.compute_z(Planck18)
    try:
        chirp_mass = PE_data['chirp_mass']
        PE_data['chirp_mass_source'] = chirp_mass / one_plus_z
    except KeyError:
        try:
            PE_data['mass_1_source'] = PE_data['mass_1'] / one_plus_z
            PE_data['mass_2_source'] = PE_data['mass_2'] / one_plus_z
        except KeyError:
            raise ValueError(
                "Posterior samples missing chirp mass "
                "or component mass information."
            )
    return PE_data


def masses2chirp(m1, m2):
    """
    Convert component masses to chirp mass

    Parameters
    ----------
    m1 : numpy.ndarray
        larger component mass
    m2 : numpy.ndarray
        smaller component mass

    Returns
    -------
    mchirp : numpy.ndarray
        chirp mass
    """
    mchirp = ((m1*m2)**(3./5.)) * ((m1 + m2)**(-1./5.))

    return mchirp


def cgmi(group, mchirp_det, PE_data, sky_map, plot=False, cgmi_type='both',
         plot_det_mc=False, save_path='chirp_estimates', MDC=False):
    """
    function to find cgmi estimates

    Parameters
    ----------
    group: str
        search group, CBC or Burst
    mchirp_det: float
        detector frame chirp mass
    PE_data: pandas DataFrame
        parameter estimation table
    sky_map:
        HEALPix array and dictionary of metadata
    plot: bool
        whether to plot a cgmi histogram
    cgmi_type: str
        cgmi estimates to find for CBC event: 'LL', 'PE', or 'both'
    plot_det_mc: bool
        whether to include detector chirp mass point estimate in the plot
    save_path: str
        where to save plots and PE
    MDC: bool
        True is event is from MDC, False otherwise
    Returns
    -------
    chirp_bins : numpy.ndarray
        Array of left and right source-frame chirp mass bin edges
    probs_LL : numpy.ndarray
        Array of source-frame chirp mass probabilities from low-latency
        point estimate This array has a length that is one less than the
        length of ``bin_edges``. The value of ``prob[i]`` is the probability
        that the source-frame chirp mass is between ``bin_edges[i]``
        and ``bin_edges[i] + 1``.
    probs_PE : numpy.ndarray
        Array of source-frame chirp mass probabilities from low-latency
        point estimate This array has a length that is one less than the
        length of ``bin_edges``. The value of ``prob[i]`` is the probability
        that the source-frame chirp mass is between ``bin_edges[i]``
        and ``bin_edges[i] + 1``.
    """

    rel_path = 'conf.ini'
    conf_path = Path(__file__).parents[0] / rel_path
    config = ConfigParser()
    config.read(conf_path)

    # chirp mass bins
    chirp_bins = np.asarray([float(bin) for bin in
                             config.get('conf', 'chirp_bins').split()])

    probs_LL, probs_PE = None, None

    if plot:
        LL_path = f'{save_path}/mchirp_histogram_LL.png'
        PE_path = f'{save_path}/mchirp_histogram_PE.png'
    else:
        LL_path, PE_path = None, None

    if cgmi_type in ['LL', 'both']:
        # CBC events
        if str(group).lower() == 'cbc':
            probs_LL = chirp_mass_histogram_LL(sky_map, mchirp_det,
                                               chirp_bins, cosmo,
                                               save_path=LL_path,
                                               plot_det_mc=plot_det_mc)
        # cWB BBH events
        else:
            mchirp_det = np.array([mchirp_det])
            probs_LL = chirp_mass_histogram_LL(False, mchirp_det, chirp_bins,
                                               None, save_path=LL_path,
                                               plot_det_mc=plot_det_mc)
    if cgmi_type in ['PE', 'both']:
        try:
            mchirp_source = PE_data['chirp_mass_source']
        except KeyError:
            mchirp_source = masses2chirp(PE_data['mass_1_source'],
                                         PE_data['mass_2_source'])
        probs_PE = chirp_mass_histogram_PE(mchirp_source, mchirp_det,
                                           chirp_bins,
                                           save_path=PE_path,
                                           plot_det_mc=plot_det_mc)

    return chirp_bins, probs_LL, probs_PE


def main(verbose=True):
    parser = get_parser()
    args = parser.parse_args()

    if args.type not in ['PE', 'LL', 'both']:
        print('Type should be: "PE", "LL", or "both"')
        quit()
    mchirp_det, group = fetch_event(args.event, PE_filename=args.PE_filename,
                                    skymap_filename=args.skymap_filename,
                                    save_path=args.save_path, MDC=args.MDC)

    save_path = f'{args.save_path}/{args.event}'
    PE_path = f'{save_path}/{args.PE_filename}'
    skymap_path = f'{save_path}/{args.skymap_filename}'

    if str(group).lower() == 'cbc':
        if args.type in ['PE', 'both']:
            PE_data = load_posterior_samples(PE_path)
        else:
            PE_data = None
        if args.type in ['LL', 'both']:
            sky_map = read_sky_map(skymap_path, moc=True)
        else:
            sky_map = None
    else:
        PE_data, sky_map = None, None
    chirp_bins, probs_LL, probs_PE = cgmi(group,
                                          mchirp_det,
                                          PE_data,
                                          sky_map,
                                          plot=args.plot,
                                          cgmi_type=args.type,
                                          plot_det_mc=args.plot_det_mc,
                                          save_path=save_path,
                                          MDC=args.MDC)

    if args.json:
        if args.type in ['LL', 'both']:
            data_LL = {
                'bin_edges': chirp_bins.tolist(),
                'probabilities': probs_LL.tolist(),
            }
            with open('mchirp_source.json', 'w') as f:
                json.dump(data_LL, f)

        if args.type in ['PE', 'both']:
            data_PE = {
                'bin_edges': chirp_bins.tolist(),
                'probabilities': probs_PE.tolist(),
            }
            with open('mchirp_source_PE.json', 'w') as f:
                json.dump(data_PE, f)

    if verbose:
        print(f'Chirp mass bins: {chirp_bins}')
        print(f'Low-latency bin probabilities {probs_LL}')
        print(f'Parameter estimation bin probabilities {probs_PE}')


if __name__ == "__main__":
    main()
