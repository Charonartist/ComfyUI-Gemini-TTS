"""
ComfyUI Gemini Text-to-Speech Node
Google Gemini APIを使用してテキストから音声を生成するカスタムノード
"""

from .gemini_tts_node import GeminiTTSNode

NODE_CLASS_MAPPINGS = {
    "GeminiTTSNode": GeminiTTSNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GeminiTTSNode": "Gemini Text-to-Speech",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
