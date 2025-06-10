# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_hidden_by_stock = fields.Boolean(
        string='Oculto por Stock',
        default=False,
        help='Indica si este producto está oculto automáticamente por falta de stock'
    )
    
    stock_hide_date = fields.Datetime(
        string='Fecha de Ocultación por Stock',
        help='Fecha en que se ocultó este producto por falta de stock'
    )
    
    days_out_of_stock = fields.Integer(
        string='Días Sin Stock',
        compute='_compute_days_out_of_stock',
        help='Número de días que lleva este producto sin stock'
    )
    
    last_stock_move_date = fields.Datetime(
        string='Último Movimiento de Stock',
        compute='_compute_last_stock_move',
        help='Fecha del último movimiento de stock positivo'
    )

    @api.depends('product_variant_ids')
    def _compute_days_out_of_stock(self):
        """Calcula los días que lleva sin stock"""
        for product in self:
            days = 0
            
            try:
                # Verificar si tiene stock actual
                total_qty = sum(product.product_variant_ids.mapped('qty_available'))
                
                if total_qty <= 0:
                    # Buscar el último movimiento positivo
                    last_positive_move = self.env['stock.move'].sudo().search([
                        ('product_id', 'in', product.product_variant_ids.ids),
                        ('state', '=', 'done'),
                        ('location_dest_id.usage', '=', 'internal'),
                    ], order='date desc', limit=1)
                    
                    if last_positive_move:
                        days = (fields.Date.today() - last_positive_move.date).days
                    else:
                        days = 999  # Producto sin movimientos recientes
                
                product.days_out_of_stock = max(0, days)
            except Exception as e:
                _logger.warning(f"Error calculando días sin stock para producto {product.id}: {e}")
                product.days_out_of_stock = 0

    @api.depends('product_variant_ids')
    def _compute_last_stock_move(self):
        """Calcula la fecha del último movimiento de stock"""
        for product in self:
            try:
                last_move = self.env['stock.move'].sudo().search([
                    ('product_id', 'in', product.product_variant_ids.ids),
                    ('state', '=', 'done'),
                    ('location_dest_id.usage', '=', 'internal'),
                ], order='date desc', limit=1)
                
                product.last_stock_move_date = last_move.date if last_move else False
            except Exception as e:
                _logger.warning(f"Error calculando último movimiento para producto {product.id}: {e}")
                product.last_stock_move_date = False

    def action_force_show_on_website(self):
        """Acción para forzar mostrar el producto en el sitio web"""
        for product in self:
            product.write({
                'website_published': True,
                'is_hidden_by_stock': False,
                'stock_hide_date': False
            })
            _logger.info(f"Producto {product.name} forzado a mostrarse en sitio web")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Producto Mostrado'),
                'message': _('El producto ahora es visible en el sitio web.'),
                'type': 'success',
            }
        }

    def action_force_hide_from_website(self):
        """Acción para forzar ocultar el producto del sitio web"""
        for product in self:
            product.write({
                'website_published': False,
                'is_hidden_by_stock': True,
                'stock_hide_date': fields.Datetime.now()
            })
            _logger.info(f"Producto {product.name} forzado a ocultarse del sitio web")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Producto Oculto'),
                'message': _('El producto ahora está oculto del sitio web.'),
                'type': 'success',
            }
        }

    @api.model
    def get_stock_analysis_data(self):
        """Obtiene datos de análisis de stock para dashboard"""
        
        total_products = self.search_count([('sale_ok', '=', True)])
        
        # Productos sin stock
        out_of_stock = self.search_count([
            ('sale_ok', '=', True),
            ('qty_available', '<=', 0)
        ])
        
        # Productos ocultos por stock
        hidden_by_stock = self.search_count([
            ('is_hidden_by_stock', '=', True)
        ])
        
        # Productos sin stock por más de 10 meses (aproximado)
        long_out_of_stock = self.search_count([
            ('sale_ok', '=', True),
            ('qty_available', '<=', 0),
            ('days_out_of_stock', '>=', 300)
        ])
        
        return {
            'total_products': total_products,
            'out_of_stock': out_of_stock,
            'hidden_by_stock': hidden_by_stock,
            'long_out_of_stock': long_out_of_stock,
            'in_stock': total_products - out_of_stock,
        }

    def write(self, vals):
        """Override write para trackear cambios de visibilidad"""
        result = super().write(vals)
        
        # Si se está ocultando por stock, registrar la fecha
        if vals.get('is_hidden_by_stock') and not vals.get('stock_hide_date'):
            self.write({'stock_hide_date': fields.Datetime.now()})
        
        # Si se está mostrando, limpiar fecha de ocultación
        if vals.get('website_published') and vals.get('is_hidden_by_stock') == False:
            self.write({'stock_hide_date': False})
        
        return result
