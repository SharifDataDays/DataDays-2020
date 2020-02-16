from ast import literal_eval
import os
from typing import List, Union
import uuid

from django.conf import settings
from django.core.files.base import ContentFile

from apps.contest.models import Trial, QuestionSubmission
from apps.contest.serializers import TrialPostSerializer
from apps.question.models import QuestionTypes, AnswerDataTypes
from apps.contest.Exceptions import trial_submit_exception


class TrialSubmitValidation:

    def __init__(self, request, contest_id, milestone_id, task_id, trial_id):
        self._request = request
        self.contest_id: int = contest_id
        self.milestone_id: int = milestone_id
        self.task_id: int = task_id
        self.trial_id: int = trial_id
        self._trial: Union[Trial, None] = None
        self._question_submissions: \
            Union[List[QuestionSubmission], None] = None
        self._valid: bool = True
        self._errors = {}
        pass

    def validate(self):
        self._trial = self.get_trial()
        if self._valid:
            self._question_submissions = self._trial.question_submissions
            self._check_different_question_types()
        return self._trial, self._valid, self._errors

    def get_trial(self):
        try:
            trial = TrialPostSerializer(data=self._request.data)
            if trial.is_valid():
                trial.save()
                self.final_submit = self._request.data['final_submit']
                return Trial.objects.get(id=self.trial_id)
            else:
                self._valid = False
                self._errors = {'trial': trial.errors}
                return None
        except Trial.DoesNotExist:
            self._valid = False
            self._errors = \
                {'trial':
                 trial_submit_exception.ErrorMessages.TRIAL_NOT_FOUNT}
            return None

    def _check_different_question_types(self):
        for submission in self._question_submissions.all():
            question_type = submission.question.type
            self._common_validations(submission)
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
        if submission.answer and not isinstance(submission.answer, str):
            self._errors[submission.question_id] = 'answer must be a string'
            self._valid = False

    def _validate_single_answer(self, submission):
        try:
            answer = literal_eval(submission.answer)
        except ValueError:
            self._errors[submission.question_id] = \
                trial_submit_exception.ErrorMessages.\
                ANSWER_STRING_MUST_BE_A_LIST
            self._valid = False
            return
        if len(answer) >= 2:
            self._errors[submission.question_id] = \
                trial_submit_exception.ErrorMessages.SINGLE_ANSWER_ERROR
            self._valid = False
            return
        answer_type = submission.question.answer_type
        if answer_type == AnswerDataTypes.INTEGER:
            try:
                int(answer[0])
            except ValueError:
                self._errors[submission.question_id] = \
                    trial_submit_exception.ErrorMessages.\
                    ANSWER_TYPE_ERROR.format(
                        answer_type)
                self._valid = False
        elif answer_type == AnswerDataTypes.DOUBLE:
            try:
                float(answer[0])
            except ValueError:
                self._errors[submission.question_id] = \
                    trial_submit_exception.ErrorMessages.\
                    ANSWER_TYPE_ERROR.format(
                        answer_type)
                self._valid = False

    def _validate_multi_answer(self, submission):
        try:
            answers = literal_eval(submission.answer)
        except ValueError:
            self._errors[submission.question_id] = \
                trial_submit_exception.ErrorMessages.\
                ANSWER_STRING_MUST_BE_A_LIST
            self._valid = False
            return
        answer_type = submission.question.answer_type
        answer_count = submission.question.answer_count_limit
        if len(answers) > answer_count:
            self._errors[
                submission.question_id] = \
                trial_submit_exception.ErrorMessages.\
                MULTI_ANSWER_LIMIT_REACHED_ERROR.format(
                    answer_count)
            self._valid = False
            return
        for answer in answers:
            if answer_type == AnswerDataTypes.INTEGER:
                try:
                    int(answer)
                except ValueError:
                    self._errors[submission.question_id] = \
                        trial_submit_exception.ErrorMessages.\
                        ANSWER_TYPE_ERROR.format(
                            answer_type)
                    self._valid = False
                    break
            elif answer_type == AnswerDataTypes.DOUBLE:
                try:
                    float(answer)
                except ValueError:
                    self._errors[submission.question_id] = \
                        trial_submit_exception.ErrorMessages.\
                        ANSWER_TYPE_ERROR.format(
                            answer_type)
                    self._valid = False
                    break

    def _validate_single_select(self, submission):
        try:
            label = literal_eval(submission.answer)
        except ValueError:
            self._errors[submission.question_id] = \
                trial_submit_exception.ErrorMessages.\
                ANSWER_STRING_MUST_BE_A_LIST
            self._valid = False
            return
        if len(label) >= 2:
            self._errors[submission.question_id] = trial_submit_exception.\
                ErrorMessages.SINGLE_SELECT_ERROR
            self._valid = False
            return

    def _validate_multi_select(self, submission):
        try:
            labels = literal_eval(submission.answer)
        except ValueError:
            self._errors[submission.question_id] = \
                trial_submit_exception.ErrorMessages.\
                ANSWER_STRING_MUST_BE_A_LIST
            self._valid = False
            return
        answer_count = submission.question.answer_count_limit

        if len(labels) > answer_count:
            self._errors[
                submission.question_id] = \
                trial_submit_exception.ErrorMessages.\
                MULTI_SELECT_LIMIT_REACHED_ERROR.format(
                answer_count)
            self._valid = False
            return

    def _validate_file_upload(self, submission):
        if not {qs['id']: qs['has_file'] for qs in
                self._request._data['question_submissions']}[submission.id]:
            return
        try:
            answer_file = self._request._files[str(submission.id)]
        except Exception:
            self._valid = False
            self._errors[submission.question_id] = \
                f'file with name {submission.id} does not exists'
            return
        file_format = submission.question.file_format
        file_size_limit = submission.question.file_size_limit

        answer_file_format = os.path.splitext(answer_file.name)[1][1:]

        if file_format != answer_file_format:
            self._errors[submission.question_id] = \
                trial_submit_exception.ErrorMessages.\
                INVALID_FILE_FORMAT.format(
                    file_format)
            self._valid = False
            return
        if answer_file.size > file_size_limit * 1024 * 1024:
            self._errors[submission.question_id] = \
                trial_submit_exception.ErrorMessages.\
                FILE_SIZE_LIMIT_EXCEEDED.format(
                    file_size_limit)
            self._valid = False
            return

        answer = [self._save_to_storage(answer_file, answer_file_format,
                                        submission.id)]
        qs = self._trial.question_submissions.get(id=submission.id)
        qs.answer = str(answer)
        qs.save()

    def _validate_manual_judgment(self, submission):
        pass

    def _validate_numeric_range(self, submission):
        try:
            answer = eval(submission.answer)
        except ValueError:
            self._errors[
                submission.question_id] = \
                trial_submit_exception.ErrorMessages.\
                INVALID_LITERALS_FOR_NUMERIC_RANGE
            self._valid = False
            return
        if answer[0] > answer[1]:
            self._errors[submission.question_id] = \
                trial_submit_exception.ErrorMessages.INVALID_NUMERIC_RANGE
            self._valid = False
            return

    def _save_to_storage(self, given_file, file_format, submission_id):
        destination = (
            f'/teams/{self._trial.team_task.team.name}/'
            f'trial_{self.trial_id}/qs_{submission_id}/'
        )
        uploaded_filename = 'f_' + uuid.uuid4().hex[:16] + '.' + file_format
        try:
            os.makedirs(settings.MEDIA_ROOT + destination, exist_ok=True)
        except OSError:
            print('oops')
        full_filename = settings.MEDIA_ROOT + destination + uploaded_filename
        copied_file = open(full_filename, 'wb+')
        file_content = ContentFile(given_file.read())
        for chunk in file_content.chunks():
            copied_file.write(chunk)
        copied_file.close()
        return destination + uploaded_filename
