# iot-hub-messaging

Azure IoT Hub を使用して、IoT デバイスとクラウド間でメッセージの送受信を行います。

## アーキテクチャ図

[![architecture](./docs/images/architecture.png)](./docs/images/architecture.png)

## インフラ構築

[Setup.md](https://github.com/Azure-Samples/MqttApplicationSamples/blob/main/Setup.md) の手順に従って、各種証明書を作成します。
ショートカットとして、以下のコマンドを実行します。

```shell
make resource-group
make event-grid

make create-certificate
make create-event-grid-certificate
make create-client-certificate
make create-event-grid-client

# to dump res_id
make info
res_id="/subscriptions/..."

# create permission bindings
az resource create --id "$res_id/permissionBindings/samplesPub" --properties '{
    "clientGroupName":"$all",
    "topicSpaceName":"samples",
    "permission":"Publisher"
}'
az resource create --id "$res_id/permissionBindings/samplesSub" --properties '{
    "clientGroupName":"$all",
    "topicSpaceName":"samples",
    "permission":"Subscriber"
}'

cd sample_client

# case1: local mosquitto
cp .env.sample sample_client/.env
# case2: event grid
cp .env.eg.sample sample_client/.env

# run getting started binary for Go
Azure-Samples/MqttApplicationSamples/scenarios/getting_started/go/bin/getting_started .env
```

[scenarios/getting_started](https://github.com/Azure-Samples/MqttApplicationSamples/tree/main/scenarios/getting_started#create-topic-spaces-and-permission-bindings) を参考に疎通確認をします。
