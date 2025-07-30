# MLflow SDK for Experiment Tracking 🚀
  This SDK is designed to streamline the integration of MLflow into machine learning pipelines across your organization, offering a seamless approach to tracking experiments, parameters, metrics, and models.

  It provides a library that simplifies the incorporation of MLflow into your training code, enabling easy implementation with just a few function calls and configuration files.

  * start_training_tracking_job

  * log_training_metric

  * end_training_tracking_job



## 📦 Installation

clone repositories and Install library and the SDK by running:

    pip install .

## Mlflow access [*mlflow UI*](http://172.27.72.23:5000/)


## ✨ Key Features
  Configurable Experiment Tracking: Easily control tracking via a YAML configuration file.

* Parameter Tracking: Log and store model hyperparameters.

* Metric Tracking: Monitor training metrics like loss, accuracy, etc.

* Model Artifact Logging: Automatically log model artifacts and versions from the location of your code running 
  it supporting file format 
  * [h5,pkl,model,joblib,metadata.json,metrics.json,png,jpg]

## ⚙️ Configuration

  Create a config.yml file in your project directory with the following structure:

    tracking_uri: http://172.27.72.23:5000/
    project_name: <project_name> 
    experiment_name: <eperiment_name>
    run_name: <run_name>
    tags: {sdk: test}
    model_name: <model_name>



## 🚀 Usage Example

    # import the libary with modules 
      from ExperimentTracking.training_tracker import (
          start_training_tracking_job,
          end_training_tracking_job,
          log_training_metric
      )

    # Start the training tracking job. Use this command at start of the training to initialize the tracker.

      start_training_tracking_job()

    {
    # Your model training code here
    }
      for epoch in range(num_epochs):
          train_loss = ...  # Calculate training loss
          # if want to track the metrics for each epoch use below function and pass variables in given format.
          log_training_metric(key="train_loss", value=train_loss, step=epoch)

    # After training is done, log parameters, metrics, and register the model. call below function to stop tracker.

      end_training_tracking_job(params, metrics, model_artifact_path)

## 🔍 Notes
* Configuration Management: The config.yml controls how the tracker connects to MLflow. Ensure it's present in your project directory.

* Tracking URI: Replace the tracking URI with your MLflow server's address.


