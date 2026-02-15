import argparse
import os
from huggingface_hub import snapshot_download

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_INPUT_DIR = os.path.join(SCRIPT_DIR, "input")

def download_hf_model(repo_id):
    folder_name = repo_id.replace("/", "_")
    target_dir = os.path.join(BASE_INPUT_DIR, folder_name)

    print(f">>> Начинаю скачивание репозитория: {repo_id}")
    print(f">>> Путь сохранения: {os.path.abspath(target_dir)}")

    os.makedirs(target_dir, exist_ok=True)

    try:
        snapshot_download(
            repo_id=repo_id,
            local_dir=target_dir,
            local_dir_use_symlinks=False,
            ignore_patterns=["*.msgpack", "*.h5", "*.ot"],
            token=None
        )
        print(f"\n--- Успешно скачано в: {target_dir} ---")
    except Exception as e:
        print(f"\n[Ошибка] Не удалось скачать модель: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Скачивание моделей с Hugging Face")
    parser.add_argument("repo", help="ID репозитория (например: Qwen/Qwen3-0.5B)")

    args = parser.parse_args()
    download_hf_model(args.repo)
