# Demo 1: Connect to the API with Functions
* [Functions](https://console.eu-frankfurt-1.oraclecloud.com/functions)
* [Functions Dev](https://docs.oracle.com/en-us/iaas/developer-tutorials/tutorials/functions/func-setup-cli/01-summary.htm#setup-functions-dev)
### Prepare context
```
fn list context
fn create context eu-frankfurt-1 --provider oracle
fn use context eu-frankfurt-1
fn update context oracle.compartment-id ocid1.compartment.oc1..aaaaaaaa2nxjnqpnaafi3ybwvifgg3mzpgrdztpp6ehk6gmg4w5bvasbst6q
fn update context api-url https://functions.eu-frankfurt-1.oraclecloud.com
fn update context registry fra.ocir.io/oraseemeaceeociworkshop/ivandelic/fn/techdata-demo
```
### Create Application in Console
```
fn create app <app-name> --annotation oracle.com/oci/subnetIds='["<subnet-ocid>"]'
fn create app metropole-app --annotation oracle.com/oci/subnetIds='["ocid1.subnet.oc1.eu-frankfurt-1.aaaaaaaavvofj2w65vvttuklkvg33zv77a7566hienkj5s32lwwrpgvqrbvq"]'
```

### Build api-consumer-function
Init:
```
fn init --runtime python api-consumer-function
```
Code:
```
pip install -r requirements.txt
env PYTHONPATH=. FDK_DEBUG=1 FN_FORMAT=http-stream FN_LISTENER=unix://tmp/func.sock fdk func.py
curl -v --unix-socket /tmp/func.sock -H "Fn-Call-Id: 0000000000000000" -H "Fn-Deadline: 2030-01-01T00:00:00.000Z" -XPOST http://function/call

```
Deploy:
```
fn -v deploy --app metropole-app
fn invoke metropole-app api-consumer-function
```
### Build transformation-function
Init:
```
fn init --runtime python transformation-function
```
Code:
```
pip install -r requirements.txt
env PYTHONPATH=. FDK_DEBUG=1 FN_FORMAT=http-stream FN_LISTENER=unix://tmp/func.sock fdk func.py
curl -v --unix-socket /tmp/func.sock -H "Fn-Call-Id: 0000000000000000" -H "Fn-Deadline: 2030-01-01T00:00:00.000Z" -XPOST http://function/call

```
Deploy:
```
fn -v deploy --app metropole-app
fn invoke metropole-app transformation-function
```
