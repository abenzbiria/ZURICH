# -*- coding: utf-8 -*-
##############################################



from openerp.osv import  osv,fields
from openerp import models ,fields ,api, _
from openerp.tools.translate import _


class account_invoice(models.Model):

    _inherit = 'account.invoice'

    budget_id = fields.Many2one(comodel_name="purchase.budget", string="Budget",readonly=True, states={'draft': [('readonly', False)]})
    rubrique_id = fields.Many2one(comodel_name="rubrique.rubrique", string="Rubrique",readonly=True, states={'draft': [('readonly', False)]})
    department_id = fields.Many2one(comodel_name="hr.department", string="Département",readonly=True, states={'draft': [('readonly', False)]})
    responsible_id = fields.Many2one(string="Responsable Demande", comodel_name="res.users",readonly=True, states={'draft': [('readonly', False)]})
    demandeur_id = fields.Many2one(string="Demandeur", comodel_name="res.users",readonly=True, states={'draft': [('readonly', False)]})
    requisition_id = fields.Many2one(string="Demande interne", comodel_name="purchase.requisition",readonly=True, states={'draft': [('readonly', False)]})

account_invoice