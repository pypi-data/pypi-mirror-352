import wandb


def push(
    project: str,
    dataset: str,
    data_type: str,
    data_dir_path: str,
):
    """_summary_

    :param project: Name of the project
    :type project: str
    :param dataset: Name of the dataset
    :type dataset: str
    :param data_type: It should be one of dataset or result
    :type data_type: str
    :param data_dir_path: data directory path
    :type data_dir_path: str
    """
    assert data_type in [
        "dataset",
        "result",
    ], f"data_type should be one of dataset or result, but {data_type}"
    run = wandb.init(project=project, job_type="add-dataset")
    artifact = wandb.Artifact(name=dataset, type=data_type)
    artifact.add_dir(local_path=data_dir_path)
    run.log_artifact(artifact)
    run.finish()


def pull(project: str, dataset: str, alias: str = "latest", data_dir_path: str = None):
    api = wandb.Api()
    artifact = api.artifact(f"{project}/{dataset}:{alias}")
    artifact_dir = artifact.download(data_dir_path)
    return artifact_dir
