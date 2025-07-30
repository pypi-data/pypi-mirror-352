from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType
from oarepo_model_builder.datatypes.components import PIDModelComponent


class RDMPIDModelComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [PIDModelComponent]

    def before_model_prepare(self, datatype, *, context, **kwargs):
        pid = datatype.definition["pid"]
        pid["provider-base-classes"].insert(0, "oarepo_runtime.records.pid_providers.UniversalPIDMixin")