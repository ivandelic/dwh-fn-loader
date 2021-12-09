import json
import oci
import logging

logging.basicConfig(level=logging.DEBUG)

def putobject(bucketName, objectName, content):
    signer = oci.auth.signers.get_resource_principals_signer()
    client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
    namespace = client.get_namespace().data
    try:
        client.put_object(namespace, bucketName, objectName, content)
    except Exception as e:
        logging.getLogger().error(str(e.message))