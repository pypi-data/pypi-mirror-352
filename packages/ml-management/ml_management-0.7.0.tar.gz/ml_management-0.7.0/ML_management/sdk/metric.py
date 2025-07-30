from sgqlc.operation import Operation

from ML_management.graphql.schema import schema
from ML_management.graphql.send_graphql_request import send_graphql_request


def list_metric_jobs(metric_name: str, job_names: list[str]) -> list[dict]:
    """
    Return metrics by job names and metric_name.

    Parameters
    ----------
    metric_name: str
        Name of the metric.
    job_names: list[str]
        List of job names.

    Returns
    -------
    list[dict]
        List of metrics.
    """
    op = Operation(schema.Query)

    op.list_metric_jobs(metric_name=metric_name, job_names=job_names)

    metrics = send_graphql_request(op, json_response=False)

    return metrics.list_metric_jobs
