import enum
import random

from random import randint
from typing import Union, List, Tuple

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.contest.Exceptions import trial_validation_exception
from apps.contest.models import Trial, TeamTask, QuestionSubmission, Task, TrialRecipe, Score

from apps.question.models import Question


class Constants(enum.Enum):
    HOUR = 3600  # Seconds


class TrialMaker:

    def __init__(self, request, contest_id, milestone_id, task_id):
        self.request = request
        self.contest_id = contest_id
        self.milestone_id = milestone_id
        self.task_id = task_id
        self.team_task: Union[TeamTask, None] = None
        self.task: Union[Task, None] = None
        self.trial_recipe: Union[TrialRecipe, None] = None
        self.previous_trials: Union[List[Trial], None] = None
        self.before_selected_questions_ids: Union[List[int], None] = None
        self.trial_questions: Union[List[Tuple[Question, int]], None] = None
        self.trial: Union[Trial, None] = None
        self.question_submissions: Union[List[QuestionSubmission], None] = None
        self.errors = []

    def make_trial(self):

        self._set_team_task()
        if self.errors:
            return None, self.errors
        validator = TrialValidation(self.team_task)
        valid, errors = validator.validate()
        if not valid:
            return None, errors
        print(self._has_uncompleted_trial())
        if not self._has_uncompleted_trial():
            try:
                self.task = self.team_task.task
                self.trial_recipe = self.task.trial_recipe
                self.previous_trials = self.team_task.trials
                self.before_selected_questions_ids = self._set_before_selected_questions_ids()
                self.trial_questions = self._set_trial_questions()
                self.trial = self._create_trial()
                self.question_submissions = self._create_trial_question_submissions()
            except Exception as e:
                print(e)
                if self.trial is not None:
                    self.trial.delete()
                if self.question_submissions is not None:
                    [qs.delete() for qs in self.question_submissions]
        return self.trial, errors

    def _set_team_task(self):
        team = self.request.user.participant.team
        try:
            team_task = TeamTask.objects.get(team=team, task_id=self.task_id)
        except (TeamTask.DoesNotExist, TeamTask.MultipleObjectsReturned) as e:
            self.errors.append(str(e))
            return
        self.team_task = team_task

    def _has_uncompleted_trial(self):
        try:
            existing_trial = Trial.objects.get(
                    team_task=self.team_task,
                    submit_time__isnull=True
                )
            self.trial = existing_trial
        except (Trial.DoesNotExist, Trial.MultipleObjectsReturned):
            return False
        return True

    def _set_before_selected_questions_ids(self):
        questions = []
        for trial in self.previous_trials.all():
            questions += QuestionSubmission.objects.filter(trial=trial).values_list('question_id', flat=True)
        return questions

    def _set_trial_questions(self):
        questions = []
        for question_recipe in self.trial_recipe.question_recipes.all():
            questions_available = Question.objects.filter(task=self.task, type=question_recipe.question_type)
            repeated_questions = list(questions_available.filter(id__in=self.before_selected_questions_ids))
            questions_available = list(questions_available)
            while len(repeated_questions) > 0 and len(questions_available) > question_recipe.count:
                removed = repeated_questions[0]
                questions_available.remove(removed)
                repeated_questions.remove(removed)
            random.shuffle(questions_available)
            final_count = min(len(questions_available), question_recipe.count)
            questions += [(question, question_recipe.priority)
                    for question in questions_available[:final_count]]
        return sorted(questions, key=lambda x: x[1])

    def _create_trial_question_submissions(self):
        question_submissions = []
        for question, priority in self.trial_questions:
            qs = QuestionSubmission(
                    trial=self.trial,
                    question=question,
                    question_priority=priority,
                    answer=[],
                )
            qs.save()
            question_submissions.append(qs)

        return question_submissions

    def _create_trial(self):
        due_time = timezone.now() + timezone.timedelta(hours=self.task.trial_time)
        trial = Trial(team_task=self.team_task, due_time=due_time)
        trial.save()
        return trial


class TrialValidation:

    def __init__(self, team_task: TeamTask):
        self.team_task = team_task
        self.task = team_task.task
        self.valid = True
        self.errors = []

    def validate(self):
        self._content_finished_check()
        self._trial_cooldown_check()
        self._trial_count_limit_check()
        self._milestone_date_range_check()
        return self.valid, self.errors

    def _content_finished_check(self):
        if not self.team_task.content_finished:
            self.errors.append(_(trial_validation_exception.ErrorMessages.CONTENT_NOT_FINISHED))
            self.valid = False

    def _trial_cooldown_check(self):
        trials_count = self.team_task.trials.count()
        if trials_count != 0:
            last_trial_time = self.team_task.trials.last().submit_time
            if last_trial_time is None:
                self.errors.append(_(trial_validation_exception.ErrorMessages.ACTIVE_TRIAL))
                self.valid = False
            elif (timezone.now() - last_trial_time).total_seconds() // Constants.HOUR.value <= self.task.trial_cooldown:
                self.errors.append(_(trial_validation_exception.ErrorMessages.COOLING_DOWN))
                self.valid = False

    def _trial_count_limit_check(self):
        trials_count = self.team_task.trials.count()
        if trials_count >= self.task.max_trials_count:
            self.errors.append(_(trial_validation_exception.ErrorMessages.TRIAL_COUNT_LIMIT_REACHED))

    def _milestone_date_range_check(self):
        now = timezone.now()
        milestone_start = self.task.milestone.start_time
        if now < milestone_start:
            self.errors.append(_(trial_validation_exception.ErrorMessages.OUT_OF_DATE_RANGE))
