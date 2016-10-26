from rest_framework import serializers
from natural_keys import NaturalKeyModelSerializer
from wq.db.patterns import serializers as patterns
from wq.db.rest.serializers import ModelSerializer
from vera.results.serializers import ResultSerializer


class EventSerializer(ModelSerializer):
    is_valid = serializers.ReadOnlyField()
    results = ResultSerializer(many=True, read_only=True)

    class Meta:
        list_exclude = ('results',)


class ReportSerializer(NaturalKeyModelSerializer,
                       patterns.AttachedModelSerializer):
    is_valid = serializers.ReadOnlyField()
    results = ResultSerializer(many=True)

    def get_fields(self):
        # wq.db.{rest,patterns} fields
        fields = patterns.AttachedModelSerializer.get_fields(self)

        # natural_keys fields
        fields.update(self.build_natural_key_fields())
        return fields

    def to_internal_value(self, data):
        data = data.copy()
        if 'request' in self.context and not data.get('user_id', None):
            user = self.context['request'].user
            if user.is_authenticated():
                data['user_id'] = user.pk
        return super(ReportSerializer, self).to_internal_value(data)

    def create(self, validated_data):
        # natural_keys create
        self.convert_natural_keys(
            validated_data
        )

        # wq.db.patterns create
        return patterns.AttachedModelSerializer.create(
            self, validated_data
        )
