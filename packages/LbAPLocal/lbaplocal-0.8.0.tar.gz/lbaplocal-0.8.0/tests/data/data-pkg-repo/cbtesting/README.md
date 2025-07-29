# LbToL0ll ntuple options

Option files for creating ntuples for the measurement of $`R(\Lambda^{0})`$ using $`\Lambda_{b}^{0} \to \Lambda^{0} \mathcal{l}\mathcal{l}`$ decays. 
Based on the BsToJpsiPhi option files. 
The different decay mode files use the `tuple_maker` helper file to add all the required TupleTools, DecayTreeFits, and LoKi functions. 
The electron modes include upstream tracks using the `Bu2LLK_eeLine4` stripping line.

## Datasets

* $`\Lambda_{b}^{0} \to \Lambda^{0} \mathcal{e}^{+}\mathcal{e}^{-}`$
* $`\Lambda_{b}^{0} \to \Lambda^{0} \mathcal{e}^{+}\mathcal{e}^{+}`$
* $`\Lambda_{b}^{0} \to \Lambda^{0} \mu^{+}\mu^{-}`$
* $`\Lambda_{b}^{0} \to \Lambda^{0} \mathcal{e}^{+}\mu^{-}`$
* $`\Lambda_{b}^{0} \to \Lambda^{0} \mathcal{e}^{+}\mu^{+}`$
* $`B^{0} \to K^{0}_{S} \mathcal{e}^{+}\mathcal{e}^{-}`$
* $`B^{0} \to K^{0}_{S} \mu^{+}\mu^{-}`$
* $`B^{\pm} \to K^{\pm} e^{+}e^{-}`$
* $`B^{\pm} \to K^{\pm} \mu^{+}\mu^{-}`$

## Monte Carlo samples
For now no MC samples yet.

## Local testing
1. Clone the repository using `git clone -b lex-Lb2L0ll ssh://git@gitlab.cern.ch:7999/lhcb-datapkg/WG/CharmWGProd.git`.
2. Go into directory `cd CharmWGProd`
3. Run `/path/to/CharmWGProd/test_locally.py Lb2L0ll YEAR_MagDown_Leptonic --n-events=-1` where YEAR is the year you want to test
4. Check the output folder in the `/path/to/CharmWGProd/output/Lb2L0ll` directory, it contains a job directory with the logs and output root file.
