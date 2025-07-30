from core.choices import ObjectChangeActionChoices
from dcim.models import Device
from dcim.models import Site
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import View
from django_tables2 import RequestConfig
from ipfabric.diagrams import Network
from ipfabric.diagrams import NetworkSettings
from netbox.views import generic
from netbox.views.generic.base import BaseObjectView
from netbox_branching.models import ChangeDiff
from utilities.data import shallow_compare_dict
from utilities.forms import ConfirmationForm
from utilities.paginator import EnhancedPaginator
from utilities.paginator import get_paginate_count
from utilities.query import count_related
from utilities.views import get_viewname
from utilities.views import register_model_view
from utilities.views import ViewTab

from .filtersets import IPFabricDataFilterSet
from .filtersets import IPFabricIngestionChangeFilterSet
from .filtersets import IPFabricIngestionFilterSet
from .filtersets import IPFabricSnapshotFilterSet
from .filtersets import IPFabricSourceFilterSet
from .forms import IPFabricIngestionFilterForm
from .forms import IPFabricIngestionMergeForm
from .forms import IPFabricRelationshipFieldForm
from .forms import IPFabricSnapshotFilterForm
from .forms import IPFabricSourceFilterForm
from .forms import IPFabricSourceForm
from .forms import IPFabricSyncForm
from .forms import IPFabricTableForm
from .forms import IPFabricTransformFieldForm
from .forms import IPFabricTransformMapForm
from .models import IPFabricData
from .models import IPFabricIngestion
from .models import IPFabricRelationshipField
from .models import IPFabricSnapshot
from .models import IPFabricSource
from .models import IPFabricSync
from .models import IPFabricTransformField
from .models import IPFabricTransformMap
from .tables import DeviceIPFTable
from .tables import IPFabricDataTable
from .tables import IPFabricIngestionChangesTable
from .tables import IPFabricIngestionTable
from .tables import IPFabricRelationshipFieldTable
from .tables import IPFabricSnapshotTable
from .tables import IPFabricSourceTable
from .tables import IPFabricTransformFieldTable
from .tables import IPFabricTransformMapTable
from .utilities.ipfutils import IPFabric
from .utilities.transform_map import build_transform_maps
from .utilities.transform_map import get_transform_map


# Transform Map Relationship Field


@register_model_view(IPFabricRelationshipField, "edit")
class IPFabricRelationshipFieldEditView(generic.ObjectEditView):
    queryset = IPFabricRelationshipField.objects.all()
    form = IPFabricRelationshipFieldForm
    default_return_url = "plugins:ipfabric_netbox:ipfabricrelationshipfield_list"


class IPFabricRelationshipFieldDeleteView(generic.ObjectDeleteView):
    queryset = IPFabricRelationshipField.objects.all()
    default_return_url = "plugins:ipfabric_netbox:ipfabricrelationshipfield_list"


@register_model_view(IPFabricTransformMap, "relationships")
class IPFabricTransformRelationshipView(generic.ObjectChildrenView):
    queryset = IPFabricTransformMap.objects.all()
    child_model = IPFabricRelationshipField
    table = IPFabricRelationshipFieldTable
    template_name = "ipfabric_netbox/inc/transform_map_relationship_map.html"
    tab = ViewTab(
        label="Relationship Maps",
        badge=lambda obj: IPFabricRelationshipField.objects.filter(
            transform_map=obj
        ).count(),
        permission="ipfabric_netbox.view_ipfabricrelationshipfield",
    )

    def get_children(self, request, parent):
        return self.child_model.objects.filter(transform_map=parent)


class IPFabricRelationshipFieldListView(generic.ObjectListView):
    queryset = IPFabricRelationshipField.objects.all()
    table = IPFabricRelationshipFieldTable


# Transform Map


class IPFabricTransformMapListView(generic.ObjectListView):
    queryset = IPFabricTransformMap.objects.all()
    table = IPFabricTransformMapTable
    template_name = "ipfabric_netbox/ipfabrictransformmap_list.html"


class IPFabricTransformMapRestoreView(generic.ObjectListView):
    queryset = IPFabricTransformMap.objects.all()
    table = IPFabricTransformMapTable

    def get_required_permission(self):
        return "ipfabric_netbox.tm_restore"

    def get(self, request):
        if request.htmx:
            viewname = get_viewname(self.queryset.model, action="restore")
            form_url = reverse(viewname)
            form = ConfirmationForm(initial=request.GET)
            dependent_objects = {
                IPFabricTransformMap: IPFabricTransformMap.objects.all(),
                IPFabricTransformField: IPFabricTransformField.objects.all(),
                IPFabricRelationshipField: IPFabricRelationshipField.objects.all(),
            }
            print(dependent_objects)
            return render(
                request,
                "ipfabric_netbox/ipfabrictransformmap_restore.html",
                {
                    "form": form,
                    "form_url": form_url,
                    "dependent_objects": dependent_objects,
                },
            )

    def post(self, request):
        IPFabricTransformMap.objects.all().delete()
        build_transform_maps(data=get_transform_map())
        return redirect("plugins:ipfabric_netbox:ipfabrictransformmap_list")


@register_model_view(IPFabricTransformMap, "edit")
class IPFabricTransformMapEditView(generic.ObjectEditView):
    queryset = IPFabricTransformMap.objects.all()
    form = IPFabricTransformMapForm
    default_return_url = "plugins:ipfabric_netbox:ipfabrictransformmap_list"


class IPFabricTransformMapDeleteView(generic.ObjectDeleteView):
    queryset = IPFabricTransformMap.objects.all()
    default_return_url = "plugins:ipfabric_netbox:ipfabrictransformmap_list"


class IPFabricTransformMapBulkDeleteView(generic.BulkDeleteView):
    queryset = IPFabricTransformMap.objects.all()
    table = IPFabricTransformMapTable


@register_model_view(IPFabricTransformMap)
class IPFabricTransformMapView(generic.ObjectView):
    queryset = IPFabricTransformMap.objects.all()


# Transform Map Field


class IPFabricTransformFieldListView(generic.ObjectListView):
    queryset = IPFabricTransformField.objects.all()
    table = IPFabricTransformFieldTable


@register_model_view(IPFabricTransformField, "edit")
class IPFabricTransformFieldEditView(generic.ObjectEditView):
    queryset = IPFabricTransformField.objects.all()
    form = IPFabricTransformFieldForm


class IPFabricTransformFieldDeleteView(generic.ObjectDeleteView):
    queryset = IPFabricTransformField.objects.all()


@register_model_view(IPFabricTransformMap, "fields")
class IPFabricTransformFieldView(generic.ObjectChildrenView):
    queryset = IPFabricTransformMap.objects.all()
    child_model = IPFabricTransformField
    table = IPFabricTransformFieldTable
    template_name = "ipfabric_netbox/inc/transform_map_field_map.html"
    tab = ViewTab(
        label="Field Maps",
        badge=lambda obj: IPFabricTransformField.objects.filter(
            transform_map=obj
        ).count(),
        permission="ipfabric_netbox.view_ipfabrictransformfield",
    )

    def get_children(self, request, parent):
        return self.child_model.objects.filter(transform_map=parent)


# Snapshot


class IPFabricSnapshotListView(generic.ObjectListView):
    queryset = IPFabricSnapshot.objects.all()
    table = IPFabricSnapshotTable
    filterset = IPFabricSnapshotFilterSet
    filterset_form = IPFabricSnapshotFilterForm


@register_model_view(IPFabricSnapshot)
class IPFabricSnapshotView(generic.ObjectView):
    queryset = IPFabricSnapshot.objects.all()


class IPFabricSnapshotDeleteView(generic.ObjectDeleteView):
    queryset = IPFabricSnapshot.objects.all()


class IPFabricSnapshotBulkDeleteView(generic.BulkDeleteView):
    queryset = IPFabricSnapshot.objects.all()
    filterset = IPFabricSnapshotFilterSet
    table = IPFabricSnapshotTable


@register_model_view(IPFabricSnapshot, "data")
class IPFabricSnapshotRawView(generic.ObjectChildrenView):
    queryset = IPFabricSnapshot.objects.all()
    child_model = IPFabricData
    table = IPFabricDataTable
    template_name = "ipfabric_netbox/inc/snapshotdata.html"
    tab = ViewTab(
        label="Raw Data",
        badge=lambda obj: IPFabricData.objects.filter(snapshot_data=obj).count(),
        permission="ipfabric_netbox.view_ipfabricsnapshot",
        hide_if_empty=True,
    )

    def get_children(self, request, parent):
        return self.child_model.objects.filter(snapshot_data=parent)


class IPFabricSnapshotDataDeleteView(generic.ObjectDeleteView):
    queryset = IPFabricData.objects.all()


class IPFabricSnapshotDataBulkDeleteView(generic.BulkDeleteView):
    queryset = IPFabricData.objects.all()
    filterset = IPFabricDataFilterSet
    table = IPFabricDataTable


@register_model_view(
    IPFabricData,
    name="data",
    path="json",
    kwargs={},
)
class IPFabricSnapshotDataJSONView(LoginRequiredMixin, View):
    template_name = "ipfabric_netbox/inc/json.html"

    def get(self, request, **kwargs):
        print(kwargs)
        # change_id = kwargs.get("change_pk", None)

        if request.htmx:
            data = get_object_or_404(IPFabricData, pk=kwargs.get("pk"))
            return render(
                request,
                self.template_name,
                {
                    "object": data,
                },
            )

        #         return render(
        #             request,
        #             self.template_name,
        #             {
        #                 "change": change,
        #                 "prechange_data": prechange_data,
        #                 "postchange_data": postchange_data,
        #                 "diff_added": diff_added,
        #                 "diff_removed": diff_removed,
        #                 "size": "lg",
        #             },
        #         )


# Source


class IPFabricSourceListView(generic.ObjectListView):
    queryset = IPFabricSource.objects.annotate(
        snapshot_count=count_related(IPFabricSnapshot, "source")
    )
    filterset = IPFabricSourceFilterSet
    filterset_form = IPFabricSourceFilterForm
    table = IPFabricSourceTable


@register_model_view(IPFabricSource, "edit")
class IPFabricSourceEditView(generic.ObjectEditView):
    queryset = IPFabricSource.objects.all()
    form = IPFabricSourceForm


@register_model_view(IPFabricSource)
class IPFabricSourceView(generic.ObjectView):
    queryset = IPFabricSource.objects.all()

    def get_extra_context(self, request, instance):
        related_models = (
            (
                IPFabricSnapshot.objects.restrict(request.user, "view").filter(
                    source=instance
                ),
                "source_id",
            ),
        )

        job = instance.jobs.order_by("id").last()
        data = {"related_models": related_models, "job": job}
        if job:
            data["job_results"] = job.data
        return data


@register_model_view(IPFabricSource, "sync")
class IPFabricSourceSyncView(BaseObjectView):
    queryset = IPFabricSource.objects.all()

    def get_required_permission(self):
        return "ipfabric_netbox.sync_source"

    def get(self, request, pk):
        ipfabricsource = get_object_or_404(self.queryset, pk=pk)
        return redirect(ipfabricsource.get_absolute_url())

    def post(self, request, pk):
        ipfabricsource = get_object_or_404(self.queryset, pk=pk)
        job = ipfabricsource.enqueue_sync_job(request=request)

        messages.success(request, f"Queued job #{job.pk} to sync {ipfabricsource}")
        return redirect(ipfabricsource.get_absolute_url())


@register_model_view(IPFabricSource, "delete")
class IPFabricSourceDeleteView(generic.ObjectDeleteView):
    queryset = IPFabricSource.objects.all()


class IPFabricSourceBulkDeleteView(generic.BulkDeleteView):
    queryset = IPFabricSource.objects.all()
    filterset = IPFabricSourceFilterSet
    table = IPFabricSourceTable


# Sync
class IPFabricSyncListView(View):
    def get(self, request):
        syncs = IPFabricSync.objects.prefetch_related("snapshot_data")
        return render(
            request,
            "ipfabric_netbox/ipfabricsync_list.html",
            {"model": IPFabricSync, "syncs": syncs},
        )


@register_model_view(IPFabricSync, "edit")
class IPFabricSyncEditView(generic.ObjectEditView):
    queryset = IPFabricSync.objects.all()
    form = IPFabricSyncForm

    def alter_object(self, obj, request, url_args, url_kwargs):
        obj.user = request.user
        return obj


@register_model_view(IPFabricSync)
class IPFabricSyncView(generic.ObjectView):
    queryset = IPFabricSync.objects.all()
    actions = ("edit",)

    def get(self, request, **kwargs):
        instance = self.get_object(**kwargs)
        last_ingestion = instance.ipfabricingestion_set.last()

        if request.htmx:
            response = render(
                request,
                "ipfabric_netbox/partials/sync_last_ingestion.html",
                {"last_ingestion": last_ingestion},
            )

            if instance.status not in ["queued", "syncing"]:
                messages.success(
                    request,
                    f"Ingestion ({instance.name}) {instance.status}. Ingestion {last_ingestion.name} {last_ingestion.job.status}.",
                )
                response["HX-Refresh"] = "true"
            return response

        return render(
            request,
            self.get_template_name(),
            {
                "object": instance,
                "tab": self.tab,
                **self.get_extra_context(request, instance),
            },
        )

    def get_extra_context(self, request, instance):
        if request.GET.get("format") in ["json", "yaml"]:
            format = request.GET.get("format")
            if request.user.is_authenticated:
                request.user.config.set("data_format", format, commit=True)
        elif request.user.is_authenticated:
            format = request.user.config.get("data_format", "json")
        else:
            format = "json"

        last_ingestion = instance.ipfabricingestion_set.last()

        return {"format": format, "last_ingestion": last_ingestion}


@register_model_view(IPFabricSync, "sync")
class IPFabricStartSyncView(BaseObjectView):
    queryset = IPFabricSync.objects.all()

    def get_required_permission(self):
        return "ipfabric_netbox.start_sync"

    def get(self, request, pk):
        ipfabric = get_object_or_404(self.queryset, pk=pk)
        return redirect(ipfabric.get_absolute_url())

    def post(self, request, pk):
        ipfabric = get_object_or_404(self.queryset, pk=pk)
        job = ipfabric.enqueue_sync_job(user=request.user, adhoc=True)

        messages.success(request, f"Queued job #{job.pk} to sync {ipfabric}")
        return redirect(ipfabric.get_absolute_url())


@register_model_view(IPFabricSync, "delete")
class IPFabricSyncDeleteView(generic.ObjectDeleteView):
    queryset = IPFabricSync.objects.all()
    default_return_url = "plugins:ipfabric_netbox:ipfabricsync_list"


class IPFabricSyncBulkDeleteView(generic.BulkDeleteView):
    queryset = IPFabricSync.objects.all()
    filterset = IPFabricSnapshotFilterSet
    table = IPFabricSnapshotTable


# Ingestion
class IPFabricIngestionListView(generic.ObjectListView):
    queryset = IPFabricIngestion.objects.annotate(
        description=models.F("branch__description"),
        user=models.F("sync__user__username"),
        staged_changes=models.Count(models.F("branch__changediff")),
    )
    filterset = IPFabricIngestionFilterSet
    filterset_form = IPFabricIngestionFilterForm
    table = IPFabricIngestionTable


@register_model_view(
    IPFabricIngestion,
    name="logs",
    path="logs",
)
class IPFabricIngestionLogView(LoginRequiredMixin, View):
    template_name = "ipfabric_netbox/partials/ingestion_all.html"

    def get(self, request, **kwargs):
        ingestion_id = kwargs.get("pk")
        if request.htmx:
            ingestion = IPFabricIngestion.objects.get(pk=ingestion_id)
            data = ingestion.get_statistics()
            data["object"] = ingestion
            data["job"] = ingestion.jobs.first()
            response = render(
                request,
                self.template_name,
                data,
            )
            if ingestion.job.completed:
                response["HX-Refresh"] = "true"
                return response
            else:
                return response


@register_model_view(IPFabricIngestion)
class IPFabricIngestionView(generic.ObjectView):
    queryset = IPFabricIngestion.objects.annotate(
        num_created=models.Count(
            "branch__changediff",
            filter=models.Q(
                branch__changediff__action=ObjectChangeActionChoices.ACTION_CREATE
            )
            & ~models.Q(branch__changediff__object_type__model="objectchange"),
        ),
        num_updated=models.Count(
            "branch__changediff",
            filter=models.Q(
                branch__changediff__action=ObjectChangeActionChoices.ACTION_UPDATE
            )
            & ~models.Q(branch__changediff__object_type__model="objectchange"),
        ),
        num_deleted=models.Count(
            "branch__changediff",
            filter=models.Q(
                branch__changediff__action=ObjectChangeActionChoices.ACTION_DELETE
            )
            & ~models.Q(branch__changediff__object_type__model="objectchange"),
        ),
        description=models.F("branch__description"),
        user=models.F("sync__user__username"),
        staged_changes=models.Count(models.F("branch__changediff")),
    )

    def get_extra_context(self, request, instance):
        data = instance.get_statistics()
        return data


@register_model_view(IPFabricIngestion, "merge")
class IPFabricIngestionMergeView(BaseObjectView):
    queryset = IPFabricIngestion.objects.annotate(
        description=models.F("branch__description"),
        user=models.F("sync__user__username"),
        staged_changes=models.Count(models.F("branch__changediff")),
    )
    template_name = "ipfabric_netbox/inc/merge_form.html"
    form = IPFabricIngestionMergeForm

    def get_required_permission(self):
        return "ipfabric_netbox.merge_ingestion"

    def get(self, request, pk):
        obj = get_object_or_404(self.queryset, pk=pk)

        if request.htmx:
            viewname = get_viewname(self.queryset.model, action="merge")
            form_url = reverse(viewname, kwargs={"pk": obj.pk})
            form = self.form(initial=request.GET)
            return render(
                request,
                "ipfabric_netbox/inc/merge_form.html",
                {
                    "object": obj,
                    "object_type": self.queryset.model._meta.verbose_name,
                    "form": form,
                    "form_url": form_url,
                    **self.get_extra_context(request, obj),
                },
            )

        return redirect(obj.get_absolute_url())

    def post(self, request, pk):
        ingestion = get_object_or_404(self.queryset, pk=pk)
        form = self.form(request.POST)
        if form.is_valid():
            job = ingestion.enqueue_merge_job(
                user=request.user, remove_branch=form.cleaned_data["remove_branch"]
            )
            messages.success(request, f"Queued job #{job.pk} to sync {ingestion}")
            return redirect(ingestion.get_absolute_url())
        raise ValidationError("Form is not valid.")


@register_model_view(
    IPFabricIngestion,
    name="change_diff",
    path="change/<int:change_pk>",
    kwargs={"model": IPFabricIngestion},
)
class IPFabricIngestionChangesDiffView(LoginRequiredMixin, View):
    template_name = "ipfabric_netbox/inc/diff.html"

    def get(self, request, model, **kwargs):
        def _return_empty():
            return render(
                request,
                self.template_name,
                {
                    "change": None,
                    "prechange_data": None,
                    "postchange_data": None,
                    "diff_added": None,
                    "diff_removed": None,
                    "size": "lg",
                },
            )

        change_id = kwargs.get("change_pk", None)

        if not request.htmx:
            return _return_empty()
        if not change_id:
            return _return_empty()

        change = ChangeDiff.objects.get(pk=change_id)
        if change.original and change.modified:
            diff_added = shallow_compare_dict(
                change.original or dict(),
                change.modified or dict(),
                exclude=["last_updated"],
            )
            diff_removed = (
                {x: change.original.get(x) for x in diff_added}
                if change.modified
                else {}
            )
        else:
            diff_added = None
            diff_removed = None

        return render(
            request,
            self.template_name,
            {
                "change": change,
                "prechange_data": change.original,
                "postchange_data": change.modified,
                "diff_added": diff_added,
                "diff_removed": diff_removed,
                "size": "lg",
            },
        )


@register_model_view(IPFabricIngestion, "change")
class IPFabricIngestionChangesView(generic.ObjectChildrenView):
    queryset = IPFabricIngestion.objects.all()
    child_model = ChangeDiff
    table = IPFabricIngestionChangesTable
    filterset = IPFabricIngestionChangeFilterSet
    template_name = "generic/object_children.html"
    tab = ViewTab(
        label="Changes",
        badge=lambda obj: ChangeDiff.objects.filter(branch=obj.branch).count(),
        permission="ipfabric_netbox.view_ipfabricingestion",
    )

    def get_children(self, request, parent):
        return self.child_model.objects.filter(branch=parent.branch)


@register_model_view(IPFabricIngestion, "delete")
class IPFabricIngestionDeleteView(generic.ObjectDeleteView):
    queryset = IPFabricIngestion.objects.all()


@register_model_view(IPFabricSync, "ingestion")
class IPFabricIngestionTabView(generic.ObjectChildrenView):
    queryset = IPFabricSync.objects.all()
    child_model = IPFabricIngestion
    table = IPFabricIngestionTable
    filterset = IPFabricIngestionFilterSet
    template_name = "generic/object_children.html"
    tab = ViewTab(
        label="Ingestions",
        badge=lambda obj: IPFabricIngestion.objects.filter(sync=obj).count(),
        permission="ipfabric_netbox.view_ipfabricingestion",
    )

    def get_children(self, request, parent):
        return self.child_model.objects.filter(sync=parent).annotate(
            description=models.F("branch__description"),
            user=models.F("sync__user__username"),
            staged_changes=models.Count(models.F("branch__changediff")),
        )


@register_model_view(Device, "ipfabric")
class IPFabricTable(View):
    template_name = "ipfabric_netbox/ipfabric_table.html"
    tab = ViewTab("IP Fabric", permission="ipfabric_netbox.view_devicetable")

    def get(self, request, pk):
        device = get_object_or_404(Device, pk=pk)
        form = (
            IPFabricTableForm(request.GET)
            if "table" in request.GET
            else IPFabricTableForm()
        )
        data = None

        if form.is_valid():
            table = form.cleaned_data["table"]
            test = {
                "True": True,
                "False": False,
            }
            cache_enable = test.get(form.cleaned_data["cache_enable"])
            snapshot_id = ""

            if not form.cleaned_data["snapshot_data"]:
                snapshot_id = "$last"
                source = IPFabricSource.objects.get(
                    pk=device.custom_field_data["ipfabric_source"]
                )

            else:
                snapshot_id = form.cleaned_data["snapshot_data"].snapshot_id
                source = form.cleaned_data["snapshot_data"].source

            source.parameters["snapshot_id"] = snapshot_id
            source.parameters["base_url"] = source.url

            cache_key = (
                f"ipfabric_{table}_{device.serial}_{source.parameters['snapshot_id']}"
            )
            if cache_enable:
                data = cache.get(cache_key)

            if not data:
                try:
                    ipf = IPFabric(parameters=source.parameters)
                    raw_data, columns = ipf.get_table_data(table=table, device=device)
                    data = {"data": raw_data, "columns": columns}
                    cache.set(cache_key, data, 60 * 60 * 24)
                except Exception as e:
                    messages.error(request, e)

        if not data:
            data = {"data": [], "columns": []}

        table = DeviceIPFTable(data["data"], extra_columns=data["columns"])

        RequestConfig(
            request,
            {
                "paginator_class": EnhancedPaginator,
                "per_page": get_paginate_count(request),
            },
        ).configure(table)

        if request.htmx:
            return render(
                request,
                "htmx/table.html",
                {
                    "table": table,
                },
            )

        source = None

        if source_id := device.custom_field_data["ipfabric_source"]:
            source = IPFabricSource.objects.get(pk=source_id)

        return render(
            request,
            self.template_name,
            {
                "object": device,
                "source": source,
                "tab": self.tab,
                "form": form,
                "table": table,
            },
        )


@register_model_view(
    IPFabricSource,
    name="topology",
    path="topology/<int:site>",
    kwargs={"snapshot": ""},
)
class IPFabricSourceTopology(LoginRequiredMixin, View):
    template_name = "ipfabric_netbox/inc/site_topology_modal.html"

    def get(self, request, pk, site, **kwargs):
        if request.htmx:
            try:
                site = get_object_or_404(Site, pk=site)
                source_id = request.GET.get("source")
                if not source_id:
                    raise Exception("Source ID not available in request.")
                source = get_object_or_404(IPFabricSource, pk=source_id)
                snapshot = request.GET.get("snapshot")
                if not snapshot:
                    raise Exception("Snapshot ID not available in request.")

                source.parameters.update(
                    {"snapshot_id": snapshot, "base_url": source.url}
                )

                ipf = IPFabric(parameters=source.parameters)
                snapshot_data = ipf.ipf.snapshots.get(snapshot)
                if not snapshot_data:
                    raise Exception(
                        f"Snapshot ({snapshot}) not available in IP Fabric."  # noqa E713
                    )

                sites = ipf.ipf.inventory.sites.all(
                    filters={"siteName": ["eq", site.name]}
                )
                if not sites:
                    raise Exception(
                        f"{site.name} not available in snapshot ({snapshot})."  # noqa E713
                    )

                net = Network(sites=site.name, all_network=False)
                settings = NetworkSettings()
                settings.hide_protocol("xdp")
                settings.hiddenDeviceTypes.extend(["transit", "cloud"])

                link = ipf.ipf.diagram.share_link(net, graph_settings=settings)
                svg_data = ipf.ipf.diagram.svg(net, graph_settings=settings).decode(
                    "utf-8"
                )
                error = None
            except Exception as e:
                error = e
                svg_data = link = None

            return render(
                request,
                self.template_name,
                {
                    "site": site,
                    "source": source,
                    "svg": svg_data,
                    "size": "xl",
                    "link": link,
                    "time": timezone.now(),
                    "snapshot": snapshot_data,
                    "error": error,
                },
            )
