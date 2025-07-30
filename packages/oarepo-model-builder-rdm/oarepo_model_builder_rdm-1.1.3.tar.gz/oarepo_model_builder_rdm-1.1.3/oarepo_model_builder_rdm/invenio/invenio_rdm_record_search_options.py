from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder



class InvenioRDMRecordSearchOptionsBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "invenio_rdm_record_search_options"
    section = "search-options"
    template = "rdm-record-search-options"
