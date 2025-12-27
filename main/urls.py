from django.urls import path
from django.contrib import admin
from main.views import (
    DashboardView, 
    PortfolioMetricsAPIView, 
    PortfolioListAPIView, 
    PortfolioDetailAPIView
)

app_name = 'portfolios'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', DashboardView.as_view(), name='dashboard'),  # Vista principal del dashboard con gráficos
    path('dashboard/', DashboardView.as_view(), name='dashboard-alt'),  # Alias alternativo
    path('api/metrics/', PortfolioMetricsAPIView.as_view(), name='portfolio-metrics'), # API de métricas (Pregunta 4 del challenge)
    path('api/portfolios/', PortfolioListAPIView.as_view(), name='portfolio-list'), # API de listado de portafolios
    path('api/portfolios/<int:portfolio_id>/', PortfolioDetailAPIView.as_view(), name='portfolio-detail'), # API de detalle de portafolio
]