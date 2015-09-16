# -*- coding: utf-8 -*-
##############################################



from openerp.osv import  osv,fields
from openerp import models ,fields ,api, _
from openerp.tools.translate import _

class purchase_budget(osv.osv):

    _name = "purchase.budget"

    name = fields.Char(string="Libellé", required=True)
    rubrique_ids = fields.Many2many(comodel_name="rubrique.rubrique", relation="budget_rubrique_rel", column1="rubrique_id", column2="budget_id", string="Rubriques", )


purchase_budget()
