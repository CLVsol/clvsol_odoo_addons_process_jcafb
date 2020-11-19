# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from functools import reduce
from ast import literal_eval

from odoo import models

_logger = logging.getLogger(__name__)


def secondsToStr(t):

    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class AbstractProcess(models.AbstractModel):
    _inherit = 'clv.abstract.process'

    def _do_reregistration_import_xls(self, schedule):

        _logger.info(u'%s %s', '>>>>>>>> schedule:', schedule.name)

        from time import time
        start = time()

        method_args = {}
        if schedule.method_args is not False:
            method_args = literal_eval(schedule.method_args)
        _logger.info(u'%s %s', '>>>>>>>>>> method_args: ', method_args)

        _logger.info(u'%s %s', '>>>>>>>> Execution time: ', secondsToStr(time() - start))
