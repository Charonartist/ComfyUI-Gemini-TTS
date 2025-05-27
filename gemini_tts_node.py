import os
import io
import base64
import tempfile
import json
import folder_paths
import requests
from datetime import datetime
import numpy as np
import torch
import torchaudio


class GeminiTTSNode:
    """
    Gemini Text-to-Speech Node for ComfyUI
    Google Cloud Text-to-Speech APIを使用してテキストから音声を生成します
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": "こんにちは、これはGemini TTSのテストです。",
                    "placeholder": "音声に変換したいテキストを入力してください"
                }),
                "voice_style": ([
                    "ja-JP-Neural2-A",  # 女性的で自然な声
                    "ja-JP-Neural2-B",  # 中性的でバランスの取れた声
                    "ja-JP-Neural2-C",  # 男性的で落ち着いた声
                    "ja-JP-Neural2-D",  # 深みのある男性的な声
                    "ja-JP-Wavenet-A",  # 高品質な女性的な声
                    "ja-JP-Wavenet-B",  # 高品質な女性的な声（異なるトーン）
                    "ja-JP-Wavenet-C",  # 高品質な男性的な声
                    "ja-JP-Wavenet-D",  # 高品質な男性的な声（異なるトーン）
                    "ja-JP-Standard-A", # 標準品質の女性的な声
                    "ja-JP-Standard-B", # 標準品質な女性的な声
                    "ja-JP-Standard-C", # 標準品質の男性的な声
                    "ja-JP-Standard-D"  # 標準品質の男性的な声
                ], {
                    "default": "ja-JP-Neural2-B"
                }),
                "speaking_rate": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.25,
                    "max": 4.0,
                    "step": 0.1,
                    "display": "slider"
                }),
                "pitch": ("FLOAT", {
                    "default": 0.0,
                    "min": -20.0,
                    "max": 20.0,
                    "step": 0.5,
                    "display": "slider"
                }),
                "volume_gain_db": ("FLOAT", {
                    "default": 0.0,
                    "min": -96.0,
                    "max": 16.0,
                    "step": 1.0,
                    "display": "slider"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "placeholder": "Google Cloud APIキーを入力してください"
                })
            },
            "optional": {
                "output_filename": ("STRING", {
                    "default": "",
                    "placeholder": "出力ファイル名（空の場合は自動生成）"
                }),
                "ssml_enabled": ("BOOLEAN", {
                    "default": False,
                    "label_on": "SSML有効",
                    "label_off": "プレーンテキスト"
                }),
                "audio_encoding": (["MP3", "WAV", "OGG"], {
                    "default": "MP3"
                })
            }
        }

    RETURN_TYPES = ("AUDIO", "STRING")
    RETURN_NAMES = ("audio", "file_path")
    FUNCTION = "generate_speech"
    CATEGORY = "audio"
    DESCRIPTION = "Google Cloud Text-to-Speech APIを使用してテキストから音声を生成します"

    def generate_speech(self, text, voice_style, speaking_rate, pitch, volume_gain_db, 
                       api_key, output_filename="", ssml_enabled=False, audio_encoding="MP3"):
        """
        Google Cloud Text-to-Speech APIを使用してテキストから音声を生成
        """
        try:
            # APIキーの検証
            if not api_key or api_key.strip() == "":
                raise ValueError("Google Cloud APIキーが設定されていません")

            # 出力ディレクトリの準備
            output_dir = folder_paths.get_output_directory()
            
            # ファイル拡張子の決定
            extension_map = {
                "MP3": ".mp3",
                "WAV": ".wav",
                "OGG": ".ogg"
            }
            file_ext = extension_map.get(audio_encoding, ".mp3")
            
            # ファイル名の生成
            if not output_filename or output_filename.strip() == "":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                voice_short = voice_style.split('-')[-1]  # 音声名の短縮版
                output_filename = f"gemini_tts_{voice_short}_{timestamp}{file_ext}"
            elif not output_filename.endswith(file_ext):
                output_filename += file_ext
            
            output_path = os.path.join(output_dir, output_filename)

            # Google Cloud Text-to-Speech API エンドポイント
            api_url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"
            
            # 音声設定の準備
            voice_gender = self._get_voice_gender(voice_style)
            
            # リクエストデータの準備
            request_data = {
                "input": {},
                "voice": {
                    "languageCode": "ja-JP",
                    "name": voice_style,
                    "ssmlGender": voice_gender
                },
                "audioConfig": {
                    "audioEncoding": audio_encoding,
                    "speakingRate": speaking_rate,
                    "pitch": pitch,
                    "volumeGainDb": volume_gain_db
                }
            }
            
            # テキスト入力の設定（SSML対応）
            if ssml_enabled:
                request_data["input"]["ssml"] = text
            else:
                request_data["input"]["text"] = text

            # APIリクエストの実行
            headers = {
                "Content-Type": "application/json"
            }
            
            print(f"Google Cloud TTS APIを呼び出しています...")
            print(f"音声: {voice_style}, 速度: {speaking_rate}, ピッチ: {pitch}")
            
            response = requests.post(api_url, json=request_data, headers=headers, timeout=30)
            
            if response.status_code != 200:
                # エラーレスポンスの詳細を取得
                try:
                    error_detail = response.json()
                    error_message = error_detail.get("error", {}).get("message", "Unknown error")
                except:
                    error_message = f"HTTP {response.status_code}: {response.text}"
                raise Exception(f"API request failed: {error_message}")
            
            # レスポンスからオーディオデータを取得
            response_data = response.json()
            audio_content = response_data.get("audioContent")
            
            if not audio_content:
                raise Exception("Audio content not found in API response")
            
            # Base64デコードして音声ファイルを保存
            audio_data = base64.b64decode(audio_content)
            
            with open(output_path, "wb") as f:
                f.write(audio_data)
            
            print(f"音声ファイルが生成されました: {output_path}")
            print(f"ファイルサイズ: {len(audio_data)} bytes")
            
            # ComfyUIのAUDIO形式で返す
            audio_tensor = self._load_audio_as_tensor(output_path)
            
            return (audio_tensor, output_path)
            
        except Exception as e:
            error_msg = f"Gemini TTS エラー: {str(e)}"
            print(error_msg)
            # エラー時は空の音声データを返す
            empty_audio = {
                "waveform": torch.zeros(1, 1000),
                "sample_rate": 24000
            }
            return (empty_audio, error_msg)

    def _get_voice_gender(self, voice_style):
        """
        音声スタイルから性別を推定
        """
        # A, Bは一般的に女性、C, Dは男性
        if voice_style.endswith('-A') or voice_style.endswith('-B'):
            return "FEMALE"
        elif voice_style.endswith('-C') or voice_style.endswith('-D'):
            return "MALE"
        else:
            return "NEUTRAL"

    def _load_audio_as_tensor(self, audio_path):
        """
        音声ファイルをComfyUI用のテンソルとして読み込み
        """
        try:
            # torchaudioを使用して音声を読み込み
            waveform, sample_rate = torchaudio.load(audio_path)
            
            # 1次元の場合は2次元に変換（モノラル音声対応）
            if waveform.dim() == 1:
                waveform = waveform.unsqueeze(0)  # [samples] -> [1, samples]
            
            # ComfyUIのAUDIO形式に合わせる（辞書形式）
            return {
                "waveform": waveform,
                "sample_rate": sample_rate
            }
            
        except Exception as e:
            print(f"音声ファイルの読み込みエラー: {e}")
            # エラー時は空のテンソルを返す（2次元）
            return {
                "waveform": torch.zeros(1, 1000),  # [channels, samples]
                "sample_rate": 24000
            }

    @classmethod
    def IS_CHANGED(cls, text, voice_style, speaking_rate, pitch, volume_gain_db, 
                   api_key, output_filename="", ssml_enabled=False, audio_encoding="MP3"):
        """
        ノードの入力が変更されたかどうかを判定
        """
        # 主要パラメータが変更された場合に再実行
        return hash((text, voice_style, speaking_rate, pitch, volume_gain_db, ssml_enabled, audio_encoding))

    @classmethod
    def VALIDATE_INPUTS(cls, text, voice_style, speaking_rate, pitch, volume_gain_db, 
                       api_key, **kwargs):
        """
        入力値の検証
        """
        if not text or text.strip() == "":
            return "テキストが空です"
        
        if not api_key or api_key.strip() == "":
            return "APIキーが設定されていません"
        
        if not (0.25 <= speaking_rate <= 4.0):
            return "話速は0.25〜4.0の範囲で設定してください"
        
        if not (-20.0 <= pitch <= 20.0):
            return "ピッチは-20.0〜20.0の範囲で設定してください"
        
        if not (-96.0 <= volume_gain_db <= 16.0):
            return "音量は-96.0〜16.0dBの範囲で設定してください"
        
        return True
