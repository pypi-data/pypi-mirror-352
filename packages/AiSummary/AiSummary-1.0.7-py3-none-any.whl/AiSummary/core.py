# summarizer.py
from os import system

try:
    import logging
    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    from langdetect import detect
    from googletrans import Translator
    import re
    import spacy
    from spacy.lang.en.stop_words import STOP_WORDS
    from string import punctuation
    from heapq import nlargest
    from hazm import Normalizer, word_tokenize
except:
    system('pip install torch transformers langdetect googletrans spacy hazm sentencepiece')
    try:
        import logging
        import torch
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        from langdetect import detect
        from googletrans import Translator
        import re
        import spacy
        from spacy.lang.en.stop_words import STOP_WORDS
        from string import punctuation
        from heapq import nlargest
        from hazm import Normalizer, word_tokenize
    except:
        print("""
    Library Error!

        Please install libs with  
              
            pip install torch transformers langdetect googletrans spacy hazm sentencepiece
              
              
              """)
        exit()

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
_spacy_loaded = False
_en_tokenizer = None
_en_model = None
_fa_tokenizer = None
_fa_model = None
_nlp_en = None
_fa_normalizer = None
_translator = None

# Constants for model names and limits
_EN_MODEL_NAME = "facebook/bart-large-cnn"
_FA_MODEL_NAME = "nafisehNik/mt5-persian-summary"
_EN_MAX_POS = None
_EN_PAD_ID = None
_FA_MAX_POS = None
_FA_PAD_ID = None

def _load_deep_models():
    """
    Load models and tokenizers for DeepSummarizer.
    Only called when user invokes DeepSummarizer.
    """
    global _models_loaded, _en_tokenizer, _en_model, _fa_tokenizer, _fa_model
    global _EN_MAX_POS, _EN_PAD_ID, _FA_MAX_POS, _FA_PAD_ID, _translator
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

    # Persian Model
    logger.info(f"📥 Loading Persian model: {_FA_MODEL_NAME}")
    _fa_tokenizer = AutoTokenizer.from_pretrained(_FA_MODEL_NAME, use_fast=True)
    _fa_model = AutoModelForSeq2SeqLM.from_pretrained(_FA_MODEL_NAME).to(DEVICE)
    _fa_model.eval()
    if DEVICE == "cuda":
        _fa_model.half()
    _FA_MAX_POS = _fa_tokenizer.model_max_length
    _FA_PAD_ID = _fa_tokenizer.pad_token_id

    # Translator
    _translator = Translator()

    _models_loaded = True

def _load_spacy_and_hazm():
    """
    Load spaCy English model and Hazm normalizer for FastSummarizer.
    """
    global _spacy_loaded, _nlp_en, _fa_normalizer
    if _spacy_loaded:
        return

    try:
        _nlp_en = spacy.load("en_core_web_sm")
    except Exception:
        import subprocess
        subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
        _nlp_en = spacy.load("en_core_web_sm")
    _fa_normalizer = Normalizer()
    _spacy_loaded = True

# ----------------------------
# Helper Functions
# ----------------------------
def _translate_google(text: str, src_lang: str, tgt_lang: str) -> str:
    """
    Uses googletrans to translate text from `src_lang` to `tgt_lang`.
    """
    try:
        res = _translator.translate(text, src=src_lang, dest=tgt_lang)
        return res.text
    except Exception as e:
        logger.warning(f"⚠️ Google translation failed: {e}")
        return text

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
    Break text into chunks of max_chars, ensuring splits happen at spaces.
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
# Two-Stage Summarization
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

def _two_stage_summary_fa(
    text: str,
    min1: int,
    max1: int,
    min2: int,
    max2: int,
    max_chars: int,
    batch_size: int
) -> str:
    normalized = _fa_normalizer.normalize(text)
    raw_chunks = _chunk_text_by_chars(normalized, max_chars)

    ids_chunks = [
        _fa_tokenizer.encode(chunk, add_special_tokens=True)
        for chunk in raw_chunks
    ]
    intermediate = []
    for i in range(0, len(ids_chunks), batch_size):
        batch = ids_chunks[i : i + batch_size]
        intermediate.extend(
            _summarize_batch(
                model=_fa_model,
                tokenizer=_fa_tokenizer,
                ids_batch=batch,
                pad_id=_FA_PAD_ID,
                min_len=min1,
                max_len=max1
            )
        )

    merged = " ".join(intermediate)
    merged_ids = _fa_tokenizer.encode(merged, add_special_tokens=True)
    chunks2 = _chunk_ids(merged_ids, _FA_MAX_POS)

    finals = []
    for c in chunks2:
        finals.extend(
            _summarize_batch(
                model=_fa_model,
                tokenizer=_fa_tokenizer,
                ids_batch=[c],
                pad_id=_FA_PAD_ID,
                min_len=min2,
                max_len=max2
            )
        )

    final_text = " ".join(finals)
    final_ids = _fa_tokenizer.encode(final_text, add_special_tokens=True)

    if len(final_ids) > _FA_MAX_POS:
        truncated = final_ids[:_FA_MAX_POS]
        final_text = _summarize_batch(
            model=_fa_model,
            tokenizer=_fa_tokenizer,
            ids_batch=[truncated],
            pad_id=_FA_PAD_ID,
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
      - Detects language: if 'en' use two-stage BART, if 'fa' use two-stage mT5
      - Otherwise translate to English, summarize, translate back
      - Loads heavy models only on first invocation
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
    elif lang == "fa":
        return _two_stage_summary_fa(text, min1, max1, min2, max2, max_chars=3000, batch_size=8)
    else:
        logger.info(f"🌐 Translating from {lang} to en for summarization")
        text_en = _translate_google(text, src_lang=lang, tgt_lang="en")
        summary_en = _two_stage_summary_en(text_en, min1, max1, min2, max2, batch_size=8)
        logger.info(f"🌐 Translating summary back to {lang}")
        summary_src = _translate_google(summary_en, src_lang="en", tgt_lang=lang)
        return summary_src

def FastSummarizer(text: str, percentage: float = 0.2, max_tokens: int = 4000) -> str:
    """
    A fast, language-aware summarizer:
      - Detects if `text` is primarily English or Persian.
      - Uses frequency-based scoring + heapq to pick top sentences.
      - Iteratively truncates summary to be under `max_tokens` characters.
      - Loads spaCy and Hazm models only on first invocation.
    """
    if not text or len(text.strip()) == 0:
        return ""

    # Lazy load for fast summarizer
    _load_spacy_and_hazm()

    # Heuristic language detection
    persian_chars = sum(1 for ch in text if "\u0600" <= ch <= "\u06FF")
    lang = "fa" if persian_chars / max(len(text), 1) > 0.5 else "en"
    logger.info(f"🏷️ Detected language for FastSummarizer: {lang}")

    if lang == "en":
        doc = _nlp_en(text)
        freq = {}
        for tok in doc:
            w = tok.text.lower()
            if w in STOP_WORDS or w in punctuation:
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
        best_sents = nlargest(n, scores, key=scores.get)
        best_sents = sorted(best_sents, key=lambda s: s.start)
        summary = " ".join([s.text.strip() for s in best_sents])

    else:
        normalized_text = _fa_normalizer.normalize(text)
        tokens = word_tokenize(normalized_text)
        freq = {}
        for w in tokens:
            w_norm = w.lower().strip()
            if len(w_norm) < 2:
                continue
            freq[w_norm] = freq.get(w_norm, 0) + 1
        if not freq:
            return ""
        maxf = max(freq.values())
        for w in freq:
            freq[w] /= maxf

        paragraphs = normalized_text.split("\n\n")
        scores = {}
        for chunk in paragraphs:
            sents = re.split(r'(?<=[\.\?!])\s+', chunk)
            for sent in sents:
                tokens_sent = word_tokenize(_fa_normalizer.normalize(sent))
                if not tokens_sent:
                    continue
                score = sum(freq.get(tok.lower(), 0) for tok in tokens_sent)
                scores[sent] = score
        if not scores:
            return ""
        n = max(1, int(len(scores) * percentage))
        best = nlargest(n, scores, key=scores.get)
        summary = " ".join(best)

    if len(summary) > max_tokens:
        logger.info("🔄 Summary too long, re-summarizing to fit max_tokens")
        return FastSummarizer(summary, percentage=percentage, max_tokens=max_tokens)
    return summary
