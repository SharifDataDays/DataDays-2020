import ast

from apps.contest.models import ScoreStatusTypes
from apps.question.models import QuestionTypes


class JudgeException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args)

    pass


class JudgeService:

    def get_score(self, question_submission):
        question = question_submission.question
        answer = question_submission.answer
        answer = ast.literal_eval(answer)

        def get_path():
            return question.dir_path

        score = 0
        try:
            exec(question.judge_function)
            function_name = question.judge_function_name
            answer_name, answer = self.get_parameters(question.type, answer)
            call_function = f'{function_name}({answer_name}={answer})'
            score = exec(call_function)
            score.save()
        except JudgeException as e:
            score.status = ScoreStatusTypes.FAILED
            score.info = str(e)
            score.save()
        except Exception:
            score.status = ScoreStatusTypes.ERROR
            score.save()

    def get_parameters(self, question_type, answer):
        if question_type in [QuestionTypes.SINGLE_ANSWER, QuestionTypes.SINGLE_SELECT]:
            return 'answer', answer[0]
        elif question_type in [QuestionTypes.NUMERIC_RANGE, QuestionTypes.MULTI_ANSWER, QuestionTypes.MULTI_SELECT]:
            return 'answers', answer
        elif question_type == QuestionTypes.FILE_UPLOAD:
            return 'file_path', answer[0]
