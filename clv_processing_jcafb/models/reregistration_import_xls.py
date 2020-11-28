# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from functools import reduce
from ast import literal_eval
import xlrd
from datetime import datetime

from odoo import models

_logger = logging.getLogger(__name__)


def secondsToStr(t):

    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class AbstractProcess(models.AbstractModel):
    _inherit = 'clv.abstract.process'

    def _do_reregistration_import_xls(self, schedule):

        _logger.info(u'%s %s', '>>>>>>>> schedule:', schedule.name)

        schedule.processing_log = 'Executing: "' + '_do_reregistration_import_xls' + '"...\n\n'
        schedule.processing_log += '>>>>>>>> schedule:' + schedule.name + '"...\n\n'
        date_last_exec = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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

        Person = self.env['clv.person']
        PersonAux = self.env['clv.person_aux']
        Address = self.env['clv.address']
        AddressAux = self.env['clv.address_aux']

        param_value = self.env['ir.config_parameter'].sudo().get_param(
            'clv.global_settings.current_phase_id', '').strip()
        phase_id = False
        if param_value:
            phase_id = int(param_value)

        CEP = '17455-000'

        for i in range(sheet.nrows):

            rec = sheet.cell_value(i, 0)
            ok = sheet.cell_value(i, 1)
            # person_code = sheet.cell_value(i, 2)
            person_name = sheet.cell_value(i, 3)
            gender = sheet.cell_value(i, 4)
            date_of_birth = sheet.cell_value(i, 5)
            address_name = sheet.cell_value(i, 6)
            # district = sheet.cell_value(i, 7)
            # city = sheet.cell_value(i, 8)
            # responsible = shOk: %seet.cell_value(i, 9)

            if ok == 'x':

                _logger.info(u'>>>>>>>>>> Rec: %s, Ok: %s, Name: %s, Address: %s', rec, ok, person_name, address_name)

                person = Person.search([
                    ('name', '=', person_name),
                ])
                _logger.info(u'>>>>>>>>>>>>>>>> Person: %s', person)

                person_aux = PersonAux.search([
                    ('name', '=', person_name),
                ])
                _logger.info(u'>>>>>>>>>>>>>>>> Person (Aux): %s', person_aux)

                if person_aux.id is not False:

                    new_person = False

                    _logger.info(u'>>>>>>>>>>>>>>>>>>>>> Reference Address (Aux): %s', person_aux.ref_address_aux_id)
                    _logger.info(u'>>>>>>>>>>>>>>>>>>>>> Related Person: %s', person_aux.related_person_id)
                    _logger.info(u'>>>>>>>>>>>>>>>>>>>>> Reference Address: %s', person_aux.ref_address_id)

                else:

                    new_person = True

                address = Address.search([
                    ('name', '=', address_name),
                ])
                _logger.info(u'>>>>>>>>>>>>>>>> Address: %s', address)

                address_aux = AddressAux.search([
                    ('name', '=', address_name),
                ])
                _logger.info(u'>>>>>>>>>>>>>>>> Address (Aux): %s', address_aux)

                if address_aux.id is not False:

                    new_address = False

                    _logger.info(u'>>>>>>>>>>>>>>>>>>>>> Related Address: %s', address_aux.related_address_id)

                    if person_aux.ref_address_aux_id == address_aux:
                        change_address = False
                    else:
                        change_address = True

                else:

                    change_address = True

                    if address_name is False or address_name == '':
                        new_address = 'NULL'
                    else:
                        new_address = True

                _logger.info(u'>>>>>>>>>>>>>>>> New Person: %s', new_person)
                _logger.info(u'>>>>>>>>>>>>>>>> Change Address: %s', change_address)
                _logger.info(u'>>>>>>>>>>>>>>>> New Address: %s', new_address)

                if new_person is False and change_address is False and new_address is False:

                    if address_aux.reg_state != 'revised':
                        address_aux.reg_state = 'revised'
                    if address_aux.state != 'available':
                        address_aux.state = 'available'
                    if address_aux.phase_id.id != phase_id:
                        address_aux.phase_id = phase_id

                    if person_aux.reg_state != 'revised':
                        person_aux.reg_state = 'revised'
                    if person_aux.state != 'available':
                        person_aux.state = 'available'
                    if person_aux.phase_id.id != phase_id:
                        person_aux.phase_id = phase_id

                elif new_person is False and change_address is True and new_address is False:

                    if person_aux.reg_state != 'revised':
                        person_aux.reg_state = 'revised'

                    if person_aux.state != 'available':
                        person_aux.state = 'available'

                    if person_aux.phase_id.id != phase_id:
                        person_aux.phase_id = phase_id

                    if person_aux.ref_address_id.id != address.id:
                        person_aux.ref_address_id = address.id

                    if person_aux.ref_address_aux_id.id != address_aux.id:
                        person_aux.ref_address_aux_id = address_aux.id
                        person_aux.do_person_aux_get_ref_address_aux_data()

                    if address_aux.reg_state != 'revised':
                        address_aux.reg_state = 'revised'

                    if address_aux.state != 'available':
                        address_aux.state = 'available'

                    if address_aux.phase_id.id != phase_id:
                        address_aux.phase_id = phase_id

                elif new_person is False and change_address is True and new_address is True:

                    vals = {}
                    vals['zip'] = CEP
                    address_aux = AddressAux.create(vals)
                    address_aux.zip_search()
                    street_name = address_name[:address_name.find(',')]
                    street_number = address_name[address_name.find(', ') + 2:address_name.find('(') - 1]
                    street2 = address_name[address_name.find('(') + 1:address_name.find(')')]
                    address_aux.street_name = street_name
                    address_aux.street2 = street2
                    address_aux.street_number = street_number

                    if address_aux.reg_state != 'revised':
                        address_aux.reg_state = 'revised'

                    if address_aux.state != 'available':
                        address_aux.state = 'available'

                    if address_aux.phase_id.id != phase_id:
                        address_aux.phase_id = phase_id

                    if person_aux.reg_state != 'revised':
                        person_aux.reg_state = 'revised'

                    if person_aux.state != 'available':
                        person_aux.state = 'available'

                    if person_aux.phase_id.id != phase_id:
                        person_aux.phase_id = phase_id

                    if person_aux.ref_address_aux_id.id != address_aux.id:
                        person_aux.ref_address_aux_id = address_aux.id
                        person_aux.do_person_aux_get_ref_address_aux_data()

                elif new_person is False and change_address is True and new_address == 'NULL':

                    if person_aux.reg_state != 'revised':
                        person_aux.reg_state = 'revised'

                    if person_aux.state != 'unavailable':
                        person_aux.state = 'unavailable'

                    if person_aux.ref_address_is_unavailable is False:
                        person_aux.ref_address_is_unavailable = True

                    if person_aux.ref_address_id is not False:
                        person_aux.ref_address_id = False

                    if person_aux.ref_address_aux_is_unavailable is False:
                        person_aux.ref_address_aux_is_unavailable = True

                    if person_aux.ref_address_aux_id is not False:
                        person_aux.ref_address_aux_id = False
                        person_aux.do_person_aux_clear_address_data()
                        person_aux.contact_info_is_unavailable = True

                    if person_aux.phase_id.id != phase_id:
                        person_aux.phase_id = phase_id

                elif new_person is True and change_address is True and new_address is False:

                    vals = {}
                    vals['name'] = person_name
                    vals['gender'] = gender[:1]
                    datetime_date = xlrd.xldate_as_datetime(date_of_birth, 0)
                    date_object = datetime_date.date()
                    string_date = date_object.isoformat()
                    vals['birthday'] = datetime.strptime(string_date, '%Y-%m-%d')
                    person_aux = PersonAux.create(vals)

                    if person_aux.ref_address_id.id != address.id:
                        person_aux.ref_address_id = address.id

                    if person_aux.ref_address_aux_id.id != address_aux.id:
                        person_aux.ref_address_aux_id = address_aux.id
                        # person_aux.do_person_aux_get_ref_address_aux_data()

                    if person_aux.reg_state != 'revised':
                        person_aux.reg_state = 'revised'

                    if person_aux.state != 'available':
                        person_aux.state = 'available'

                    if person_aux.phase_id.id != phase_id:
                        person_aux.phase_id = phase_id

                    if address_aux.reg_state != 'revised':
                        address_aux.reg_state = 'revised'

                    if address_aux.state != 'available':
                        address_aux.state = 'available'

                    if address_aux.phase_id.id != phase_id:
                        address_aux.phase_id = phase_id

                elif new_person is True and change_address is True and new_address is True:

                    vals = {}
                    vals['zip'] = CEP
                    address_aux = AddressAux.create(vals)
                    address_aux.zip_search()
                    street_name = address_name[:address_name.find(',')]
                    street_number = address_name[address_name.find(', ') + 2:address_name.find('(') - 1]
                    street2 = address_name[address_name.find('(') + 1:address_name.find(')')]
                    address_aux.street_name = street_name
                    address_aux.street2 = street2
                    address_aux.street_number = street_number

                    if address_aux.reg_state != 'revised':
                        address_aux.reg_state = 'revised'

                    if address_aux.state != 'available':
                        address_aux.state = 'available'

                    if address_aux.phase_id.id != phase_id:
                        address_aux.phase_id = phase_id

                    vals = {}
                    vals['name'] = person_name
                    vals['gender'] = gender[:1]
                    datetime_date = xlrd.xldate_as_datetime(date_of_birth, 0)
                    date_object = datetime_date.date()
                    string_date = date_object.isoformat()
                    vals['birthday'] = datetime.strptime(string_date, '%Y-%m-%d')
                    person_aux = PersonAux.create(vals)

                    if person_aux.ref_address_id.id != address.id:
                        person_aux.ref_address_id = address.id

                    if person_aux.ref_address_aux_id.id != address_aux.id:
                        person_aux.ref_address_aux_id = address_aux.id
                        # person_aux.do_person_aux_get_ref_address_aux_data()

                    if person_aux.reg_state != 'revised':
                        person_aux.reg_state = 'revised'

                    if person_aux.state != 'available':
                        person_aux.state = 'available'

                    if person_aux.phase_id.id != phase_id:
                        person_aux.phase_id = phase_id

        _logger.info(u'%s %s', '>>>>>>>> Execution time: ', secondsToStr(time() - start))

        schedule.processing_log +=  \
            'date_last_exec: ' + str(date_last_exec) + '\n' + \
            'Execution time: ' + str(secondsToStr(time() - start)) + '\n'
