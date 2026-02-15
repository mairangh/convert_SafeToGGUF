# convert_SafeToGGUF


```
git clone https://github.com/ggerganov/llama.cpp.git
cd ./llama.cpp
pip install -r requirements.txt
cmake -B build
cmake --build build --config Release -j $(nproc) --target llama-quantize
cd ..
```
```
python download_model.py Qwen/Qwen2.5-0.5B
```
```
python run.py Q8
```
```
python only_quantize.py Q6
```
