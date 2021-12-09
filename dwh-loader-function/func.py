import io
import json
import logging
from fdk import response
import collections
import os
import datetime
import oci
import random
import string
from zipfile import ZipFile
import cx_Oracle

logging.basicConfig(level=logging.DEBUG)

defargs = {}
args = collections.ChainMap(os.environ, defargs)

dbwalletzip_location = "/tmp/dbwallet.zip"

def readobject(bucketName, objectName):
    signer = oci.auth.signers.get_resource_principals_signer()
    client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
    namespace = client.get_namespace().data
    try:
        obj = client.get_object(namespace, bucketName, objectName)
    except Exception as e:
        logging.getLogger().error(str(e.message))
        obj = None
    return obj

def get_dbwallet_from_autonomousdb():
    signer = oci.auth.signers.get_resource_principals_signer() 
    atp_client = oci.database.DatabaseClient(config={}, signer=signer)
    atp_wallet_pwd = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15)) # random string
    atp_wallet_details = oci.database.models.GenerateAutonomousDatabaseWalletDetails(password=atp_wallet_pwd)
    obj = atp_client.generate_autonomous_database_wallet(args.get("ADB_OCID"), atp_wallet_details)
    with open(dbwalletzip_location, 'w+b') as f:
        for chunk in obj.data.raw.stream(1024 * 1024, decode_content=False):
            f.write(chunk)
    with ZipFile(dbwalletzip_location, 'r') as zipObj:
            zipObj.extractall(args.get("TNS_ADMIN"))
    with open(args.get("TNS_ADMIN") + '/sqlnet.ora') as existingSqlnet:
        newContent = existingSqlnet.read().replace('DIRECTORY=\"?/network/admin\"', 'DIRECTORY=\"{}\"'.format(args.get("TNS_ADMIN")))
    with open(args.get("TNS_ADMIN") + '/sqlnet.ora', "w") as newSqlnet:
        newSqlnet.write(newContent)

def handler(ctx, data: io.BytesIO = None):
    try:
        eventbody = json.loads(data.getvalue())
        eventtype = eventbody.get("eventType")

        if eventtype is not None and eventtype == "com.oraclecloud.objectstorage.createobject":
            # Cloud Event is triggered
            stageobj = readobject(eventbody["data"]["additionalDetails"]["bucketName"], eventbody["data"]["resourceName"])
        else:
            # Manual trigger
            stageobj = readobject(args.get("bucketNameStaging"), args.get("objectNameStaging"))

        if stageobj.status == 200:
            xml = stageobj.data.text
            logging.getLogger().info("Found xml: " + str(xml))

            get_dbwallet_from_autonomousdb()
            dbpool = cx_Oracle.SessionPool(args.get("DB_USER"), args.get("DB_PASS"), args.get("DB_SERVICE"), min=1, max=1, encoding="UTF-8", nencoding="UTF-8")

            with dbpool.acquire() as dbconnection:
                with dbconnection.cursor() as dbcursor:
                    dbcursor.execute("INSERT INTO tradinghub VALUES ('" + str(xml) + "')")
                    dbconnection.commit()

            return response.Response(ctx, response_data=json.dumps({"Lake updated": str(xml)}), headers={"Content-Type": "application/json"})
        else:
            logging.getLogger().info("Unable to find staging object")
            return response.Response(ctx, response_data=json.dumps({"message": "Unable to find staging object"}), headers={"Content-Type": "application/json"})
    except (Exception, ValueError) as ex:
        logging.getLogger().error("error parsing json payload: " + str(ex))
        return response.Response(ctx, response_data=json.dumps({"message": "Error" + str(ex)}), headers={"Content-Type": "application/json"})
