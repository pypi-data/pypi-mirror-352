from oarepo_model_builder.datatypes import ModelDataType
from oarepo_model_builder.datatypes.components.model.search_options import (
    SearchOptionsModelComponent,
)
from oarepo_model_builder.datatypes.components.model.utils import set_default

from .defaults import DefaultsModelComponent


class DraftSearchOptionsModelComponent(SearchOptionsModelComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [DefaultsModelComponent]
    dependency_remap = SearchOptionsModelComponent

    def before_model_prepare(self, datatype, *, context, **kwargs):
        module = datatype.definition["module"]["qualified"]
        profile_module = context["profile_module"]

        record_draft_search_prefix = datatype.definition["module"]["prefix"]

        record_search_options = set_default(datatype, "search-options", {})
        module = record_search_options.setdefault(
            "module", f"{module}.services.{profile_module}.search"
        )
        record_search_options.setdefault(
            "class", f"{module}.{record_draft_search_prefix}SearchOptions"
        )
        if datatype.root.profile == "draft":
            record_search_options.setdefault(
                "base-classes",
                [
                    "invenio_drafts_resources.services.records.config.SearchDraftsOptions{InvenioSearchDraftsOptions}"
                ],
            )
        super().before_model_prepare(datatype, context=context, **kwargs)
