# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from functools import reduce
from ast import literal_eval
import xlrd

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

        filepath = method_args['file_path']
        _logger.info(u'>>>>>>>>>> file_path: %s', filepath)
        sheet_name = method_args['sheet_name']
        _logger.info(u'>>>>>>>>>> sheet_name: %s', sheet_name)

        book = xlrd.open_workbook(filepath)
        sheet = book.sheet_by_name(sheet_name)

        for i in range(sheet.nrows):

            rec = sheet.cell_value(i, 0)
            ok = sheet.cell_value(i, 1)
            person_code = sheet.cell_value(i, 2)
            name = sheet.cell_value(i, 3)
            gender = sheet.cell_value(i, 4)
            date_of_birth = sheet.cell_value(i, 5)
            address = sheet.cell_value(i, 6)
            district = sheet.cell_value(i, 7)
            city = sheet.cell_value(i, 8)
            responsible = sheet.cell_value(i, 9)

            _logger.info(u'>>>>>>>>>> Ok: %s', ok)
            if ok == 'x':
                _logger.info(u'>>>>>>>>>>>>>>>> Name: %s', name)

        _logger.info(u'%s %s', '>>>>>>>> Execution time: ', secondsToStr(time() - start))
