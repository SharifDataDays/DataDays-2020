import ast

from apps.contest.models import ScoreStatusTypes, Score, TaskScoringType
from apps.question.models import QuestionTypes


class JudgeException(Exception):
    ERROR_MESSAGE = 'failed judge, format is wrong'

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args)


class JudgeService:

    def __init__(self, trial, errors):
        self.trial = trial
        self.errors = errors
        pass

    def __call__(self, *args, **kwargs):
        return self.judge_trial()

    def judge_trial(self):
        self.trial.score = sum([self.get_score(question) for question in self.trial.question_submissions.all()])
        self.trial.save()
        set_task_score(self.trial)
        return self.trial.score

    def get_score(self, question_submission):
        if not hasattr(question_submission, 'score'):
            score = Score()
        else:
            score = question_submission.score
        print(question_submission.question_id)
        score.question_submission = question_submission
        for id, error in self.errors:
            if question_submission.question_id == id:
                score.number = 0
                score.status = ScoreStatusTypes.ERROR
                score.status = error
                score.save()
                return 0

        question = question_submission.question
        answer = question_submission.answer
        answer = ast.literal_eval(answer)

        def get_path():
            return question.dir_path()

        try:
            exec(question.judge_function)
            function_name = question.judge_function_name
            answer_name, answer = self.get_parameters(question.type, answer, question_submission.file_answer)
            call_function = f'{function_name}({answer_name}={answer})'
            if question.type == QuestionTypes.SINGLE_SELECT:
                call_function = f'{function_name}({answer_name}=\'{answer}\')'
            print(call_function)
            score.number = eval(call_function) * question.max_score
            score.status = ScoreStatusTypes.SCORED
            score.info = "Judged Successfully"
        except JudgeException as e:
            score.status = ScoreStatusTypes.FAILED
            score.info = str(e.ERROR_MESSAGE)
        except Exception as e:
            score.status = ScoreStatusTypes.ERROR
            print(e)
            score.info = 'judge function runtime error'

        score.save()

        return score.number

    def get_parameters(self, question_type, answer, file_answer):
        if question_type in [QuestionTypes.SINGLE_ANSWER, QuestionTypes.SINGLE_SELECT]:
            return 'answer', answer[0]
        elif question_type in [QuestionTypes.NUMERIC_RANGE, QuestionTypes.MULTI_ANSWER, QuestionTypes.MULTI_SELECT]:
            return 'answers', answer
        elif question_type == QuestionTypes.FILE_UPLOAD:
            return 'file_path', file_answer


def set_task_score(trial):
    task = trial.team_task.task
    if task.scoring_type == TaskScoringType.FINAL_TRIAL:
        if trial.team_task.final_trial is not None:
            trial.team_task.final_score = trial.score.number
            trial.team_task.save()
    else:
        trials = trial.team_task.trials.all()
        if len(trials) == 0:
            return
        trials.sort(key=lambda x: x.id)
        team_task_score = 0
        factors = [1, 0.9, 0.7, 0.5]
        for i in range(len(trials)):
            team_task_score += factors[i] * trials[i]
        trial.team_task.final_score = team_task_score / len(trials)
        trial.team_task.save()
