from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType
from oarepo_model_builder.datatypes.components import RecordModelComponent
from oarepo_model_builder_drafts.datatypes.components import DraftRecordModelComponent

from .utils import replace_base_class


class RDMRecordModelComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [RecordModelComponent, DraftRecordModelComponent]

    def before_model_prepare(self, datatype, *, context, **kwargs):
        if datatype.root.profile == "draft":
            replace_base_class(  # is this needed in draft profile?
                datatype.definition["record"],
                "invenio_records_resources.records.api.Record{InvenioRecord}",
                "invenio_rdm_records.records.api.RDMDraft",
            )
            replace_base_class(
                datatype.definition["record"],
                "invenio_drafts_resources.records.api.Draft{InvenioDraft}",
                "invenio_rdm_records.records.api.RDMDraft",
            )

            datatype.definition["record"]["fields"]["media_files"] = (
                "FilesField("
                'key=MediaFilesAttrConfig["_files_attr_key"],'
                'bucket_id_attr=MediaFilesAttrConfig["_files_bucket_id_attr_key"],'
                'bucket_attr=MediaFilesAttrConfig["_files_bucket_attr_key"],'
                "store=False,"
                "dump=False,"
                "file_cls={{invenio_rdm_records.records.api.RDMMediaFileDraft}},"
                "create=False,"
                "delete=False,"
                ")"
            )
        elif datatype.root.profile == "record":
            replace_base_class(
                # is this needed in record profile?
                datatype.definition["record"],
                "invenio_drafts_resources.records.api.Record{InvenioRecord}",
                "invenio_rdm_records.records.api.RDMRecord",
            )
            replace_base_class(
                datatype.definition["record"],
                "invenio_records_resources.records.api.Record{InvenioRecord}",
                "invenio_rdm_records.records.api.RDMRecord",
            )
            datatype.definition["record"]["fields"]["media_files"] = (
                "FilesField("
                'key=MediaFilesAttrConfig["_files_attr_key"],'
                'bucket_id_attr=MediaFilesAttrConfig["_files_bucket_id_attr_key"],'
                'bucket_attr=MediaFilesAttrConfig["_files_bucket_attr_key"],'
                "store=False,"
                "dump=False,"
                "file_cls={{invenio_rdm_records.records.api.RDMMediaFileRecord}},"
                "create=False,"
                "delete=False,"
                ")"
            )
