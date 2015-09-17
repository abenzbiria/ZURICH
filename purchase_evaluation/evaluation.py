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


class purchase_order_evaluation(osv.osv):
    _name = 'purchase.order.evaluation'

    _columns = {
        'evaluation_id':fields.many2one('purchase.evaluation','Evaluation'),
        'purchase_id':fields.many2one('purchase.order','Bon commande'),
        'note':fields.integer('Note'),

    }

purchase_order_evaluation()


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


class purchase_order(osv.osv):
    _inherit = 'purchase.order'

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        todo = []
        for po in self.browse(cr, uid, ids, context=context):
            if not po.order_line:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a purchase order without any purchase order line.'))
            if po.invoice_method == 'picking' and not any([l.product_id and l.product_id.type in ('product', 'consu') for l in po.order_line]):
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
            for eval in po.evaluation_ids:
                if eval.note<0 or eval.note>10:
                    raise osv.except_osv(_('Error!'),_('Note de critère non autorisé (note comprise entre 0 et 10) .'))

            res_eval_obj=self.pool.get('res.partner.evaluation')
            res_obj=self.pool.get('res.partner')
            vals={}
            j=[]
            for eval in po.evaluation_ids:
                if po.partner_id.evaluation_ids:
                    for eval_par in po.partner_id.evaluation_ids:
                        if  eval_par.evaluation_id.id==eval.evaluation_id.id :
                            res_eval_obj.write(cr,uid,eval_par.id,{'note':(eval_par.note+eval.note)/2})
                        else:
                            vals['partner_id']=po.partner_id.id
                            vals['evaluation_id']=eval.evaluation_id.id
                            vals['note']=eval.note
                            res_eval_obj.create(cr,uid,vals)

                else:
                    vals['partner_id']=po.partner_id.id
                    vals['evaluation_id']=eval.evaluation_id.id
                    vals['note']=eval.note
                    res_eval_obj.create(cr,uid,vals)

        self.pool.get('purchase.order.line').action_confirm(cr, uid, todo, context)
        for id in ids:
            self.write(cr, uid, [id], {'state' : 'confirmed', 'validator' : uid})

        return True

    _columns = {
        'evaluation_ids':fields.one2many('purchase.order.evaluation', 'purchase_id', "Lignes d'évaluation"),


                }


purchase_order()