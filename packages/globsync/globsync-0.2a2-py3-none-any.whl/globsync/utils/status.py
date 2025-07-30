"""Status utilities."""
import os.path
import shutil
import pandas as pd
import numpy as np
import math
from typing import Optional, Any
from bs4 import BeautifulSoup

from globsync import utils
import globsync.utils.db
import globsync.utils.paths
import globsync.utils.flows
import globsync.utils.users
import globsync.utils.email
from globsync.utils.paths import PathsRow
from globsync.utils.flows import FlowRunsRow
from globsync.utils.users import UsersRow
from globsync.utils.logging import log


def convert_size(size_bytes: int) -> str:
    """Get the a size in bytes to a human readable format."""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


def get_status(db: str, globus_secrets_file: Optional[str] = None, sql_stmt: Optional[str] = None) -> pd.DataFrame:
    """Get the status of paths and flow runs."""
    paths = utils.db.get_dataframe(db, PathsRow, sql_stmt)
    flow_runs = utils.db.get_dataframe(db, FlowRunsRow)
    status = pd.merge(paths, flow_runs, on="source_path", how="outer")
    status["source_exists"] = status["source_path"].apply(lambda path: os.path.exists(path))
    flows_client = utils.flows.get_flows_client(globus_secrets_file=globus_secrets_file)
    status["run_status"] = status.apply(lambda row: flows_client.get_run(row["run_id"])["status"] if pd.notna(row["run_id"]) else np.nan, axis=1)
    # possible values run_status: "SUCCEEDED" "FAILED" "ENDED" "ACTIVE" "INACTIVE"
    status = status[["source_path", "source_exists", "user", "size", "run_id", "remove_source", "time_started", "run_status"]]

    return status


def autoclean(db: str, status: pd.DataFrame) -> pd.DataFrame:
    """Automatically clean the paths and flow runs based on status."""
    # rm non-existing paths from database
    utils.db.rm_rows(db, PathsRow, status[~status["source_exists"]]["source_path"])

    # rm flow_runs which have ended (successfully or not) from database
    utils.db.rm_rows(db, FlowRunsRow, status[status["run_status"].isin(["SUCCEEDED", "FAILED", "ENDED"])]["run_id"])

    # rm paths with flow runs that all have ended successfully and requested remove_source from database and disk
    rows = (status[pd.notna(status["run_id"])]).copy()
    rows["run_succeeded"] = rows["run_status"].isin(["SUCCEEDED"])
    grouped = rows[["source_path", "source_exists", "remove_source", "run_succeeded"]].groupby("source_path").all()
    synced_paths = grouped[grouped["run_succeeded"]].index.values
    utils.db.rm_rows(db, PathsRow, synced_paths)
    paths_to_rm = grouped[grouped["source_exists"] & grouped["remove_source"] & grouped["run_succeeded"]].index.values
    for path in paths_to_rm:
        shutil.rmtree(path)

    return status[status["source_exists"] & ~status["run_status"].isin(["SUCCEEDED", "FAILED", "ENDED"]) & ~status["source_path"].isin(synced_paths)].copy()


def notify(db: str, status: pd.DataFrame, load_modules_file: str, email_sender: str, email_backend: str, **kwargs) -> None:
    """Notify users of actions to be taken based on status."""
    rows = status[pd.notna(status["user"]) & status["source_exists"] & pd.isna(status["run_id"])]
    grouped = rows.groupby("user")
    for user, group in grouped:
        user_row = utils.db.get_row(db, UsersRow, user)
        if not user_row:
            log('warning', f"User {user} not registered within globsync.")
            continue
        data: dict[str, Any] = {}
        data["user_name"] = user_row.name
        data["cluster_name"] = (" " + os.getenv("VSC_INSTITUTE_CLUSTER", default="")) if os.getenv("VSC_INSTITUTE_CLUSTER", default="") else ""
        data["load_modules_file"] = load_modules_file
        data["source_paths"] = {source_path: convert_size(size) for source_path, size in zip(group["source_path"], group["size"])}
        subtype2body = {'html': utils.email.create_body('user_notification.html', data)}
        subtype2body['plain'] = BeautifulSoup(subtype2body['html'], "html.parser").get_text()
        subject = f'HPC storage usage notification'
        msg = utils.email.create_msg(email_sender, user_row.email, subject, subtype2body)
        utils.email.send_msg(msg, email_backend, **kwargs)
