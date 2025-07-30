import marshmallow as ma
from oarepo_model_builder.datatypes import (
    DataType,
    DataTypeComponent,
    ModelDataType,
    Section,
)
from oarepo_model_builder.datatypes.components import DefaultsModelComponent
from oarepo_model_builder.datatypes.components.model.utils import set_default
from oarepo_model_builder.datatypes.model import Link
from oarepo_model_builder.utils.links import url_prefix2link
from oarepo_model_builder.utils.python_name import Import

class RDMLinksComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    affects = [DefaultsModelComponent]

    def process_links(self, datatype, section: Section, **kwargs):

        if datatype.root.profile == "record":
            section.config.setdefault("links_item", {})
            section.config["links_item"] += [
                Link(
                    name="access_links",
                    link_class="RecordLink",
                    link_args=[
                        '"{+api}/records/{id}/access/links"',
                    ],
                    imports=[
                        Import("invenio_records_resources.services.RecordLink"),
                    ],
                ),
                Link(
                    name="access_grants",
                    link_class="RecordLink",
                    link_args=[
                        '"{+api}/records/{id}/access/grants"',
                    ],
                    imports=[
                        Import("invenio_records_resources.services.RecordLink"),
                    ],
                ),
                Link(
                    name="access_users",
                    link_class="RecordLink",
                    link_args=[
                        '"{+api}/records/{id}/access/users"',
                    ],
                    imports=[
                        Import("invenio_records_resources.services.RecordLink"),
                    ],
                ),
                Link(
                    name="access_groups",
                    link_class="RecordLink",
                    link_args=[
                        '"{+api}/records/{id}/access/groups"',
                        'when=_groups_enabled',
                    ],
                    imports=[
                        Import("invenio_records_resources.services.RecordLink"),
                        Import("invenio_rdm_records.services.config._groups_enabled"),
                    ],
                ),
            ]