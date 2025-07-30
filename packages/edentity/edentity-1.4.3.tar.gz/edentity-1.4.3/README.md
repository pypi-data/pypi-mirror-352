# edentity-metabarcoding-pipeline

![alt text](dag.png)

## Table of Contents

- [Brief on Vsearch](#brief-on-vsearch)
- [Usage of this workflow](#usage-of-this-workflow)
    - [Using Conda](#using-conda)
        - [Install Requirements](#install-requirements)
            - [Install conda or miniconda](#install-conda-or-miniconda)
            - [Steps to run edentity-metabarcoding-pipeline](#steps-to-run-edentity-metabarcoding-pipeline)
    - [Using Docker](#using-docker)
        - [Install Requirements](#install-requirements-1)
    - [Deploying to Galaxy](#deploying-to-galaxy)
        - [Prerequisites](#prerequisites)
        - [Steps to Deploy](#steps-to-deploy)

# Brief on Vsearch

Vsearch is a metabarcoding pipeline for illumina/AVITI paired-end data. More details can be found at [vsearch github](https://github.com/torognes/vsearch)


Vsearch publication: https://doi.org/10.7717/peerj.2584

Technical implementation of this pipeline is inspired by [APSCALE]( https://doi.org/10.1093/bioinformatics/btac588); please cite them if you use this pipeline.

# Usage of this workflow

This workflow can run on:

    - Conda

    - Docker 

    - Galaxy


## Using Conda

### Install Requirements

#### Install conda or miniconda
Ensure (mini)conda is installed on your system. Information on installing miniconda can be found [here](https://docs.anaconda.com/miniconda/)


#### Steps to run  edentity-metabarcoding-pipeline

###### 1 Clone this repo

```
git clone https://gitlab.com/naturalis/bii/bioinformatics/edentity/pipelines/edentity-metabarcoding-pipeline.git && cd edentity-metabarcoding-pipeline/

```

###### 2 Install snakemake conda environment from yaml file 
```
conda env create -n snakemake -f workflow/envs/snakemake.yaml
```


###### 3 Activate snakemake conda environment

```
conda activate snakemake
```


###### 4 Run the workflow: parameters used here are only for example; replace them with params specific to your project.

```
snakemake -p --profile workflow/profile/ \
    --config forward_primer=AAACTCGTGCCAGCCACC \
    reverse_primer=GGGTATCTAATCCCAGTTTG \
    raw_data_dir=/path/to/your/raw_data/ \
    work_dir=/path/to/your/work_directory \
    min_length=200 max_length=600 
```

Explain parameters and where more info can be found. Link to validation schema.

## Using Docker

### Install Requirements

###### 1. Apptainer:
Install [apptainer](https://apptainer.org/docs/user/latest/quick_start.html#installation)



###### 2. Run the workflow:

```
snakemake -p --profile workflow/profile/ \
    --config forward_primer=AAACTCGTGCCAGCCACC \
    reverse_primer=GGGTATCTAATCCCAGTTTG \
    raw_data_dir=/path/to/your/raw_data/ \
    work_dir=/path/to/your/work_directory \
    min_length=200 max_length=600 --use-apptainer
```

## Deploying to Galaxy

### Prerequisites

Ensure you have access to a Galaxy instance where you have administrative privileges or the ability to install tools and workflows.

### Steps to Deploy

###### 1. Clone the Galaxy branch of this repository
Clone galaxy branch of this pipeline into your Galaxy tools directory (for Naturalis clone into: `/data/galaxy/local_tools/`)

```

git clone -b galaxy git@gitlab.com:naturalis/bii/bioinformatics/edentity/pipelines/edentity-metabarcoding-pipeline.git

```

###### 2. Configure Galaxy tools xml
Edit your Galaxy tool configuration xml file to include the `edentity-galaxy-pipeline.xml` file located at the root directory of this repository.

For example to add this pipeline to your galaxy instance: Open `galaxy/config/tool_config.xml`  and add the lines below.

```
<section id="metabarcoding-pipeline" name="Metabarcoding Pipelines">
    <tool file="edentity-metabarcoding-pipeline/edentity-galaxy-pipeline.xml"/>
</section>

```

NB: 
- Ensure you paste the above lines within `<toolbox> </toolbox>` section in the `galaxy/config/tool_config.xml`
- Ensure paths are correctly referenced depending on where you cloned the pipeline 
- Some useful tips on adding custom tools on galaxy can be found [here](https://galaxyproject.org/admin/tools/add-tool-tutorial/)


###### 3. Restart Galaxy

Restart your Galaxy instance to load the new tool configuration.


###### 4. Running the pipeline on Galaxy:
Example on how to run this pipeline on Galaxy is available [here](https://gitlab.com/naturalis/bii/bioinformatics/edentity/pipelines/edentity-metabarcoding-pipeline/-/wikis/eDentity-metabarcoding-pipeline)


