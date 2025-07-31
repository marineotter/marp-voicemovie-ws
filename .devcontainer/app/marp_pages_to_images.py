#!/usr/bin/env python3
"""
Marpスライドをページごとの画像に変換するスクリプト

このスクリプトは：
1. marp-cliコマンドを使用してMarpスライドをPNG画像に変換
2. ページごとの画像ファイルとして出力
3. 出力ディレクトリを指定可能

使用方法:
    python marp_page_to_images.py slide.md --utput-dir images/
"""

import subprocess
import sys
from pathlib import Path
import argparse
from typing import Optional


class MarpToImages:
    def __init__(self, output_dir: str = "/workspace/images"):
        """
        初期化
        
        Args:
            output_dir: 出力ディレクトリのパス
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
    def check_marp_cli_available(self) -> bool:
        """
        marp-cliの利用可能性をチェック
        
        Returns:
            bool: marp-cliが利用可能かどうか
        """
        try:
            print("marp-cliの利用可能性を確認中...")
            result = subprocess.run(
                ["npx", "-y", "@marp-team/marp-cli@latest", "--version"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"marp-cli利用可能 (バージョン: {result.stdout.strip()})")
                return True
            else:
                print(f"marp-cliチェックエラー: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("エラー: marp-cliの確認がタイムアウトしました")
            return False
        except FileNotFoundError:
            print("エラー: npxコマンドが見つかりません。Node.jsがインストールされているか確認してください")
            return False
        except Exception as e:
            print(f"エラー: marp-cliの確認中にエラーが発生しました: {e}")
            return False
    
    def convert_to_images(self, input_file: str) -> bool:
        """
        Marpスライドをページごとの画像に変換
        
        Args:
            input_file: 入力スライドファイルのパス
            
        Returns:
            bool: 成功したかどうか
        """
        input_path = Path(input_file)
        
        # 入力ファイルの存在確認
        if not input_path.exists():
            print(f"エラー: 入力ファイル '{input_file}' が見つかりません")
            return False
        
        try:
            print(f"Marpスライドを画像に変換中...")
            print(f"入力ファイル: {input_file}")
            print(f"出力ディレクトリ: {self.output_dir}")
            
            # marp-cliコマンドを実行
            # --images png: PNG画像として出力
            # -o: 出力ディレクトリを指定
            cmd = [
                "npx", "-y", "@marp-team/marp-cli@latest",
                "--images", "png",
                "-o", str((Path(self.output_dir) / "page.png").as_posix()),
                "--image-scale", "2",
                str(input_path)
            ]
            
            print(f"実行コマンド: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print("変換が正常に完了しました")
                if result.stdout:
                    print(f"出力: {result.stdout}")
                return True
            else:
                print(f"エラー: marp-cli実行に失敗しました (終了コード: {result.returncode})")
                if result.stderr:
                    print(f"エラー詳細: {result.stderr}")
                if result.stdout:
                    print(f"出力: {result.stdout}")
                return False
                
        except subprocess.TimeoutExpired:
            print("エラー: 画像変換がタイムアウトしました")
            return False
        except Exception as e:
            print(f"エラー: 画像変換中にエラーが発生しました: {e}")
            return False
    
    def list_generated_images(self) -> None:
        """
        生成された画像ファイルの一覧を表示
        """
        image_files = list(self.output_dir.glob("*.png"))
        
        if image_files:
            print(f"\n生成された画像ファイル ({len(image_files)}枚):")
            for image_file in sorted(image_files):
                file_size = image_file.stat().st_size
                print(f"  - {image_file.name} ({file_size:,} bytes)")
        else:
            print("\n生成された画像ファイルが見つかりません")
    
    def process_slide(self, input_file: str) -> None:
        """
        スライドファイルを処理して画像変換を実行
        
        Args:
            input_file: 入力スライドファイルのパス
        """
        print("=== Marpスライド → 画像変換開始 ===")
        
        # marp-cliの利用可能性確認
        if not self.check_marp_cli_available():
            print("エラー: marp-cliが利用できません")
            return
        
        # 画像変換実行
        if self.convert_to_images(input_file):
            print("\n=== 変換完了 ===")
            self.list_generated_images()
        else:
            print("\n=== 変換失敗 ===")
            print("変換に失敗しました。エラー内容を確認してください。")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Marpスライドをページごとの画像に変換",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s
  %(prog)s --input slide.md
  %(prog)s --input slide.md --output /path/to/images/
  %(prog)s -i slide.md -o images/
        """
    )
    
    parser.add_argument(
        "slide_file",
        nargs="?",
        default="/workspace/slide.md",
        help="入力するMarpスライドファイルのパス (デフォルト: /workspace/slide.md)"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        default="/workspace/images",
        help="出力ディレクトリのパス (デフォルト: /workspace/images)"
    )
    
    args = parser.parse_args()
    
    # 変換器を初期化して実行
    converter = MarpToImages(output_dir=args.output_dir)
    converter.process_slide(args.slide_file)


if __name__ == "__main__":
    main()
