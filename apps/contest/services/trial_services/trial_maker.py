import enum
import random

from random import randint
from typing import Union, List, Tuple

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from apps.contest.Exceptions import trial_validation_exception
from apps.contest.models import Trial, TeamTask, QuestionSubmission, Task, TrialRecipe

from apps.question.models import Question


class Constants(enum.Enum):
    HOUR = 3600  # Seconds


class TrialMaker:

    def __init__(self, request):
        self.request = request
        self.team_task = self._set_team_task()
        self.task: Union[Task, None] = None
        self.trial_recipe: Union[TrialRecipe, None] = None
        self.previous_trials: Union[List[Trial], None] = None
        self.before_selected_questions_ids: Union[List[int], None] = None
        self.trial_questions: Union[List[Tuple[Question, int]], None] = None
        self.trial: Union[Trial, None] = None
        self.question_submissions: Union[List[QuestionSubmission], None] = None
        self.errors = []

    def make_trial(self):

        validator = TrialValidation(self.team_task)
        valid, errors = validator.validate()
        if not valid:
            return None, errors

        self.task = self.team_task.task
        self.trial_recipe = self.task.trial_recipe
        self.previous_trials = self.team_task.trials
        self.before_selected_questions_ids = self._set_before_selected_questions_ids()
        self.trial_questions = self._set_trial_questions()
        self.trial = self._create_trial()
        self.question_submissions = self._create_trial_question_submissions()
        return self.trial, errors

    def _set_team_task(self):
        team = self.request.user.participant.team
        return TeamTask.objects.filter(team=team)

    def _set_before_selected_questions_ids(self):
        questions = []
        for trial in self.previous_trials:
            questions += QuestionSubmission.objects.filter(trial=trial).values_list('question_id', flat=True)
        return questions

    def _set_trial_questions(self):
        questions = []
        for question_recipe in self.trial_recipe.question_recipes:
            questions_available = Question.objects.filter(task=self.task).exlclude(
                id__in=self.before_selected_questions_ids).filter(type=question_recipe.question_type)
            random.shuffle(question_recipe)
            questions += [(question, question_recipe.priority) for question in
                          questions_available[:question_recipe.count]]
        return sorted(questions, key=lambda x: x[1])

    def _create_trial_question_submissions(self):
        question_submissions = []
        for question, priority in self.trial_questions:
            question_submissions += QuestionSubmission(trial=self.trial,
                                                       question=question,
                                                       question_priority=priority)

        QuestionSubmission.objects.bulk_create(question_submissions)

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
            self.errors += _(trial_validation_exception.ErrorMessages.CONTENT_NOT_FINISHED)
            self.valid = False

    def _trial_cooldown_check(self):
        trials_count = len(self.team_task.trials)
        if trials_count != 0:
            last_trial_time = self.team_task.trials[-1].submit_time
            if (
                    timezone.now() - last_trial_time).total_seconds() // Constants.HOUR.value <= self.task.trial_cooldown:
                self.errors += _(trial_validation_exception.ErrorMessages.COOLING_DOWN)
                self.valid = False

    def _trial_count_limit_check(self):
        trials_count = len(self.team_task.trials)
        if trials_count >= self.task.max_trials_count:
            self.errors += _(trial_validation_exception.ErrorMessages.TRIAL_COUNT_LIMIT_REACHED)

    def _milestone_date_range_check(self):
        now = timezone.now()
        milestone_start = self.task.milestone.start_date
        milestone_end = self.task.milestone.end_date
        if now < milestone_start or now > milestone_end:
            self.errors += _(trial_validation_exception.ErrorMessages.OUT_OF_DATE_RANGE)
