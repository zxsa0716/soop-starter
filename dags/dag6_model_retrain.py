"""
DAG6 — Model Re-train (월 1회)
==============================
LightGBM(M3) + KNN/GAT(M4) + Prophet(M5) 재학습
+ Monte Carlo grid 93,000 시나리오 재계산.

ml/*.py 스크립트를 Airflow BashOperator로 trigger.
"""
from __future__ import annotations
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

DEFAULT_ARGS = {"owner": "soop", "retries": 2, "retry_delay": timedelta(minutes=10)}

ML_DIR = "/opt/airflow/ml"

with DAG(
    dag_id="dag6_model_retrain",
    default_args=DEFAULT_ARGS,
    description="LGBM + KNN + Prophet 재학습 + 93k grid 재계산",
    schedule="@monthly", start_date=datetime(2026, 5, 12), catchup=False,
    tags=["W2-T1", "ml", "retrain"],
) as dag:
    t_calib = BashOperator(task_id="m05_mc_calibration", bash_command=f"cd {ML_DIR} && python -m m05_mc_calibration")
    t_lgbm  = BashOperator(task_id="m03_lgbm_train", bash_command=f"cd {ML_DIR} && python -m m03_lgbm_train --stage all --save")
    t_knn   = BashOperator(task_id="m04_knn_train",  bash_command=f"cd {ML_DIR} && python -m m04_knn_train")
    t_grid  = BashOperator(task_id="m05_grid_precompute",
                           bash_command=f"cd {ML_DIR} && python -m m05_grid_precompute --trajectories 10000 --products 10")

    [t_calib, t_lgbm, t_knn] >> t_grid
