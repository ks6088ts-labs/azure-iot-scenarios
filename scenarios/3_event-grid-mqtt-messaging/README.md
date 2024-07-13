# event-grid-mqtt-messaging

Azure Event Grid を使用して、IoT デバイスとクラウド間で双方向通信を行います。

## アーキテクチャ図

[![architecture](./docs/images/architecture.png)](./docs/images/architecture.png)

## インフラ構築

[Setup.md](https://github.com/Azure-Samples/MqttApplicationSamples/blob/main/Setup.md) の手順に従って、各種証明書を作成し、[scenarios/getting_started](https://github.com/Azure-Samples/MqttApplicationSamples/tree/main/scenarios/getting_started#create-topic-spaces-and-permission-bindings) を参考に疎通確認をします。
手早く実行できるようにコードは [Makefile](./Makefile) に整理して `make` コマンドで実行できるようにしています。

**証明書を作成**

```shell
make create-certificate
make create-client-certificate
```

**Azure リソースを作成**

[main.parameters.bicepparam](./infra/main.parameters.bicepparam) の `encodedCertificate` パラメータの値を作成した中間 CA 証明書で上書きします。
以下のコマンドで出力される値をコピーして、 `encodedCertificate` パラメータの値を上書きします(FIXME: 自動化)。

```shell
cat ~/.step/certs/intermediate_ca.crt | tr -d "\n"
```

Azure リソースを作成します。

```shell
cd infra
make deploy
```

**MOSQUITTO の設定とサービス起動**

ローカル環境で検証する場合、MOSQUITTO をセットアップして、サービスを起動しておく必要があります。

```shell
# MOSQUITTO セットアップ
make mosquitto

# サービスの起動
make mosquitto-start
```

**動作検証**

`sample_client/event-grid.env` の MQTT_HOST_NAME を Azure Event Grid のホスト名で上書きします(FIXME: 自動化)。

サンプル CLI を使用して、IoT デバイスからのメッセージを受信します。

```shell
# CLI のビルド
go build -C go/ -o bin/egcli
```

```shell
cd sample_client

# ローカル環境上にホストされた Mosquitto との通信の場合
../go/bin/egcli getstarted local.env

# Event Grid との通信の場合
../go/bin/egcli getstarted event-grid.env
```
