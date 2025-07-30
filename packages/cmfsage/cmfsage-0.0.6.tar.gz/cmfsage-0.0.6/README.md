# cmf_sage
This project is to enable cmf metadata logging for waggle sensor plugins: https://github.com/waggle-sensor. 
The kickstart  use case is based on the wildfire detetion plugin:git@github.com:hpeliuhan/sage-smoke-detection.git.


## Backgroud
Plugin are deploye on the waggle sensor nodes to collect scientific data. The result is published via pywaggle plugin.
Developer build metadata database of AI pipelines to keep track of the code, the artifacts and evaluation metrics of each executions performed during the training. Verifying the training model and using the inferencing data for continous learning helps training better AI model.
Logging of the inferencing enviornment, artifacts and models becomes important in distributed network such as waggle sensor platform.

Waggle sensor provides data api for end users to query the inference data. However, it will be time consuming to sort the data based on the version of trained model. 

By integrating CMF client with pywaggle, developer can create the artifact linage with real-time inferencing while the metadata structure is build on the fly.

## Apporch
CMF monitors the artifacts by versioning them using DVC. CMF also leverage git for code versioning control. 
At the edge, a model is deplivered in loaded in containers. CMF_SAGE keeps track of two types of artifacts: model (execution input) and (execution output).
1.We will have background thread that keep tracking of the "PYWAGGLE_LOG_DIR" for the newly created inference results and perform cmf logging.
2.The logged cmf data are uploaded to waggle sensor datastore for cmf server metadata push.


## HOW TO USE
pip install cmf-sage

import cmf_sage

cmf_sage.cmf_logging_thread(pipeline_name, pipeline_file, model_path, result_dir,git_remote_url)

What information you need to give cmf_sage to start logging:
1. pipeline_name: Use the same pipeline name you are using to train the model.
2. pipeline_file: default "mlmd". the sqlite file name to store the metadata.
3. result_dir: Give the directory of the inference result you are going to save.
4. model_path: Give the path of the model you are going to load.
5. git_remote_url: git repository link for code versioning control.
#to-do: define "stage_name" and "execution_name" Now using "inference" as default



