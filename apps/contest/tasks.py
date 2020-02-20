from django.utils import timezone

from apps.contest.services.scoreboard import Scoreboard
from apps.contest.services.trial_services.scoring_service import \
    JudgeTrial, JudgeQuestionSubmission, set_task_score
from thebackend.celery import app


@app.task(name='judge_submissions')
def judge_submissions(question_submission_pk: int,
                      rejudge_model_pk: int = None) -> None:
    from apps.contest.models import Score, QuestionSubmission, Rejudge
    """ This task Judges a single QuestionSubmission and set it's score
        and save it in database.

        If rejudge a QuestionSubmission is requested,
        the rejudge_model_pk field should be settled
        to a Rejudge object primary key.

    :param rejudge_model: Rejudge
    :param question_submission: QuestionSubmission
    :return: None
    """
    question_submission = QuestionSubmission.objects.get(
        pk=question_submission_pk)
    if not hasattr(question_submission, 'score'):
        score = Score()
    else:
        score = question_submission.score
    judge_submission = JudgeQuestionSubmission(
        question_submission=question_submission, score=score)
    judge_submission.judge()
    if rejudge_model_pk:
        rejudge_model = Rejudge.objects.get(pk=rejudge_model_pk)
        recalculate_trials_scores.delay()
        rejudge_model.finished = True


@app.task(name='judge_trials')
def judge_trials(trial_pk: int) -> None:
    """ This task judges a single trial
    :param trial_pk:
    :return:
    """
    from apps.contest.models import Trial

    trial = Trial.objects.get(pk=trial_pk)
    if trial.submit_time is None:
        trial.submit_time = timezone.now()
        trial.save()
    trial.score = 0
    trial.save()
    judge_trial = JudgeTrial(trial=trial)
    judge_trial.judge_trial()


@app.task(name='rejudge_trials')
def recalculate_trials_scores():
    """ This Task recalculate the score of a
        trial after Updating it's QuestionSubmissions
    :return:
    """
    from apps.contest.models import Trial

    trials = Trial.objects.filter(submit_time__isnull=False)
    for trial in trials:
        trial.score = 0.0
        for submission in trial.question_submissions.all():
            trial.score += submission.score.number
        trial.save()
        set_task_score(trial=trial)
        Scoreboard.update_score(
            task=trial.team_task.task,
            team=trial.team_task.team,
            score=trial.team_task.final_score
        )
