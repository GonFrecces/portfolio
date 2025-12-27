
from django.contrib import admin
from django.utils.html import format_html
from main.models import (
    Asset,
    Portfolio,
    Price,
    PortfolioWeight,
    Holding,
    Transaction
)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    """Administración de Activos"""
    list_display = ['symbol', 'name', 'total_prices', 'created_at']
    list_filter = ['created_at']
    search_fields = ['symbol', 'name']
    readonly_fields = ['created_at']
    
    def total_prices(self, obj):
        """Muestra el total de precios registrados para el activo"""
        count = obj.prices.count()
        return format_html(
            '<span style="font-weight: bold;">{}</span>',
            count
        )
    total_prices.short_description = 'Total Precios'


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    """Administración de Portafolios"""
    list_display = [
        'name', 
        'initial_value_formatted', 
        'start_date', 
        'total_assets',
        'created_at'
    ]
    list_filter = ['start_date', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']
    
    def initial_value_formatted(self, obj):
        """Formatea el valor inicial"""
        return format_html(
            '<span style="color: green; font-weight: bold;">${:,.2f}</span>',
            obj.initial_value
        )
    initial_value_formatted.short_description = 'Valor Inicial'
    
    def total_assets(self, obj):
        """Muestra el total de activos en el portafolio"""
        count = obj.weights.count()
        return format_html(
            '<span style="font-weight: bold;">{}</span>',
            count
        )
    total_assets.short_description = 'Total Activos'


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    """Administración de Precios"""
    list_display = ['asset', 'date', 'price_formatted']
    list_filter = ['date', 'asset']
    search_fields = ['asset__symbol', 'asset__name']
    date_hierarchy = 'date'
    list_select_related = ['asset']
    
    def price_formatted(self, obj):
        """Formatea el precio"""
        return format_html(
            '<span style="color: blue;">${:,.6f}</span>',
            obj.price
        )
    price_formatted.short_description = 'Precio'


@admin.register(PortfolioWeight)
class PortfolioWeightAdmin(admin.ModelAdmin):
    """Administración de Weights"""
    list_display = [
        'portfolio', 
        'asset', 
        'weight_formatted',
        'weight_percentage_formatted'
    ]
    list_filter = ['portfolio']
    search_fields = ['asset__symbol', 'portfolio__name']
    list_select_related = ['portfolio', 'asset']
    
    def weight_formatted(self, obj):
        """Formatea el weight como decimal"""
        return format_html(
            '<span style="font-weight: bold;">{:.8f}</span>',
            obj.weight
        )
    weight_formatted.short_description = 'Weight'
    
    def weight_percentage_formatted(self, obj):
        """Formatea el weight como porcentaje"""
        percentage = float(obj.weight) * 100
        color = 'green' if percentage > 10 else 'gray'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.4f}%</span>',
            color,
            percentage
        )
    weight_percentage_formatted.short_description = 'Weight %'


@admin.register(Holding)
class HoldingAdmin(admin.ModelAdmin):
    """Administración de Holdings (Cantidades)"""
    list_display = [
        'portfolio', 
        'asset', 
        'date', 
        'quantity_formatted'
    ]
    list_filter = ['portfolio', 'date']
    search_fields = ['asset__symbol', 'portfolio__name']
    date_hierarchy = 'date'
    list_select_related = ['portfolio', 'asset']
    
    def quantity_formatted(self, obj):
        """Formatea la cantidad"""
        return format_html(
            '<span style="color: blue; font-weight: bold;">{:,.4f}</span>',
            obj.quantity
        )
    quantity_formatted.short_description = 'Cantidad'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Administración de Transacciones"""
    list_display = [
        'portfolio',
        'asset',
        'transaction_type_colored',
        'amount_formatted',
        'date',
        'created_at'
    ]
    list_filter = ['transaction_type', 'date', 'portfolio']
    search_fields = ['asset__symbol', 'portfolio__name', 'notes']
    date_hierarchy = 'date'
    readonly_fields = ['created_at']
    list_select_related = ['portfolio', 'asset']
    
    def transaction_type_colored(self, obj):
        """Colorea el tipo de transacción"""
        color = 'green' if obj.transaction_type == 'BUY' else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_transaction_type_display()
        )
    transaction_type_colored.short_description = 'Tipo'
    
    def amount_formatted(self, obj):
        """Formatea el monto"""
        color = 'green' if obj.transaction_type == 'BUY' else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">${:,.2f}</span>',
            color,
            obj.amount
        )
    amount_formatted.short_description = 'Monto'


# Personalización del admin site
admin.site.site_header = "Administración de Portafolios"
admin.site.site_title = "Portafolios Admin"
admin.site.index_title = "Gestión de Portafolios de Inversión"