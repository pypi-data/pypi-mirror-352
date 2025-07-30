# -*- coding: utf-8 -*-
# Copyright 2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
from asgiref.sync import async_to_sync
from lino.api import rt
from lino.modlib.linod.mixins import start_task_runner

# import logging
# from lino import logger
# def getHandlerByName(name):
#     for l in logger.handlers:
#         if l.name == name:
#             return l

def objects():
    raise Exception("""

    This fixture isn't used at the moment.  I wrote it because I thought it
    would be nice to run the system task runner automatically when ``pm prep``
    in order to cover the sync_ibanity system task. But (1) this would require
    me to integrate also the ``checkdata`` and ``checksummaries`` fixtures into
    it (otherwise they would run again as a system task) and (2) we don't want
    to start `sync_ibanity` automatically on GitLab because it can't work
    without credentials.

        """)
    ar = rt.login("robin")
    # logger.setLevel(logging.DEBUG)
    # getHandlerByName('console').setLevel(logging.DEBUG)
    # ar.debug("Coucou")
    async_to_sync(start_task_runner)(ar, max_count=1)
    return []
