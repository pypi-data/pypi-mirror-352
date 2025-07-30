````markdown
# AiSummary

AiSummary is a lightweight Python library for text summarization, developed by **Mohammad Taha Gorji**. It provides two main summarization methods:

- **FastSummarizer**: A quick, frequency-based summarizer for English and Persian texts.
- **DeepSummarizer**: A deep-learning–based summarizer using BART (for English) and mT5 (for Persian), with automatic language detection and optional translation for other languages.

## PyPI

You can install the package from PyPI:

[AiSummary on PyPI](https://pypi.org/project/AiSummary)

---

## Features

- **FastSummarizer**  
  - Language-aware (detects English vs. Persian based on character heuristics).  
  - Ranks sentences by frequency score and selects top sentences.  
  - Iteratively shortens the summary until it fits under a maximum token/character limit.

- **DeepSummarizer**  
  - Detects input language (English, Persian, or others via `langdetect`).  
  - For English: uses a two-stage BART-based summarization (chunking + beam search).  
  - For Persian: uses a two-stage mT5-based summarization (hazm normalization + token chunking).  
  - For other languages: translates to English, summarizes, then translates back.  
  - Heavy models are loaded only on first invocation (lazy loading).  
  - Supports GPU (CUDA) if available.

- **Logging Control**  
  - Call `enable_logging(True)` or `enable_logging(False)` to toggle INFO-level logs.

---

## Installation

```bash
pip install AiSummary
````

### Requirements

The essential dependencies (in `install_requires`) are:

```plaintext
torch>=1.10.0
transformers>=4.0.0
langdetect>=1.0.9
googletrans>=4.0.0-rc1
spacy>=3.0.0
hazm>=0.7.0
sentencepiece>=0.1.95
```

If you plan to use `DeepSummarizer`, make sure you have a compatible version of PyTorch and CUDA (if you intend to use GPU acceleration). For `FastSummarizer`, spaCy will automatically download the English model (`en_core_web_sm`) on first use if it is not already installed.

---

## Usage

Below is a minimal example demonstrating how to use both summarizers.

```python
from AiSummary import FastSummarizer, DeepSummarizer, enable_logging

text = '''This Text ! A long text'''

# Enable INFO-level logging (optional)
enable_logging(True)

# Fast summarization
fast_summary = FastSummarizer(text)
print("Fast summary:", fast_summary)

# Deep summarization
deep_summary = DeepSummarizer(text)
print("Deep summary:", deep_summary)
```

### Examples

1. **English text**

   ```python
   from AiSummary import FastSummarizer, DeepSummarizer, enable_logging

   enable_logging(True)

   text_en = """
   Artificial intelligence (AI) refers to the simulation of human intelligence in machines 
   that are programmed to think like humans and mimic their actions. The term may also be 
   applied to any machine that exhibits traits associated with a human mind such as learning 
   and problem-solving.
   """

   fast_summary_en = FastSummarizer(text_en, percentage=0.3)
   print("Fast summary (EN):", fast_summary_en)

   deep_summary_en = DeepSummarizer(text_en)
   print("Deep summary (EN):", deep_summary_en)
   ```

2. **Persian text**

   ```python
   from AiSummary import FastSummarizer, DeepSummarizer, enable_logging

   enable_logging(True)

   text_fa = """
   هوش مصنوعی به شبیه‌سازی هوش انسان در ماشین‌ها اشاره دارد که برای تفکر مانند انسان و تقلید 
   از عملکردهای او برنامه‌ریزی شده‌اند. این اصطلاح ممکن است برای هر ماشینی که صفاتی مرتبط با 
   ذهن انسان مانند یادگیری و حل مسئله را نشان می‌دهد نیز به کار رود.
   """

   fast_summary_fa = FastSummarizer(text_fa, percentage=0.3)
   print("Fast summary (FA):", fast_summary_fa)

   deep_summary_fa = DeepSummarizer(text_fa)
   print("Deep summary (FA):", deep_summary_fa)
   ```

3. **Other language (e.g., Spanish)**

   ```python
   from AiSummary import FastSummarizer, DeepSummarizer, enable_logging

   enable_logging(True)

   text_es = """
   La inteligencia artificial (IA) se refiere a la simulación de la inteligencia humana en máquinas 
   programadas para pensar como humanos y emular sus acciones. El término también puede aplicarse 
   a cualquier máquina que exhiba rasgos asociados con la mente humana, como el aprendizaje y la 
   resolución de problemas.
   """

   # FastSummarizer will treat it as English or Persian depending on character heuristics,
   # so for non-Latin scripts it may translate under the hood if detected as neither.
   fast_summary_es = FastSummarizer(text_es, percentage=0.3)
   print("Fast summary (ES):", fast_summary_es)

   deep_summary_es = DeepSummarizer(text_es)
   print("Deep summary (ES):", deep_summary_es)
   ```

---

## Configuration

* **Logging**
  By default, logging is set to WARNING level (no INFO logs). To see detailed INFO logs (e.g., model-loading steps, language detection), call:

  ```python
  from AiSummary import enable_logging
  enable_logging(True)
  ```

* **DeepSummarizer Parameters**

  ```python
  DeepSummarizer(text: str, 
                 min1: int = 40, 
                 max1: int = 150, 
                 min2: int = 60, 
                 max2: int = 200) -> str
  ```

  * `min1`, `max1`: Minimum/maximum length (in tokens) for the first stage of summarization.
  * `min2`, `max2`: Minimum/maximum length (in tokens) for the second (final) stage.

* **FastSummarizer Parameters**

  ```python
  FastSummarizer(text: str, 
                 percentage: float = 0.2, 
                 max_tokens: int = 4000) -> str
  ```

  * `percentage`: Fraction of sentences (or scored segments) to include in the summary.
  * `max_tokens`: Maximum length of the returned summary (in characters).

---

## Project Structure

```plaintext
AiSummary/
├── summarizer.py        # Core implementation (FastSummarizer, DeepSummarizer, logger)
├── README.md            # This file
├── setup.py             # Package metadata and dependencies
└── LICENSE              # (Optional) License file if any
```

* `summarizer.py`: Contains all the functions and lazy-loading logic.
* `setup.py`: Points to `install_requires` (PyPI dependencies) and metadata like author, version, etc.
* `README.md`: Documentation and examples.

---

## License

This project is currently provided without a specific license. If you plan to use it in other projects, please contact **Mohammad Taha Gorji** for licensing details.

---

```
```
