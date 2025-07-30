from ExperimentTracking.tracker import ExperimentTrackingProtocol
from utils.logger import logger

runner = ExperimentTrackingProtocol()
def start_training_tracking_job():
    r"""This function runs a given model with experiment tracker
    Parameters:
    --------
    experiment_tracking_params: dict, parameters for mlflow with the following keys:
                                tracking_uri: str, tracking uri to run on mlflow (e.g. http://127.0.0.1:5000)
                                experiment_name: str, name of the model we're experimenting,
                                run_name: str, name of the runner of the experiment
                                tags: dict, specific tags for the experiment
    Returns:
    --------
    run_id: str
            run id of the current run. This might be helpful if customer metrics need to be added later
    """
    experiment_tracking_params = runner.config_data
    # set up the protocol
    runner.read_params(experiment_tracking_params)
    runner.set_tracking_uri()
    runner.set_experiment_id()
    # and here we go record the training session
    run_id = runner.run_training()
    return run_id

def log_training_metric(**kwargs):
    """
    This function will help to log training metrics such losses.
    params:
    -------
    key: str, name of the metric
    value: float, value of the metric
    step: int, step of the metric
    Returns:
    --------
    None
    
    """
    required_args = ['key', 'value', 'step']
    for arg in required_args:
        if arg not in kwargs:
            logger.error("Missing required argument: {}".format(arg))
    runner.log_training_metric(**kwargs)
    
    

def end_training_tracking_job(paramas=None,metrics=None,model=None):
    r""" This function helps to complete an experiment. The function take the very last run
    of a given experiment family and reports artefacts and files
    
    Parameters
    -------

        params: Training parameter in dict format. 
        metrics: Training & accuracy metrics in dict format.
        model: callable object to store the model using mlflow.pyfunc.log_model 
    """
    # set up the protocol
    experiment_tracking_params = runner.config_data
    # read the parameters
    runner.read_params(experiment_tracking_params)
    #set the tracking uri
    runner.set_tracking_uri()
    # check for any possible model which has not been saved - possibly due to mlflow experimental autlogs
    runner.log_custom_params_metrics(paramas,metrics)
    if model:
        runner.log_custom_model(model)
    # log any supported file created while running trackinf 
    runner.log_any_model_file()