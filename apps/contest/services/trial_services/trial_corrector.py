from django.utils import timezone

from apps.contest.models import Trial


class TrialCorrector:

    def __init__(self, trial: Trial):
        self.trial = trial

    def __call__(self):
        self.trial.submit_time = timezone.now()
        return 100
