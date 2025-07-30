#!/usr/bin/bash

# ask for MPI tasks
#SBATCH --ntasks=1
 
# name the job
#SBATCH --job-name=count_numbers
 
# declare the merged STDOUT/STDERR file
#SBATCH --output=count_numbers_%J-out.txt
#SBATCH --error=count_numbers_%J-err.txt

# runtime limit
#SBATCH --time=00:01:00

wc -l ../nth_numbers/numbers.txt > num_of_nums.txt
