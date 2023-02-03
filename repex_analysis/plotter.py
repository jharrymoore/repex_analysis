# loop over output directories, plot all complex rmsd on the same plot


from repex_analysis.repex_analysis import plot_rmsd, plot_overlap, plot_replica_mixing
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
    for leg in ["complex", "solvent"]:
        for output_dir in tqdm(os.listdir(args.directory)):
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

   

            
if __name__ == "__main__":
    main()