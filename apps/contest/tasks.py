from typing import List, Tuple

from celery import task, shared_task

from apps.contest.services.trial_services.scoring_service import JudgeTrial, JudgeQuestionSubmission, set_task_score
from thebackend.celery import app


@app.task(name='judge_submissions')
def judge_submissions(question_submission, rejudge_model=None) -> None:
    from apps.contest.models import Score
    """ This task Judges a single submission and set it's score
        and save it in database
    :param rejudge_model: Rejudge
    :param question_submission: QuestionSubmission
    :return: None
    """
    if not hasattr(question_submission, 'score'):
        score = Score()
    else:
        score = question_submission.score
    judge_submission = JudgeQuestionSubmission(question_submission=question_submission, score=score)
    judge_submission.judge()
    if rejudge_model:
        rejudge_model.finished = True


@app.task(name='judge_trials')
def judge_trials(trial_pk):
    from apps.contest.models import Trial

    trial = Trial.objects.get(pk=trial_pk)
    judge_trial = JudgeTrial(trial=trial)
    judge_trial.judge_trial()
    # rejudge_trials.apply_async([], queue='main')


@app.task(name='rejudge_trials')
def rejudge_trials():
    from apps.contest.models import Trial

    trials = Trial.objects.filter(submit_time__isnull=False)
    for trial in trials:
        for submission in trial.question_submissions:
            trial.score += submission.score.number
        trial.save()
        set_task_score(trial=trial)
