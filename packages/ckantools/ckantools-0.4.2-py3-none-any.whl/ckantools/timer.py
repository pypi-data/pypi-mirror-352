# !/usr/bin/env python
# encoding: utf-8

from collections import OrderedDict
from datetime import datetime


class Timer:
    """
    A simple class which can be used to time events.
    """

    def __init__(self):
        """
        The timer is started upon instantiation (i.e. when this function is called).
        """
        self.start = datetime.now()
        self.events = []

    def add_event(self, label):
        """
        Add a new event at the current time with the given label.

        :param label: the label for the event
        """
        self.events.append((label, datetime.now()))

    def to_dict(self):
        """
        Return an OrderedDict of timings. Each key in the returned OrderedDict is a
        label and the value associated with it is the number of seconds it took between
        the previous event and this one.

        :return: an OrderedDict of events and how long they took
        """
        timings = OrderedDict()
        split = self.start
        for label, date in self.events:
            timings[label] = (date - split).total_seconds()
            split = date
        return timings
