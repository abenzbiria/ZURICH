# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (http://tiny.be). All Rights Reserved
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _
import datetime


class res_partner_evaluation(osv.osv):
    _name = 'res.partner.evaluation'

    _columns = {
        'evaluation_id':fields.many2one('purchase.evaluation','Evaluation'),
        'partner_id':fields.many2one('res.partner','Partenaire'),
        'note':fields.float('Note'),

    }


class account_invoice_evaluation(osv.osv):
    _name = 'account.invoice.evaluation'

    _columns = {
        'evaluation_id':fields.many2one('purchase.evaluation','Evaluation'),
        'invoice_id':fields.many2one('account.invoice','Facture'),
        'note':fields.integer('Note'),

    }


class purchase_evaluation(osv.osv):
    _name = 'purchase.evaluation'

    _columns = {
        'name': fields.char('Nom critère', size=64, required=True),

    }

purchase_evaluation()


class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'evaluation_ids':fields.one2many('res.partner.evaluation', 'partner_id', "Lignes d'évaluation"),

    }

res_partner()