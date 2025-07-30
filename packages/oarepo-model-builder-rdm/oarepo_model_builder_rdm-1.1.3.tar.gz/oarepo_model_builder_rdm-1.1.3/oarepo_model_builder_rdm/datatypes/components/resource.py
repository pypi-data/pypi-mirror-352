from oarepo_model_builder.datatypes import DataTypeComponent
from oarepo_model_builder.datatypes.components.model import ResourceModelComponent
from oarepo_model_builder.datatypes.model import ModelDataType

from oarepo_model_builder_rdm.datatypes.components.utils import replace_base_class

PLAIN_RECORD_RESOURCE = (
    "invenio_records_resources.resources.RecordResource"
)
DRAFT_RECORD_RESOURCE = (
    "invenio_drafts_resources.resources.RecordResource"
)
RDM_RECORD_RESOURCE = "oarepo_runtime.resources.resource.BaseRecordResource"

PLAIN_RESOURCE_CONFIG = (
    "invenio_records_resources.resources.RecordResourceConfig"
)
DRAFT_RESOURCE_CONFIG = "invenio_drafts_resources.resources.RecordResourceConfig"
RDM_RESOURCE_CONFIG = "oarepo_runtime.resources.config.BaseRecordResourceConfig"


class RDMResourceComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [ResourceModelComponent]

    def before_model_prepare(self, datatype, *, context, **kwargs):

        if datatype.profile not in ["record", "draft"]:
            return

        replace_base_class(
            datatype.definition["resource"],
            PLAIN_RECORD_RESOURCE,
            RDM_RECORD_RESOURCE,
        )

        replace_base_class(
            datatype.definition["resource"],
            DRAFT_RECORD_RESOURCE,
            RDM_RECORD_RESOURCE,
        )

        replace_base_class(
            datatype.definition["resource-config"],
            PLAIN_RESOURCE_CONFIG,
            RDM_RESOURCE_CONFIG,
        )

        replace_base_class(
            datatype.definition["resource-config"],
            DRAFT_RESOURCE_CONFIG,
            RDM_RESOURCE_CONFIG,
        )