# iot-hub-messaging

Azure IoT Hub を使用して、IoT デバイスとクラウド間でメッセージの送受信を行います。

## アーキテクチャ図

[![architecture](./docs/images/architecture.png)](./docs/images/architecture.png)

## インフラ構築

### 1. Azure リソースの作成

```shell
cd infra

# リソースグループ作成
make create-resource-group

# CI テスト実行
make ci-test

# デプロイ
make deployment-create
```

### 2. 手動設定

#### デバイス ID の作成

[デバイス ID の作成と管理を行う](https://learn.microsoft.com/ja-jp/azure/iot-hub/create-connect-device?tabs=portal)を参考に、Azure Portal からデバイス ID を作成します。

デバイス側で実行するスクリプトとして [samples/async-hub-scenarios/receive_direct_method.py](https://github.com/Azure/azure-iot-sdk-python/blob/main/samples/async-hub-scenarios/receive_direct_method.py) を使用します。

発行したデバイス ID に対してダイレクトメソッドを呼び出して動作確認します。(動作確認のみであるためスキップしても問題ありません)

```shell
# Azure Portal からデバイス接続文字列を取得して環境変数に設定
export IOTHUB_DEVICE_CONNECTION_STRING="HostName=IOT_HUB_NAME.azure-devices.net;DeviceId={DEVICE_ID};SharedAccessKey={SHARED_ACCESS_KEY}"

# 仮想環境を作成
python3.10 -m venv .venv

# 仮想環境を有効化
source .venv/bin/activate

# パッケージのインストール
pip install azure-iot-device

# 依存関係の出力
# pip freeze > requirements.txt

# Direct Method の受信待ち
python receive_direct_method.py
```

デバイス側で受信待ちの状態になったら、Azure Portal からデバイスに対して direct method を送信します。

- [IoT Hub からのダイレクト メソッドの呼び出しについて](https://learn.microsoft.com/ja-jp/azure/iot-hub/iot-hub-devguide-direct-methods)

#### ファイルアップロード設定

[Azure IoT Hub を使用してデバイスからクラウドにファイルをアップロードする (Python) > IoT Hub への Azure Storage アカウントの関連付け](https://learn.microsoft.com/ja-jp/azure/iot-hub/file-upload-python#associate-an-azure-storage-account-to-iot-hub)を参考に IoT Hub と Azure Storage の関連付けを行います。

関連付けが完了したら、ファイルアップロードの動作確認を行います。(動作確認のみであるためスキップしても問題ありません)

```shell
# Azure Portal からデバイス接続文字列を取得して環境変数に設定
export IOTHUB_DEVICE_CONNECTION_STRING="HostName=IOT_HUB_NAME.azure-devices.net;DeviceId={DEVICE_ID};SharedAccessKey={SHARED_ACCESS_KEY}"

# 先程の仮想環境を有効化
source .venv/bin/activate

# パッケージの追加インストール
pip install azure.storage.blob

# 依存関係の出力
# pip freeze > requirements.txt

# Azure Storage Blob にファイルをアップロード
python upload_file.py
```

## エッジ側のスクリプト開発

opencv-python を使用して、カメラ画像を取得して Azure IoT Hub に送信するスクリプトを開発します。

```shell
# パッケージの追加インストール
pip install opencv-python

# 依存関係の出力
# pip freeze > requirements.txt

# カメラの動作確認のため実行 (動作確認のみであるためスキップしても問題ありません)
python capture_image.py
python show_video.py

# Azure Portal からデバイス接続文字列を取得して環境変数に設定
export IOTHUB_DEVICE_CONNECTION_STRING="HostName=IOT_HUB_NAME.azure-devices.net;DeviceId={DEVICE_ID};SharedAccessKey={SHARED_ACCESS_KEY}"

# ファイルアップロード機能を実装したスクリプトを実行
python upload_image_direct_method.py
```

# References

- [Monitoring Azure IoT Hub](https://learn.microsoft.com/en-us/azure/iot-hub/monitor-iot-hub)
