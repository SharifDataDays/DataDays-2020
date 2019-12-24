class ErrorMessages:
    TRIAL_COUNT_LIMIT_REACHED = 'Count limit of trials reached for this user'
    COOLING_DOWN = 'Cooling down time of trial not finished'
    CONTENT_NOT_FINISHED = 'User must finish his content first'


class TrialNotAllowed(Exception):
    pass
