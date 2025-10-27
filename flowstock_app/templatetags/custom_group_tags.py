from django import template
from django.contrib.auth.models import User
from django.db.models.query import QuerySet

register = template.Library()

@register.filter(name='available_for')
def available_for(subgroups_queryset, member):
    if not isinstance(subgroups_queryset, QuerySet) or not isinstance(member, User):
        return []

    return subgroups_queryset.exclude(members=member)