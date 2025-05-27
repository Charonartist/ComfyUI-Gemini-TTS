# ComfyUI Gemini Text-to-Speech Node

Google Cloud Text-to-Speech APIを使用してテキストから音声を生成するComfyUIカスタムノードです。

## 機能

- **豊富な音声選択**: 12種類の日本語音声から選択可能
  - Neural2音声（高品質・自然）: A, B, C, D
  - Wavenet音声（高品質）: A, B, C, D  
  - Standard音声（標準品質）: A, B, C, D
- **詳細な音声制御**:
  - 話速: 0.25〜4.0倍
  - ピッチ: -20.0〜20.0
  - 音量: -96.0〜16.0dB
- **SSML対応**: 高度な音声制御マークアップ
- **複数フォーマット**: MP3, WAV, OGG出力
- **カスタムファイル名**: 自動生成または手動指定

## インストール

### ComfyUI Manager使用（推奨）

1. ComfyUI Managerで「ComfyUI-Gemini-TTS」を検索してインストール

### 手動インストール

1. ComfyUIのcustom_nodesフォルダにクローン：
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/Charonartist/ComfyUI-Gemini-TTS.git
   ```

2. 依存関係をインストール：
   ```bash
   cd ComfyUI-Gemini-TTS
   pip install -r requirements.txt
   ```

3. ComfyUIを再起動

## セットアップ

1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
2. Text-to-Speech APIを有効化  
3. APIキーを作成
4. ノードの`api_key`パラメータに設定

## 使用方法

1. ComfyUIワークフローに「Gemini Text-to-Speech」ノードを追加
2. パラメータを設定：
   - **text**: 音声に変換するテキスト
   - **voice_style**: 音声の種類
   - **speaking_rate**: 話速（1.0が標準）
   - **pitch**: ピッチ（0.0が標準）  
   - **volume_gain_db**: 音量（0.0が標準）
   - **api_key**: Google Cloud APIキー
   - **output_filename** (オプション): 出力ファイル名
   - **ssml_enabled** (オプション): SSML形式使用
   - **audio_encoding** (オプション): 音声フォーマット

## SSML例

```xml
<speak>
  こんにちは、<break time="500ms"/>
  <emphasis level="strong">強調</emphasis>されたテキストです。
  <prosody rate="slow" pitch="+2st">ゆっくりと高い声</prosody>
</speak>
```

## 注意事項

- Google Cloud Text-to-Speech APIの従量課金に注意
- APIキーは安全に管理してください
- ネットワーク接続が必要

## サンプルワークフロー

`sample_workflow.json`ファイルにサンプルワークフローが含まれています。ComfyUIにインポートして使用してください。

## ライセンス

MIT License

## 貢献

プルリクエストや改善提案を歓迎します。Issuesで報告してください。
