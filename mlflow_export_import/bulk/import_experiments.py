""" 
Import a list of experiment from a directory.
"""

import os
from concurrent.futures import ThreadPoolExecutor
import click

import mlflow
from mlflow_export_import.common.click_options import (
    opt_input_dir, 
    opt_import_source_tags,
    opt_use_src_user_id, 
    opt_use_threads
)
from mlflow_export_import.common import io_utils
from mlflow_export_import.experiment.import_experiment import import_experiment


def _import_experiment(mlflow_client, exp_name, input_dir, import_source_tags, use_src_user_id):
    try:
        import_experiment(
            mlflow_client = mlflow_client,
            experiment_name = exp_name,
            input_dir = input_dir,
            import_source_tags = import_source_tags,
            use_src_user_id = use_src_user_id
        )
    except Exception:
        import traceback
        traceback.print_exc()


def import_experiments(
        input_dir, 
        import_source_tags = False,
        use_src_user_id = False, 
        use_threads = False,
        mlflow_client = None
    ): 
    mlflow_client = mlflow_client or mlflow.client.MlflowClient()
    dct = io_utils.read_file_mlflow(os.path.join(input_dir, "experiments.json"))
    exps = dct["experiments"]
    for exp in exps:
        print("  ",exp)

    max_workers = os.cpu_count() or 4 if use_threads else 1
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for exp in exps:
            exp_input_dir = os.path.join(input_dir,exp["id"])
            exp_name = exp["name"]
            executor.submit(_import_experiment, mlflow_client, 
                exp_name, exp_input_dir, import_source_tags, use_src_user_id)


@click.command()
@opt_input_dir
@opt_import_source_tags
@opt_use_src_user_id
@opt_use_threads

def main(input_dir, import_source_tags, use_src_user_id, use_threads): 
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    import_experiments(
        input_dir = input_dir, 
        import_source_tags = import_source_tags,
        use_src_user_id = use_src_user_id,
        use_threads = use_threads
    )


if __name__ == "__main__":
    main()
