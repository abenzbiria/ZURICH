# -*- coding: utf-8 -*-
##############################################



from openerp.osv import  osv,fields
from openerp import models ,fields ,api, _

from openerp.tools.translate import _
from datetime import datetime

class purchase_requisition(osv.osv):
    _inherit = "purchase.requisition"

    def _prepare_purchase_order(self, cr, uid, requisition, supplier, context=None):
        supplier_pricelist = supplier.property_product_pricelist_purchase
        return {
            'origin': requisition.name,
            'rubrique_id':requisition.rubrique_id.id,
            'date_order': requisition.date_end or fields.datetime.now(),
            'partner_id': supplier.id,
            'pricelist_id': supplier_pricelist.id,
            'currency_id': supplier_pricelist and supplier_pricelist.currency_id.id or requisition.company_id.currency_id.id,
            'location_id': requisition.procurement_id and requisition.procurement_id.location_id.id or requisition.picking_type_id.default_location_dest_id.id,
            'company_id': requisition.company_id.id,
            'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
            'requisition_id': requisition.id,
            'notes': requisition.description,
            'picking_type_id': requisition.picking_type_id.id
        }

    budget_id = fields.Many2one(comodel_name="purchase.budget",required=True,string="Budget")
    rubrique_id= fields.Many2one(comodel_name="rubrique.rubrique",required=True,string="Rubrique")
    responsible_id = fields.Many2one(string="Responsable", comodel_name="res.users")
    department_id = fields.Many2one(comodel_name="hr.department",required=True,string="Département origine")

class purchase_order(osv.osv):

    _inherit = "purchase.order"


    state = fields.Many2one(string="Statut", comodel_name="purchase.order.stage",default=11)
    rubrique_id = fields.Many2one(comodel_name="rubrique.rubrique", string="Rubrique",default=1)


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



