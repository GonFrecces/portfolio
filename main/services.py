from typing import List, Dict
from decimal import Decimal
from datetime import date
from main.models import Portfolio, Holding, Price


class PortfolioAnalysisService:
    """
    Servicio para análisis y cálculos de portafolios.
    
    Implementa las fórmulas:
    - x_i,t = p_i,t * c_i,t  (valor del activo i en tiempo t)
    - V_t = Σ x_i,t  (valor total del portafolio)
    - w_i,t = x_i,t / V_t  (weight del activo i en tiempo t)
    """
    
    @staticmethod
    def calculate_portfolio_metrics(
        portfolio: Portfolio,
        fecha_inicio: date,
        fecha_fin: date
    ) -> List[Dict]:
        """
        Calcula w_i,t y V_t para un rango de fechas.
        
        Dado que c_i,t = c_i,0 (cantidades invariantes después de t=0):
        - x_i,t = p_i,t * c_i,0
        - V_t = Σ x_i,t
        - w_i,t = x_i,t / V_t
        
        Args:
            portfolio: Instancia del portafolio
            fecha_inicio: Fecha de inicio del análisis
            fecha_fin: Fecha de fin del análisis
            
        Returns:
            Lista de diccionarios con métricas por fecha:
            [
                {
                    'date': '2022-02-15',
                    'portfolio_value': 1000000000.00,
                    'weights': {'EEUU': 0.28, 'Europa': 0.087, ...},
                    'asset_values': {'EEUU': 280000000.00, ...}
                },
                ...
            ]
        """
        # Obtener holdings iniciales (cantidades constantes)
        initial_holdings = Holding.objects.filter(
            portfolio=portfolio,
            date=portfolio.start_date
        ).select_related('asset')
        
        if not initial_holdings.exists():
            return []
        
        # Crear diccionario de cantidades por activo: {asset_id: quantity}
        quantities = {h.asset_id: h.quantity for h in initial_holdings}
        
        # Obtener todos los precios en el rango de fechas
        prices = Price.objects.filter(
            asset__in=quantities.keys(),
            date__gte=fecha_inicio,
            date__lte=fecha_fin
        ).order_by('date', 'asset').select_related('asset')
        
        # Agrupar precios por fecha y calcular métricas
        results = []
        current_date_data = {}
        current_date = None
        
        for price in prices:
            # Cuando cambia la fecha, procesar la anterior
            if current_date != price.date:
                if current_date is not None:
                    results.append(
                        PortfolioAnalysisService._calculate_daily_metrics(
                            current_date,
                            current_date_data,
                            quantities,
                            portfolio
                        )
                    )
                
                # Resetear para nueva fecha
                current_date = price.date
                current_date_data = {}
            
            # Almacenar datos del precio
            current_date_data[price.asset_id] = {
                'symbol': price.asset.symbol,
                'price': price.price,
                'quantity': quantities.get(price.asset_id, Decimal('0'))
            }
        
        # Procesar última fecha
        if current_date is not None:
            results.append(
                PortfolioAnalysisService._calculate_daily_metrics(
                    current_date,
                    current_date_data,
                    quantities,
                    portfolio
                )
            )
        
        return results
    
    @staticmethod
    def _calculate_daily_metrics(
        date: date,
        assets_data: Dict,
        quantities: Dict,
        portfolio: Portfolio
    ) -> Dict:
        """
        Calcula las métricas para un día específico.
        
        Args:
            date: Fecha del cálculo
            assets_data: Datos de activos y precios del día
            quantities: Cantidades de cada activo
            portfolio: Instancia del portafolio
            
        Returns:
            Diccionario con métricas del día
        """
        # Calcular x_i,t = p_i,t * c_i,t para cada activo
        asset_values = {}
        V_t = Decimal('0')
        
        for asset_id, data in assets_data.items():
            # x_i,t = precio * cantidad
            x_i_t = data['price'] * data['quantity']
            asset_values[data['symbol']] = x_i_t
            V_t += x_i_t
        
        # Calcular w_i,t = x_i,t / V_t para cada activo
        weights = {}
        for symbol, x_i_t in asset_values.items():
            weights[symbol] = float(x_i_t / V_t) if V_t > 0 else 0.0
        
        return {
            'date': date.isoformat(),
            'portfolio_value': float(V_t),
            'weights': weights,
            'asset_values': {k: float(v) for k, v in asset_values.items()}
        }
    
    @staticmethod
    def get_portfolio_summary(portfolio: Portfolio) -> Dict:
        """
        Obtiene un resumen del portafolio.
        
        Args:
            portfolio: Instancia del portafolio
            
        Returns:
            Diccionario con información resumida
        """
        weights = portfolio.weights.select_related('asset').all()
        holdings = Holding.objects.filter(
            portfolio=portfolio,
            date=portfolio.start_date
        ).select_related('asset')
        
        return {
            'id': portfolio.id,
            'name': portfolio.name,
            'initial_value': float(portfolio.initial_value),
            'start_date': portfolio.start_date.isoformat(),
            'total_assets': weights.count(),
            'assets': [
                {
                    'symbol': w.asset.symbol,
                    'name': w.asset.name,
                    'initial_weight': float(w.weight),
                    'initial_quantity': float(
                        holdings.filter(asset=w.asset).first().quantity
                    ) if holdings.filter(asset=w.asset).exists() else 0.0
                }
                for w in weights
            ]
        }