# summarizer.py
from os import system

try:
    import logging
    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    from langdetect import detect
    from googletrans import Translator
except:
    system('pip install torch transformers langdetect googletrans')
    try:
        import logging
        import torch
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        from langdetect import detect
        from googletrans import Translator
    except:
        print("""
    Library Error!

        Please install libs with  
              
            pip install torch transformers langdetect googletrans
              
              
              """)
        exit()







# summarizer.py



# ----------------------------
# Logger Configuration
# ----------------------------
logger = logging.getLogger(__name__)
# Default: no logging (WARNING and above)
logger.setLevel(logging.WARNING)
_handler = logging.StreamHandler()
_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
_handler.setFormatter(_formatter)
logger.addHandler(_handler)

def enable_logging(enabled: bool):
    """
    Enable or disable logging for the summarizer library.
    """
    if enabled:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

# ----------------------------
# Device Setup
# ----------------------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ----------------------------
# Lazy-loaded Models & Tokenizers
# ----------------------------
_models_loaded = False
_en_tokenizer = None
_en_model = None
_translator = None

# Constant for English model name and limits
_EN_MODEL_NAME = "facebook/bart-large-cnn"
_EN_MAX_POS = None
_EN_PAD_ID = None

def _load_deep_models():
    """
    Load models and tokenizers for DeepSummarizer.
    Only called when user invokes DeepSummarizer.
    """
    global _models_loaded, _en_tokenizer, _en_model, _EN_MAX_POS, _EN_PAD_ID, _translator
    if _models_loaded:
        return

    logger.info(f"🔌 DeepSummarizer using device: {DEVICE}")

    # English Model
    logger.info(f"📥 Loading English model: {_EN_MODEL_NAME}")
    _en_tokenizer = AutoTokenizer.from_pretrained(_EN_MODEL_NAME, use_fast=True)
    _en_model = AutoModelForSeq2SeqLM.from_pretrained(_EN_MODEL_NAME).to(DEVICE)
    _en_model.eval()
    if DEVICE == "cuda":
        _en_model.half()
    _EN_MAX_POS = _en_model.config.max_position_embeddings
    _EN_PAD_ID = _en_tokenizer.pad_token_id

    # Translator
    _translator = Translator()

    _models_loaded = True

def _chunk_ids(ids: list[int], chunk_size: int) -> list[list[int]]:
    return [ids[i : i + chunk_size] for i in range(0, len(ids), chunk_size)]

def _summarize_batch(
    model: AutoModelForSeq2SeqLM,
    tokenizer: AutoTokenizer,
    ids_batch: list[list[int]],
    pad_id: int,
    min_len: int,
    max_len: int,
    num_beams: int = 4,
    length_penalty: float = 2.0,
    no_repeat_ngram_size: int = 3,
    early_stopping: bool = True
) -> list[str]:
    """
    Summarize batches of token ID lists with given model and tokenizer.
    """
    input_ids = torch.nn.utils.rnn.pad_sequence(
        [torch.tensor(ids, dtype=torch.long) for ids in ids_batch],
        batch_first=True,
        padding_value=pad_id
    ).to(DEVICE)
    attention_mask = input_ids.ne(pad_id).long()

    with torch.no_grad():
        if DEVICE == "cuda":
            with torch.cuda.amp.autocast():
                summary_ids = model.generate(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    max_length=max_len,
                    min_length=min_len,
                    num_beams=num_beams,
                    length_penalty=length_penalty,
                    no_repeat_ngram_size=no_repeat_ngram_size,
                    early_stopping=early_stopping
                )
        else:
            summary_ids = model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_length=max_len,
                min_length=min_len,
                num_beams=num_beams,
                length_penalty=length_penalty,
                no_repeat_ngram_size=no_repeat_ngram_size,
                early_stopping=early_stopping
            )

    return [
        tokenizer.decode(ids, skip_special_tokens=True).strip()
        for ids in summary_ids
    ]

def _chunk_text_by_chars(text: str, max_chars: int) -> list[str]:
    """
    Break text into chunks of max_chars، ensuring splits happen at spaces.
    """
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + max_chars, length)
        if end < length:
            last_space = text.rfind(" ", start, end)
            if last_space > start:
                end = last_space
        chunks.append(text[start:end])
        start = end
    return chunks

# ----------------------------
# Two-Stage Summarization (فقط انگلیسی)
# ----------------------------
def _two_stage_summary_en(
    text: str,
    min1: int,
    max1: int,
    min2: int,
    max2: int,
    batch_size: int
) -> str:
    tokens_all = _en_tokenizer.encode(text, add_special_tokens=True)
    chunks1 = _chunk_ids(tokens_all, _EN_MAX_POS)

    intermediate = []
    for i in range(0, len(chunks1), batch_size):
        batch = chunks1[i : i + batch_size]
        intermediate.extend(
            _summarize_batch(
                model=_en_model,
                tokenizer=_en_tokenizer,
                ids_batch=batch,
                pad_id=_EN_PAD_ID,
                min_len=min1,
                max_len=max1
            )
        )

    merged = " ".join(intermediate)
    merged_ids = _en_tokenizer.encode(merged, add_special_tokens=True)
    chunks2 = _chunk_ids(merged_ids, _EN_MAX_POS)

    finals = []
    for c in chunks2:
        finals.extend(
            _summarize_batch(
                model=_en_model,
                tokenizer=_en_tokenizer,
                ids_batch=[c],
                pad_id=_EN_PAD_ID,
                min_len=min2,
                max_len=max2
            )
        )

    final_text = " ".join(finals)
    final_ids = _en_tokenizer.encode(final_text, add_special_tokens=True)

    if len(final_ids) > _EN_MAX_POS:
        truncated = final_ids[:_EN_MAX_POS]
        final_text = _summarize_batch(
            model=_en_model,
            tokenizer=_en_tokenizer,
            ids_batch=[truncated],
            pad_id=_EN_PAD_ID,
            min_len=min2,
            max_len=max2
        )[0]

    return final_text

# ----------------------------
# Public API Functions
# ----------------------------
def DeepSummarizer(
    text: str,
    min1: int = 40,
    max1: int = 150,
    min2: int = 60,
    max2: int = 200
) -> str:
    """
    Universal Deep Summarizer:
      - Detects language: اگر 'en' باشد مستقیماً خلاصهٔ دو مرحله‌ای انگلیسی؛
        در غیر این صورت: ترجمه به انگلیسی، خلاصه‌سازی، ترجمه به مبدأ.
      - مدل‌های سنگین فقط در اولین فراخوانی لود می‌شوند.
    """
    if not text or len(text.strip()) == 0:
        return ""

    # Lazy load
    _load_deep_models()

    try:
        lang = detect(text)
    except:
        lang = "en"
    logger.info(f"🏷️ Detected language for DeepSummarizer: {lang}")

    if lang == "en":
        return _two_stage_summary_en(text, min1, max1, min2, max2, batch_size=8)
    else:
        logger.info(f"🌐 Translating from {lang} to en for summarization")
        text_en = _translator.translate(text, src=lang, dest="en").text
        summary_en = _two_stage_summary_en(text_en, min1, max1, min2, max2, batch_size=8)
        logger.info(f"🌐 Translating summary back to {lang}")
        summary_src = _translator.translate(summary_en, src="en", dest=lang).text
        return summary_src

def FastSummarizer(text: str, percentage: float = 0.2, max_tokens: int = 4000) -> str:
    """
    A fast, language-aware summarizer:
      - اگر متن انگلیسی باشد، با روش مبتنی بر فرکانسِ کلمات (spaCy) خلاصه می‌کند.
      - در غیر این صورت: اول متن را به انگلیسی ترجمه می‌کند، 
        FastSummarizer را روی متن انگلیسی اجرا می‌کند، 
        سپس خلاصه را به زبان مبدأ برمی‌گرداند.
      - spaCy و مدل‌های مربوط فقط در اولین فراخوانی لود می‌شوند.
    """
    if not text or len(text.strip()) == 0:
        return ""

    # Lazy load برای spaCy (انگلیسی)
    global _nlp_en, _spacy_loaded
    try:
        import spacy
        from spacy.lang.en.stop_words import STOP_WORDS
    except ImportError:
        raise RuntimeError("برای FastSummarizer ابتدا باید spaCy و مدل en_core_web_sm نصب شوند.")
    if '_spacy_loaded' not in globals() or not _spacy_loaded:
        try:
            _nlp_en = spacy.load("en_core_web_sm")
        except Exception:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
            _nlp_en = spacy.load("en_core_web_sm")
        _spacy_loaded = True

    # تشخیص زبان ساده
    try:
        lang = detect(text)
    except:
        lang = "en"
    logger.info(f"🏷️ Detected language for FastSummarizer: {lang}")

    if lang == "en":
        doc = _nlp_en(text)
        freq = {}
        for tok in doc:
            w = tok.text.lower()
            if w in STOP_WORDS or w in __import__('string').punctuation:
                continue
            freq[w] = freq.get(w, 0) + 1
        if not freq:
            return ""
        maxf = max(freq.values())
        for w in freq:
            freq[w] /= maxf

        scores = {}
        sentences = list(doc.sents)
        for s in sentences:
            for tok in s:
                w = tok.text.lower()
                if w in freq:
                    scores[s] = scores.get(s, 0) + freq[w]
        if not scores:
            return ""
        n = max(1, int(len(sentences) * percentage))
        from heapq import nlargest
        best_sents = nlargest(n, scores, key=scores.get)
        best_sents = sorted(best_sents, key=lambda s: s.start)
        summary = " ".join([s.text.strip() for s in best_sents])

        if len(summary) > max_tokens:
            logger.info("🔄 Summary too long, re-summarizing to fit max_tokens")
            return FastSummarizer(summary, percentage=percentage, max_tokens=max_tokens)
        return summary

    else:
        # برای همهٔ زبان‌های غیرانگلیسی (مثل فارسی)، مسیر ترجمه → خلاصه‌سازی انگلیسی → بازترجمه
        if not _models_loaded:
            _load_deep_models()
        logger.info(f"🌐 Translating from {lang} to en for fast summarization")
        text_en = _translator.translate(text, src=lang, dest="en").text
        summary_en = FastSummarizer(text_en, percentage=percentage, max_tokens=max_tokens)
        logger.info(f"🌐 Translating summary back to {lang}")
        summary_src = _translator.translate(summary_en, src="en", dest=lang).text
        return summary_src
