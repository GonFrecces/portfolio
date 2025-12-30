from django.core.management.base import BaseCommand
from django.db import transaction
from main.models import Portfolio, Holding, Price
from decimal import Decimal


class Command(BaseCommand):
    help = 'Calcula las cantidades iniciales (c_i,0) para cada portafolio'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('CALCULANDO CANTIDADES INICIALES (c_i,0)'))
        self.stdout.write(self.style.SUCCESS('='*70))
        
        portfolios = Portfolio.objects.all()
        
        if not portfolios.exists():
            self.stdout.write(self.style.ERROR('✗ No hay portafolios. Ejecuta load_portfolio_data primero.'))
            return
        
        for portfolio in portfolios:
            self.calculate_for_portfolio(portfolio)
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('✓ Cantidades calculadas exitosamente'))
        self.stdout.write(self.style.SUCCESS('='*70))

    def calculate_for_portfolio(self, portfolio):
        """
        Calcula c_i,0 = (w_i,0 * V_0) / p_i,0
        
        Donde:
        - c_i,0 = cantidad inicial del activo i
        - w_i,0 = weight inicial del activo i
        - V_0 = valor inicial del portafolio
        - p_i,0 = precio inicial del activo i
        """
        self.stdout.write(f'\n💼 PORTAFOLIO: {portfolio.name}')
        self.stdout.write(f'   Valor inicial: ${portfolio.initial_value:,.2f}')
        self.stdout.write(f'   Fecha inicio: {portfolio.start_date}')
        
        weights = portfolio.weights.select_related('asset').all()
        V0 = portfolio.initial_value
        t0 = portfolio.start_date
        
        if not weights.exists():
            self.stdout.write(self.style.WARNING('   ⚠ No hay weights para este portafolio'))
            return
        
        holdings_to_create = []
        total_value_check = Decimal('0')
        
        self.stdout.write(f'\n   {"Activo":<20} {"Weight":<10} {"Precio":<12} {"Cantidad":<15} {"Valor":<15}')
        self.stdout.write('   ' + '-'*75)
        
        for weight_obj in weights:
            asset = weight_obj.asset
            w_i_0 = weight_obj.weight
            
            # Obtener precio inicial p_i,0
            try:
                price_obj = Price.objects.get(asset=asset, date=t0)
                p_i_0 = price_obj.price
                
                # Calcular cantidad: c_i,0 = (w_i,0 * V_0) / p_i,0
                # La cantidad invertida por activo (c_i_0) 
                c_i_0 = (w_i_0 * V0) / p_i_0
                
                # Verificación: x_i,0 = p_i,0 * c_i,0
                x_i_0 = p_i_0 * c_i_0
                total_value_check += x_i_0
                
                holdings_to_create.append(
                    Holding(
                        portfolio=portfolio,
                        asset=asset,
                        date=t0,
                        quantity=c_i_0
                    )
                )
                
                self.stdout.write(
                    f'   {asset.symbol:<20} '
                    f'{w_i_0*100:>8.4f}% '
                    f'${p_i_0:>10.4f} '
                    f'{c_i_0:>14.4f} '
                    f'${x_i_0:>13,.2f}'
                )
                
            except Price.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f'   {asset.symbol:<20} ⚠ No hay precio para {t0}'
                    )
                )
        
        # Crear holdings en batch
        with transaction.atomic():
            # Eliminar holdings existentes para esta fecha
            Holding.objects.filter(portfolio=portfolio, date=t0).delete()
            Holding.objects.bulk_create(holdings_to_create)
        
        self.stdout.write('   ' + '-'*75)
        self.stdout.write(f'   {"TOTAL":<20} {"":10} {"":12} {"":15} ${total_value_check:>13,.2f}')
        self.stdout.write(f'\n   ✓ {len(holdings_to_create)} holdings creados')
        
        # Verificar que el total sea correcto
        diff = abs(total_value_check - V0)
        if diff < Decimal('0.01'):
            self.stdout.write(self.style.SUCCESS(f'   ✓ Verificación OK (diferencia: ${diff:.2f})'))
        else:
            self.stdout.write(
                self.style.WARNING(f'   ⚠ Diferencia detectada: ${diff:,.2f}')
            )