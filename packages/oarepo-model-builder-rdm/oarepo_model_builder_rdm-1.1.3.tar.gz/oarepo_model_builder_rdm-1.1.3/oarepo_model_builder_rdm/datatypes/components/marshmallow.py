from typing import Any

from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType
from oarepo_model_builder.datatypes.components import MarshmallowModelComponent

from .utils import replace_base_class


class RDMMarshmallowModelComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [MarshmallowModelComponent]

    def before_model_prepare(
        self, datatype: Any, *, context: dict[str, Any], **kwargs: Any
    ):
        if datatype.root.profile == "record":
            replace_base_class(
                datatype.definition["parent-record-marshmallow"],
                "oarepo_workflows.services.records.schema.WorkflowParentSchema",
                "oarepo_workflows.services.records.schema.RDMWorkflowParentSchema",
            )
            replace_base_class(
                datatype.definition["marshmallow"],
                "oarepo_runtime.services.schema.marshmallow.BaseRecordSchema",
                "oarepo_runtime.services.schema.marshmallow.RDMBaseRecordSchema",
            )
