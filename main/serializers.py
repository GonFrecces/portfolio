from rest_framework import serializers
from main.models import Portfolio, Asset, PortfolioWeight


class AssetSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Asset"""
    class Meta:
        model = Asset
        fields = ['id', 'symbol', 'name']


class PortfolioWeightSerializer(serializers.ModelSerializer):
    """Serializer para el modelo PortfolioWeight"""
    asset_symbol = serializers.CharField(source='asset.symbol', read_only=True)
    weight_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = PortfolioWeight
        fields = ['asset_symbol', 'weight', 'weight_percentage']
    
    def get_weight_percentage(self, obj):
        return float(obj.weight) * 100


class PortfolioSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Portfolio"""
    weights = PortfolioWeightSerializer(many=True, read_only=True)
    
    class Meta:
        model = Portfolio
        fields = ['id', 'name', 'initial_value', 'start_date', 'weights']


class PortfolioMetricsSerializer(serializers.Serializer):
    """
    Serializer para las métricas calculadas del portafolio.
    
    Representa los valores de w_i,t y V_t para una fecha específica.
    """
    date = serializers.DateField(
        help_text="Fecha de las métricas"
    )
    portfolio_value = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2,
        help_text="Valor total del portafolio (V_t)"
    )
    weights = serializers.DictField(
        help_text="Weights de cada activo (w_i,t) - formato {symbol: weight}"
    )
    asset_values = serializers.DictField(
        help_text="Valores de cada activo (x_i,t) - formato {symbol: value}"
    )


class PortfolioQuerySerializer(serializers.Serializer):
    """
    Serializer para validar los parámetros de consulta de la API.
    
    Valida:
    - portfolio_id: Debe existir
    - fecha_inicio: Debe ser válida
    - fecha_fin: Debe ser válida y >= fecha_inicio
    """
    portfolio_id = serializers.IntegerField(
        min_value=1,
        help_text="ID del portafolio a consultar"
    )
    fecha_inicio = serializers.DateField(
        help_text="Fecha de inicio del análisis (formato: YYYY-MM-DD)"
    )
    fecha_fin = serializers.DateField(
        help_text="Fecha de fin del análisis (formato: YYYY-MM-DD)"
    )
    
    def validate(self, data):
        """
        Validación de nivel de objeto.
        
        Verifica que fecha_inicio <= fecha_fin
        """
        if data['fecha_inicio'] > data['fecha_fin']:
            raise serializers.ValidationError({
                'fecha_fin': 'La fecha_fin debe ser mayor o igual a fecha_inicio'
            })
        return data
    
    def validate_portfolio_id(self, value):
        """
        Validación del campo portfolio_id.
        
        Verifica que el portafolio exista.
        """
        from main.models import Portfolio
        
        if not Portfolio.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                f'No existe un portafolio con ID {value}'
            )
        return value