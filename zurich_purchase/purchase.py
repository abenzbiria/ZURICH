# -*- coding: utf-8 -*-
##############################################



from openerp.osv import  osv,fields
from openerp import models ,fields ,api, _,exceptions
import time
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
            'rubrique_id':requisition.rubrique_id and requisition.rubrique_id.id or False,
            'budget_id':requisition.budget_id and requisition.budget_id.id or False,
            'department_id':requisition.department_id and requisition.department_id.id or False,
            'demandeur_id':requisition.user_id and requisition.user_id.id or False,
            'responsible_id':requisition.responsible_id and requisition.responsible_id.id or False,
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
            if po.internal_state and po.internal_state.is_start:
                raise osv.except_osv(_('Attention'),_("Cette demande de prix nécessite une validation interne"))
            ####################FIN KAZACUBE###################"
        self.pool.get('purchase.order.line').action_confirm(cr, uid, todo, context)
        for id in ids:
            self.write(cr, uid, [id], {'state' : 'confirmed', 'validator' : uid})
        return True

    @api.onchange('user_id')
    def onchange_user_id(self):
        department = False
        if self.user_id:
            user = self.user_id
            department_id = self.env['hr.employee'].search_read([('user_id','=',user.id)],['department_id'])
            if department_id:
                department = department_id[0]['department_id']
                if department:
                    department=department_id[0]['department_id'][0]
        self.department_id = department

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
            if ids:
                self.rubrique_id = ids[0]
            else:
                self.rubrique_id = False
            return {'domain':{'rubrique_id':domain}}

    _defaults = {
        'ordering_date':lambda *a: time.strftime('%Y-%m-%d'),
    }



class purchase_order(osv.osv):

    _inherit = "purchase.order"

    @api.multi
    @api.depends('state','internal_state')
    def get_is_visible(self):
        is_visible= False
        if self.state in ("draft","sent","bid") and self.internal_state.is_start:
            is_visible = True
        self.is_validate_visible = is_visible


    internal_state = fields.Many2one(string="Statut Interne", comodel_name="purchase.order.stage",domain="[('rubrique_ids','=',rubrique_id)]")
    budget_id = fields.Many2one(comodel_name="purchase.budget", string="Budget",states={'confirmed':[('readonly',True)],
                                                                 'approved':[('readonly',True)],
                                                                 'done':[('readonly',True)]})
    rubrique_id = fields.Many2one(comodel_name="rubrique.rubrique", string="Rubrique",states={'confirmed':[('readonly',True)],
                                                                 'approved':[('readonly',True)],
                                                                 'done':[('readonly',True)]})
    department_id = fields.Many2one(comodel_name="hr.department", string="Département",states={'confirmed':[('readonly',True)],
                                                                 'approved':[('readonly',True)],
                                                                 'done':[('readonly',True)]})
    responsible_id = fields.Many2one(string="Responsable Demande", comodel_name="res.users",states={'confirmed':[('readonly',True)],
                                                                 'approved':[('readonly',True)],
                                                                 'done':[('readonly',True)]})
    demandeur_id = fields.Many2one(string="Demandeur", comodel_name="res.users",states={'confirmed':[('readonly',True)],
                                                                 'approved':[('readonly',True)],
                                                                 'done':[('readonly',True)]})
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

    def _prepare_invoice(self, cr, uid, order, line_ids, context=None):
        """Prepare the dict of values to create the new invoice for a
           purchase order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: purchase.order record to invoice
           :param list(int) line_ids: list of invoice line IDs that must be
                                      attached to the invoice
           :return: dict of value to create() the invoice
        """
        journal_ids = self.pool['account.journal'].search(
                            cr, uid, [('type', '=', 'purchase'),
                                      ('company_id', '=', order.company_id.id)],
                            limit=1)
        if not journal_ids:
            raise osv.except_osv(
                _('Error!'),
                _('Define purchase journal for this company: "%s" (id:%d).') % \
                    (order.company_id.name, order.company_id.id))
        return {
            'name': order.partner_ref or order.name,
            'reference': order.partner_ref or order.name,
            'account_id': order.partner_id.property_account_payable.id,
            'type': 'in_invoice',
            'partner_id': order.partner_id.id,
            'currency_id': order.currency_id.id,
            'journal_id': len(journal_ids) and journal_ids[0] or False,
            'invoice_line': [(6, 0, line_ids)],
            'origin': order.name,
            'fiscal_position': order.fiscal_position.id or False,
            'payment_term': order.payment_term_id.id or False,
            'company_id': order.company_id.id,
            'rubrique_id':order.rubrique_id and order.rubrique_id.id or False,
            'budget_id':order.budget_id and order.budget_id.id or False,
            'department_id':order.department_id and order.department_id.id or False,
            'demandeur_id':order.demandeur_id and order.demandeur_id.id or False,
            'responsible_id':order.responsible_id and order.responsible_id.id or False,
        }



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



