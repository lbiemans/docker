
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from tools.translate import _
import time
import decimal_precision as dp

class stock_partial_picking(osv.osv_memory):
    _name = "stock.partial.picking"
    _description = "Partial Picking"
    _columns = {
        'date': fields.datetime('Date', required=True),
        'product_moves_out' : fields.one2many('stock.move.memory.out', 'wizard_pick_id', 'Moves'),
        'product_moves_in' : fields.one2many('stock.move.memory.in', 'wizard_pick_id', 'Moves'),
     }

    def get_picking_type(self, cr, uid, picking, context=None):
        picking_type = picking.type
        for move in picking.move_lines:
            if picking.type == 'in' and move.product_id.cost_method == 'average':
                picking_type = 'in'
                break
            else:
                picking_type = 'out'
        return picking_type

    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}

        pick_obj = self.pool.get('stock.picking')
        res = super(stock_partial_picking, self).default_get(cr, uid, fields, context=context)
        picking_ids = context.get('active_ids', [])
        if not picking_ids:
            return res

        result = []
        for pick in pick_obj.browse(cr, uid, picking_ids, context=context):
            pick_type = self.get_picking_type(cr, uid, pick, context=context)
            for m in pick.move_lines:
                if m.state in ('done', 'cancel'):
                    continue
                result.append(self.__create_partial_picking_memory(m, pick_type))

        if 'product_moves_in' in fields:
            res.update({'product_moves_in': result})
        if 'product_moves_out' in fields:
            res.update({'product_moves_out': result})
        if 'date' in fields:
            res.update({'date': time.strftime('%Y-%m-%d %H:%M:%S')})
        return res

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        result = super(stock_partial_picking, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)

        pick_obj = self.pool.get('stock.picking')
        picking_ids = context.get('active_ids', False)

        if not picking_ids:
            # not called through an action (e.g. buildbot), return the default.
            return result

        for pick in pick_obj.browse(cr, uid, picking_ids, context=context):
            picking_type = self.get_picking_type(cr, uid, pick, context=context)

        _moves_arch_lst = """<form string="%s">
                        <field name="date" invisible="1"/>
                        <separator colspan="4" string="%s"/>
                        <field name="%s" colspan="4" nolabel="1" mode="tree,form" width="550" height="200" ></field>
                        """ % (_('Process Document'), _('Products'), "product_moves_" + picking_type)
        _moves_fields = result['fields']

        # add field related to picking type only
        _moves_fields.update({
                            'product_moves_' + picking_type: {'relation': 'stock.move.memory.'+picking_type, 'type' : 'one2many', 'string' : 'Product Moves'},
                            })

        _moves_arch_lst += """
                <separator string="" colspan="4" />
                <label string="" colspan="2"/>
                <group col="2" colspan="2">
                <button icon='gtk-cancel' special="cancel"
                    string="_Cancel" />
                <button name="do_partial" string="_Validate"
                    colspan="1" type="object" icon="gtk-go-forward" />
            </group>
        </form>"""
        result['arch'] = _moves_arch_lst
        result['fields'] = _moves_fields
        return result

    def __create_partial_picking_memory(self, move, pick_type):
        move_memory = {
            'product_id' : move.product_id.id,
            'quantity' : move.product_qty,
            'product_uom' : move.product_uom.id,
            'prodlot_id' : move.prodlot_id.id,
            'move_id' : move.id,
        }

        if pick_type == 'in':
            move_memory.update({
                'cost' : move.product_id.standard_price,
                'currency' : move.product_id.company_id and move.product_id.company_id.currency_id.id or False,
            })
        return move_memory

    def do_partial(self, cr, uid, ids, context=None):
        """ Makes partial moves and pickings done.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for which we want default values
        @param context: A standard dictionary
        @return: A dictionary which of fields with values.
        """
        pick_obj = self.pool.get('stock.picking')
        uom_obj = self.pool.get('product.uom')

        picking_ids = context.get('active_ids', False)
        partial = self.browse(cr, uid, ids[0], context=context)
        partial_datas = {
            'delivery_date' : partial.date
        }

        for pick in pick_obj.browse(cr, uid, picking_ids, context=context):
            picking_type = self.get_picking_type(cr, uid, pick, context=context)
            moves_list = picking_type == 'in' and partial.product_moves_in or partial.product_moves_out

            for move in moves_list:

                #Adding a check whether any line has been added with new qty
                if not move.move_id:
                    raise osv.except_osv(_('Processing Error'),\
                    _('You cannot add any new move while validating the picking, rather you can split the lines prior to validation!'))

                calc_qty = uom_obj._compute_qty(cr, uid, move.product_uom.id, \
                                    move.quantity, move.move_id.product_uom.id)

                #Adding a check whether any move line contains exceeding qty to original moveline
                if calc_qty > move.move_id.product_qty:
                    precision = '%0.' + str(dp.get_precision('Product UoM')(cr)[1] or 0) + 'f'
                    raise osv.except_osv(_('Processing Error'),
                    _('Processing quantity %s %s for %s is larger than the available quantity %s %s !')\
                    % (precision % calc_qty, move.product_uom.name, move.product_id.name,\
                       precision % move.move_id.product_qty, move.move_id.product_uom.name))

                #Adding a check whether any move line contains qty less than zero
                if calc_qty < 0:
                    precision = '%0.' + str(dp.get_precision('Product UoM')(cr)[1] or 0) + 'f'
                    raise osv.except_osv(_('Processing Error'), \
                            _('Can not process quantity %s for Product %s !') \
                            % (precision % move.quantity, move.product_id.name))

                partial_datas['move%s' % (move.move_id.id)] = {
                    'product_id': move.product_id.id,
                    'product_qty': calc_qty,
                    'product_uom': move.move_id.product_uom.id,
                    'prodlot_id': move.prodlot_id.id,
                }
                if (picking_type == 'in') and (move.product_id.cost_method == 'average'):
                    partial_datas['move%s' % (move.move_id.id)].update({
                                                    'product_price' : move.cost,
                                                    'product_currency': move.currency.id,
                                                    })
        pick_obj.do_partial(cr, uid, picking_ids, partial_datas, context=context)
        return {'type': 'ir.actions.act_window_close'}

stock_partial_picking()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
