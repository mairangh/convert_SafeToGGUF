import os
import subprocess
import sys
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

LLAMA_DIR = os.path.join(SCRIPT_DIR, "llama.cpp")
INPUT_DIR = os.path.join(SCRIPT_DIR, "input")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

CONVERT_SCRIPT = os.path.join(LLAMA_DIR, "convert_hf_to_gguf.py")
QUANTIZE_BIN = os.path.join(LLAMA_DIR, "build", "bin", "llama-quantize")

QUANT_MAP = {
    "Q8": "Q8_0",
    "Q6": "Q6_K",
    "Q5": "Q5_K_M",
    "Q4": "Q4_K_M",
    "Q3": "Q3_K_M",
    "Q2": "Q2_K"
}

def run_command(command):
    try:
        print(f">>> Запуск: {' '.join(command)}")
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[Ошибка] Команда не удалась: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Конвертация и квантизация моделей")
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

    for d in [INPUT_DIR, OUTPUT_DIR]:
        os.makedirs(d, exist_ok=True)

    model_folders = [d for d in os.listdir(INPUT_DIR) if os.path.isdir(os.path.join(INPUT_DIR, d))]

    if not model_folders:
        print(f"--- Положи папку с моделью (с файлом config.json) в {INPUT_DIR} ---")
        return

    for model_name in model_folders:
        model_path = os.path.join(INPUT_DIR, model_name)

        temp_f16_path = os.path.join(OUTPUT_DIR, f"{model_name}_f16.gguf")
        final_quant_path = os.path.join(OUTPUT_DIR, f"{model_name}_{quant_type}.gguf")

        print(f"\n=== Обработка модели: {model_name} ===")

        if not os.path.exists(temp_f16_path):
            print(">>> Шаг 1: Конвертация в GGUF F16...")
            run_command([sys.executable, CONVERT_SCRIPT, model_path, "--outtype", "f16", "--outfile", temp_f16_path])
        else:
            print(">>> Шаг 1 пропущен (F16 файл уже существует)")

        print(f">>> Шаг 2: Квантование в {quant_type}...")
        actual_bin = QUANTIZE_BIN if os.path.exists(QUANTIZE_BIN) else QUANTIZE_BIN.replace("llama-quantize", "quantize")

        run_command([actual_bin, temp_f16_path, final_quant_path, quant_type])

        if os.path.exists(temp_f16_path) and os.path.exists(final_quant_path):
            os.remove(temp_f16_path)
            print(f">>> Временный файл {temp_f16_path} удален.")

        print(f"\n--- Успех! Модель готова: {final_quant_path} ---")

if __name__ == "__main__":
    main()
