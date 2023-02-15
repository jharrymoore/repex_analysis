# loop over output directories, plot all complex rmsd on the same plot


from repex_analysis.repex_analysis import plot_rmsd, plot_overlap, plot_replica_mixing, plot_correction_timeseries, write_correction
from openmmtools.multistate import MultiStateSamplerAnalyzer, MultiStateReporter
import os
import sys
import logging
import matplotlib.pyplot as plt
from tqdm import tqdm
from argparse import ArgumentParser
from multiprocessing import Pool


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.getLogger("openmmtools").setLevel(logging.CRITICAL)

def make_plots(values):
    directory, output_dir, plots, timeseries = values
    print(f"Generating plots for {output_dir}")
    if plots:
        for leg in ["complex", "solvent"]:
            logger.info(f"Analysing directory {output_dir}")
            try:
                resname = "UNK" if leg == "complex" else ".pd"
                pdb_file = os.path.join(directory, output_dir, f"{leg}/prepared_system.pdb")
                path_nc = os.path.join(directory, output_dir, f"{leg}/repex.nc")
                rep_com = MultiStateReporter(path_nc)
                analyser = MultiStateSamplerAnalyzer(rep_com)
                plot_rmsd(pdb_file=pdb_file, path_nc=path_nc, analyser=analyser, resname=resname, out_file=os.path.join(directory, output_dir,f"{leg}/rmsd.png"))
                plot_overlap(output_dir, leg, analyser, os.path.join(directory, output_dir, f"{leg}/overlap.png"))
                plot_replica_mixing(analyser=analyser, out_file = os.path.join(directory, output_dir, f"{leg}/mixing.png"))

            except Exception as e:
                logger.warning(e)

    # now do the timeseries
    # print("Plotting Timeseries...")
    if timeseries:
        try:
            ana_com = MultiStateSamplerAnalyzer(MultiStateReporter(os.path.join(directory, output_dir, "complex/repex.nc")))
            ana_sol = MultiStateSamplerAnalyzer(MultiStateReporter(os.path.join(directory, output_dir, "solvent/repex.nc")))
            # print(f"writing correction for {output_dir}")
            write_correction(ana_com=ana_com, ana_sol=ana_sol, temp=298, out_file=os.path.join(directory, output_dir, "correction.txt"))
            plot_correction_timeseries(output_com=os.path.join(directory, output_dir, f"complex/repex.nc"),
                    output_sol=os.path.join(directory, output_dir, f"solvent/repex.nc"),
                    out_file=os.path.join(directory, output_dir, "correction_ts.png"),
                    n_iterations_com=1400, n_iterations_sol=1400, temp=298

                    )
        except Exception as e:
            print(e)



def main():
    parser = ArgumentParser()
    parser.add_argument('-d', '--directory')
    parser.add_argument("-t", help="construct timeseries", action="store_true")
    parser.add_argument("-p", help="construct plots", action="store_true")
    parser.add_argument("-n", "--nprocs", default=4, type=int)
    args = parser.parse_args()
    dirs = os.listdir(args.directory)
    print(dirs)
    plots = [args.t for _ in range(len(dirs))]
    timeseries = [args.p for _ in range(len(dirs))]
    print(plots, timeseries)
    values = [(args.directory, direc, plot, ts) for direc, plot, ts in zip(dirs, plots, timeseries)]
    print(values)
    p = Pool(args.nprocs)

    p.map(make_plots, values)

        
      

   

            
if __name__ == "__main__":
    main()