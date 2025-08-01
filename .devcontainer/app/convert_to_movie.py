#!/usr/bin/env python3
"""
スライド画像と音声ファイルを結合してMP4動画を生成するスクリプト

使用方法:
    python convert_to_movie.py <入力フォルダパス> [出力ファイル名]

例:
    python convert_to_movie.py ./dist presentation.mp4
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Optional
import json

try:
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
except ImportError:
    print("Error: moviepyがインストールされていません。")
    print("次のコマンドでインストールしてください: pip install moviepy")
    sys.exit(1)


class SlideVideoGenerator:
    """スライド画像と音声を動画に変換するクラス"""
    
    def __init__(self, input_dir: str, verbose: bool = True):
        """
        初期化
        
        Args:
            input_dir: 画像と音声ファイルが格納されたディレクトリパス
            verbose: 詳細ログを表示するかどうか
        """
        self.input_dir = Path(input_dir)
        self.verbose = verbose
        
        if not self.input_dir.exists():
            raise FileNotFoundError(f"入力ディレクトリが存在しません: {input_dir}")
    
    def extract_number_from_filename(self, filename: str) -> Optional[int]:
        """
        ファイル名から数字を抽出する
        
        Args:
            filename: ファイル名
            
        Returns:
            抽出された数字（見つからない場合はNone）
        """
        # ファイル名から数字を全て抽出
        numbers = re.findall(r'\d+', filename)
        if numbers:
            # 最後の数字を使用（通常はページ番号）
            return int(numbers[-1])
        return None
    
    def find_matching_files(self) -> List[Tuple[Path, Path]]:
        """
        対応する画像ファイルと音声ファイルのペアを見つける
        
        Returns:
            (画像ファイル, 音声ファイル)のタプルのリスト（番号順）
        """
        # 画像ファイルを収集
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
        image_files = {}
        
        for ext in image_extensions:
            for img_file in self.input_dir.glob(f"*{ext}"):
                number = self.extract_number_from_filename(img_file.name)
                if number is not None:
                    image_files[number] = img_file
        
        # 音声ファイルを収集
        audio_extensions = {'.wav', '.mp3', '.aac', '.m4a', '.ogg'}
        audio_files = {}
        
        for ext in audio_extensions:
            for audio_file in self.input_dir.glob(f"*{ext}"):
                number = self.extract_number_from_filename(audio_file.name)
                if number is not None:
                    audio_files[number] = audio_file
        
        # ペアを作成
        pairs = []
        common_numbers = set(image_files.keys()) & set(audio_files.keys())
        
        if not common_numbers:
            raise ValueError("対応する画像と音声ファイルのペアが見つかりません")
        
        for number in sorted(common_numbers):
            pairs.append((image_files[number], audio_files[number]))
            if self.verbose:
                print(f"ペア {number:02d}: {image_files[number].name} + {audio_files[number].name}")
        
        if self.verbose:
            print(f"合計 {len(pairs)} ペアのファイルが見つかりました")
            
            # 見つからなかったファイルを報告
            missing_audio = set(image_files.keys()) - set(audio_files.keys())
            missing_images = set(audio_files.keys()) - set(image_files.keys())
            
            if missing_audio:
                print(f"警告: 音声ファイルが見つからない画像: {sorted(missing_audio)}")
            if missing_images:
                print(f"警告: 画像ファイルが見つからない音声: {sorted(missing_images)}")
        
        return pairs
    
    def create_slide_clip(self, image_path: Path, audio_path: Path) -> ImageClip:
        """
        単一スライドのクリップを作成
        
        Args:
            image_path: 画像ファイルのパス
            audio_path: 音声ファイルのパス
            
        Returns:
            作成されたビデオクリップ
        """
        if self.verbose:
            print(f"クリップ作成中: {image_path.name} + {audio_path.name}")
        
        # 音声の長さを取得
        audio_clip = AudioFileClip(str(audio_path))
        duration = audio_clip.duration
        
        if self.verbose:
            print(f"  音声長: {duration:.2f}秒")
        
        # 画像クリップを作成（音声の長さに合わせる）
        image_clip = ImageClip(str(image_path), duration=duration)
        
        # 音声を結合
        video_clip = image_clip.with_audio(audio_clip)
        
        return video_clip
    
    def generate_video(self, 
                      output_path: str = "presentation.mp4",
                      fps: int = 24,
                      resolution: Optional[Tuple[int, int]] = None,
                      codec: str = 'libx264',
                      audio_codec: str = 'aac',
                      pause_before: float = 0.75,
                      pause_after: float = 0.75) -> Path:
        """
        全スライドを結合して動画を生成
        
        Args:
            output_path: 出力ファイルパス
            fps: フレームレート
            resolution: 解像度 (width, height)。Noneの場合は元画像サイズ
            codec: 動画コーデック
            audio_codec: 音声コーデック
            pause_before: 各スライドの前に追加する間隔（秒）
            pause_after: 各スライドの後に追加する間隔（秒）
            
        Returns:
            生成された動画ファイルのパス
        """
        if self.verbose:
            print("=== スライド動画生成開始 ===")
        
        # ファイルペアを取得
        slide_pairs = self.find_matching_files()
        
        if not slide_pairs:
            raise ValueError("処理可能なファイルペアが見つかりません")
        
        clips = []
        total_duration = 0
        
        try:
            # 各スライドのクリップを作成
            for i, (image_file, audio_file) in enumerate(slide_pairs):
                if self.verbose:
                    print(f"\n[{i+1}/{len(slide_pairs)}] 処理中...")
                
                # 前の間隔を追加（最初のスライドには追加しない）
                if i > 0 and pause_before > 0:
                    pause_clip = ImageClip(str(image_file), duration=pause_before)
                    if resolution:
                        pause_clip = pause_clip.resized(resolution)
                    clips.append(pause_clip)
                    total_duration += pause_before
                    if self.verbose:
                        print(f"  前間隔: {pause_before}秒")
                
                clip = self.create_slide_clip(image_file, audio_file)
                
                # 解像度調整
                if resolution:
                    clip = clip.resized(resolution)
                
                clips.append(clip)
                total_duration += clip.duration
                
                # 後の間隔を追加（最後のスライドには追加しない）
                if i < len(slide_pairs) - 1 and pause_after > 0:
                    pause_clip = ImageClip(str(image_file), duration=pause_after)
                    if resolution:
                        pause_clip = pause_clip.resized(resolution)
                    clips.append(pause_clip)
                    total_duration += pause_after
                    if self.verbose:
                        print(f"  後間隔: {pause_after}秒")
            
            if self.verbose:
                print(f"\n全スライド処理完了。総時間: {total_duration:.2f}秒")
                print("動画ファイル生成中...")
            
            # クリップを結合
            final_video = concatenate_videoclips(clips, method="compose")
            
            # 出力パスを準備
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 動画ファイルを出力
            final_video.write_videofile(
                str(output_path),
                fps=fps,
                codec=codec,
                audio_codec=audio_codec,
            )
            
            if self.verbose:
                file_size = output_path.stat().st_size / (1024 * 1024)  # MB
                print(f"\n=== 生成完了 ===")
                print(f"出力ファイル: {output_path}")
                print(f"ファイルサイズ: {file_size:.2f} MB")
                print(f"総時間: {total_duration:.2f}秒")
                print(f"スライド数: {len(slide_pairs)}")
            
            return output_path
            
        finally:
            # メモリクリーンアップ
            if 'final_video' in locals():
                final_video.close()
            for clip in clips:
                try:
                    clip.close()
                except:
                    pass


def create_config_template(config_path: str):
    """設定ファイルのテンプレートを作成"""
    config = {
        "video_settings": {
            "fps": 24,
            "resolution": None,  # [1920, 1080] for 1080p, None for original
            "codec": "libx264",
            "audio_codec": "aac",
            "pause_before": 0.75,  # 各スライドの前の間隔（秒）
            "pause_after": 0.75    # 各スライドの後の間隔（秒）
        },
        "input_settings": {
            "image_extensions": [".png", ".jpg", ".jpeg"],
            "audio_extensions": [".wav", ".mp3", ".aac"]
        }
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"設定ファイルテンプレートを作成しました: {config_path}")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="スライド画像と音声ファイルをMP4動画に変換",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python convert_to_movie.py ./dist
  python convert_to_movie.py ./dist --output my_presentation.mp4
  python convert_to_movie.py ./dist --fps 30 --resolution 1920 1080
  python convert_to_movie.py ./dist --pause-before 1.0 --pause-after 0.5
  python convert_to_movie.py --create-config config.json
        """
    )
    
    parser.add_argument('input_dir', nargs='?', 
                       help='画像と音声ファイルが格納されたディレクトリ')
    parser.add_argument('-o', '--output', default='presentation.mp4',
                       help='出力動画ファイル名 (デフォルト: presentation.mp4)')
    parser.add_argument('--fps', type=int, default=24,
                       help='フレームレート (デフォルト: 24)')
    parser.add_argument('--resolution', nargs=2, type=int, metavar=('WIDTH', 'HEIGHT'),
                       help='出力解像度 例: --resolution 1920 1080')
    parser.add_argument('--codec', default='libx264',
                       help='動画コーデック (デフォルト: libx264)')
    parser.add_argument('--audio-codec', default='aac',
                       help='音声コーデック (デフォルト: aac)')
    parser.add_argument('--pause-before', type=float, default=0.75,
                       help='各スライドの前に追加する間隔（秒） (デフォルト: 0.75)')
    parser.add_argument('--pause-after', type=float, default=0.75,
                       help='各スライドの後に追加する間隔（秒） (デフォルト: 0.75)')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='詳細ログを非表示')
    parser.add_argument('--create-config', metavar='CONFIG_FILE',
                       help='設定ファイルテンプレートを作成して終了')
    
    args = parser.parse_args()
    
    # 設定ファイル作成モード
    if args.create_config:
        create_config_template(args.create_config)
        return
    
    # 入力ディレクトリが指定されていない場合
    if not args.input_dir:
        parser.error("入力ディレクトリが指定されていません")
    
    try:
        # 動画生成器を作成
        generator = SlideVideoGenerator(args.input_dir, verbose=not args.quiet)
        
        # 解像度設定
        resolution = tuple(args.resolution) if args.resolution else None
        
        # 動画生成実行
        output_file = generator.generate_video(
            output_path=args.output,
            fps=args.fps,
            resolution=resolution,
            codec=args.codec,
            audio_codec=args.audio_codec,
            pause_before=args.pause_before,
            pause_after=args.pause_after
        )
        
        print(f"\n✅ 動画生成が完了しました: {output_file}")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
