# -*- coding: utf-8 -*-
##############################################



from openerp.osv import  osv,fields
from openerp import models ,fields ,api, _

from openerp.tools.translate import _
from datetime import datetime


class purchase_order(osv.osv):

    _inherit = "purchase.order"


    state = fields.Many2one(string="Statut", comodel_name="purchase.order.stage",)
    rubrique_id = fields.Many2one(comodel_name="rubrique.rubrique", string="Rubrique",default=1)

    @api.onchange('rubrique_id')
    def get_selection(self):
        if not self.rubrique_id:
            return
        rubrique = self.rubrique_id
        ids = []
        for stage in rubrique.stage_ids:
            ids.append(stage.id)
        domain=[('id','in',tuple(ids))]
        print '1111111111',domain
        return {'domain':{'state':domain}}




purchase_order()

class purchase_order_stage(osv.osv):

    _name = "purchase.order.stage"

    _order = 'sequence asc'

    name = fields.Char(string="Libellé", required=True)
    code = fields.Char(string="code", required=True)
    sequence = fields.Integer(string="Sequence", required=True)
    rubrique_ids = fields.Many2many(comodel_name="rubrique.rubrique", relation="rubrique_stage_rel", column1="rubrique_id", column2="stage_id", string="Rubriques", )


purchase_order_stage()



