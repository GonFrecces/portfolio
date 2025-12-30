from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from main.models import Portfolio
from main.services import PortfolioAnalysisService
from main.serializers import (
    PortfolioMetricsSerializer,
    PortfolioQuerySerializer,
    PortfolioSerializer
)

class DashboardView(View):
    """
    Vista para renderizar el dashboard con gráficos.
    
    Implementa el Bonus 1 del challenge:
    - Gráfico stacked area para w_i,t (weights)
    - Gráfico de línea para V_t (portfolio value)
    """

    def get(self, request):
        context = {
            'portfolios': Portfolio.objects.all()
        }
        return render(request, 'dashboard.html', context)


class PortfolioMetricsAPIView(APIView):
    """
    API para obtener w_i,t y V_t de un portafolio en un rango de fechas.
    
    **Query Parameters:**
    - `portfolio_id` (int): ID del portafolio
    - `fecha_inicio` (date): Fecha de inicio en formato YYYY-MM-DD
    - `fecha_fin` (date): Fecha de fin en formato YYYY-MM-DD
    
    **Ejemplo de uso:**
    ```
    GET /portfolios/api/metrics/?portfolio_id=1&fecha_inicio=2022-02-15&fecha_fin=2022-03-15
    ```
    
    **Respuesta:**
    ```json
    {
        "portfolio": {
            "id": 1,
            "name": "Portafolio 1",
            "initial_value": "1000000000.00"
        },
        "metrics": [
            {
                "date": "2022-02-15",
                "portfolio_value": 1000000000.00,
                "weights": {
                    "EEUU": 0.28,
                    "Europa": 0.087,
                    ...
                },
                "asset_values": {
                    "EEUU": 280000000.00,
                    "Europa": 87000000.00,
                    ...
                }
            },
            ...
        ]
    }
    ```
    """
    
    def get(self, request):
        """
        Maneja las peticiones GET para obtener métricas del portafolio.
        
        Args:
            request: Objeto de petición HTTP
            
        Returns:
            Response con las métricas del portafolio o errores de validación
        """
        # Validar parámetros de query
        query_serializer = PortfolioQuerySerializer(data=request.query_params)
        
        if not query_serializer.is_valid():
            return Response(
                {
                    'error': 'Parámetros inválidos',
                    'details': query_serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validated_data = query_serializer.validated_data
        
        # Obtener portafolio
        try:
            portfolio = Portfolio.objects.get(id=validated_data['portfolio_id'])
        except Portfolio.DoesNotExist:
            return Response(
                {'error': f'Portafolio con ID {validated_data["portfolio_id"]} no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calcular métricas usando el servicio
        metrics = PortfolioAnalysisService.calculate_portfolio_metrics(
            portfolio=portfolio,
            fecha_inicio=validated_data['fecha_inicio'],
            fecha_fin=validated_data['fecha_fin']
        )
        
        # Serializar respuesta
        metrics_serializer = PortfolioMetricsSerializer(metrics, many=True)
        
        return Response({
            'portfolio': {
                'id': portfolio.id,
                'name': portfolio.name,
                'initial_value': str(portfolio.initial_value),
                'start_date': portfolio.start_date.isoformat()
            },
            'query': {
                'fecha_inicio': validated_data['fecha_inicio'].isoformat(),
                'fecha_fin': validated_data['fecha_fin'].isoformat(),
                'total_days': len(metrics)
            },
            'metrics': metrics_serializer.data
        })


class PortfolioListAPIView(APIView):
    """
    API para listar todos los portafolios disponibles.
    
    **Ejemplo de uso:**
    ```
    GET /portfolios/api/portfolios/
    ```
    
    **Respuesta:**
    ```json
    {
        "count": 2,
        "portfolios": [
            {
                "id": 1,
                "name": "Portafolio 1",
                "initial_value": "1000000000.00",
                "start_date": "2022-02-15",
                "weights": [...]
            },
            ...
        ]
    }
    ```
    """
    
    def get(self, request):
        """
        Maneja las peticiones GET para listar portafolios.
        
        Args:
            request: Objeto de petición HTTP
            
        Returns:
            Response con la lista de portafolios
        """
        portfolios = Portfolio.objects.prefetch_related('weights__asset').all()
        serializer = PortfolioSerializer(portfolios, many=True)
        
        return Response({
            'count': portfolios.count(),
            'portfolios': serializer.data
        })


class PortfolioDetailAPIView(APIView):
    """
    API para obtener detalles de un portafolio específico.
    
    **Ejemplo de uso:**
    ```
    GET /portfolios/api/portfolios/1/
    ```
    """
    
    def get(self, request, portfolio_id):
        """
        Maneja las peticiones GET para un portafolio específico.
        
        Args:
            request: Objeto de petición HTTP
            portfolio_id: ID del portafolio
            
        Returns:
            Response con los detalles del portafolio
        """
        try:
            portfolio = Portfolio.objects.prefetch_related(
                'weights__asset'
            ).get(id=portfolio_id)
        except Portfolio.DoesNotExist:
            return Response(
                {'error': f'Portafolio con ID {portfolio_id} no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener resumen completo
        summary = PortfolioAnalysisService.get_portfolio_summary(portfolio)
        
        return Response(summary)