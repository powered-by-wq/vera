from data_wizard import registry
from wq.db.patterns import serializers as patterns
import swapper

Site = swapper.load_model('params', 'Site')
Parameter = swapper.load_model('params', 'Parameter')


class SiteSerializer(patterns.IdentifiedModelSerializer):
    class Meta:
        model = Site
        fields = "__all__"


class ParameterSerializer(patterns.IdentifiedModelSerializer):
    class Meta:
        model = Parameter
        fields = "__all__"


registry.register('Site Metadata', SiteSerializer)
registry.register('Parameter Metadata', ParameterSerializer)
