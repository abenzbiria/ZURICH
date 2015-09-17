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

    @api.onchange('department_id')
    def onchange_department_id(self):
        user_id = False
        if self.department_id:
            if self.department_id.manager_id:
                if self.department_id.manager_id.user_id:
                    user_id = self.department_id.manager_id.user_id.id
        self.responsible_id = user_id



class purchase_order(osv.osv):

    _inherit = "purchase.order"


    internal_state = fields.Many2one(string="Statut Interne", comodel_name="purchase.order.stage",domain="[('rubrique_ids','=',rubrique_id)]")
    rubrique_id = fields.Many2one(comodel_name="rubrique.rubrique", string="Rubrique")


    def wkf_confirm_order(self, cr, uid, ids, context=None):
        todo = []
        for po in self.browse(cr, uid, ids, context=context):
            if not any(line.state != 'cancel' for line in po.order_line):
                raise osv.except_osv(_('Error!'),_('You cannot confirm a purchase order without any purchase order line.'))
            if po.invoice_method == 'picking' and not any([l.product_id and l.product_id.type in ('product', 'consu') and l.state != 'cancel' for l in po.order_line]):
                raise osv.except_osv(
                    _('Error!'),
                    _("You cannot confirm a purchase order with Invoice Control Method 'Based on incoming shipments' that doesn't contain any stockable item."))
            for line in po.order_line:
                if line.state=='draft':
                    todo.append(line.id)
            ######################KAZACUBE##################
            stage_ids = po.rubrique_id and po.rubrique_id.stage_ids or False
            #raise osv.except_osv(_("jjjjjjjj"),_("%s")%stage_ids)
            print "11111111111111111111111"

            ####################FIN KAZACUBE###################"
        self.pool.get('purchase.order.line').action_confirm(cr, uid, todo, context)
        for id in ids:
            self.write(cr, uid, [id], {'state' : 'confirmed', 'validator' : uid})
        return True

    def wkf_approve_order(self, cr, uid, ids, context=None):
        print "22222222222222222222222222"
        from openerp.osv import fields, osv
        self.write(cr, uid, ids, {'state': 'approved', 'date_approve': fields.date.context_today(self,cr,uid,context=context)})
        return True

    #def first_validate_order(self):


    @api.onchange('rubrique_id')
    def get_selection(self):
        rubrique = self.rubrique_id
        ids = [x.id for x in rubrique.stage_ids]
        domain=[('id','in',tuple(ids))]
        return {'domain':{'internal_state':domain}}
purchase_order()

class purchase_order_stage(osv.osv):

    _name = "purchase.order.stage"

    _order = 'sequence asc'

    name = fields.Char(string="Libellé", required=True)
    code = fields.Char(string="code", required=True)
    sequence = fields.Integer(string="Sequence", required=True)
    rubrique_ids = fields.Many2many(comodel_name="rubrique.rubrique", relation="rubrique_stage_rel", column1="rubrique_id", column2="stage_id", string="Rubriques", )


purchase_order_stage()



