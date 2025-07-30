import mlflow
from mlflow.tracking.client import MlflowClient
import abc
import os
import sys
import datetime
from ConfigLoader.config_reader import ConfigFileReader
from utils.logger import logger
import warnings
warnings.filterwarnings("module", category=DeprecationWarning)


# Define a class interface
class ExperimentTrackingInterface(object, metaclass=abc.ABCMeta):
    r"""A class to implement experiment tracking in a portable and integrable way
    """
    @abc.abstractmethod
    def __init__(self):
        r""" Default value if not specified"""
        pass
    ... # all methods
    
# Define the protocol 
class ExperimentTrackingProtocol(ExperimentTrackingInterface):
    r""" Protocol for experiment tracking.

    Attributes
    ----------
    config: ConfigFileReader
            ConfigFileReader object to read config.yml file
            config_data: dict

    read_params: dict
                parameters for mlflow with the following keys:
                tracking_uri: str, tracking uri to run on mlflow (e.g. http://127.0.0.1:5000)
                tracking_storage: str, output path, this can be a local folder or cloud storage
                experiment_name: str, name of the model we're experimenting,
                run_name: str, name of the runner of the experiment
                tags: dict, specific tags for the experiment

    run_training: dict
                parameters for mlflow with the following keys:
                model_name: str, name of the model we're experimenting,
                model_version: str, version of the model we're experimenting,
                model_path: str, path to the model we're experimenting,
                model_metrics: dict, metrics of the model we're experimenting,
                model_params: dict, parameters of the model we're experimenting,
                model_tags: dict, tags of the model we're experimenting,
                model_artifacts: dict, artifacts of the model we're experimenting,
                model_artifact_path: str, path to the artifacts of the model we're experimenting,
    
    """

    def __init__(self):
        r""" Initialize experiment tracking default values"""
        self.config = ConfigFileReader()
        self.config_data = self.config.read_config()
    

    def read_params(self, experiment_tracking_params):
        r""" Read input parameters from experiment_tracking_params dictionary for setting up MLflow
        Parameters
        ----------
        experiment_tracking_params: dict, parameters for mlflow with the following keys:
                                    tracking_uri: str, tracking uri to run on mlflow (e.g. http://127.0.0.1:5000)
                                    tracking_storage: str, output path, this can be a local folder or cloud storage
                                    experiment_name: str, name of the model we're experimenting,
                                    run_name: str, name of the runner of the experiment
                                    tags: dict, specific tags for the experiment
        """
        self.tracking_uri = experiment_tracking_params['tracking_uri']
        #self.tracking_storage = experiment_tracking_params['tracking_storage']
        self.run_name = experiment_tracking_params['run_name'] +"__" + datetime.datetime.today().strftime("%Y-%m-%d_%H_%M_%S")
        self.tags = experiment_tracking_params['tags']

        # define some metrics 
        self.metrics_per_epochs = ['loss',
                                'accuracy',
                                'val_loss',
                                'val_accuracy',
                                'lr']
        self.experiment_name = experiment_tracking_params['experiment_name'] 

        self.model_name = experiment_tracking_params['model_name']


    def set_tracking_uri(self):
        r""" This function set the MLflow tracking uri, so results will be reported to that specific server. """
        try:
            mlflow.set_tracking_uri(self.tracking_uri)
            logger.info("Experiment Tracking url set to {}".format(self.tracking_uri))
        except Exception as e:
            logger.error("Error Occured while setting tracking uri {}".format(e))

    def get_tracking_uri(self):
        r""" Getter for tracking_uri"""
        try:
            logger.info("Tracking uri: {}".format(mlflow.get_tracking_uri()))
            return mlflow.get_tracking_uri()
        except:
            pass

        
    def set_experiment_id(self):
        r""" Setter for experiment id. Initially a check is done based on self.experiment_name.
        If the experiment already exists, the function retrieves the experiment_id, otherwise
        a new experiment is set up. If experiment_name is None, datetime is used to create a new
        experiment name"""

        if not self.experiment_name:
            # if experiment name is not given create a new one
            self.experiment_name = datetime.datetime.today().strftime("%Y-%m-%d_%H_%M_%S")
            # check if experiment exists already and retrieve the bucket location, otherwise create a new one
        try:
            self.experiment_id = mlflow.get_experiment_by_name(self.experiment_name).experiment_id
        except:
            # let's add the experiment name for the artifact location
            # if experiment_id is None let's create a new experiment
            self.experiment_id = mlflow.create_experiment(self.experiment_name)
            
        return self.experiment_id


    def get_experiment_id(self):
        r""" Getter for experiment id"""
        logger.info("Experiment id {}".format(self.experiment_id))
        return self.experiment_id
    
    
    def set_run_id(self, run_id):
        r"""Set run id, this can be useful to retrieve info for a specific run"""
        self.run_id = run_id
        

    def get_run_id(self):
        r""" return the run id"""
        return self.run_id
    

    def run_training(self,params=None):
        r""" Function to run an experiment tracking job, given a model and its fitting params
        """
        def run_mlflow():
            r""" Function to run experiment tracking on mlflow
            Parameters
            ----------
            """
            try:
                # autolog model parameters
                mlflow.autolog()
                # here run an inspect to cehck what's in input
                mlflow.xgboost.autolog(log_input_examples=True)

                mlflow.sklearn.autolog(log_models=True,
                                    log_input_examples=True,
                                    log_model_signatures=True,
                                    registered_model_name=self.model_name)

                mlflow.tensorflow.autolog(log_every_epoch=True,
                                        log_models=True,
                                        registered_model_name=self.model_name,
                                        )
                mlflow.keras.autolog(log_models=True,log_every_epoch=True)
                mlflow.lightgbm.autolog(log_input_examples=True)
                mlflow.keras.log_model = "h5"
                # record the model training
                starter = mlflow.start_run(experiment_id=self.experiment_id,
                                run_name=self.run_name,
                                nested=False,
                                tags=self.tags)

                # run_id
                run_id = starter.info.run_id
                #
                logger.info("Experiment Run id: {}".format(run_id))
                return run_id
            except Exception as e:
                logger.error("Error occured while running the mlflow tracker {}".format(e))


        # run MLFLOW
        run_id = run_mlflow()
        return run_id
    


    def log_training_metric(self, **kwargs):
        """
        Logs training metrics.

        Args:
            **kwargs: Expected to contain 'key', 'value', 'step', and optionally others.
        """
        # Extract required arguments
        key = kwargs.get('key')
        value = kwargs.get('value')
        step = kwargs.get('step')

        if key is None or value is None or step is None:
            raise ValueError("Arguments 'key', 'value', and 'step' are required.")

        # Log metric using MLflow
        mlflow.log_metric(key=key, value=value, step=step)

    def log_custom_params_metrics(self,params,metrics):
        """
        This function helps to log the metrics and parameter which are not cpatured by the autolog
        """
        if params:
            mlflow.log_params(params)
        if metrics:
            mlflow.log_metrics(metrics)

    def log_custom_model(self,model):
        """
        This helps to log cutom models 

        """

        mlflow.pyfunc.log_model(python_model=model,
                                registered_model_name=self.model_name,
                                artifact_path="model",
                                pip_requirements=["tensorflow", "numpy"]
                                )

    def log_any_model_file(self):
        r""" This function looks for pkl, h5,.model, .joblib files in the current working
        directory, as well as metadata and metrics files.
        Log all these files to the MLflow server if those has not been saved.
        This ensures we can save all the possible models, including, for example,
        hybrid sklearn pipelines."""
        def parse_local(artifact_path):
            r""" Function to return artifacts from local folder
            
            Parameters
            ----------
            artifact_path: str, path to local folder where model artifacts are saved
            
            Returns
            -------
            artifacts: list, list of all the files saved on the tracking storage
            """
            # given the current working folder check what files are contained
            artifacts = []

            for root, dirs, files in os.walk(artifact_path):
                for file in files:
                    # just take the name of the file
                    artifacts.append(file)

            return artifacts

        def list_artifacts(last_run):
            r""" From the last run retrieve all the files in the artifact storage
            
            Parameters
            ----------
            last_run: dict, last run info retrieved from MLflow server
            
            Return
            ------
            artifacts: list, list of all the files saved on the tracking storage
            (under model folder)
            """
            # enlist all the files in the cloud storage or local
            artifact_prefix = last_run['info']['artifact_uri'] 
            artifacts = parse_local(artifact_prefix)

            return artifacts


        def local_files_to_upload(working_dir, artifacts, run_date):
            r""" This function looks for local files to upload. Firstly files in working_dir
            are scanned and added to a list. If the file is already present in artifacts
            the file is ignored. Then, we take only the most recent files
            
            Parameters
            ----------
            working_dir: str, current working directory (os.getcwd())
            artifacts: list, list of artifacts on MLflow server or local MLflow folder
            run_date: str, this is the run date timestamp
            
            Returns
            -------
            list_of_files: list, list of most recent files to be uploaded
            """
            format_files = ["h5",
                            "pkl",
                            "model",
                            "joblib",
                            "metadata.json",
                            "metrics.json",
                            "png",
                            "jpg",
                            "json"]
            # list of excluded directories, where we do not want to scan for files
            excluded_dirs = ["exclude_directories_you_do_not_want"]
            # define a list of files to be uplaoded
            list_of_files = []
            # check if a file has this extension. if the file already is contained in artifacts skip it
            # otherwise add it to the upload list
            for root, dirs, files in os.walk(working_dir, topdown=True):
                # exclude these directories:
                dirs[:] = [d for d in dirs if d not in excluded_dirs]
                for file in files:
                    extension = file.split(".")[-1]
                    filename = file.split("/")[-1]
                    if (extension in format_files) or (filename in format_files):
                        # check if file is already present in artifacts
                        if filename in artifacts:
                            continue
                        else:
                            # just add the most recent file if the file is arleady in list
                            file_path = os.path.join(root, file)
                            # check timestamp
                            creation_date = os.path.getctime(file_path)
                            if creation_date > run_date:
                                # this means the file has been created after the run
                                list_of_files.append(os.path.join(root, file))
                            else:
                                continue

            return list_of_files

        # MAIN FUNCTION
        client = MlflowClient(tracking_uri=self.tracking_uri)
        # read the experiment
        experiment = dict(client.get_experiment_by_name(self.experiment_name))
        # check if there's a run
        try:
            last_run = client.search_runs([experiment['experiment_id']])[0].to_dictionary()
        except:
            logger.info("No runs found for the given experiment")
            sys.exit(-1)

        run_date = (last_run['info']['start_time'])/1000 # timestamp
        # take run_id
        run_id = last_run['info']['run_id']
        # enlist all the files on the cloud or local
        artifacts = list_artifacts(last_run)
        # now check if model/metrics files are on local or cloud and push them to MLflow serfver
        files_to_upload = local_files_to_upload(os.getcwd(), artifacts, run_date)
        # upload
        for file_to_upload in files_to_upload:
            logger.info("Uploading {} to artifcatory store".format(file_to_upload))
            client.log_artifact(run_id, file_to_upload, artifact_path='model')
        mlflow.end_run()

