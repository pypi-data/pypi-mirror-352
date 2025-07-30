from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType
from oarepo_model_builder.datatypes.components import SearchOptionsModelComponent

from .utils import replace_base_class

PLAIN_SEARCH_OPTIONS = (
    "invenio_records_resources.services.SearchOptions{InvenioSearchOptions}"
)
RDM_SEARCH_OPTIONS = "oarepo_runtime.services.search.I18nRDMSearchOptions"

DRAFT_SEARCH_OPTIONS = "invenio_drafts_resources.services.records.config.SearchDraftsOptions{InvenioSearchDraftsOptions}"
RDM_DRAFT_SEARCH_OPTIONS = "oarepo_runtime.services.search.I18nRDMDraftsSearchOptions"


class RDMSearchOptionsModelComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [SearchOptionsModelComponent]

    def before_model_prepare(self, datatype, *, context, **kwargs):
        if datatype.root.profile == "record":
            module = datatype.definition["module"]["qualified"]
            record_search_prefix = datatype.definition["module"]["prefix"]
            datatype.definition["search-options"]["versions"] = {
                "class": f"{module}.{record_search_prefix}VersionsSearchOptions",
                "base-classes": [
                    "invenio_rdm_records.services.config.RDMSearchVersionsOptions"
                ],
            }
            replace_base_class(
                datatype.definition["search-options"],
                PLAIN_SEARCH_OPTIONS,
                RDM_SEARCH_OPTIONS,
            )

        elif datatype.root.profile == "draft":
            replace_base_class(
                datatype.definition["search-options"],
                DRAFT_SEARCH_OPTIONS,
                RDM_DRAFT_SEARCH_OPTIONS,
            )
