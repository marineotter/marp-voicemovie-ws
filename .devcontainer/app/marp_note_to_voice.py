#!/usr/bin/env python3
"""
Marpスライドのコメントをずんだもんボイスで音声変換するスクリプト

このスクリプトは：
1. slide.mdファイルからコメント（<!-- -->で囲まれた部分）を抽出
2. VOICEVOXコンテナのAPIを使用してずんだもんボイスで音声合成
3. ページごとの音声ファイル（WAV形式）として出力

使用方法:
    python marp_note_to_voice.py [スライドファイル] [--output-dir 出力ディレクトリ]
"""

import re
import json
import time
import argparse
import requests
from pathlib import Path
from typing import List, Tuple


class MarpToVoice:
    def __init__(self, voicevox_url: str = "http://voicevox:50021", output_dir: str = "/workspace/output"):
        """
        初期化
        
        Args:
            voicevox_url: VOICEVOXエンジンのURL
            output_dir: 出力ディレクトリのパス
        """
        self.voicevox_url = voicevox_url
        self.zundamon_speaker_id = 3  # ずんだもんのスピーカーID
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_comments_from_slide(self, slide_path: str) -> List[Tuple[int, str]]:
        """
        Marpスライドファイルからコメントを抽出
        
        Args:
            slide_path: スライドファイルのパス
            
        Returns:
            List[Tuple[int, str]]: (ページ番号, コメント内容)のリスト
        """
        try:
            with open(slide_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"エラー: ファイル '{slide_path}' が見つかりません")
            return []
        except Exception as e:
            print(f"エラー: ファイル読み込み中にエラーが発生しました: {e}")
            return []
        
        # スライドをページごとに分割（---で区切られている）
        slides = content.split('---')
        
        comments = []
        page_num = 0
        
        for slide in slides:
            # 空のスライドまたはヘッダー部分をスキップ
            if not slide.strip() or slide.strip().startswith('marp:'):
                continue
                
            page_num += 1
            
            # コメント部分を抽出（<!-- -->で囲まれた部分）
            comment_pattern = r'<!--\s*(.*?)\s*-->'
            matches = re.findall(comment_pattern, slide, re.DOTALL)
            
            if matches:
                # 複数のコメントがある場合は結合
                comment_text = ' '.join(matches).strip()
                if comment_text:
                    comments.append((page_num, comment_text))
                    print(f"ページ {page_num}: コメントを抽出しました")
        
        return comments
    
    def text_to_speech(self, text: str, page_num: int) -> bool:
        """
        テキストを音声に変換してファイルに保存
        
        Args:
            text: 音声変換するテキスト
            page_num: ページ番号
            
        Returns:
            bool: 成功したかどうか
        """
        try:
            # 1. 音声合成用のクエリを生成
            print(f"ページ {page_num}: 音声クエリを生成中...")
            audio_query_response = requests.post(
                f"{self.voicevox_url}/audio_query",
                params={"text": text, "speaker": self.zundamon_speaker_id},
                timeout=30
            )
            
            if audio_query_response.status_code != 200:
                print(f"エラー: 音声クエリ生成に失敗しました (ステータス: {audio_query_response.status_code})")
                return False
                
            audio_query = audio_query_response.json()
            
            # 2. 音声合成を実行
            print(f"ページ {page_num}: 音声合成中...")
            synthesis_response = requests.post(
                f"{self.voicevox_url}/synthesis",
                params={"speaker": self.zundamon_speaker_id},
                headers={"Content-Type": "application/json"},
                data=json.dumps(audio_query),
                timeout=60
            )
            
            if synthesis_response.status_code != 200:
                print(f"エラー: 音声合成に失敗しました (ステータス: {synthesis_response.status_code})")
                return False
            
            # 3. 音声ファイルを保存
            output_file = self.output_dir / f"slide_page_{page_num:02d}.wav"
            with open(output_file, 'wb') as f:
                f.write(synthesis_response.content)
            
            print(f"ページ {page_num}: 音声ファイルを保存しました -> {output_file}")
            return True
            
        except requests.exceptions.Timeout:
            print(f"エラー: ページ {page_num} の音声変換がタイムアウトしました")
            return False
        except requests.exceptions.ConnectionError:
            print(f"エラー: VOICEVOXサーバーに接続できません ({self.voicevox_url})")
            return False
        except Exception as e:
            print(f"エラー: ページ {page_num} の音声変換中にエラーが発生しました: {e}")
            return False
    
    def check_voicevox_connection(self) -> bool:
        """
        VOICEVOXサーバーとの接続確認
        
        Returns:
            bool: 接続できるかどうか
        """
        try:
            print("VOICEVOXサーバーとの接続を確認中...")
            response = requests.get(f"{self.voicevox_url}/version", timeout=10)
            if response.status_code == 200:
                version_info = response.json()
                print(f"VOICEVOX接続OK (バージョン: {version_info})")
                return True
            else:
                print(f"VOICEVOX接続エラー (ステータス: {response.status_code})")
                return False
        except Exception as e:
            print(f"VOICEVOX接続エラー: {e}")
            return False
    
    def process_slide(self, slide_path: str = "/workspace/slide.md"):
        """
        スライドファイルを処理してすべてのコメントを音声変換
        
        Args:
            slide_path: スライドファイルのパス
        """
        print("=== Marpスライド → ずんだもんボイス変換開始 ===")
        
        # VOICEVOXサーバーとの接続確認
        if not self.check_voicevox_connection():
            print("エラー: VOICEVOXサーバーに接続できません。コンテナが起動しているか確認してください。")
            return
        
        # コメント抽出
        comments = self.extract_comments_from_slide(slide_path)
        
        if not comments:
            print("コメントが見つかりませんでした。")
            return
        
        print(f"合計 {len(comments)} ページのコメントを見つけました。")
        
        # 音声変換処理
        success_count = 0
        total_count = len(comments)
        
        for page_num, comment_text in comments:
            print(f"\n--- ページ {page_num} の処理中 ---")
            print(f"テキスト: {comment_text[:100]}{'...' if len(comment_text) > 100 else ''}")
            
            if self.text_to_speech(comment_text, page_num):
                success_count += 1
                # 連続リクエストを避けるための待機
                time.sleep(0.5)
            else:
                print(f"ページ {page_num} の音声変換に失敗しました。")
        
        print(f"\n=== 変換完了 ===")
        print(f"成功: {success_count}/{total_count} ページ")
        print(f"出力先: {self.output_dir}")
        
        if success_count > 0:
            print("\n生成された音声ファイル:")
            for audio_file in sorted(self.output_dir.glob("slide_page_*.wav")):
                print(f"  - {audio_file.name}")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Marpスライドのコメントをずんだもんボイスで音声変換するスクリプト"
    )
    parser.add_argument(
        "slide_file",
        nargs="?",
        default="/workspace/slide.md",
        help="入力するMarpスライドファイルのパス (デフォルト: /workspace/slide.md)"
    )
    parser.add_argument(
        "--output-dir",
        default="/workspace/output",
        help="出力ディレクトリのパス (デフォルト: /workspace/output)"
    )
    
    args = parser.parse_args()
    
    converter = MarpToVoice(output_dir=args.output_dir)
    converter.process_slide(args.slide_file)


if __name__ == "__main__":
    main()