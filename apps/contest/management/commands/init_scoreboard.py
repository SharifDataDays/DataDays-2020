import requests
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from rest_framework import status

from apps.contest import models as contest_models
from apps.contest.services.scoreboard import Scoreboard


class Command(BaseCommand):
    """ This command initializes the scoreboard
        by created milestones.
    """
    help = 'Initialize Scoreboard'

    def add_arguments(self, parser):

        parser.add_argument(
            '--init',
            action='store_true',
            help='initialize whole scoreboard'
        )

        parser.add_argument(
            '--add_task_to_milestone',
            action='store_true',
            help='attach given task to given milestone'
        )
        parser.add_argument(
            '--add_task',
            action='store_true',
            help='add given task to scoreboard'
        )
        parser.add_argument(
            '--add_milestone',
            action='store_true',
            help='add given milestone to scoreboard'
        )

        parser.add_argument(
            'ids',
            nargs='*',
            type=int,
            help='Task or milestone ids',
        )

    def handle(self, *args, **options):
        if options.get('init'):
            self._handle_init_all()
        elif options.get('add_task_to_milestone'):
            self._handle_add_task_to_milestone(options)
        elif options.get('add_task'):
            self._handle_add_task(options)
        elif options.get('add_milestone'):
            self._handle_add_milestone(options)

    def _handle_init_all(self):
        contests = contest_models.Contest.objects.all()
        for contest in contests:
            self._add_milestone(contest)
            milestones = contest_models.Milestone.objects.all()
            for milestone in milestones:
                self._add_milestone(milestone)
                for task in milestone.tasks.all():
                    self._add_task(task)
                    self._add_task_to_milestone(task, milestone)
                    self._add_task_to_milestone(task, contest)

    def _handle_add_task_to_milestone(self, options):
        if not options.get('ids') or len(options.get('ids')) != 2:
            print("Please Enter Command Like This: --add_task_to_milestone {task_id} {milestone_id}")
        else:
            task_id, milestone_id = options.get('ids')[0], options.get('ids')[1]
            try:
                task = contest_models.Task.objects.get(id=task_id)
            except contest_models.Task.DoesNotExist as e:
                task = None
                print(e)
            try:
                milestone = contest_models.Milestone.objects.get(id=milestone_id)
            except contest_models.Milestone.DoesNotExist as e:
                milestone = None
                print(e)
            if task and milestone:
                self._add_task_to_milestone(task, milestone)

    def _handle_add_task(self, options):
        if not options.get('ids') or len(options.get('ids')) != 1:
            print("Please Enter Command Like This: --add_task {task_id}")
        else:
            task_id = options.get('ids')[0]
            try:
                task = contest_models.Task.objects.get(id=task_id)
            except contest_models.Task.DoesNotExist as e:
                task = None
                print(e)
            if task:
                self._add_task(task)

    def _handle_add_milestone(self, options):
        if not options.get('ids') or len(options.get('ids')) != 1:
            print("Please Enter Command Like This: --add_milestone {milestone_id}")
        else:
            milestone_id = options.get('ids')[0]
            try:
                milestone = contest_models.Milestone.objects.get(id=milestone_id)
            except contest_models.Milestone.DoesNotExist as e:
                milestone = None
                print(e)
            if milestone:
                self._add_milestone(milestone)

    def _add_milestone(self, milestone: contest_models.Milestone) -> None:
        Scoreboard.add_milestone(milestone)

    def _add_task(self, task: contest_models.Task) -> None:
        Scoreboard.add_task(task)

    def _add_task_to_milestone(self, task: contest_models.Task, milestone: contest_models.Milestone) -> None:
        Scoreboard.add_task_to_milestone(task, milestone)
