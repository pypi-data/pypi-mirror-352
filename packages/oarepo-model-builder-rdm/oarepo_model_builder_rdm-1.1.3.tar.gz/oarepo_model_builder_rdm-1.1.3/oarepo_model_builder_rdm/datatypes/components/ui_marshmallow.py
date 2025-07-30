from typing import Any

from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType
from oarepo_model_builder.datatypes.components import UIMarshmallowModelComponent

from .utils import replace_base_class


class RDMUIMarshmallowModelComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [UIMarshmallowModelComponent]

    def before_model_prepare(
        self, datatype: Any, *, context: dict[str, Any], **kwargs: Any
    ):
        if datatype.root.profile == "record":
            replace_base_class(
                datatype.definition["ui"]["marshmallow"],
                "oarepo_runtime.services.schema.ui.InvenioUISchema",
                "oarepo_runtime.services.schema.ui.InvenioRDMUISchema",
            )
