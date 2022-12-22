# Eco-desing in the building sector

This is the code used in the analysis presented in:

_Ipsen K L, Pizzol M, Birkved M, Amor B, Environmental performance of eco-design strategies applied to the building sector, journal unknown (XXXX),_[doi....](https://doi.org/....).

The supplementary materials to the article include the raw data: 

- LCI tables: `Database_demand.csv` and `Database_material.csv`

These are needed to run the script contained in this repository, for example if you want to reproduce the results of the paper. 

To run the script in this repository the following is also needed: 

- brightway2 
- ecoinvent 3.6 consequential database for brigtway2
- numpy
- pandas
- itertools

##The repository includes:

`Housing_simulation.py` Python script to reproduce results of the LCA using the brightway2 LCA software. The scipt imports the LCIs, performs LCA calculations and then exports results to excel files.

`IW_bw2.bw2package` bw2package file to implement IMPACT World+ impact assessment method in Brightway2. Reference: http://doi.org/10.5281/zenodo.3521041`lci_to_bw2.py` Python script to import inventory tables in .csv directly into brightway2.

`scenario_file.csv` csv file containing the scenarios to run in the `Housing_simulation.py` to reproduce the results of the article.


