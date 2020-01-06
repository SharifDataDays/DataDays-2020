import ast
from typing import List, Tuple

from apps.question.models import QuestionTypes


class JudgeException(Exception):
    ERROR_MESSAGE = 'failed judge, format is wrong'

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args)


class JudgeTrial:

    def __init__(self, trial):
        self.trial = trial
        pass

    def judge_trial(self):
        from apps.contest.models import Score

        for question_submission in self.trial.question_submissions.all():
            if not hasattr(question_submission, 'score'):
                score = Score()
            else:
                score = question_submission.score
            JudgeQuestionSubmission(question_submission=question_submission, score=score).judge()
            self.trial.score += score.number
        self.trial.save()
        set_task_score(self.trial)
        return self.trial.score


class JudgeQuestionSubmission:
    """ This class judges a single QuestionSubmission
        and generate a number as it's score by calling
        a judge function that entered in admin panel
        for question.
    """

    def __init__(self, question_submission, score):
        from apps.contest.models import Score, QuestionSubmission
        self.question_submission: QuestionSubmission = question_submission
        self.score: Score = score

    def judge(self) -> None:
        self.score.question_submission = self.question_submission
        self._judge_question(self.score)
        self.score.save()

    def _judge_question(self, score):
        from apps.contest.models import ScoreStatusTypes

        question = self.question_submission.question
        answer = ast.literal_eval(
            self.question_submission.answer) if not self.question_submission.file_answer else self.question_submission.file_answer

        def get_path():
            return question.dir_path()

        try:
            exec(question.judge_function)
            answer_name, answer = self.get_parameters(question.type, answer)
            call_function = f'{question.judge_function_name}({answer_name}={answer})'
            if question.type == QuestionTypes.SINGLE_SELECT:
                call_function = f'{question.judge_function_name}({answer_name}=\'{answer}\')'
            score.number = eval(call_function) * question.max_score
            score.status = ScoreStatusTypes.SCORED
            score.info = "Judged Successfully"
        except JudgeException as e:
            score.status = ScoreStatusTypes.FAILED
            score.info = str(e.ERROR_MESSAGE)
        except Exception as e:
            score.status = ScoreStatusTypes.ERROR
            score.info = 'Judge function runtime error'

    def get_parameters(self, question_type, answer):
        if question_type in [QuestionTypes.SINGLE_ANSWER, QuestionTypes.SINGLE_SELECT]:
            return 'answer', answer[0]
        elif question_type in [QuestionTypes.NUMERIC_RANGE, QuestionTypes.MULTI_ANSWER, QuestionTypes.MULTI_SELECT]:
            return 'answers', answer
        elif question_type == QuestionTypes.FILE_UPLOAD:
            return 'file_path', answer


def set_task_score(trial) -> None:
    from apps.contest.models import TaskScoringType

    task = trial.team_task.task
    if task.scoring_type == TaskScoringType.FINAL_TRIAL:
        if trial.team_task.final_trial is not None:
            trial.team_task.final_score = trial.score
            trial.team_task.save()
    else:
        trials = list(trial.team_task.trials.all())
        if len(trials) == 0:
            return
        trials.sort(key=lambda x: x.id)
        team_task_score = 0
        factors = [1, 0.9, 0.7, 0.5]
        for i in range(len(trials)):
            team_task_score += factors[i] * trials[i].score
        trial.team_task.final_score = team_task_score / len(trials)
        trial.team_task.save()
