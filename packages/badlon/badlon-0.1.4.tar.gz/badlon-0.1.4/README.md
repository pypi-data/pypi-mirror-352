# Badlon

## Installation 

Bablon can be installed with `pip`:

```bash
pip install badlon
```

Now you can run tool from any directory as `badlon`.

## Pipeline Usage

### Modules

Badlon includes multiple modules to process data. They can be listed with help command:

```bash
$ badlon --help
usage: badlon [-h] {prepare,analysis,match} ...

Tool for block based analysis of bacterial populations. Choose one of available modules.

positional arguments:
  {prepare,analysis,match}
    prepare             Prepare draft dataset for SibeliaZ.
    analysis            Analyze pan-genome and other block-based features based on synteny blocks.
    match               Performs matching of block and genes based on coordinates.

optional arguments:
  -h, --help            show this help message and exit
```

Here is recommended pipeline to process data with badlon:

### Step 1: prepare data with [`PanACoTA` pipeline](https://github.com/gem-pasteur/PanACoTA)

If you have genomes in some folder called `some_folder` (one file for genome), we suggest preparing data for badlon using [`PanACoTA` pipeline](https://github.com/gem-pasteur/PanACoTA).

To do so, you can use those commands:

#### 1.1 Preparing data and tables with `PanACoTA prepare` module:

```
PanACoTA prepare --norefseq --min 0 --max 1 -o 1-prepare -d some_folder --cutn 125
```

* `--min 0 --max 1` are used to keep all genomes, parameter can be changed depending on task as well as all other parameters;
* For check other parameters visit [`PanACoTA prepare`](https://aperrin.pages.pasteur.fr/pipeline_annotation/html-doc/usage.html#prepare-subcommand) documentation.

#### 1.2 Annotating genomes with `PanACoTA annotate` module:

```
PanACoTA annotate --info 1-prepare/L* -r 2-annotate -n ESCO --threads 16
```

* You can change label `-n ESCO` depending on your species (ESCO is for *Escherichia coli*);
* For check parameters visit [`PanACoTA annotate`](https://aperrin.pages.pasteur.fr/pipeline_annotation/html-doc/usage.html#annotate-subcommand) documentation.

#### 1.3 Calling orthology genes using `PanACoTA pangenome` module:

```
PanACoTA pangenome -l 2-annotate/LSTINFO-* -n ESCO -d 2-annotate/Proteins/ -o 3-pangenome
```

* You can change `-i` which is minimum sequence identity to be considered in the same cluster (float between 0 and 1). Default is 0.8.
* For check parameters visit [`PanACoTA pangenome`](https://aperrin.pages.pasteur.fr/pipeline_annotation/html-doc/usage.html#pangenome-subcommand) documentation.

### Step 2: Preparing data for alignment with `badlon prepare` module

Prepare module is used to prepare data for using SibeliaZ package keeping all necessary information: genome labels and chromosome numbers.

Parameters can be checked with help option:

```bash
$ badlon prepare --help
usage: badlon prepare [-h] --folder FOLDER [--contigs CONTIGS]
                      [--output OUTPUT]
                      [--annotate_subfolder ANNOTATE_SUBFOLDER]
                      [--min_len MIN_LEN]

optional arguments:
  -h, --help            show this help message and exit
  --contigs CONTIGS, -c CONTIGS
                        Number of maximum contigs to take from every genome.
                        By default, keeps all.
  --output OUTPUT, -o OUTPUT
                        Output file path.
  --annotate_subfolder ANNOTATE_SUBFOLDER, -a ANNOTATE_SUBFOLDER
                        Subfolder of PanACoTA contains results of annotate
                        module. Used for finding LSTINFO file. Default is
                        '2-annotate'.
  --min_len MIN_LEN, -l MIN_LEN
                        Minimum contig length, less then that value will be
                        filtered. Default is 1000.

Required arguments:
  --folder FOLDER, -f FOLDER
                        Folder with PanACoTA output. Will be used to search
                        genome files based on LSTINFO file from annotate
                        module.
```

Example command:

```
badlon prepare -f 2-annotate -o for_sibeliaz.fna
```

### Step 3: Obtaining blocks with [SibeliaZ](https://github.com/medvedevgroup/SibeliaZ)

#### 3.1 Running SibeliaZ with recommended command based on `badlon prepare` output.

Example:
```
sibeliaz -k 15 -a 100 -n -t 32 -o sibeliaz_out for_sibeliaz.fna
```

* Watch out `-a` it needs to be equal around `number_of_genome * 20`, `badlon prepare` calculates it automatically.

#### 3.2 Obtaining blocks from alignment

Check recommended command from `badlon prepare` module output. Usually it's (blocks minimal size 3000):
```bash
cd sibeliaz_out
echo $'30 150\n100 500\n500 1500' > fine.txt
maf2synteny -s fine.txt -b 3000 blocks_coords.gff
```

### Step 4: Calculating block based statistics and charts with `badlon analysis` module:

Parameters can be checked with help option:

```bash
$ badlon analysis --help
usage: badlon analysis [-h] --blocks_file BLOCKS_FILE --type {chr,contig}
                       [--output OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Path to output folder. Default: blockomics_output.

Required arguments:
  --blocks_file BLOCKS_FILE, -b BLOCKS_FILE
                        Blocks resulted as output of original Sibelia or
                        maf2synteny tool. Usually it's
                        sibeliaz_out/3000/block_coords.txt file.
  --type {chr,contig}, -t {chr,contig}
                        Type of genome assembly, either 'chr' or 'contig'
```

Example command:

```bash
cd ..
badlon analysis -b sibeliaz_out/3000/blocks_coords.txt
```

### Step 5 (optional): Match block and genes annotation with  `badlon match` module

Parameters can be checked with help option:

```bash
$ badlon match --help
usage: badlon match [-h] --blocks_file BLOCKS_FILE --annotated_folder
                    ANNOTATED_FOLDER --pangenome_file PANGENOME_FILE --type
                    {chr,contig} [--output OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Path to output folder. Default: blockomics_output.

Required arguments:
  --blocks_file BLOCKS_FILE, -b BLOCKS_FILE
                        Blocks folder resulted as output of original Sibelia
                        or maf2synteny tool. Usually it's `sibeliaz_out/3000/`
                        folder.
  --annotated_folder ANNOTATED_FOLDER, -a ANNOTATED_FOLDER
                        LSTINFO folder path, output of `annotate` step of
                        PanACoTA.
  --pangenome_file PANGENOME_FILE, -pg PANGENOME_FILE
                        File .lst with orthologous genes, output of
                        `pangenome` step of PanACoTA.
  --type {chr,contig}, -t {chr,contig}
                        Type of genome assembly, either 'chr' or 'contig'
```

Example command:

```
badlon match -b sibeliaz_out/3000/blocks_coords.txt -a 2-annotate/ -pg 3-pangenome/*.lst -t contig
```