{
    'name': 'Hide Out of Stock Products',
    'version': '18.0.1.0.8',
    'category': 'Website/Website',
    'summary': 'Hide out-of-stock products from e-commerce website with smart filtering',
    'description': """
Hide Out of Stock Products
==========================

Este addon permite ocultar productos agotados del sitio web de comercio electrónico de Odoo.

Características principales:
* Oculta automáticamente productos sin stock del sitio web
* Prioriza ocultar productos agotados por más de 10 meses
* Configuración flexible para diferentes estrategias de ocultación
* Panel de administración para gestionar la funcionalidad
* Logs detallados para seguimiento del comportamiento
* Compatible con múltiples sitios web

Funcionalidades:
- Filtrado inteligente por tiempo sin stock
- Configuración por sitio web
- Excepciones para productos específicos
- Reportes de productos ocultos
- Automatización programable
    """,
    'author': 'Tu Empresa',
    'website': 'https://www.tuempresa.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'website',
        'website_sale',
        'stock',
        'product',
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
        'views/hide_stock_config_views.xml',
        'views/product_template_views.xml',
        'views/website_sale_templates.xml',
        'data/cron_data.xml',
    ],
    'demo': [],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 100,
    'external_dependencies': {
        'python': [],
    },
}
