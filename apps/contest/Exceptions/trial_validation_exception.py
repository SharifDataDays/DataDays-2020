class ErrorMessages:
    TRIAL_COUNT_LIMIT_REACHED = 'Count limit of trials reached for this user'
    ACTIVE_TRIAL = 'A trial is already open'
    COOLING_DOWN = 'Cooling down time of trial not finished'
    CONTENT_NOT_FINISHED = 'User must finish his content first'
    OUT_OF_DATE_RANGE = 'Milestone finished or not started yet!'


class TrialNotAllowed(Exception):
    pass
