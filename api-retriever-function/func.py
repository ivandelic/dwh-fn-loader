import io
import json
import logging
from fdk import response
import collections
import os
import apimanager
import osmanager

logging.basicConfig(level=logging.DEBUG)


defargs = {
    'url': 'https://datenservice.tradinghub.eu/XmlInterface/getXML.ashx',
    'reportId': 'PricesEnergyImbalance',
    'start': '01-10-2021',
    'end': '31-10-2021'
}

def handler(ctx, data: io.BytesIO = None):
    payload = json.loads(data.getvalue())
    args = collections.ChainMap(payload, os.environ, defargs)

    uri = "{0}?ReportId={1}&Start={2}&End={3}".format(args.get("url"), args.get("reportId"), args.get("start"), args.get("end"))
    logging.getLogger().debug("Requested URI\n" + uri)

    content = apimanager.getApi(uri)
    logging.getLogger().debug("Response XML:\n" + str(content))

    if args.get("OCI_RESOURCE_PRINCIPAL_VERSION") is not None:
        osmanager.putobject(bucketName=args.get("bucketNameStaging"), objectName=args.get("objectNameStaging"), content=content)
        return response.Response(ctx, response_data=json.dumps({"message": "Function succesfully executed operation"}), headers={"Content-Type": "application/json"})

if __name__ == "__main__":
    handler(None, io.BytesIO(b"{\"url\": \"https://datenservice.tradinghub.eu/XmlInterface/getXML.ashx\",\"reportId\": \"PricesEnergyImbalance\",\"start\":\"01-10-2021\",\"end\":\"02-10-2021\"}"))