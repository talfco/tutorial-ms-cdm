# coding=utf-8
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator 0.17.0.0
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from .md_entity_properties import MDEntityProperties


class RelationshipProperties(MDEntityProperties):
    """Database properties.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :param origin_object_id: Entity object id maintained by the caller.
    :type origin_object_id: str
    :ivar object_id: Entity object id maintained by SyMS.
    :vartype object_id: str
    :ivar object_version: Entity object version maintained by SyMS.
    :vartype object_version: long
    :param publish_status: Possible values include: 'PUBLISHED'
    :type publish_status: str or :class:`PublishStatus
     <Microsoft.ADF.SyMSAPIClient.models.PublishStatus>`
    :param properties: Property bag
    :type properties: dict
    :param namespace:
    :type namespace: :class:`Namespace
     <Microsoft.ADF.SyMSAPIClient.models.Namespace>`
    :ivar from_table_id: From Table Id
    :vartype from_table_id: str
    :param from_table_name: From Table Name
    :type from_table_name: str
    :ivar to_table_id: To Table Id
    :vartype to_table_id: str
    :param to_table_name: To Table Name
    :type to_table_name: str
    :param relationship_type: Possible values include: 'ONETOONE',
     'ONETOMANY', 'MANYTOONE', 'MANYTOMANY'
    :type relationship_type: str or :class:`RelationshipType
     <Microsoft.ADF.SyMSAPIClient.models.RelationshipType>`
    :param column_relationship_informations: List of Column Relationships.
    :type column_relationship_informations: list of
     :class:`ColumnRelationshipInformation
     <Microsoft.ADF.SyMSAPIClient.models.ColumnRelationshipInformation>`
    """ 

    _validation = {
        'object_id': {'readonly': True},
        'object_version': {'readonly': True},
        'namespace': {'required': True},
        'from_table_id': {'readonly': True},
        'from_table_name': {'required': True},
        'to_table_id': {'readonly': True},
        'to_table_name': {'required': True},
        'column_relationship_informations': {'required': True},
    }

    _attribute_map = {
        'origin_object_id': {'key': 'OriginObjectId', 'type': 'str'},
        'object_id': {'key': 'ObjectId', 'type': 'str'},
        'object_version': {'key': 'ObjectVersion', 'type': 'long'},
        'publish_status': {'key': 'PublishStatus', 'type': 'PublishStatus'},
        'properties': {'key': 'Properties', 'type': '{object}'},
        'namespace': {'key': 'Namespace', 'type': 'Namespace'},
        'from_table_id': {'key': 'FromTableId', 'type': 'str'},
        'from_table_name': {'key': 'FromTableName', 'type': 'str'},
        'to_table_id': {'key': 'ToTableId', 'type': 'str'},
        'to_table_name': {'key': 'ToTableName', 'type': 'str'},
        'relationship_type': {'key': 'RelationshipType', 'type': 'RelationshipType'},
        'column_relationship_informations': {'key': 'ColumnRelationshipInformations', 'type': '[ColumnRelationshipInformation]'},
    }

    def __init__(self, namespace, from_table_name, to_table_name, column_relationship_informations, origin_object_id=None, publish_status=None, properties=None, relationship_type=None):
        super(RelationshipProperties, self).__init__(origin_object_id=origin_object_id, publish_status=publish_status, properties=properties)
        self.namespace = namespace
        self.from_table_id = None
        self.from_table_name = from_table_name
        self.to_table_id = None
        self.to_table_name = to_table_name
        self.relationship_type = relationship_type
        self.column_relationship_informations = column_relationship_informations
