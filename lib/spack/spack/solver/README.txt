README
--------------------------------------------------
To run a single comparison at variable depth:

>> spack install py-tabulate
>> spack load py-tabulate
>> cd {SPACK_ROOT}/lib/spack/spack/solver
>> ./parse.py -D{depth} {spec name}

For example: this will do a comparison at depth 1 (not fresh)
>> ./parse.py -D1 hdf5

Another example: this will make the solve fresh and print out the spectree both solutions.
>> ./parse.py -D1 --fresh --spectree hdf5

--------------------------------------------------
To generate comparison data for a set of packages:
The mpi-comp.py script uses mpi4py to collect data for comparisons across an input list of spec names. The
results are stored in the outputfile argument as a list of dictionaries.

To run on quartz, two tasks per node are recommended and at least two tasks total are required. For example:
>> srun -N4 --ntasks-per-node=2 -ppbatch mpi-comp.py inputfile.txt outputfile.txt -b10

The -b argument determines the buffer size, namely how often results are written to disk.

For my results on quartz, I used the following input to generate data for all available packages.
INPUTFILE = sample-results/all_packages.txt
OUTPUTFILE = sample-results/all_results.txt

The data collected for each comparison:
- Error (Boolean)
- Depth: depth of deep solve
- Index: index of standard solve model closest to deep solve
- Weights Match (Boolean)
- Attrs Match (Boolean)
- Deep Attr Outliers: if attributes don't match, list of attrs that are only in the deep solve
- Stand Attr Outliers: if attributes don't match, list of attrs that are only in standard solve

--------------------------------------------------
To generate dataframes with summary data:

Once the comparison data has been generated for some set of packages (using mpi-comp.py), use
create_df.py to create the dataframe to summarize the data. This can be done for all packages in the collected data:

>> ./create-df.py "sample-results/all_results.txt"

Or for a selection of packages in the collected data (using the --filteron argument), where the filteron input is a
filename for a file of a list of the filtered package names, formatted a list item per line:

>> ./create-df.py "sample-results/all_results.txt" -f "sample-results/filtered_specs.txt"

The create-df.py script also has functions for operating on this dataframe with finer control over the result.
