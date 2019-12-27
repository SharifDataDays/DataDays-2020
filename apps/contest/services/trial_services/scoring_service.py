import ast

from apps.contest.models import ScoreStatusTypes, Score
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
        return sum([self.get_score(question) for question in self.trial.question_submissions])

    def get_score(self, question_submission):
        score = Score()
        score.question_submission = question_submission
        for id, error in self.errors:
            if question_submission.question_id == id:
                score.number = 0
                score.status = ScoreStatusTypes.ERROR
                score.status = error
                return 0

        question = question_submission.question
        answer = question_submission.answer
        answer = ast.literal_eval(answer)

        def get_path():
            return question.dir_path()

        try:
            exec(question.judge_function)
            function_name = question.judge_function_name
            answer_name, answer = self.get_parameters(question.type, answer)
            call_function = f'{function_name}({answer_name}={answer})'
            score.number = exec(call_function)
            score.status = ScoreStatusTypes.SCORED
        except JudgeException as e:
            score.status = ScoreStatusTypes.FAILED
            score.info = str(e.ERROR_MESSAGE)
        except Exception:
            score.status = ScoreStatusTypes.ERROR
            score.info = 'judge function runtime error'

        score.save()

        return score.number

    def get_parameters(self, question_type, answer):
        if question_type in [QuestionTypes.SINGLE_ANSWER, QuestionTypes.SINGLE_SELECT]:
            return 'answer', answer[0]
        elif question_type in [QuestionTypes.NUMERIC_RANGE, QuestionTypes.MULTI_ANSWER, QuestionTypes.MULTI_SELECT]:
            return 'answers', answer
        elif question_type == QuestionTypes.FILE_UPLOAD:
            return 'file_path', answer[0]
