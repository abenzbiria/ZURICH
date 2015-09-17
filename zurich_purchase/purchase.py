# -*- coding: utf-8 -*-
##############################################



from openerp.osv import  osv,fields
from openerp import models ,fields ,api, _,exceptions

from openerp.tools.translate import _
from datetime import datetime

class purchase_requisition(osv.osv):

    _inherit = "purchase.requisition"

    def _prepare_purchase_order(self, cr, uid, requisition, supplier, context=None):
        supplier_pricelist = supplier.property_product_pricelist_purchase
        start_id = False
        for stage in requisition.rubrique_id.stage_ids:
            if stage.is_start:
                start_id = stage.id
        return {
            'origin': requisition.name,
            'rubrique_id':requisition.rubrique_id.id,
            'internal_state':start_id,
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

    @api.onchange('department_id')
    def onchange_department_id(self):
        user_id = False
        if self.department_id:
            if self.department_id.manager_id:
                if self.department_id.manager_id.user_id:
                    user_id = self.department_id.manager_id.user_id.id
        self.responsible_id = user_id

    @api.onchange('budget_id')
    def onchange_budget_id(self):
        user_id = False
        if self.budget_id:
            rubrique_ids = self.budget_id.rubrique_ids
            ids = [x.id for x in rubrique_ids]
            domain = [('id','in',tuple(ids))]
            return {'domain':{'rubrique_id':domain}}



class purchase_order(osv.osv):

    _inherit = "purchase.order"

    @api.multi
    @api.depends('state','internal_state')
    def get_is_visible(self):
        is_visible= False
        if self.state == "draft" and self.internal_state.is_start:
            is_visible = True
        self.is_validate_visible = is_visible


    internal_state = fields.Many2one(string="Statut Interne", comodel_name="purchase.order.stage",domain="[('rubrique_ids','=',rubrique_id)]")
    rubrique_id = fields.Many2one(comodel_name="rubrique.rubrique", string="Rubrique")
    is_validate_visible = fields.Boolean("Visible",compute=get_is_visible)

    def copy(self, cr, uid, id, default=None, context=None, done_list=None, local=False):
        default = {} if default is None else default.copy()
        po = self.browse(cr, uid, id, context=context)
        start_id = False
        if po.rubrique_id:
            for stage in po.rubrique_id.stage_ids:
                if stage.is_start:
                    start_id = stage.id
        default['internal_state']=start_id

        return super(purchase_order, self).copy(cr, uid, id, default, context=context)


    @api.multi
    def first_validation(self):
        if not self.rubrique_id:
            return
        end_id = False
        for stage in self.rubrique_id.stage_ids:
            if stage.is_end:
                end_id = stage.id
        self.internal_state=end_id

    @api.onchange('rubrique_id')
    def get_selection(self):
        rubrique = self.rubrique_id
        ids = []
        start_id = False
        for stage in rubrique.stage_ids:
            ids.append(stage.id)
            if stage.is_start:
                start_id = stage.id
        ids = [x.id for x in rubrique.stage_ids]
        domain=[('id','in',tuple(ids))]
        self.internal_state = start_id
        return {'domain':{'internal_state':domain}}



purchase_order()

class purchase_order_stage(osv.osv):

    _name = "purchase.order.stage"

    _order = 'sequence asc'

    name = fields.Char(string="Libellé", required=True)
    is_start = fields.Boolean(string="Début ?")
    is_end = fields.Boolean(string="Fin ?")
    sequence = fields.Integer(string="Sequence", required=True)
    rubrique_ids = fields.Many2many(comodel_name="rubrique.rubrique", relation="rubrique_stage_rel", column1="rubrique_id", column2="stage_id", string="Rubriques", )


purchase_order_stage()



