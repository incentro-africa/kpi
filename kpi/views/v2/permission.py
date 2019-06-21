# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.contrib.auth.models import Permission
from rest_framework import viewsets

from kpi.models.asset import Asset
from kpi.models.collection import Collection
from kpi.serializers.v2.permission import PermissionSerializer


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    <span class='label label-danger'>TODO - Add name</span>

    **Display all assignable permissions for `Asset` and `Collection`**

    `implied` property shows which permission is assigned at the time as
    the corresponding permission.

    `contradictory` property shows which permissions are removed when assigning
    the corresponding permission.


    <pre class="prettyprint">
    <b>GET</b> /api/v2/permissions/
    </pre>

    > Example
    >
    >       curl -X GET https://[kpi]/api/v2/permissions/

    > Response
    >
    >        {
    >           "count": 9,
    >           "next": null,
    >           "previous": null,
    >           "results": [
    >               {
    >                   "url": "http://kpi/api/v2/permissions/change_submissions/",
    >                   "codename": "change_submissions",
    >                   "implied": [
    >                       "http://kpi/api/v2/permissions/view_asset/"
    >                   ],
    >                   "contradictory": [
    >                       "http://kpi/api/v2/permissions/partial_submissions/"
    >                   ],
    >                   "name": "Change data",
    >                   "description": "Can modify submitted data for asset"
    >                },
    >                ...
    >               {
    >                   "url": "http://kpi/api/v2/permissions/view_collection/",
    >                   "codename": "add_submissions",
    >                   "implied": [],
    >                   "contradictory": [],
    >                   "name": "View collection",
    >                   "description": "Can view collection"
    >                }
    >           ]
    >        }


    <pre class="prettyprint">
    <b>GET</b> /api/v2/permissions/{codename}
    </pre>

    > Example
    >
    >       curl -X GET https://[kpi]/api/v2/permissions/change_submissions


    > Response
    >
    >               {
    >                   "url": "http://kpi/api/v2/permissions/change_submissions/",
    >                   "codename": "change_submissions",
    >                   "implied": [
    >                       "http://kpi/api/v2/permissions/view_asset/"
    >                   ],
    >                   "contradictory": [
    >                       "http://kpi/api/v2/permissions/partial_submissions/"
    >                   ],
    >                   "name": "Change data",
    >                   "description": "Can modify submitted data for asset"
    >                }


    ### CURRENT ENDPOINT
    """

    queryset = Permission.objects.all()
    model = Permission
    lookup_field = 'codename'
    serializer_class = PermissionSerializer

    def get_queryset(self, *args, **kwargs):
        queryset = super(PermissionViewSet, self).get_queryset(*args, **kwargs)
        # Codenames are unique per content_type. So, we ensure we don't return
        # codenames for different app or content_type
        models = [Asset._meta.model_name, Collection._meta.model_name]
        assignable_permissions = list(Asset.ASSIGNABLE_PERMISSIONS +
                                      Collection.ASSIGNABLE_PERMISSIONS)

        queryset = queryset.filter(content_type__app_label='kpi',
                                   content_type__model__in=models,
                                   codename__in=assignable_permissions).\
            select_related("content_type")
        return queryset

    def list(self, request, *args, **kwargs):
        return super(PermissionViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super(PermissionViewSet, self).retrieve(request, *args, **kwargs)