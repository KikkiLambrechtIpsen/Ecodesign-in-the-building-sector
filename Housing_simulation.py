#!/usr/bin/env python
# coding: utf-8

# # 1. Ecoinvent and World+ import

# In[1]:


import pandas as pd
import numpy as np
import brightway2 as bw
from lci_to_bw2 import *
import itertools


# In[2]:


bw.projects.set_current('PhD_ecodesign_final')


# In[3]:


# Import of the biosphere3 database
bw.bw2setup()


# In the following cell the impact assessment method *Impact World+* is imported. The file *IW_bw2.BW2PACKAGE* is from: 
# 
# laurepatou. (2019). laurepatou/IMPACT-World-in-Brightway: IW in Brightway: Midpoint 1.28 and Damage 1.46 (1.28_1.46). Zenodo. https://doi.org/10.5281/zenodo.3521041

# In[4]:


# Import of the World+ impact assessment method
#Note: Validate that there are no duplicates in the endpoint flows
import bw2io
imp = bw2io.package.BW2Package.load_file('IW_bw2.BW2PACKAGE', whitelist=True)

# Extract the methods from the import variable and detail the content 
for methods in imp :
    new_method = methods['name']
    new_cfs = methods['data']
    new_metadata = methods['metadata']
    my_method = bw.Method(new_method)
    my_method.register(**new_metadata)
    my_method.write(new_cfs)

# Validate that everything went well by checking one of the last methods
my_method_as_list1=[]
for ef in my_method.load() :
    my_method_as_list1.append([bw.get_activity(ef[0])['name'],bw.get_activity(ef[0])['categories'],
                                     ef[1]])    
df = pd.DataFrame(my_method_as_list1)
df.to_excel('Characterization method_detailed_3.xlsx', header = ('Elementary flow',"Emission locations", 
                                                       'Characterization factor'))

# Update the list of methods and validate that they are all present 
list_methods = []
for objects in bw.methods :
        list_methods.append(objects)

dataframe_methods = pd.DataFrame(data = list_methods, columns =('Method name',"Impact type",'Details') )
   
dataframe_methods.to_excel('Methodes.xlsx')


# In[5]:


# Import ecoinvent database (change directory with the directory where ecoinvent files are stored)
ei36dir = "/Users/kikki/Sync/50-Kikki Ipsen/14_Databases/ecoinvent_3.6_consequential/datasets"

if 'ecoinvent 3.6 conseq' in bw.databases:
    print("Database has already been imported")
else:
    ei36 = bw.SingleOutputEcospold2Importer(ei36dir, 'ecoinvent 3.6 conseq')
    ei36.apply_strategies()
    ei36.statistics()
    ei36.write_database()


# # 2. Import the databases for the assessment

# ## 2.1 Demand database

# This is a database containing different scenarios for the potential future demand of newly constructed housing, housing transformations and housing demolitions. The potential future demand is given for every 5 years, from 2025 to 2100. This database is imported to create the LCI, by mulltiplying the numbers in this database with the ones from the material database, see 2.2. 

# In[8]:


#Loading the demand database
mydemand = pd.read_csv('Database_demand.csv', header = 0, sep = ";")
mydemand.head()


# In[9]:


# clean up a bit
mydemand = mydemand.drop('Year', 1) 
mydemand.head()


# In[10]:


#Saving the demand database as a list
d=mydemand.to_numpy()
demandlist=d.tolist()


# ## 2.2 Material intensities database

# This is a database containing various scenarios for the material flows for:
# * material input and waste output for newly constructed housing
# * material input and waste output for housing transformation 
# * waste output for housing demolitions
# 
# This database is imported to create the LCI, by mulltiplying the numbers in this database with the ones from the demand database, see 2.1.

# In[14]:


#Loading the material database
mydb = pd.read_csv('Database_material.csv', header = 0, sep = ";")
mydb.head()


# In[15]:


# clean up a bit
mydb = mydb.drop('Notes', 1)
mydb['Exchange uncertainty type'] = mydb['Exchange uncertainty type'].fillna(0).astype(int)
mydb.head()


# In[16]:


# Create a dict that can be written as database
bw2_db = lci_to_bw2(mydb)
bw2_db


# In[17]:


t_db = bw.Database('material') # shut down all other notebooks using the same project
t_db.write(bw2_db)


# In[18]:


[print(act) for act in t_db]  


# # 3. Impact assessment

# Here the two importet databases *demand* and *material* are multiplied according to the given scenario and the environmental impacts are assessed using brightway2. The results are exported to an excel file. 
# 
# For how the other parts of the assessment of the main scenarios and the sensitivity scenarios are done see: 
# *scenario_file.csv*

# In[20]:


# The newly_constructed_housing for scenario group #1 is assessed here

method = ['IMPACTWorld+ (Default_Recommended_Midpoint 1.28)']
category = ['Climate change, short term','Climate change, long term','Fossil and nuclear energy use', 'Mineral resources use',
            'Photochemical oxidant formation', 'Ozone Layer Depletion','Freshwater ecotoxicity', 'Human toxicity cancer',
            'Human toxicity non cancer', 'Water scarcity','Freshwater acidification','Terrestrial acidification',
            'Freshwater eutrophication','Marine eutrophication','Land transformation, biodiversity',
            'Land occupation, biodiversity','Particulate matter formation', 'Ionizing radiations']

demand = demandlist[0]

housing = [t_db.get('new_mi_detached_best'), t_db.get('new_mi_detached_worst'), 
           t_db.get('new_mi_apartment_best'), t_db.get('new_mi_apartment_worst'),
           t_db.get('new_mi_high-rise_best'), t_db.get('new_mi_high-rise_worst'),
           t_db.get('new_waste_on-site_detached_best'), t_db.get('new_waste_on-site_detached_worst'),
           t_db.get('new_waste_on-site_apartment_best'), t_db.get('new_waste_on-site_apartment_worst'),
           t_db.get('new_waste_on-site_high-rise_best'), t_db.get('new_waste_on-site_high-rise_worst')]

result=[]
for (a, b) in itertools.zip_longest(method, category, fillvalue='IMPACTWorld+ (Default_Recommended_Midpoint 1.28)'):
    method=(a,b)
    for h in housing [0:len(housing)]:
        house = h
        for m in demand [0:len(demand)]:
            fu = m
            lca = bw.LCA({house:fu}, method)
            lca.lci()
            lca.lcia()
            result.append(lca.score)

x=len(result)
list = result

matrix = []
while list != []:
    matrix.append(list[:len(demand)])
    list = list[len(demand):]

idx = pd.Index(category)
index_cat = idx.repeat(12) #This must be the lenght of housing, otherwise the results cannot be exported to excel

# The results are exported to an excel sheet (change directory with the directory where you want the file stored)
Results = pd.DataFrame(columns=demand, index = index_cat, data=matrix)
Results.to_excel(r'C:\Users\kikki\Sync\50-Kikki Ipsen\00_LCA_results.xlsx',index = True, header = True)

