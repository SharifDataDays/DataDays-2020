from apps.contest.models import Trial


class TrialCorrector:

    def __init__(self, trial: Trial):
        self.trial = trial

    def __call__(self):
        return 100
