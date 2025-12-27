import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction, models
from main.models import Asset, Portfolio, Price, PortfolioWeight
from datetime import datetime
from decimal import Decimal


class Command(BaseCommand):
    help = 'Carga datos desde datos.xlsx'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Ruta al archivo datos.xlsx'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('Iniciando carga de datos ETL'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        try:
            with transaction.atomic():
                # 1. Cargar Precios (crea los activos)
                self.load_prices(file_path)
                
                # 2. Cargar Weights y Portafolios
                self.load_weights(file_path)
                
            self.stdout.write(self.style.SUCCESS('\n' + '='*60))
            self.stdout.write(self.style.SUCCESS('✓ Datos cargados exitosamente'))
            self.stdout.write(self.style.SUCCESS('='*60))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error: {str(e)}'))
            raise

    def load_prices(self, file_path):
        """Carga la hoja de Precios"""
        self.stdout.write('\n📊 CARGANDO PRECIOS...')
        
        df_prices = pd.read_excel(file_path, sheet_name='Precios')
        
        # La primera columna 'Dates' contiene las fechas
        dates = pd.to_datetime(df_prices['Dates'])
        
        # Las demás columnas son los activos
        asset_columns = [col for col in df_prices.columns if col != 'Dates']
        
        self.stdout.write(f'  • Fechas encontradas: {len(dates)} (desde {dates.min().date()} hasta {dates.max().date()})')
        self.stdout.write(f'  • Activos encontrados: {len(asset_columns)}')
        
        # Crear activos si no existen
        assets_dict = {}
        for asset_symbol in asset_columns:
            asset, created = Asset.objects.get_or_create(
                symbol=asset_symbol,
                defaults={'name': asset_symbol}
            )
            assets_dict[asset_symbol] = asset
            if created:
                self.stdout.write(f'    ✓ Activo creado: {asset_symbol}')
        
        # Crear precios en batch
        prices_to_create = []
        for idx, date in enumerate(dates):
            for asset_symbol in asset_columns:
                price_value = df_prices.loc[idx, asset_symbol]
                
                if pd.notna(price_value) and price_value > 0:
                    prices_to_create.append(
                        Price(
                            asset=assets_dict[asset_symbol],
                            date=date.date(),
                            price=Decimal(str(round(price_value, 6)))
                        )
                    )
        
        # Bulk create para mejor performance
        Price.objects.bulk_create(prices_to_create, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(prices_to_create)} precios cargados'))

    def load_weights(self, file_path):
        """Carga la hoja de weights"""
        self.stdout.write('\n⚖️  CARGANDO WEIGHTS...')
        
        df_weights = pd.read_excel(file_path, sheet_name='weights')
        
        # Crear portafolios
        start_date = datetime(2022, 2, 15).date()
        initial_value = Decimal('1000000000.00')  # $1,000,000,000
        
        portfolio1, created1 = Portfolio.objects.get_or_create(
            name='Portafolio 1',
            defaults={
                'initial_value': initial_value,
                'start_date': start_date
            }
        )
        if created1:
            self.stdout.write(f'  ✓ {portfolio1.name} creado')
        
        portfolio2, created2 = Portfolio.objects.get_or_create(
            name='Portafolio 2',
            defaults={
                'initial_value': initial_value,
                'start_date': start_date
            }
        )
        if created2:
            self.stdout.write(f'  ✓ {portfolio2.name} creado')
        
        # Cargar weights
        weights_p1 = 0
        weights_p2 = 0
        
        for idx, row in df_weights.iterrows():
            asset_symbol = row['activos']
            weight_p1 = row['portafolio 1']
            weight_p2 = row['portafolio 2']
            
            try:
                asset = Asset.objects.get(symbol=asset_symbol)
                
                # Weight Portafolio 1
                if pd.notna(weight_p1):
                    PortfolioWeight.objects.update_or_create(
                        portfolio=portfolio1,
                        asset=asset,
                        defaults={'weight': Decimal(str(weight_p1))}
                    )
                    weights_p1 += 1
                
                # Weight Portafolio 2
                if pd.notna(weight_p2):
                    PortfolioWeight.objects.update_or_create(
                        portfolio=portfolio2,
                        asset=asset,
                        defaults={'weight': Decimal(str(weight_p2))}
                    )
                    weights_p2 += 1
                    
            except Asset.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ Activo no encontrado: {asset_symbol}')
                )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ {weights_p1} weights para Portafolio 1'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ {weights_p2} weights para Portafolio 2'))
        
        # Validar que los weights suman 1 (o muy cerca)
        total_w1 = PortfolioWeight.objects.filter(portfolio=portfolio1).aggregate(
            total=models.Sum('weight')
        )['total']
        total_w2 = PortfolioWeight.objects.filter(portfolio=portfolio2).aggregate(
            total=models.Sum('weight')
        )['total']
        
        self.stdout.write(f'\n  📊 Suma de weights:')
        self.stdout.write(f'    • Portafolio 1: {total_w1:.6f} ({total_w1*100:.2f}%)')
        self.stdout.write(f'    • Portafolio 2: {total_w2:.6f} ({total_w2*100:.2f}%)')