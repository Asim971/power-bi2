# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "jupyter",
# META     "jupyter_kernel_name": "python3.11"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse_name": "",
# META       "default_lakehouse_workspace_id": "",
# META       "known_lakehouses": [
# META         {
# META           "id": "d3cfe56a-4276-4098-9570-e29cff91e8f3"
# META         }
# META       ]
# META     }
# META   }
# META }

# MARKDOWN ********************

# ## Best Practice Analyzer
# 
# When you run this notebook, the [Best Practice Analyzer](https://learn.microsoft.com/python/api/semantic-link-sempy/sempy.fabric?view=semantic-link-python#sempy-fabric-run-model-bpa) (BPA) will offer tips to improve the design and performance of your semantic model. 
# 
# By default, the BPA checks a set of 60+ rules against your semantic model and summarizes the results. These rules come from experts within Microsoft and the Fabric Community.  
# 
# You’ll get suggestions for improvement in five categories: Performance, DAX Expressions, Error Prevention, Maintenance, and Formatting. 
# 
# ### Powering this feature: Semantic Link
# This notebook leverages [Semantic Link](https://learn.microsoft.com/fabric/data-science/semantic-link-overview), a python library which lets you optimize Fabric items for performance, memory and cost. The "[run_model_bpa](https://learn.microsoft.com/python/api/semantic-link-sempy/sempy.fabric?view=semantic-link-python#sempy-fabric-run-model-bpa)" function used in this notebook is just one example of the useful [functions]((https://learn.microsoft.com/python/api/semantic-link-sempy/sempy.fabric)) which Semantic Link offers.
# 
# You can find more [functions](https://github.com/microsoft/semantic-link-labs#featured-scenarios) and [helper notebooks](https://github.com/microsoft/semantic-link-labs/tree/main/notebooks) in [Semantic Link Labs](https://github.com/microsoft/semantic-link-labs), a Python library that extends Semantic Link's capabilities to automate technical tasks.
# 
# ### Low-code solutions for data tasks
# You don't have to be a Python expert to use Semantic Link or Semantic Link Labs. Many functions can be used simply by entering your parameters and running the notebook.


# CELL ********************

%pip install semantic-link-labs


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# MARKDOWN ********************

# #### Import the Semantic Link library

# CELL ********************

import sempy.fabric as fabric
import sempy_labs as labs
from sempy_labs import migration, directlake
import sempy_labs.report as rep

dataset = "BMD_sales" # Enter the name or ID of the semantic model
workspace = "BMD_Sales" # Enter the workspace name or ID in which the semantic model exists

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

fabric.list_datasets

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# MARKDOWN ********************

# #### Run the Best Practice Analyzer on your semantic model

# CELL ********************

migration.create_pqt_file(dataset = dataset_name, workspace = workspace_name)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

fabric.run_model_bpa(dataset=dataset, workspace=workspace)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

notebookutils.fs.cp(
"file:///synfs/nb_resource/builtin/yourFile",        # Copies the file (or folder) from Notebook resources.
"abfss://<lakehouse ABFS path>",       # Target Lakehouse ABFS path
True        # Recursive?
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# CELL ********************

# This code uses AI. Always review output for mistakes. 
# Read terms: https://azure.microsoft.com/en-us/support/legal/preview-supplemental-terms/

import synapse.ml.aifunc as aifunc
import pandas as pd
import openai

df = pd.DataFrame([
        "MJ Lee lives in Tuscon, AZ, and works as a software engineer for Microsoft.",
        "Kris Turner, a nurse at NYU Langone, is a resident of Jersey City, New Jersey."
    ], columns=["descriptions"])

df_entities = df["descriptions"].ai.extract("name", "profession", "city")
display(df_entities)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "jupyter_python"
# META }

# MARKDOWN ********************

# #### Learn more about notebooks in Fabric
# Notebooks in Fabric empower you to use code and low-code solutions for a wide range of data analytics and data engineering tasks such as data transformation, pipeline automation, and machine learning modeling.
# 
# * To edit this notebook, switch the mode from **Run** only to **Edit** or **Develop**.
# * You can safely delete this notebook after running it. This won’t affect your semantic model.
# 
# 
# For more information on capabilities and features, check out [Microsoft Fabric Notebook Documentation](https://learn.microsoft.com/fabric/data-engineering/how-to-use-notebook).

