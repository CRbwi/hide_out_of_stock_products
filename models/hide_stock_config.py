# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HideStockConfig(models.Model):
    _name = 'hide.stock.config'
    _description = 'Configuración para Ocultar Productos Sin Stock'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'website_id'

    website_id = fields.Many2one(
        'website',
        string='Sitio Web',
        required=True,
        default=lambda self: self.env['website'].get_current_website(),
        help='Sitio web donde aplicar la configuración'
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True,
        tracking=True,
        help='Si está activo, se aplicará la ocultación de productos'
    )
    
    hide_strategy = fields.Selection([
        ('all_out_of_stock', 'Todos los productos sin stock'),
        ('smart_time_based', 'Inteligente basado en tiempo'),
        ('custom_days', 'Personalizado por días'),
    ], 
        string='Estrategia de Ocultación',
        default='smart_time_based',
        required=True,
        tracking=True,
        help='Estrategia para decidir qué productos ocultar'
    )
    
    smart_days_threshold = fields.Integer(
        string='Días para Estrategia Inteligente',
        default=300,  # ~10 meses
        tracking=True,
        help='Días sin stock para la estrategia inteligente (por defecto 300 días = 10 meses)'
    )
    
    custom_days_threshold = fields.Integer(
        string='Días Sin Stock para Ocultar',
        default=300,  # ~10 meses
        tracking=True,
        help='Número de días sin stock después de los cuales ocultar el producto'
    )
    
    hide_completely = fields.Boolean(
        string='Ocultar Completamente',
        default=True,
        tracking=True,
        help='Si está marcado, los productos se ocultan completamente. Si no, solo se marcan como no disponibles'
    )
    
    show_notification = fields.Boolean(
        string='Mostrar Notificación "Agotado"',
        default=False,
        help='Mostrar mensaje de "Producto agotado" en lugar de ocultar completamente'
    )
    
    exclude_product_ids = fields.Many2many(
        'product.template',
        string='Productos Excluidos',
        help='Productos que NUNCA se ocultarán, sin importar su stock'
    )
    
    exclude_category_ids = fields.Many2many(
        'product.category',
        string='Categorías Excluidas',
        help='Categorías de productos que no se ocultarán'
    )
    
    auto_update = fields.Boolean(
        string='Actualización Automática',
        default=True,
        help='Actualizar automáticamente la visibilidad de productos cada día'
    )
    
    last_update = fields.Datetime(
        string='Última Actualización',
        readonly=True,
        help='Última vez que se ejecutó la actualización automática'
    )
    
    products_hidden_count = fields.Integer(
        string='Productos Ocultos',
        compute='_compute_hidden_products_count',
        help='Número de productos actualmente ocultos'
    )
    
    log_changes = fields.Boolean(
        string='Registrar Cambios',
        default=True,
        help='Mantener log de los cambios de visibilidad'
    )

    @api.depends('website_id')
    def _compute_hidden_products_count(self):
        """Calcula el número de productos actualmente ocultos"""
        for config in self:
            hidden_products = self.env['product.template'].search([
                ('website_published', '=', False),
                ('is_hidden_by_stock', '=', True),
                ('website_id', 'in', [False, config.website_id.id])
            ])
            config.products_hidden_count = len(hidden_products)

    def action_update_product_visibility(self):
        """Acción manual para actualizar la visibilidad de productos"""
        self.ensure_one()
        return self._update_products_visibility()

    def _update_products_visibility(self):
        """Método principal para actualizar la visibilidad de productos"""
        _logger.info(f"Iniciando actualización de visibilidad para sitio web: {self.website_id.name}")
        
        if not self.active:
            _logger.info("Configuración inactiva, saltando actualización")
            return False
        
        # Obtener productos candidatos para ocultar
        products_to_evaluate = self._get_products_to_evaluate()
        _logger.info(f"Productos a evaluar: {len(products_to_evaluate)}")
        
        # Evaluar cada producto
        hidden_count = 0
        shown_count = 0
        
        for product in products_to_evaluate:
            should_hide = self._should_hide_product(product)
            
            if should_hide and not product.is_hidden_by_stock:
                # Ocultar producto
                self._hide_product(product)
                hidden_count += 1
            elif not should_hide and product.is_hidden_by_stock:
                # Mostrar producto
                self._show_product(product)
                shown_count += 1
        
        # Actualizar timestamp
        self.last_update = fields.Datetime.now()
        
        _logger.info(f"Actualización completada: {hidden_count} productos ocultos, {shown_count} productos mostrados")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Actualización Completada'),
                'message': _('Se procesaron %s productos. %s ocultos, %s mostrados.') % (
                    len(products_to_evaluate), hidden_count, shown_count
                ),
                'sticky': True,
                'type': 'success',
            }
        }

    def _get_products_to_evaluate(self):
        """Obtiene los productos que deben ser evaluados para ocultación"""
        domain = [
            ('sale_ok', '=', True),  # Solo productos vendibles
        ]
        
        # Excluir productos específicos
        if self.exclude_product_ids:
            domain.append(('id', 'not in', self.exclude_product_ids.ids))
        
        # Excluir categorías específicas
        if self.exclude_category_ids:
            domain.append(('categ_id', 'not in', self.exclude_category_ids.ids))
        
        return self.env['product.template'].search(domain)

    def _should_hide_product(self, product):
        """Determina si un producto debe ser ocultado basado en la estrategia configurada"""
        
        # Verificar stock actual
        total_qty = sum(product.product_variant_ids.mapped('qty_available'))
        
        if total_qty > 0:
            # Tiene stock, no ocultar
            return False
        
        if self.hide_strategy == 'all_out_of_stock':
            # Ocultar todos los productos sin stock
            return True
        
        elif self.hide_strategy == 'smart_time_based':
            # Ocultar productos sin stock por el tiempo configurado en estrategia inteligente
            return self._product_out_of_stock_for_days(product) >= self.smart_days_threshold
        
        elif self.hide_strategy == 'custom_days':
            # Ocultar productos sin stock por los días configurados
            return self._product_out_of_stock_for_days(product) >= self.custom_days_threshold
        
        return False

    def _product_out_of_stock_for_days(self, product):
        """Calcula cuántos días lleva un producto sin stock"""
        
        # Buscar el último movimiento de stock positivo
        last_positive_move = self.env['stock.move'].search([
            ('product_id', 'in', product.product_variant_ids.ids),
            ('state', '=', 'done'),
            ('location_dest_id.usage', '=', 'internal'),  # Movimientos hacia ubicaciones internas
        ], order='date desc', limit=1)
        
        if not last_positive_move:
            # Si no hay movimientos, asumir que lleva mucho tiempo sin stock
            return 999  # Valor alto para asegurar que se oculte
        
        # Calcular días desde el último movimiento positivo
        # Convertir datetime a date para la comparación
        last_stock_date = last_positive_move.date.date() if hasattr(last_positive_move.date, 'date') else last_positive_move.date
        today = fields.Date.today()
        days_difference = (today - last_stock_date).days
        
        return max(0, days_difference)

    def _hide_product(self, product):
        """Oculta un producto del sitio web"""
        if self.hide_completely:
            product.write({
                'website_published': False,
                'is_hidden_by_stock': True
            })
        else:
            product.write({
                'is_hidden_by_stock': True
            })
        
        if self.log_changes:
            _logger.info(f"Producto oculto: {product.name} (ID: {product.id}) - Sin stock por {self._product_out_of_stock_for_days(product)} días")

    def _show_product(self, product):
        """Muestra un producto en el sitio web"""
        product.write({
            'website_published': True,
            'is_hidden_by_stock': False
        })
        
        if self.log_changes:
            _logger.info(f"Producto mostrado: {product.name} (ID: {product.id}) - Tiene stock disponible")

    def action_view_hidden_products(self):
        """Acción para ver los productos actualmente ocultos"""
        self.ensure_one()
        
        hidden_products = self.env['product.template'].search([
            ('is_hidden_by_stock', '=', True),
        ])
        
        return {
            'name': _('Productos Ocultos por Stock'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', hidden_products.ids)],
            'context': {'default_is_hidden_by_stock': True},
        }

    def action_restore_all_products(self):
        """Acción para restaurar todos los productos ocultos"""
        self.ensure_one()
        
        hidden_products = self.env['product.template'].search([
            ('is_hidden_by_stock', '=', True),
        ])
        
        for product in hidden_products:
            self._show_product(product)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Productos Restaurados'),
                'message': _('Se restauraron %s productos ocultos.') % len(hidden_products),
                'sticky': True,
                'type': 'success',
            }
        }

    @api.model
    def cron_update_all_websites(self):
        """Método para cron que actualiza todos los sitios web configurados"""
        configs = self.search([('active', '=', True), ('auto_update', '=', True)])
        
        for config in configs:
            try:
                config._update_products_visibility()
            except Exception as e:
                _logger.error(f"Error actualizando visibilidad para {config.website_id.name}: {e}")

    def action_run_analysis(self):
        """Ejecuta un análisis detallado de productos sin stock"""
        self.ensure_one()
        
        _logger.info("=== ANÁLISIS DE PRODUCTOS SIN STOCK ===")
        
        products = self._get_products_to_evaluate()
        analysis_results = {
            'total_products': len(products),
            'out_of_stock': 0,
            'out_of_stock_10_months': 0,
            'in_stock': 0,
            'would_hide': 0,
        }
        
        for product in products:
            total_qty = sum(product.product_variant_ids.mapped('qty_available'))
            days_out_of_stock = self._product_out_of_stock_for_days(product)
            
            if total_qty <= 0:
                analysis_results['out_of_stock'] += 1
                if days_out_of_stock >= 300:  # ~10 meses
                    analysis_results['out_of_stock_10_months'] += 1
            else:
                analysis_results['in_stock'] += 1
            
            if self._should_hide_product(product):
                analysis_results['would_hide'] += 1
        
        _logger.info(f"Productos totales: {analysis_results['total_products']}")
        _logger.info(f"Productos sin stock: {analysis_results['out_of_stock']}")
        _logger.info(f"Productos sin stock >10 meses: {analysis_results['out_of_stock_10_months']}")
        _logger.info(f"Productos con stock: {analysis_results['in_stock']}")
        _logger.info(f"Productos que se ocultarían: {analysis_results['would_hide']}")
        
        message = _("""Análisis completado:

• Total de productos: %s
• Productos sin stock: %s
• Sin stock >10 meses: %s
• Productos con stock: %s
• Se ocultarían: %s

Revisa los logs para más detalles.""") % (
            analysis_results['total_products'],
            analysis_results['out_of_stock'],
            analysis_results['out_of_stock_10_months'],
            analysis_results['in_stock'],
            analysis_results['would_hide']
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Análisis de Stock Completado'),
                'message': message,
                'sticky': True,
                'type': 'info',
            }
        }
