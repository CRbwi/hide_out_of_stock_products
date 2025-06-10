# Hide Out of Stock Products - Addon para Odoo

Este addon permite ocultar automáticamente productos sin stock del sitio web de comercio electrónico de Odoo, con funcionalidad inteligente para priorizar productos que llevan más tiempo agotados.

## 🎯 Características Principales

### Estrategias de Ocultación
- **Todos los productos sin stock**: Oculta inmediatamente cualquier producto con stock 0
- **Inteligente basado en tiempo**: Solo oculta productos agotados por más de 10 meses  
- **Personalizado por días**: Configura el número exacto de días sin stock

### Funcionalidades Avanzadas
- ✅ Configuración por sitio web (multi-website)
- ✅ Excepciones para productos específicos
- ✅ Excepciones para categorías completas
- ✅ Automatización programada (cron diario)
- ✅ Dashboard con estadísticas
- ✅ Logs detallados de cambios
- ✅ Opciones de mostrar vs ocultar completamente

## 🚀 Instalación

1. Copia la carpeta `hide_out_of_stock_products` a tu directorio de addons
2. Actualiza la lista de aplicaciones en Odoo
3. Instala el addon "Hide Out of Stock Products"

## ⚙️ Configuración

### Configuración Básica
1. Ve a **Sitio Web > Configuración > Ocultar Sin Stock > Configuración de Ocultación**
2. Crea una nueva configuración para tu sitio web
3. Selecciona la estrategia deseada:
   - **Inteligente (Recomendado)**: Solo oculta productos sin stock por 10+ meses
   - **Todos**: Oculta inmediatamente productos sin stock
   - **Personalizado**: Define tus propios días

### Configuración Avanzada
- **Excepciones**: Productos o categorías que nunca se ocultarán
- **Comportamiento**: Ocultar completamente vs mostrar como "agotado"
- **Automatización**: Activar/desactivar actualización automática diaria

## 📊 Dashboard y Monitoreo

### Ver Estadísticas
- Total de productos
- Productos con stock
- Productos sin stock  
- Productos actualmente ocultos

### Gestión de Productos Ocultos
- Lista de productos ocultos con fechas
- Botones para mostrar/ocultar productos individuales
- Restauración masiva de productos

## 🔄 Automatización

### Cron Job Automático
- Se ejecuta diariamente a las 2:00 AM
- Evalúa todos los productos según la configuración
- Oculta/muestra productos automáticamente
- Registra todos los cambios en logs

### Ejecución Manual
- Botón "Actualizar Ahora" en la configuración
- Análisis sin cambios con "Ejecutar Análisis"

## 🎛️ Casos de Uso

### Tienda con Muchos Productos Descontinuados
```
Estrategia: Inteligente basado en tiempo
Días: 300 (10 meses)
Ocultar: Completamente
Automatización: Activa
```

### Tienda con Stock Dinámico
```
Estrategia: Personalizado por días  
Días: 30-60
Ocultar: Mostrar como agotado
Automatización: Activa
```

### Tienda con Productos Estacionales
```
Estrategia: Todos los productos sin stock
Excepciones: Categoría "Productos Estacionales"
Ocultar: Completamente
```

## 🔧 Funcionalidades Técnicas

### Campos Agregados a Productos
- `is_hidden_by_stock`: Boolean que indica si está oculto
- `stock_hide_date`: Fecha cuando se ocultó
- `days_out_of_stock`: Días calculados sin stock
- `last_stock_move_date`: Último movimiento de entrada

### Integración con Website Sale
- Filtrado automático en listados de productos
- Modificación de dominios de búsqueda
- Templates personalizados para productos agotados

## 📝 Logs y Seguimiento

El addon registra automáticamente:
- Productos que se ocultan/muestran
- Fechas y motivos de los cambios
- Estadísticas de ejecución del cron
- Errores y advertencias

## 🛠️ Desarrollo y Personalización

### Métodos Principales
- `_should_hide_product()`: Lógica de decisión
- `_product_out_of_stock_for_days()`: Cálculo de días sin stock
- `_update_products_visibility()`: Proceso principal de actualización

### Hooks de Extensión
- Override `_get_products_to_evaluate()` para filtros personalizados
- Extend `_should_hide_product()` para lógica adicional
- Modify templates para UI personalizada

## 🎨 Interfaz de Usuario

### Vistas Administrativas
- Configuración con wizard intuitivo
- Dashboard con métricas en tiempo real
- Lista de productos ocultos con acciones rápidas

### Frontend Web
- Productos ocultos no aparecen en listados
- Mensajes informativos para administradores
- Botones deshabilitados para productos agotados

## ⚡ Optimización y Rendimiento

### Estrategias de Rendimiento
- Cálculos en lotes para grandes catálogos
- Caché de resultados de stock
- Filtrado eficiente en base de datos
- Logs configurables para evitar spam

### Recomendaciones
- Usar estrategia "inteligente" para catálogos grandes
- Configurar excepciones para reducir procesamiento
- Monitorear logs para identificar productos problemáticos

## 🔒 Seguridad

### Permisos
- **Usuarios**: Solo lectura de configuraciones
- **Diseñadores Web**: Gestión completa
- **Administradores**: Acceso total

### Validaciones
- Verificación de sitios web válidos
- Prevención de configuraciones conflictivas
- Logs de seguridad para cambios importantes

## 📞 Soporte

Para soporte técnico o personalizaciones:
- Revisa los logs de Odoo para errores
- Usa el botón "Ejecutar Análisis" para diagnosticar
- Verifica configuraciones de stock en productos

---

**Versión**: 18.0.1.0.0  
**Compatibilidad**: Odoo 18.0+  
**Licencia**: LGPL-3
