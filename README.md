# Phylogeographic analysis of SARS-Cov-2 on April 25, 2020.

The analysis performs phylogenetic tree reconstruction, dating and phylogeographic analysis (with sampling bias correction)
for the SARS-COV-2 sequences available on [GISAID](https://www.gisaid.org) on April 28, 2020.

## Article

Anna Zhukova; Luc Blassel; Frédéric Lemoine; Marie Morel; Jakub Voznica; Olivier Gascuel. Origin, evolution and global spread of SARS-CoV-2. Comptes Rendus. Biologies, Volume 344 (2021) no. 1, pp. 57-75. [doi:10.5802/crbiol.29](https://comptes-rendus.academie-sciences.fr/biologies/articles/10.5802/crbiol.29/)


## Data
The analysis was performed with the sequences and metadata that were available on [GISAID](https://www.gisaid.org) on April 28, 2020. 
To get the sequences please refer to [GISAID](https://www.gisaid.org), 
their identifiers can be found in the file [duplicates.txt](data/20200425/alignments/duplicates.txt).

The DNA genome sequences were aligned by COVID-ALIGN
[[Lemoine et al. 2020]](https://www.biorxiv.org/content/10.1101/2020.05.25.114884v1), 
keeping one representative per identical genome group (with [goalign dedup](https://github.com/evolbioinfo/goalign) command), 
which led to an alignment of 8,541 sequences (11,316 with duplicates kept) and of 29,726 nucleotide sites.

The metadata for this dataset includes sampling dates (see [lsd2.dates](data/20200425/metadata/lsd2.dates)) and
countries (see [locations.tab](data/20200425/metadata/locations.tab)). 
70 countries and 2 cruise ships (Diamond Princess and Grand Princess) were
represented by this data set. The sampling, as the epidemic itself, progressed exponentially (see
[Figure 1](data/20200425/figures/Figure1.png)). Additionally, due to different sampling policies in different countries there is a high
sampling bias in the data: The proportions of sampled cases in certain countries with respect to
the total number of sampled cases do not correspond to the proportions of declared cases (see
[Figure 2](data/20200425/figures/Figure2.png)).

## Analysis
### Time-scaled tree
We reconstructed a maximum likelihood tree ([raxfast.nwk](data/20200425/phylogenies/raxfast.nwk))
 with RAxML-NG [[Kozlov et al. 2019]](https://academic.oup.com/bioinformatics/article/35/21/4453/5487384) 
(GTR+I+G6 model, with all parameters optimized ([raxfast.model](data/20200425/phylogenies/raxfast.model))) 
starting from a distance tree ([fastme.nwk](data/20200425/phylogenies/fastme.nwk)) reconstructed with
FASTME v2.1.6.1 [[Lefort et al. 2015]](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4576710/), 
rooted it at the most recent common ancestor of the likely
first-generation strains from [[Li et al. 2020]](https://www.nejm.org/doi/full/10.1056/nejmoa2001316) (see [outgroup.txt](data/outgroup.txt) for their identifiers), 
and put back the identical sequences (as zero-branch polytomies with the
corresponding representative sequence tip), which led to a tree with 11,316 tips 
([rooted_raxfast.duplicated.nwk](data/20200425/phylogenies/rooted_raxfast.duplicated.nwk)). We then
removed the branches without phylogenetic signal (i.e., with length corresponding to less than ≤
1/2 substitution among all alignment sites = 0.5/29,726 = 1.68 10^-5) from the tree by (1)
collapsing such internal branches and producing polytomies, and (2) setting the lengths of such
external branches to zero.
To prepare this tree for dating, we performed temporal filtering by pruning the tips whose
mutation rate (estimated as the distance to the root divided by time since the first sequence) was
larger than 3 standard deviations from the median. This led to a tree with 11,262 tips and 1,846
internal branches ([rooted_raxfast.duplicated.has_dates.collapsed.nwk](data/20200425/phylogenies/rooted_raxfast.duplicated.has_dates.collapsed.nwk)).

This tree was then dated with LSD2 [[To et al., 2016]](https://pubmed.ncbi.nlm.nih.gov/26424727/) (strict molecular clock, with temporal outlier
removal and without imposing a minimal branch length constraint): the estimated mutation rate
was 2.3 [2.0 − 2.4] · 10 −4 mutations per site per year, the root date was estimated on the 6 Dec
[25 Nov - 10 Dec] 2019 (see [raxfast.lsd2.log](data/20200425/timetrees/raxfast.lsd2.log)), which is consistent with the date of our rooting sequence, first sampled
by December 30, 2019. The time-tree ([raxfast.lsd2.nwk](data/20200425/timetrees/raxfast.lsd2.nwk)) contained 11,069 tips, after removal of 193 outliers.

### Phylogeography
The data we had did not
represent the declared cases in the countries worldwide in a homogenous way (see above and
[Figure 2](data/20200425/figures/Figure2.png)), which could bias the phylogeographic reconstructions. 
To address this issue, we employed a subsampling method based on phylogenetic
diversity [[Faith 1992]](https://www.sciencedirect.com/science/article/pii/0006320792912013). 
The aim was to select a subset of available sequences such that it
better corresponds to the [declared cases](https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide), while preserving a high level of diversity among
selected sequences (e.g. avoiding the presence of many duplicates in the same subsample). The
statistics on selected sequence distribution per country can be found in [sampling_phylogenetic.tab](data/20200425/metadata/sampling_phylogenetic.tab).
For the selected sequences we then reconstructed the tree with the same procedure as
described above (apart from temporal filtering as it was already done on the
initial tree), and dated it as described above (constraining the root date to the CI
estimated on the full tree: [25 Nov - 10 Dec] 2019). The procedure was repeated 5 times, leding to 5 slightly different subsampled trees: 
[raxfast_subsampled_phylogenetic_0.lsd2.nwk](data/20200425/timetrees/raxfast_subsampled_phylogenetic_0.lsd2.nwk), 
[raxfast_subsampled_phylogenetic_1.lsd2.nwk](data/20200425/timetrees/raxfast_subsampled_phylogenetic_1.lsd2.nwk), 
[raxfast_subsampled_phylogenetic_2.lsd2.nwk](data/20200425/timetrees/raxfast_subsampled_phylogenetic_2.lsd2.nwk), 
[raxfast_subsampled_phylogenetic_3.lsd2.nwk](data/20200425/timetrees/raxfast_subsampled_phylogenetic_3.lsd2.nwk), 
and [raxfast_subsampled_phylogenetic_4.lsd2.nwk](data/20200425/timetrees/raxfast_subsampled_phylogenetic_4.lsd2.nwk).

We reconstructed ancestral characters for countries on the full tree and on the 5 subsampled
trees, using PastML (MPPA F81) [[Ishikawa, Zhukova et al., 2019]](https://doi.org/10.1093/molbev/msz131). The visualisaton can be found in [data/20200425/acr](data/20200425/acr).

## Pipelines
The Snakemake [[Köster et al., 2012]](https://academic.oup.com/bioinformatics/article/28/19/2520/290322) pipelines allowing to reproduce this analysis are available in [pipelines](pipelines).
Running then requires [Snakemake](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html) and [Singularity](https://singularity.lbl.gov/docs-installation) installed.


To rerun the tree reconstruction pipeline, place the alignment corresponding to the file [duplicates.txt](data/20200425/alignments/duplicates.txt)
 into [data/20200425/alignments](data/20200425/alignments) folder as aln.fa.
Then from the [pipelines](pipleines) folder, run:
```bash
snakemake --snakefile Snakefile_phylogeny --keep-going --cores 7 --configfile config.yaml --use-singularity --singularity-prefix ~/.singularity --singularity-args "--home ~"
```
Once the phylogeny is reconstructed one can date it by running:
```bash
snakemake --snakefile Snakefile_dating --keep-going --cores 7 --configfile config.yaml --use-singularity --singularity-prefix ~/.singularity --singularity-args "--home ~"
```
To subsample the trees run:
```bash
snakemake --snakefile Snakefile_subsampling --configfile config.yaml --dag | dot -Tsvg > pipeline_subsampling.svg
```
To run the phylogeographic analysis:
```bash
snakemake --snakefile Snakefile_phylogeography --configfile config.yaml --dag | dot -Tsvg > pipeline_subsampling.svg
```
