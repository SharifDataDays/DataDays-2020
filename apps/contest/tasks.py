from celery import task, shared_task

from apps.contest.services.trial_services.scoring_service import JudgeService
from thebackend.celery import app


@app.task(name='scoring_service_task')
def scoring_service_task(trial, errors):
    judge_trial = JudgeService(trial, errors)
    score = judge_trial()
