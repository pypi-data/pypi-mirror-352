# core_services/services/custom_service.py

from typing import Type, Any

class CustomService:
    def __init__(self, serializer, document_type: Type[Any] = None):
        self.serializer = serializer

    def get_object(self, pk, serialized=False):
        instance = self.serializer.Meta.model.objects.get(pk=pk)
        return self.serializer(instance).data if serialized else instance

    def get_all_objects(self, serialized=False):
        instances = self.serializer.Meta.model.objects.all()
        return self.serializer(instances, many=True).data if serialized else instances

    def get_objects_with_id_in_list(self, ids: list, serialized=False):
        instances = self.serializer.Meta.model.objects.filter(pk__in=ids)
        return self.serializer(instances, many=True).data if serialized else instances

    def create_object_or_raise_exception(self, data: Any, raise_exception=True):
        serializer_instance = self.serializer(data=data)
        serializer_instance.is_valid(raise_exception=raise_exception)
        return serializer_instance.save()

    def update_object(self, data: Any):
        instance = self.serializer.Meta.model.objects.get(pk=data['id'])
        serializer_instance = self.serializer(instance, data=data)
        serializer_instance.is_valid(raise_exception=True)
        return serializer_instance.save()

    def delete_object(self, pk):
        # Assumes your serializer has this method implemented
        return self.serializer.raise_exception_if_not_valid_or_delete_data(
            raise_exception=True, pk=pk
        )
