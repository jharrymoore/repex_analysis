import os
import subprocess
import argparse


def wait_for_job_start(launch_dir: str, job_id: str):
    
    job_running = False
    while not job_running:
        with open(os.path.join(launch_dir, f"slurm-{job_id}.out"), 'r') as f:
            lines = f.readlines()
        n_propagations = len([l for l in lines if "Propagating all replica" in l])
        print(f"Got {n_propagations} propagations")
        if n_propagations == 3:
            job_running = True
            # get second iter mixing statistic - should be 20-30%
            mixing_stats = [l for l in lines if "attempted swaps ("][-1].split("(")[-1].split(")")[0]
            print(mixing_stats)
            print("Got 2 propatagations - continuing...")

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--launch_dir", "-l")
    parser.add_argument("--solvent", "-s", action="store_true")
    parser.add_argument("--complex", "-c",action="store_true")
    args = parser.parse_args()

    if args.solvent:
        batch_scripts = [f for f in os.listdir(args.launch_dir) if f.endswith("solvent.sh")]
        for script in batch_scripts:
            output = subprocess.run(f"sbatch {os.path.join(args.launch_dir, script)}", capture_output=True, shell=True)
            job_id = output.stdout.split()[-1]
            print(job_id)


            wait_for_job_start(args.launch_dir, job_id)

    if args.cplx:
        batch_scripts = [f for f in os.listdir(args.launch_dir) if f.endswith("solvent.sh")]
        for script in batch_scripts:
            output = subprocess.run(f"sbatch {os.path.join(args.launch_dir, script)}", capture_output=True, shell=True)
            job_id = output.stdout.split()[-1]
            print(job_id)


            wait_for_job_start(args.launch_dir, job_id)

            # now wait until the job has done atleast its first 2 iterations





if __name__ == "__main__":
    main()