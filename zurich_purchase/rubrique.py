# -*- coding: utf-8 -*-
##############################################



from openerp.osv import  osv,fields
from openerp import models ,fields ,api, _
from openerp.tools.translate import _

class rubrique_rubrique(osv.osv):

    _name = "rubrique.rubrique"

    name = fields.Char(string="Libellé", required=True)
    parent_id = fields.Many2one(comodel_name="rubrique.rubrique", string="Parent" )
    stage_ids = fields.Many2many(comodel_name="purchase.order.stage", relation="rubrique_stage_rel", column1="stage_id", column2="rubrique_id", string="Status", )


rubrique_rubrique()
