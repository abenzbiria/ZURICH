# -*- coding: utf-8 -*-
##############################################



from openerp.osv import  osv,fields
from openerp import models ,fields ,api, _

from openerp.tools.translate import _
from datetime import datetime


class purchase_order(osv.osv):

    _inherit = "purchase.order"


    state = fields.Many2one(string="Statut", comodel_name="purchase.order.stage",domain="[('rubrique_ids','=',rubrique_id)]")
    rubrique_id = fields.Many2one(comodel_name="rubrique.rubrique", string="Rubrique",default=1)

    # @api.onchange('rubrique_id')
    # def get_selection(self):
    #     rubrique = self.rubrique_id
    #     ids = [x.id for x in rubrique.stage_ids]
    #     domain=[('id','in',tuple(ids))]
    #     self.rubrique_id = rubrique.id
    #     return {'domain':{'state':domain}}

    def onchange_rubrique_id(self,cr,uid,ids,rubrique_id,context=None):
        if not rubrique_id:
            return {}
        rubrique = self.pool.get('rubrique.rubrique').browse(cr,uid,rubrique_id)
        ids = [x.id for x in rubrique.stage_ids]
        domain=[('id','in',tuple(ids))]
        print '2222222',rubrique.name,domain
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



