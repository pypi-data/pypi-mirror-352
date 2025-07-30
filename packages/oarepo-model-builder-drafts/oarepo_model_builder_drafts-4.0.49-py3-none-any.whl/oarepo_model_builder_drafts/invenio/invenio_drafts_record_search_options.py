from oarepo_model_builder.datatypes.components.facets import FacetDefinition
from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder
from oarepo_model_builder.invenio.invenio_record_search_options import facet_data
from oarepo_model_builder.utils.python_name import Import


class InvenioRecordSearchOptionsBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "invenio_drafts_record_search_options"
    section = "search-options"
    template = "drafts-record-search-options"

    def finish(self, **extra_kwargs):
        facets = system_field_facets()
        facet_groups, default_group, sort_options = facet_data(
            facets, self.current_model
        )

        extra_kwargs["facet_groups"] = facet_groups
        extra_kwargs["default_group"] = default_group
        extra_kwargs["sort_definition"] = sort_options
        super().finish(**extra_kwargs)


def system_field_facets():
    return [
        FacetDefinition(
            path="record_status",
            dot_path="record_status",
            searchable=True,
            imports=[
                Import(
                    import_path="invenio_records_resources.services.records.facets.TermsFacet",
                    alias=None,
                )
            ],
            facet_groups={"_default": 100000},
            facet=None,
            field="TermsFacet(field='record_status', label =_('record_status'))",
        ),

        FacetDefinition(
            path="has_draft",
            dot_path="has_draft",
            searchable=True,
            imports=[
                Import(
                    import_path="invenio_records_resources.services.records.facets.TermsFacet",
                    alias=None,
                )
            ],
            facet_groups={"_default": 100000},
            facet=None,
            field="TermsFacet(field='has_draft', label =_('has_draft'))",
        ),

        FacetDefinition(
            path="expires_at",
            dot_path="expires_at",
            searchable=True,
            imports=[
                Import(
                    import_path="oarepo_runtime.services.facets.date.DateTimeFacet",
                    alias=None,
                )
            ],
            facet_groups={"_default": 100000},
            facet=None,
            field="DateTimeFacet(field='expires_at', label=_('expires_at.label'))",
        ),
        FacetDefinition(
            path="fork_version_id",
            dot_path="fork_version_id",
            searchable=True,
            imports=[
                Import(
                    import_path="invenio_records_resources.services.records.facets.TermsFacet",
                    alias=None,
                )
            ],
            facet_groups={"_default": 100000},
            facet=None,
            field="TermsFacet(field='fork_version_id', label=_('fork_version_id.label'))",
        ),
    ]
