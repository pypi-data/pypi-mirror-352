from oarepo_model_builder.datatypes import DataTypeComponent
from oarepo_model_builder.datatypes.components.model import ServiceModelComponent
from oarepo_model_builder.datatypes.model import ModelDataType
from oarepo_model_builder_files.datatypes.components import ParentRecordComponent

from .utils import replace_base_class

PLAIN_RECORD_SERVICE = (
    "invenio_records_resources.services.RecordService{InvenioRecordService}"
)
DRAFT_RECORD_SERVICE = (
    "invenio_drafts_resources.services.RecordService{InvenioRecordService}"
)
RDM_RECORD_SERVICE = "oarepo_runtime.services.service.SearchAllRecordsService"

PLAIN_SERVICE_CONFIG = (
    "invenio_records_resources.services.RecordServiceConfig{InvenioRecordServiceConfig}"
)
DRAFT_SERVICE_CONFIG = "invenio_drafts_resources.services.RecordServiceConfig{InvenioRecordDraftsServiceConfig}"
RDM_SERVICE_CONFIG = "invenio_rdm_records.services.config.RDMRecordServiceConfig"


class RDMServiceComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [ServiceModelComponent, ParentRecordComponent]

    def before_model_prepare(self, datatype, *, context, **kwargs):

        if datatype.profile not in ["record", "draft"]:
            return
        components_to_remove = [
            "{{oarepo_runtime.services.files.FilesComponent}}",
            "{{invenio_drafts_resources.services.records.components.DraftFilesComponent}}",
            "{{oarepo_runtime.services.components.OwnersComponent}}",
        ]
        datatype.service_config["components"] = [
            component
            for component in datatype.service_config["components"]
            if component not in components_to_remove
        ]
        replace_base_class(
            datatype.definition["service"], PLAIN_RECORD_SERVICE, RDM_RECORD_SERVICE
        )
        replace_base_class(
            datatype.definition["service"], DRAFT_RECORD_SERVICE, RDM_RECORD_SERVICE
        )

        replace_base_class(
            datatype.definition["service-config"],
            PLAIN_SERVICE_CONFIG,
            RDM_SERVICE_CONFIG,
        )
        replace_base_class(
            datatype.definition["service-config"],
            DRAFT_SERVICE_CONFIG,
            RDM_SERVICE_CONFIG,
        )
        datatype.definition["service-config"]["base-classes"].insert(0, "oarepo_runtime.services.config.service.SearchAllConfigMixin")
