from ast import literal_eval
import os

from apps.contest.models import Trial
from apps.question.models import QuestionTypes, AnswerDataTypes
from ..Exceptions import trial_submit_exception


class TrialSubmitValidation:

    def __init__(self, trial: Trial):
        self.trial = trial
        self.question_submissions = trial.question_submissions
        self.valid = True
        self.errors = []
        pass

    def validate(self):
        pass

    def _check_different_question_types(self):
        for submission in self.question_submissions:
            if not literal_eval(submission.answer):
                pass
            else:
                question_type = submission.question.type
                if not self._common_validations(submission):
                    return
                if question_type == QuestionTypes.SINGLE_ANSWER:
                    self._validate_single_answer(submission)
                elif question_type == QuestionTypes.MULTI_ANSWER:
                    self._validate_multi_answer(submission)
                elif question_type == QuestionTypes.SINGLE_SELECT:
                    self._validate_single_select(submission)
                elif question_type == QuestionTypes.MULTI_SELECT:
                    self._validate_multi_select(submission)
                elif question_type == QuestionTypes.FILE_UPLOAD:
                    self._validate_file_upload(submission)
                elif question_type == QuestionTypes.MANUAL_JUDGMENT:
                    self._validate_manual_judgment(submission)
                elif question_type == QuestionTypes.NUMERIC_RANGE:
                    self._validate_numeric_range(submission)

    def _common_validations(self, submission):
        if not isinstance(submission.question.answer, str):
            self.errors += trial_submit_exception.ErrorMessages.ANSWER_NOT_STRING
            self.valid = False
            return False
        return True

    def _validate_single_answer(self, submission):
        try:
            answer = literal_eval(submission)
        except ValueError:
            self.errors += trial_submit_exception.ErrorMessages.ANSWER_STRING_MUST_BE_A_LIST
            self.valid = False
            return
        if len(answer) >= 2:
            self.errors += trial_submit_exception.ErrorMessages.SINGLE_ANSWER_ERROR
            self.valid = False
            return
        answer_type = submission.question.answer_type
        if answer_type == AnswerDataTypes.INTEGER:
            try:
                int(answer[0])
            except ValueError:
                self.errors += trial_submit_exception.ErrorMessages.ANSWER_TYPE_ERROR.format(answer_type)
                self.valid = False
        elif answer_type == AnswerDataTypes.DOUBLE:
            try:
                float(answer[0])
            except ValueError:
                self.errors += trial_submit_exception.ErrorMessages.ANSWER_TYPE_ERROR.format(answer_type)
                self.valid = False
        elif answer_type == AnswerDataTypes.TEXT:
            pass

    def _validate_multi_answer(self, submission):
        try:
            answers = literal_eval(submission)
        except ValueError:
            self.errors += trial_submit_exception.ErrorMessages.ANSWER_STRING_MUST_BE_A_LIST
            self.valid = False
            return
        answer_type = submission.question.answer_type
        answer_count = submission.question.answer_count_limit
        if len(answers) > answer_count:
            self.errors += trial_submit_exception.ErrorMessages.MULTI_ANSWER_LIMIT_REACHED_ERROR.format(answer_count)
            self.valid = False
            return
        for answer in answers:
            if answer_type == AnswerDataTypes.INTEGER:
                try:
                    int(answer)
                except ValueError:
                    self.errors += trial_submit_exception.ErrorMessages.ANSWER_TYPE_ERROR.format(answer_type)
                    self.valid = False
                    break
            elif answer_type == AnswerDataTypes.DOUBLE:
                try:
                    float(answer)
                except ValueError:
                    self.errors += trial_submit_exception.ErrorMessages.ANSWER_TYPE_ERROR.format(answer_type)
                    self.valid = False
                    break
            elif answer_type == AnswerDataTypes.TEXT:
                pass

    def _validate_single_select(self, submission):
        label = literal_eval(submission)
        if len(label) >= 2:
            self.errors += trial_submit_exception.ErrorMessages.SINGLE_SELECT_ERROR
            self.valid = False
            return

    def _validate_multi_select(self, submission):
        labels = literal_eval(submission)
        answer_count = submission.question.answer_count_limit

        if len(labels) > answer_count:
            self.errors += trial_submit_exception.ErrorMessages.MULTI_SELECT_LIMIT_REACHED_ERROR.format(answer_count)
            self.valid = False
            return

    def _validate_file_upload(self, submission):
        answer = literal_eval(submission)
        file_format = submission.question.file_format
        file_size_limit = submission.question.file_size_limit

    def _validate_manual_judgment(self, submission):
        pass

    def _validate_numeric_range(self, submission):
        pass
