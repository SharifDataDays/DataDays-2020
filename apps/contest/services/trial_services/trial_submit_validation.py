from ast import literal_eval
import os
import json
from typing import List, Union

from django.conf import settings
from django.core.files.base import ContentFile

from apps.contest.models import Trial, QuestionSubmission
from apps.contest.serializers import TrialPostSerializer
from apps.question.models import QuestionTypes, AnswerDataTypes
from apps.contest.Exceptions import trial_submit_exception


class TrialSubmitValidation:

    def __init__(self, request, contest_id, milestone_id, task_id, trial_id):
        self._request = request
        self.contest_id = contest_id
        self.milestone_id = milestone_id
        self.task_id = task_id
        self.trial_id = trial_id
        self._trial: Union[Trial, None] = None
        self._question_submissions: Union[List[QuestionSubmission], None] = None
        self._valid = True
        self._errors = []
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
                self._errors = [trial.errors[e][0] for e in trial.errors]
                return None
        except Trial.DoesNotExist as e:
            self._valid = False
            self._errors += trial_submit_exception.ErrorMessages.TRIAL_NOT_FOUNT
            return None

    def _check_different_question_types(self):
        for submission in self._question_submissions.all():
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
        if submission.answer and not isinstance(submission.answer, str):
            self._errors += (submission.question_id, trial_submit_exception.ErrorMessages.ANSWER_NOT_STRING)
            self._valid = False
            return False
        return True

    def _validate_single_answer(self, submission):
        try:
            answer = literal_eval(submission.answer)
        except ValueError:
            self._errors += (submission.question_id, trial_submit_exception.ErrorMessages.ANSWER_STRING_MUST_BE_A_LIST)
            self._valid = False
            return
        if len(answer) >= 2:
            self._errors += (submission.question_id, trial_submit_exception.ErrorMessages.SINGLE_ANSWER_ERROR)
            self._valid = False
            return
        answer_type = submission.question.answer_type
        if answer_type == AnswerDataTypes.INTEGER:
            try:
                int(answer[0])
            except ValueError:
                self._errors += (
                    submission.question_id, trial_submit_exception.ErrorMessages.ANSWER_TYPE_ERROR.format(answer_type))
                self._valid = False
        elif answer_type == AnswerDataTypes.DOUBLE:
            try:
                float(answer[0])
            except ValueError:
                self._errors += (
                    submission.question_id, trial_submit_exception.ErrorMessages.ANSWER_TYPE_ERROR.format(answer_type))
                self._valid = False
        elif answer_type == AnswerDataTypes.TEXT:
            pass

    def _validate_multi_answer(self, submission):
        try:
            answers = literal_eval(submission.answer)
        except ValueError:
            self._errors += (submission.question_id, trial_submit_exception.ErrorMessages.ANSWER_STRING_MUST_BE_A_LIST)
            self._valid = False
            return
        answer_type = submission.question.answer_type
        answer_count = submission.question.answer_count_limit
        if len(answers) > answer_count:
            self._errors += (submission.question_id,
                             trial_submit_exception.ErrorMessages.MULTI_ANSWER_LIMIT_REACHED_ERROR.format(answer_count))
            self._valid = False
            return
        for answer in answers:
            if answer_type == AnswerDataTypes.INTEGER:
                try:
                    int(answer)
                except ValueError:
                    self._errors += (
                        submission.question_id,
                        trial_submit_exception.ErrorMessages.ANSWER_TYPE_ERROR.format(answer_type))
                    self._valid = False
                    break
            elif answer_type == AnswerDataTypes.DOUBLE:
                try:
                    float(answer)
                except ValueError:
                    self._errors += (
                        submission.question_id,
                        trial_submit_exception.ErrorMessages.ANSWER_TYPE_ERROR.format(answer_type))
                    self._valid = False
                    break
            elif answer_type == AnswerDataTypes.TEXT:
                pass

    def _validate_single_select(self, submission):
        try:
            label = literal_eval(submission.answer)
        except ValueError:
            self._errors += (submission.qustion_id, trial_submit_exception.ErrorMessages.ANSWER_STRING_MUST_BE_A_LIST)
            self._valid = False
            return
        if len(label) >= 2:
            self._errors += (submission.qustion_id, trial_submit_exception.ErrorMessages.SINGLE_SELECT_ERROR)
            self._valid = False
            return

    def _validate_multi_select(self, submission):
        try:
            labels = literal_eval(submission.answer)
        except ValueError:
            self._errors += (submission.question_id, trial_submit_exception.ErrorMessages.ANSWER_STRING_MUST_BE_A_LIST)
            self._valid = False
            return
        answer_count = submission.question.answer_count_limit

        if len(labels) > answer_count:
            self._errors += (submission.question_id,
                             trial_submit_exception.ErrorMessages.MULTI_SELECT_LIMIT_REACHED_ERROR.format(answer_count))
            self._valid = False
            return

    def _validate_file_upload(self, submission):
        if not submiision.has_file:
            return
        try:
            answer_file = self._request.files[str(submission.id)]
        except:
            self._valid = False
            self._errors += ['file with name {submission.id} does not exists']
            return
        file_format = submission.question.file_format
        file_size_limit = submission.question.file_size_limit

        answer_file_format = os.path.splitext(answer_file.name)[1][1:]

        if file_format != answer_file_format:
            self._errors += (
                submission.question_id, trial_submit_exception.ErrorMessages.INVALID_FILE_FORMAT.format(file_format))
            self._valid = False
            return
        if answer_file.size > file_size_limit * 1024 * 1024:
            self._errors += (submission.question_id,
                             trial_submit_exception.ErrorMessages.FILE_SIZE_LIMIT_EXCEEDED.format(file_size_limit))
            self._valid = False
            return

        for qs in self._trial.validated_data['question_submissions']:
            if qs['id'] == submission.id:
                qs['answer'] = self._save_to_storage(self._request, submission.id)
                qqs = self._trial.question_submissions.get(id=subbmission.id)
                qqs.answer = [qs['answer']]
                qqs.save()
                break

    def _validate_manual_judgment(self, submission):
        pass

    def _validate_numeric_range(self, submission):
        try:
            answer = eval(submission.answer)
        except ValueError:
            self._errors += (
                submission.question_id, trial_submit_exception.ErrorMessages.INVALID_LITERALS_FOR_NUMERIC_RANGE)
            self._valid = False
            return
        if answer[0] > answer[1]:
            self._errors += (submission.question_id, trial_submit_exception.ErrorMessages.INVALID_NUMERIC_RANGE)
            self._valid = False
            return

    def _save_to_storage(self, request, submission_id):
        destination = os.path.join('teams', self._trial.team_task.team.name,
                                   f'trial{self.trial_id}',
                                   f'question_submission{submission_id}')
        uploaded_filename = request.FILES[submission_id].name
        try:
            os.makedirs(os.path.join(settings.MEDIA_ROOT, destination))
        except OSError:
            print('oops')
        full_filename = os.path.join(settings.MEDIA_ROOT, destination, uploaded_filename)
        copied_file = open(full_filename, 'wb+')
        file_content = ContentFile(request.FILES[submission_id].read())
        for chunk in file_content.chunks():
            copied_file.write(chunk)
        copied_file.close()
        return os.path.join(destination, uploaded_filename)
