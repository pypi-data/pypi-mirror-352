# -*- coding: UTF-8 -*-
# Copyright 2023-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
# See https://dev.lino-framework.org/plugins/linod.html

import logging
from typing import Callable
from lino.api import dd, _
from lino.core.roles import SiteStaff


class Procedure(dd.Choice):
    func: Callable
    kwargs: dict
    class_name: str

    def __init__(self, func, class_name, **kwargs):
        name = func.__name__
        super().__init__(name, name, name)
        self.func = func
        self.class_name = class_name
        self.kwargs = kwargs

    def run(self, ar):
        return self.func(ar)

    def __repr__(self):
        return f"Procedures.{self.value}"


class Procedures(dd.ChoiceList):
    verbose_name = _("Background procedure")
    verbose_name_plural = _("Background procedures")
    max_length = 100
    item_class = Procedure
    column_names = "value name text class_name kwargs"
    required_roles = dd.login_required(SiteStaff)

    task_classes = []

    @classmethod
    def task_classes(cls):
        return [
            dd.resolve_model(spec) for spec in {c.class_name for c, _ in cls.choices}
        ]

    @dd.virtualfield(dd.CharField(_("Task class")))
    def class_name(cls, choice, ar):
        return choice.class_name

    @dd.virtualfield(dd.CharField(_("Suggested recurrency")))
    def kwargs(cls, choice, ar):
        return ", ".join(["{}={}".format(*i) for i in sorted(choice.kwargs.items())])


class LogLevel(dd.Choice):
    num_value = logging.NOTSET

    def __init__(self, name):
        self.num_value = getattr(logging, name)
        super().__init__(name, name, name)


class LogLevels(dd.ChoiceList):
    verbose_name = _("Logging level")
    verbose_name_plural = _("Logging levels")
    item_class = LogLevel
    column_names = "value text num_value"

    @dd.virtualfield(dd.IntegerField(_("Numeric value")))
    def num_value(cls, choice, ar):
        return choice.num_value


LogLevel.set_widget_options("num_value", hide_sum=True)

add = LogLevels.add_item
add("DEBUG")
add("INFO")
add("WARNING")
add("ERROR")
add("CRITICAL")


def background_task(**kwargs):
    if "class_name" not in kwargs:
        kwargs["class_name"] = "linod.SystemTask"

    def decorator(func):
        Procedures.add_item(func, **kwargs)
        return func

    return decorator


def schedule_often(every=10, **kwargs):
    kwargs.update(every_unit="secondly", every=every)
    return background_task(**kwargs)


def schedule_daily(**kwargs):
    kwargs.update(every_unit="daily", every=1)
    return background_task(**kwargs)
