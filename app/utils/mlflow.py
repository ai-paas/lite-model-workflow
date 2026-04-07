import urllib.parse

POS_DICT = {
    "s3": (1, 2),  # 이노
    "artifact": (0, 1),  # 사내
    "runs": (None, 0),  # 필요시 추가
}


def get_mlflow_experiment_id_from_path(
    path: str | None
) -> str | None:
    """
    MLflow 경로에서 experiment id 추출
    """
    return get_mlflow_ids_from_path(path, True, False)[0]


def get_mlflow_run_id_from_path(
    path: str | None
) -> str | None:
    """
    MLflow 경로에서 run id 추출
    """
    return get_mlflow_ids_from_path(path, False, True)[1]


def get_mlflow_ids_from_path(
    path: str | None,
    is_experiment: bool = False,
    is_run: bool = True
) -> tuple[str | None, str | None]:
    """
    MLflow 경로에서 experiment 및 run id 추출
    """
    if path is not None:
        for prefix, pos in POS_DICT.items():
            if path.startswith(prefix):
                path_list = urllib.parse.urlparse(path).path.split('/')
                try:
                    if len(path_list) > pos[1]:
                        return (path_list[pos[0]] if is_experiment else None, path_list[pos[1]] if is_run else None)
                    return None, None
                except (IndexError, TypeError):
                    import traceback
                    traceback.print_exc()
                    return None, None
    return None, None
