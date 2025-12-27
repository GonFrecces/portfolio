from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Asset(models.Model):
    """
    Representa un activo invertible (ej: EEUU, Europa, UK, etc.)
    """
    symbol = models.CharField(max_length=50, unique=True, verbose_name='Símbolo')
    name = models.CharField(max_length=200, verbose_name='Nombre')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    
    class Meta:
        ordering = ['symbol']
        verbose_name = 'Activo'
        verbose_name_plural = 'Activos'
        db_table = 'portfolios_asset'
    
    def __str__(self):
        return f"{self.symbol} - {self.name}"


class Portfolio(models.Model):
    """
    Representa un portafolio de inversión
    """
    name = models.CharField(max_length=100, verbose_name='Nombre')
    initial_value = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor inicial (V_0)',
        help_text='Valor inicial del portafolio en dólares'
    )
    start_date = models.DateField(verbose_name='Fecha de inicio')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Portafolio'
        verbose_name_plural = 'Portafolios'
        db_table = 'portfolios_portfolio'
    
    def __str__(self):
        return f"{self.name} (${self.initial_value:,.2f})"


class Price(models.Model):
    """
    Precio de un activo en una fecha específica (p_i,t)
    
    Representa el precio p_i,t donde:
    - i = activo
    - t = tiempo (fecha)
    """
    asset = models.ForeignKey(
        Asset, 
        on_delete=models.CASCADE, 
        related_name='prices',
        verbose_name='Activo'
    )
    date = models.DateField(db_index=True, verbose_name='Fecha')
    price = models.DecimalField(
        max_digits=15, 
        decimal_places=6,
        validators=[MinValueValidator(Decimal('0.000001'))],
        verbose_name='Precio (p_i,t)'
    )
    
    class Meta:
        ordering = ['date', 'asset']
        unique_together = ['asset', 'date']
        verbose_name = 'Precio'
        verbose_name_plural = 'Precios'
        db_table = 'portfolios_price'
        indexes = [
            models.Index(fields=['asset', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.asset.symbol} @ {self.date}: ${self.price}"


class PortfolioWeight(models.Model):
    """
    Weight inicial de cada activo en un portafolio (w_i,0)
    
    Representa el peso w_i,0 donde:
    - i = activo
    - 0 = tiempo inicial
    
    w_i,0 = porcentaje que representa el activo sobre el portafolio total
    """
    portfolio = models.ForeignKey(
        Portfolio, 
        on_delete=models.CASCADE, 
        related_name='weights',
        verbose_name='Portafolio'
    )
    asset = models.ForeignKey(
        Asset, 
        on_delete=models.CASCADE,
        verbose_name='Activo'
    )
    weight = models.DecimalField(
        max_digits=10, 
        decimal_places=8,
        validators=[
            MinValueValidator(Decimal('0')), 
            MaxValueValidator(Decimal('1'))
        ],
        verbose_name='Weight (w_i,0)',
        help_text='Porcentaje del activo en el portafolio (0.0 a 1.0)'
    )
    
    class Meta:
        unique_together = ['portfolio', 'asset']
        verbose_name = 'Porcentaje del Portafolio'
        verbose_name_plural = 'Porcentajes de Portafolios'
        db_table = 'portfolios_weight'
    
    def __str__(self):
        return f"{self.portfolio.name} - {self.asset.symbol}: {self.weight:.4%}"
    
    @property
    def weight_percentage(self):
        """Retorna el weight como porcentaje"""
        return float(self.weight) * 100


class Holding(models.Model):
    """
    Cantidad de cada activo en un portafolio en el tiempo (c_i,t)
    
    Representa la cantidad c_i,t donde:
    - i = activo
    - t = tiempo (fecha)
    
    Para este caso específico: c_i,t = c_i,0 (cantidad constante)
    """
    portfolio = models.ForeignKey(
        Portfolio, 
        on_delete=models.CASCADE, 
        related_name='holdings',
        verbose_name='Portafolio'
    )
    asset = models.ForeignKey(
        Asset, 
        on_delete=models.CASCADE,
        verbose_name='Activo'
    )
    date = models.DateField(db_index=True, verbose_name='Fecha')
    quantity = models.DecimalField(
        max_digits=20, 
        decimal_places=8,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='Cantidad (c_i,t)',
        help_text='Cantidad de unidades del activo'
    )
    
    class Meta:
        unique_together = ['portfolio', 'asset', 'date']
        ordering = ['date', 'portfolio', 'asset']
        verbose_name = 'Tenencia'
        verbose_name_plural = 'Tenencias'
        db_table = 'portfolios_holding'
        indexes = [
            models.Index(fields=['portfolio', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.portfolio.name} - {self.asset.symbol} @ {self.date}: {self.quantity:.4f}"
    
    def calculate_value(self, price):
        """
        Calcula el valor del holding: x_i,t = p_i,t * c_i,t
        """
        return price * self.quantity


class Transaction(models.Model):
    """
    Transacciones de compra/venta de activos (Bonus 2)
    
    Permite registrar operaciones de compra/venta que modifican
    las cantidades c_i,t del portafolio.
    """
    TRANSACTION_TYPES = [
        ('BUY', 'Compra'),
        ('SELL', 'Venta'),
    ]
    
    portfolio = models.ForeignKey(
        Portfolio, 
        on_delete=models.CASCADE, 
        related_name='transactions',
        verbose_name='Portafolio'
    )
    asset = models.ForeignKey(
        Asset, 
        on_delete=models.CASCADE,
        verbose_name='Activo'
    )
    transaction_type = models.CharField(
        max_length=4, 
        choices=TRANSACTION_TYPES,
        verbose_name='Tipo de transacción'
    )
    date = models.DateField(db_index=True, verbose_name='Fecha')
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Monto',
        help_text='Monto en dólares de la transacción'
    )
    notes = models.TextField(blank=True, verbose_name='Notas')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        db_table = 'portfolios_transaction'
        indexes = [
            models.Index(fields=['portfolio', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} ${self.amount:,.2f} {self.asset.symbol} ({self.date})"