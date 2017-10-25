#
# Graphene schema for exposing EconomicResource model
#

import graphene
from valuenetwork.valueaccounting.models import EconomicResource as EconomicResourceProxy, EconomicResourceType, AgentUser
from valuenetwork.api.types.EconomicResource import EconomicResource
from six import with_metaclass
from django.contrib.auth.models import User
from .Auth import AuthedInputMeta, AuthedMutation
from django.core.exceptions import PermissionDenied


class Query(graphene.AbstractType):

    # define input query params

    economic_resource = graphene.Field(EconomicResource,
                                       id=graphene.Int())

    all_economic_resources = graphene.List(EconomicResource)

    # resolve methods

    def resolve_economic_resource(self, args, *rargs):
        id = args.get('id')
        if id is not None:
            resource = EconomicResourceProxy.objects.get(pk=id)
            if resource:
                #resource.current_quantity = self._current_quantity(quantity=resource.quantity, unit=resource.unit)
                return resource
        return None   

    def resolve_all_economic_resources(self, args, context, info):
        resources = EconomicResourceProxy.objects.all()
        #for resource in resources:
            #resource.current_quantity = self._current_quantity(quantity=resource.quantity, unit=resource.unit)
        return resources

'''
class CreateEconomicResource(AuthedMutation):
    class Input(with_metaclass(AuthedInputMeta)):
        resource_classified_as_id = graphene.Int(required=True)
        tracking_identifier = graphene.String(required=False)
        image = graphene.String(required=False)
        note = graphene.String(required=False)
        #current_location #TODO
        #current_quantity is not creatable or updatable directly, it always is derived from economic events

    economic_resource = graphene.Field(lambda: EconomicResource)

    @classmethod
    def mutate(cls, root, args, context, info):
        resource_classified_as_id = args.get('resource_classified_as_id')
        tracking_identifier = args.get('tracking_identifier')
        image = args.get('image')
        note = args.get('note')

        if not note:
            note = ""
        if not image:
            image = ""
        if not tracking_identifier:
            tracking_identifier = ""
        resource_classified_as = EconomicResourceType.objects.get(pk=resource_classified_as_id)
        economic_resource = EconomicResourceProxy(
            resource_type=resource_classified_as,
            photo_url=image,
            identifier=tracking_identifier,
            notes=note,
            created_by=context.user,
            #location
        )
        economic_resource.save()

        return CreateEconomicResource(economic_resource=economic_resource)
'''

class UpdateEconomicResource(AuthedMutation):
    class Input(with_metaclass(AuthedInputMeta)):
        id = graphene.Int(required=True)
        resource_classified_as_id = graphene.Int(required=False)
        tracking_identifier = graphene.String(required=False)
        image = graphene.String(required=False)
        note = graphene.String(required=False)
        #current_location #TODO

    economic_resource = graphene.Field(lambda: EconomicResource)

    @classmethod
    def mutate(cls, root, args, context, info):
        id = args.get('id')
        resource_classified_as_id = args.get('resource_classified_as_id')
        tracking_identifier = args.get('tracking_identifier')
        image = args.get('image')
        note = args.get('note')

        economic_resource = EconomicResourceProxy.objects.get(pk=id)
        if economic_resource:
            if tracking_identifier:
                economic_resource.identifier = tracking_identifier
            if note:
                economic_resource.notes=note
            if image:
                economic_resource.photo_url=image
            if resource_classified_as_id:
                economic_resource.resource_type=EconomicResourceType.objects.get(pk=resource_classified_as_id)
            economic_resource.changed_by=context.user

            user_agent = AgentUser.objects.get(user=context.user).agent
            is_authorized = user_agent.is_authorized(object_to_mutate=economic_resource)
            if is_authorized:
                economic_resource.save()
            else:
                raise PermissionDenied('User not authorized to perform this action.')

        return UpdateEconomicResource(economic_resource=economic_resource)


class DeleteEconomicResource(AuthedMutation):
    class Input(with_metaclass(AuthedInputMeta)):
        id = graphene.Int(required=True)

    economic_resource = graphene.Field(lambda: EconomicResource)

    @classmethod
    def mutate(cls, root, args, context, info):
        id = args.get('id')
        economic_resource = EconomicResourceProxy.objects.get(pk=id)
        if economic_resource:
            if economic_resource.is_deletable():
                is_authorized = user_agent.is_authorized(object_to_mutate=economic_resource)
                if is_authorized:
                    economic_resource.delete()
                else:
                    raise PermissionDenied('User not authorized to perform this action.')
            else:
                raise PermissionDenied("Economic resource has related events or quantity > 0 and cannot be deleted.")

        return DeleteEconomicResource(economic_resource=economic_resource)
