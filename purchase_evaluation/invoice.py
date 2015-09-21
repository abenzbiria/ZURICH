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

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning



class account_invoice(models.Model):
    _inherit = 'account.invoice'

    evaluation_ids = fields.One2many('account.invoice.evaluation', 'invoice_id', string="Lignes d'évaluation")



    @api.multi
    def invoice_validate(self):

        res_eval_obj=self.env['res.partner.evaluation']
        acc_eval_obj=self.env['account.invoice.evaluation']
        res_obj=self.env['res.partner']
        vals={}
        for eval in self.evaluation_ids:
            if eval.note<0 or eval.note>10:
                raise except_orm(_('Error!'), _("Note de critère non autorisé (note comprise entre 0 et 10) ."))
            res_eval_ids = res_eval_obj.search([('partner_id','=',self.partner_id.id),('evaluation_id','=',eval.evaluation_id.id)])
            if res_eval_ids:
                print 'I am old'
                res_eval_ids.note = (res_eval_ids.note+eval.note)/2
            else:
                print 'I am new'
                vals['partner_id']=self.partner_id.id
                vals['evaluation_id']=eval.evaluation_id.id
                vals['note']=eval.note
                res_eval_obj.create(vals)
        return self.write({'state': 'open'})

account_invoice()