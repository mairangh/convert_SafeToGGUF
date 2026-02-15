import os
import subprocess
import sys
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

LLAMA_DIR = os.path.join(SCRIPT_DIR, "llama.cpp")
BUILD_DIR = os.path.join(LLAMA_DIR, "build")

TARGET_NAME = "llama-quantize"
QUANTIZE_BIN = os.path.join(BUILD_DIR, "bin", TARGET_NAME)

INPUT_DIR = os.path.join(SCRIPT_DIR, "input")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

QUANT_MAP = {
    "Q8": "Q8_0",
    "Q6": "Q6_K",
    "Q5": "Q5_K_M",
    "Q4": "Q4_K_M",
    "Q3": "Q3_K_M",
    "Q2": "Q2_K"
}

def run_command(command, cwd=None):
    try:
        subprocess.run(command, cwd=cwd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[Ошибка] Команда завершилась неудачно: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Квантизация GGUF моделей")
    parser.add_argument("quant_type", nargs="?", default="Q4",
                        help="Тип квантизации: Q8, Q6, Q5, Q4 (по умолчанию), Q3, Q2")
    args = parser.parse_args()

    quant_short = args.quant_type.upper()
    if quant_short not in QUANT_MAP:
        print(f"[Ошибка] Неизвестный тип квантизации: {quant_short}")
        print(f"Доступные варианты: {', '.join(QUANT_MAP.keys())}")
        sys.exit(1)

    quant_type = QUANT_MAP[quant_short]
    print(f">>> Используется квантизация: {quant_type}")

    if not os.path.exists(QUANTIZE_BIN):
        print(f"--- Начинаю сборку {TARGET_NAME} через CMake ---")

        if not os.path.exists(BUILD_DIR):
            os.makedirs(BUILD_DIR)

        print(">>> Конфигурация проекта...")
        run_command(["cmake", "-B", "build"], cwd=LLAMA_DIR)

        print(f">>> Компиляция бинарника {TARGET_NAME}...")
        try:
            run_command(["cmake", "--build", "build", "--config", "Release", "--target", TARGET_NAME, "-j"], cwd=LLAMA_DIR)
        except:
            print("!!! Не удалось собрать llama-quantize, пробуем старое имя 'quantize'...")
            run_command(["cmake", "--build", "build", "--config", "Release", "--target", "quantize", "-j"], cwd=LLAMA_DIR)
            globals()['QUANTIZE_BIN'] = os.path.join(BUILD_DIR, "bin", "quantize")

        print("--- Сборка завершена успешно. ---\n")

    for d in [INPUT_DIR, OUTPUT_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)

    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".gguf")]

    if not files:
        print(f"--- В папке {INPUT_DIR} нет файлов .gguf. Положи модель и запусти снова. ---")
        return

    for filename in files:
        input_path = os.path.join(INPUT_DIR, filename)
        output_filename = filename.replace(".gguf", f"_{quant_type}.gguf")
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        print(f"\n>>> Начинаю квантование: {filename} -> {quant_type}")

        actual_bin = QUANTIZE_BIN if os.path.exists(QUANTIZE_BIN) else os.path.join(BUILD_DIR, "bin", "quantize")

        cmd = [actual_bin, input_path, output_path, quant_type]
        run_command(cmd)

        print(f"\n--- Готово! Файл сохранен: {output_path} ---")

    print("\n[Все задачи выполнены]")

if __name__ == "__main__":
    main()
