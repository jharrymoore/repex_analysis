import os
import sys

import argparse

def main(direc: str, replicas: int, model_path: str, smff: str, output_dir: str, n_gpu: int = 2):
    complex_files = [f for f in os.listdir(os.path.join(direc, "complex"))]
    ligand_files = [f for f in os.listdir(os.path.join(direc, "ligands"))]

    sys_names = [f.split(".")[0] for f in ligand_files]
    print(sys_names)
    # ligands should have the right coords to work with the complexes as well
    tasks_per_gpu = int(replicas / n_gpu)
    gpu_bind_components = [f"{idx}," * tasks_per_gpu for idx in range(n_gpu) ] 
    gpu_bind_string = ""
    for elem in gpu_bind_components:
        gpu_bind_string += elem
    gpu_bind_string = gpu_bind_string[:-1]


    for ligand, sys_name in zip(ligand_files, sys_names):
        # for leg in ["complex", 'solvent']:
        cplx = [f for f in complex_files if ligand.split(".")[0] in f][0]
        # print(cplx)

        # smi = [s for s in smiles if smiles_id in s][0].split()[0]
        # print("smiles is", smi)


  

        # write the ligand batch script

        lig_batch_script = f"""#!/bin/bash -l
#SBATCH -N 1
#SBATCH -t 24:00:00
#SBATCH -p ampere
#SBATCH --gres=gpu:{n_gpu}
#SBATCH -A csanyi-SL2-GPU
#SBATCH --ntasks {replicas}

export HDF5_USE_FILE_LOCKING=FALSE
source ~/.bashrc

conda activate mlmm
which python


srun -n {replicas} --gpu-bind=map_gpu:{gpu_bind_string} mace-md -f {os.path.join(direc, "ligands", ligand)} --ml_mol '{os.path.join(direc, "ligands", ligand)}' --run_type repex --replicas {replicas} --log_level 10  --model_path {model_path} --dtype float64 --neighbour_list torch_nl_n2 --output_dir {output_dir}/{sys_name}/solvent --resname {sys_name} --system_type hybrid --smff {smff} --equil gentle --restart
    """
        print(lig_batch_script)
        with open(f"mace_repex_{sys_name}_solvent.sh", 'w') as f:
            f.write(lig_batch_script)

        # now the complex batch script

        cplx_batch_script = f"""#!/bin/bash -l
#SBATCH -N 1
#SBATCH -t 24:00:00
#SBATCH -p ampere
#SBATCH --gres=gpu:1
#SBATCH -A csanyi-SL2-GPU

export HDF5_USE_FILE_LOCKING=FALSE
source ~/.bashrc

conda activate mlmm
which python


mace-md -f {os.path.join(direc, "complex", cplx)} --ml_mol '{os.path.join(direc, "ligands", ligand)}' --run_type repex --replicas {replicas} --log_level 10 --model_path {model_path} --dtype float64 --neighbour_list torch_nl_n2 --output_dir {output_dir}/{sys_name}/complex --resname UNK --system_type hybrid  --smff {smff} --equil gentle --restart
    """
        print(cplx_batch_script)

        with open(f"mace_repex_{sys_name}_cplx.sh", 'w') as f:
            f.write(cplx_batch_script)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--input', help="path to the input directory")
    # parser.add_argument('--sys_name', help='name of the system')    
    parser.add_argument("--replicas", type=int, default=8)
    parser.add_argument("--model_path", type=str )
    parser.add_argument("--smff", type=str, default="1.0")
    parser.add_argument("--ngpu", type=int, default=1)
    parser.add_argument("--output_dir", help="directory to write batch scripts to", default=".", type=str)

    # parser.add_argument()
    args = parser.parse_args()

    main(args.input,  args.replicas, args.model_path, args.smff, args.output_dir, args.ngpu)

