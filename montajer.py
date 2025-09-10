import json
import time
from pathlib import Path

import typer

from src.montajer_utils import create_videos_with_image, clean_audiotrack
from src.subtitles_utils import SubtitlesConfig

app = typer.Typer()


@app.command(name='cleanup-audio')
def cleanup_audio(audio_path: str, output_path: str = typer.Option(None)):
    """Remove silence from an audio track."""
    if output_path:
        clean_audiotrack(audio_path, output_path)
    else:
        clean_audiotrack(audio_path)


@app.command(name="create-videos")
def create_videos(
    source_audio_folder_path: str = typer.Option(...),
    source_images_folder_path: str = typer.Option(...),
    output_video_folder_path: str = typer.Option(...),
    video_caption_text: str = typer.Option(...),
    subtitles_enabled: bool = typer.Option(False),
    subtitles_max_line_width: int = typer.Option(25),
    subtitles_max_line_count: int = typer.Option(2),
    subtitles_model: str = typer.Option("base"),
    subtitles_language: str = typer.Option(None),
    threads: int = typer.Option(1)
):
    """Create videos with background images and text captions."""
    start_time = time.time()
    create_videos_with_image(
        source_audio_folder_path,
        source_images_folder_path,
        output_video_folder_path,
        video_caption_text,
        subtitles_enabled,
        SubtitlesConfig(
            subtitles_max_line_width,
            subtitles_max_line_count,
            subtitles_model,
            subtitles_language
        ) if subtitles_enabled else None,
        threads
    )
    print(f"Общее время монтажа: {time.time() - start_time:.2f}")


def clean_subtitle_videos(folder_path):
    """
    Очищает временные файлы после создания видео.
    """
    folder = Path(folder_path)
    
    # Удаляем временные файлы с суффиксом '_subtitles'
    for f in folder.glob("*_subtitles.mp4"):
        f.unlink()  # удаление файла
        print(f"Deleted temporary file:  {f.name}")


@app.command(name="montage")
def montage(config: str = typer.Option(...)):
    """
    Производит монтаж в соответствии с заданными настройками.
    :param config Путь json-файла с конфигурацией
    """

    with open(config, 'r', encoding='utf-8') as file:
        config_data = json.load(file)
        task_type = config_data['task-type']
        if task_type == 'create-videos':
            create_videos(
                source_audio_folder_path=config_data['source-audio-folder-path'],
                source_images_folder_path=config_data['source-images-folder-path'],
                output_video_folder_path=config_data['output-video-folder-path'],
                video_caption_text=config_data['video-caption-text'],
                subtitles_enabled=config_data.get('subtitles-enabled', config_data.get('subtitles_enabled', False)),
                subtitles_max_line_width=config_data['subtitles-max-line-width'],
                subtitles_max_line_count=config_data['subtitles-max-line-count'],
                subtitles_model=config_data['subtitles-model'],
                subtitles_language=config_data['subtitles-language'],
                threads=config_data['threads']
            )
        elif task_type == 'cleanup-audio':
            cleanup_audio(config_data['audio-path'])
        else:
            raise ValueError("Неверный task-type")

    clean_subtitle_videos(config_data['output-video-folder-path'])


# TODO
# Add ui.
# Хочу, чтобы можно было запускать через консоль и выбирать опции.
# Обработать только аудио, создать видео, склеивать одно видео с другим
# команды для отдельного создания субтитров (из видео и из аудио)
if __name__ == '__main__':
    app()
