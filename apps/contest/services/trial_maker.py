import enum
from random import randint

from django.utils import timezone

from datadays.apps.contest.Exceptions import trial_validation_exception
from datadays.apps.contest.Exceptions.trial_validation_exception import TrialNotAllowed
from datadays.apps.contest.models import Task, Trial, TrialQuestion

from datadays.apps.question.models import Question


class Constants(enum.Enum):
    TRIAL_TIME_LIMIT = 24
    TRIAL_COOL_DOWN = 2
    HOUR = 3600  # Seconds


class TrialMaker:

    def __init__(self, task):
        self.task = task
        self.trial = None

    def __call__(self):
        try:
            TrialValidation(self.task).validate()
        except TrialNotAllowed as e:
            raise e
        if self.task.has_unsubmitted_trial:
            self._get_existing_trial()
        else:
            self._create_new_trial()
        return self.trial

    def _get_existing_trial(self):
        if self.task.has_unsubmitted_trial:
            self.trial = self.task.trials[-1]

    def _create_new_trial(self):
        trial_recipe = self.task.trial_recipe
        question_recipes = trial_recipe.question_recipes
        due_time = timezone.now() + timezone.timedelta(hours=Constants.TRIAL_TIME_LIMIT.value)
        trial = Trial(due_time=due_time)
        self._create_trial_questions(question_recipes, trial)
        self._update_task_after_trial_created()
        trial.save()
        self.trial = trial

    def _update_task_after_trial_created(self):
        self.task.trials_count += 1
        self.task.has_unsubmitted_trial = True
        self.task.save()

    def _create_trial_questions(self, question_recipes, trial):
        questions_ids = []
        for recipe in question_recipes:
            questions_ids.append(self._get_n_random_question_ids(recipe.question_type, recipe.count))
        TrialQuestion.objects.bulk_create([TrialQuestion(
            question=Question.objects.get(id=question_id),
            trial=trial
        ) for question_id in questions_ids])
        self.task.trial_questions_ids += ','.join(str(question_id) for question_id in questions_ids)

    def _get_n_random_question_ids(self, question_type, n):
        questions_count = Question.objects.filter(type=question_type).count()
        previous_ids = [int(question_id) for question_id in self.task.trial_questions_ids]
        ids = []
        while len(ids) < n:
            random_id = randint(1, questions_count)
            while random_id in ids or random_id in previous_ids:
                random_id = randint(1, questions_count)
            ids.append(random_id)

        return ids


class TrialValidation:

    def __init__(self, task: Task):
        self.task = task

    def validate(self):
        if not self.task.content_finished:
            raise TrialNotAllowed(trial_validation_exception.ErrorMessages.CONTENT_NOT_FINISHED)
        if self.task.trials_count != 0 and (
                timezone.now() - self.task.last_trial_time).total_seconds() // Constants.HOUR.value < Constants.TRIAL_COOL_DOWN.value:
            raise TrialNotAllowed(trial_validation_exception.ErrorMessages.COOLING_DOWN)
        if self.task.trials_count >= 3:
            raise TrialNotAllowed(trial_validation_exception.ErrorMessages.TRIAL_COUNT_LIMIT_REACHED)
