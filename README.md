# Marp VoiceMovie Workspace

このワークスペースは、Marpを使用してスライドを作成し、音声と動画に変換するためのものです。
スライドの作成、音声の追加、動画への変換を行うためのタスクが設定されています。

現時点ではVOICEVOXのみを音声合成エンジンとして利用しているため、日本語のみの対応となります。

## 利用OSSについて

このワークスペースでは、代表的なものとして以下のOSSを使っています。（同梱はしていません）

- [Marp](https://marp.app/)
- [VOICEVOX](https://voicevox.hiroshiba.jp/)
    - デフォルトでのボイス： [VOICEVOX:ずんだもん](https://zunko.jp/con_ongen_kiyaku.html)

※ 本ワークスペースを用いた成果物を利用する際には、各OSSのライセンスに従ってください。特にVOICEVOXの音声を利用する場合は、VOICEVOXの利用規約に従ってください。

## つかいかた

このフォルダをVS Codeで開き、開発コンテナを起動します。

slide.md にスライドを作成します。

slide.md をVS Codeで開いた状態で、Ctrl + Shift + P を押してコマンドパレットを開き、「Tasks: Run Build Task」を選択します。  
（または、 Ctrl + Shift + B を押します。）

dist フォルダに、生成された音声ファイルや画像ファイル、動画ファイルが出力されます。

### カスタマイズ

.vscode の tasks.json を編集することで、タスクの設定を変更できます。

tasks.json から呼び出されるスクリプトは、 .devcontainer/app フォルダに格納しています。編集する場合、編集後に開発コンテナを再起動してください。
