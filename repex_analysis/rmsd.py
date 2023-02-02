# loop over output directories, plot all complex rmsd on the same plot


from repex_analysis.repex_analysis import plot_rmsd, plot_overlap, plot_replica_mixing
from openmmtools.multistate import MultiStateSamplerAnalyzer, MultiStateReporter
import os
import sys
import logging
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
        logger.info(f"Analysing directory {output_dir}")
        try:
            pdb_file = os.path.join(args.directory, output_dir, "complex/prepared_system.pdb")
            path_nc = os.path.join(args.directory, output_dir, "complex/repex.nc")
            rep_com = MultiStateReporter(path_nc)
            analyser = MultiStateSamplerAnalyzer(rep_com)
            plot_rmsd(pdb_file=pdb_file, path_nc=path_nc, analyser=analyser, resname="UNK", out_file=os.path.join(args.directory, output_dir,"complex/rmsd.png"))
            plot_overlap(output_dir, "complex", analyser, os.path.join(args.directory, output_dir, "complex/overlap.png"))
            plot_replica_mixing(analyser=analyser, out_file = os.path.join(args.directory, output_dir, "complex/overlap.png"))

        except Exception as e:
            logger.warning(e)

            
if __name__ == "__main__":
    main()