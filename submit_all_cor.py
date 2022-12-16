import os
from argparse import ArgumentParser
from subprocess import Popen, PIPE, STDOUT

# Get list of out_dirs

def get_outdirs(mmml_dir):
    """Find all out_dirs in mmml_dir

    Args:
        mmml_dir (str): Path to mmml_corrections directory.

    Yields:
        tuple: Tuple of ligand name and out_dir path.
    """
    for lig_name in os.listdir(mmml_dir):
        for leg in ["complex", "solvent"]:
            path = os.path.join(mmml_dir, lig_name, leg)
            yield lig_name, path


def submit_all_corr(mmml_dir, n_iter, n_states, pdb_name="system_endstate.pdb", use_alt_init_coords=False):
    """Submit all corrections to slurm

    Args:
        mmml_dir (str): Path to mmml_corrections directory.
        n_iter (int): Number of iterations (of 1 ps) to run 
        simulations for.
        n_states (int): Number of linearly-spaced lambda windows
        to run.
        pdb_name (str, optional): Name of pdb file to use for parametrisation.
        use_alt_init_coords (bool, optional): Whether to use different initial positions for each state.
        Defaults to True.
    """
    print(f"Use alt init coords: {use_alt_init_coords}")
    # Submit runs
    job_ids = []

    for lig_name, out_dir in get_outdirs(mmml_dir):
        cmd = f'~/Documents/research/scripts/abfe/rbatch.sh --chdir={out_dir} submit_jobs.sh {lig_name} {n_iter} {n_states} ./{pdb_name} {str(use_alt_init_coords)}'
        print(cmd)
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE,
                  stderr=STDOUT, close_fds=True)
        output = p.stdout.read()
        job_ids.append(int(output.split()[-1]))

    # Submit analysis job
    cmd = f'~/Documents/research/scripts/abfe/rbatch.sh  --dependency=afterok:{",".join([str(i) for i in job_ids])} submit_analysis.sh {mmml_dir}'
    os.system(cmd)


def clean(mmml_dir):
    """Submit all corrections to slurm

    Args:
        mmml_dir (str): Path to mmml_corrections directory.
    """
    for lig_name, out_dir in get_outdirs(mmml_dir):
        cmd = f'rm {out_dir}/repex* {out_dir}/ani_correction* {out_dir}/input_params.txt'
        print(cmd)
        os.system(cmd)


def main():
    parser = ArgumentParser()
    parser.add_argument("--mmml_dir", type=str, default="mmml_corrections",
                        help="Path to mmml_corrections directory.")
    parser.add_argument("--n_iter", type=int, default=5000,
                        help="Number of iterations (of 1 ps) to run simulations for.")
    parser.add_argument("--n_states", type=int, default=10,
                        help="Number of linearly-spaced lambda-windows to use.")
    parser.add_argument("--pdb_name", type=str, default="snapshot_0.pdb",
                        help="Name of pdb file to use for parametrisation.")
    parser.add_argument("--use_alt_int_coords", type=bool, default=False,
                        help="Use different initial positions for each state.")
    parser.add_argument("--mode", type=str, default="run",
                        help="run or clean: whether to run all corrections or clean up.")
    args = parser.parse_args()

    if args.mode == "run":
        print("Submitting all corrections...")
        submit_all_corr(args.mmml_dir, args.n_iter, args.n_states, args.pdb_name , use_alt_init_coords=args.use_alt_int_coords)
    elif args.mode == "clean":
        print("Cleaning all corrections...")
        clean(args.mmml_dir)


if __name__ == "__main__":
    main()
