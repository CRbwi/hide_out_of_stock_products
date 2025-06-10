# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api
from odoo.http import request

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    def sale_product_domain(self):
        """Extiende el dominio de productos para ocultar productos sin stock"""
        domain = super().sale_product_domain()
        
        try:
            # Obtener configuración para este sitio web
            config = self.env['hide.stock.config'].sudo().search([
                ('website_id', '=', self.id),
                ('active', '=', True)
            ], limit=1)
            
            if config and config.hide_completely:
                # Agregar filtro para excluir productos ocultos por stock
                domain.append(('is_hidden_by_stock', '=', False))
                _logger.debug(f"Aplicando filtro de stock para sitio web {self.name}")
        except Exception as e:
            _logger.warning(f"Error aplicando filtro de stock en sale_product_domain: {e}")
        
        return domain


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    def _get_products_domain(self):
        """Extiende el dominio de productos en categorías para ocultar productos sin stock"""
        domain = super()._get_products_domain()
        
        try:
            # Obtener sitio web actual
            website = self.env['website'].get_current_website()
            
            # Obtener configuración para este sitio web
            config = self.env['hide.stock.config'].sudo().search([
                ('website_id', '=', website.id),
                ('active', '=', True)
            ], limit=1)
            
            if config and config.hide_completely:
                # Agregar filtro para excluir productos ocultos por stock
                domain.append(('is_hidden_by_stock', '=', False))
                _logger.debug(f"Aplicando filtro de stock en categoría para sitio web {website.name}")
        except Exception as e:
            _logger.warning(f"Error aplicando filtro de stock en _get_products_domain: {e}")
        
        return domain


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _is_published(self):
        """Override para considerar productos ocultos por stock"""
        result = super()._is_published()
        
        # Si ya no está publicado, no hay que hacer nada más
        if not result:
            return result
        
        try:
            # Verificar si está oculto por stock
            if self.is_hidden_by_stock:
                website = self.env['website'].get_current_website()
                config = self.env['hide.stock.config'].sudo().search([
                    ('website_id', '=', website.id),
                    ('active', '=', True)
                ], limit=1)
                
                if config and config.hide_completely:
                    return False
        except Exception as e:
            _logger.warning(f"Error verificando estado publicado para producto {self.id}: {e}")
        
        return result

    def _get_website_sale_extra_domain(self):
        """Dominio extra para website sale"""
        domain = super()._get_website_sale_extra_domain() if hasattr(super(), '_get_website_sale_extra_domain') else []
        
        try:
            # Obtener sitio web actual
            website = self.env['website'].get_current_website()
            
            # Obtener configuración para este sitio web
            config = self.env['hide.stock.config'].sudo().search([
                ('website_id', '=', website.id),
                ('active', '=', True)
            ], limit=1)
            
            if config and config.hide_completely:
                domain.append(('is_hidden_by_stock', '=', False))
        except Exception as e:
            _logger.warning(f"Error aplicando dominio extra de website sale: {e}")
        
        return domain
