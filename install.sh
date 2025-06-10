#!/bin/bash

# Script de instalación rápida para Hide Out of Stock Products
# Uso: ./install.sh

echo "🚀 Instalando Hide Out of Stock Products..."

# Verificar si estamos en el directorio correcto
if [ ! -f "__manifest__.py" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio del addon"
    exit 1
fi

echo "📋 Verificando estructura del addon..."

# Verificar archivos principales
required_files=(
    "__manifest__.py"
    "__init__.py"
    "models/__init__.py"
    "models/hide_stock_config.py"
    "models/product_template.py"
    "models/website_sale.py"
    "views/hide_stock_config_views.xml"
    "views/product_template_views.xml"
    "views/website_sale_templates.xml"
    "security/ir.model.access.csv"
    "data/cron_data.xml"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "❌ Archivos faltantes:"
    printf '%s\n' "${missing_files[@]}"
    exit 1
fi

echo "✅ Estructura del addon verificada"

# Verificar permisos
echo "📝 Verificando permisos..."
find . -name "*.py" -exec chmod +x {} \;
find . -name "*.xml" -exec chmod 644 {} \;

echo "🔄 Reiniciando Odoo..."

# Buscar docker-compose en directorios padre
compose_file=""
current_dir=$(pwd)

while [ "$current_dir" != "/" ]; do
    if [ -f "$current_dir/docker-compose.yml" ]; then
        compose_file="$current_dir/docker-compose.yml"
        break
    fi
    current_dir=$(dirname "$current_dir")
done

if [ -n "$compose_file" ]; then
    echo "📦 Encontrado docker-compose en: $(dirname "$compose_file")"
    cd "$(dirname "$compose_file")"
    
    # Reiniciar Odoo
    docker-compose restart odoo
    
    echo "⏳ Esperando que Odoo se inicie..."
    sleep 10
    
    # Mostrar logs
    echo "📄 Logs de Odoo:"
    docker-compose logs --tail=20 odoo
    
else
    echo "⚠️ No se encontró docker-compose.yml"
    echo "   Reinicia Odoo manualmente"
fi

echo ""
echo "🎉 ¡Instalación completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Ve a Aplicaciones en Odoo"
echo "2. Actualiza la lista de aplicaciones"
echo "3. Busca 'Hide Out of Stock Products'"
echo "4. Instala el addon"
echo "5. Ve a Sitio Web > Configuración > Ocultar Sin Stock"
echo ""
echo "📚 Lee el README.md para más información"
