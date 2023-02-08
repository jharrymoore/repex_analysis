# loop over output directories, plot all complex rmsd on the same plot


from repex_analysis.repex_analysis import plot_rmsd, plot_overlap, plot_replica_mixing, plot_correction_timeseries, write_correction
from openmmtools.multistate import MultiStateSamplerAnalyzer, MultiStateReporter
import os
import sys
import logging
import matplotlib.pyplot as plt
from tqdm import tqdm
from argparse import ArgumentParser


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.getLogger("openmmtools").setLevel(logging.CRITICAL)

def main():
    parser = ArgumentParser()
    parser.add_argument('-d', '--directory')
    args = parser.parse_args()
    for output_dir in tqdm(os.listdir(args.directory)):
        print(output_dir)
        for leg in ["complex", "solvent"]:
            logger.info(f"Analysing directory {output_dir}")
            try:
                resname = "UNK" if leg == "complex" else ".pd"
                pdb_file = os.path.join(args.directory, output_dir, f"{leg}/prepared_system.pdb")
                path_nc = os.path.join(args.directory, output_dir, f"{leg}/repex.nc")
                rep_com = MultiStateReporter(path_nc)
                analyser = MultiStateSamplerAnalyzer(rep_com)
                plot_rmsd(pdb_file=pdb_file, path_nc=path_nc, analyser=analyser, resname=resname, out_file=os.path.join(args.directory, output_dir,f"{leg}/rmsd.png"))
                plot_overlap(output_dir, leg, analyser, os.path.join(args.directory, output_dir, f"{leg}/overlap.png"))
                plot_replica_mixing(analyser=analyser, out_file = os.path.join(args.directory, output_dir, f"{leg}/mixing.png"))

            except Exception as e:
                logger.warning(e)

        # ana_com = MultiStateSamplerAnalyzer(MultiStateReporter(os.path.join(args.directory, output_dir, "complex/repex.nc")))
        # ana_sol = MultiStateSamplerAnalyzer(MultiStateReporter(os.path.join(args.directory, output_dir, "solvent/repex.nc")))
        # print(f"writing correction for {output_dir}")
        # write_correction(ana_com=ana_com, ana_sol=ana_sol, temp=298, out_file=os.path.join(args.directory, output_dir, "correction.txt"))
    # now do the timeseries
    # print("Plotting Timeseries...")
    #     try:
    #         plot_correction_timeseries(output_com=os.path.join(args.directory, output_dir, f"complex/repex.nc"),
    #                 output_sol=os.path.join(args.directory, output_dir, f"solvent/repex.nc"),
    #                 out_file=os.path.join(args.directory, output_dir, "correction_ts.png"),
    #                 n_iterations_com=600, n_iterations_sol=600, temp=298

    #                 )
    #     except Exception as e:
    #         print(e)
      

   

            
if __name__ == "__main__":
    main()