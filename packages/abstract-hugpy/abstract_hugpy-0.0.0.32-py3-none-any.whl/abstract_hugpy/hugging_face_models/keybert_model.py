import os
import re
from urllib.parse import quote
from collections import Counter
import torch
from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    LEDTokenizer,
    LEDForConditionalGeneration
)
from sentence_transformers import SentenceTransformer, models
from sentence_transformers.util import cos_sim
from keybert import KeyBERT
from config import DEFAULT_PATHS

# ------------------------------------------------------------------------------
# CONFIG / DEFAULT PATHS
# ------------------------------------------------------------------------------
DEFAULT_KEYBERT_PATH = DEFAULT_PATHS["keybert"]
DEFAULT_KEYBERT_PATH = DEFAULT_PATHS["keybert"]
SUMMARIZER_DIR = DEFAULT_PATHS["summarizer_t5"]
FLAN_MODEL_NAME = DEFAULT_PATHS["flan"]

# ------------------------------------------------------------------------------
# 1. SENTENCE-BERT + KEYBERT LOADING & ENCODING
# ------------------------------------------------------------------------------
def load_sentence_bert_model(model_path: str = None) -> SentenceTransformer:
    """
    Load a SentenceTransformer model that applies:
      1) Transformer (e.g. MiniLM-L6-v2) for token embeddings
      2) Mean pooling over token embeddings → one sentence vector
      3) L2-normalization → unit-length embeddings

    Args:
        model_path (str): Path to a local SBERT checkpoint (MiniLM-L6-v2).
                          Defaults to DEFAULT_KEYBERT_PATH.
    Returns:
        SentenceTransformer: A model that outputs normalized sentence embeddings.
    """
    path = model_path or DEFAULT_KEYBERT_PATH
    # 1) Transformer backbone
    word_embedding_model = models.Transformer(
        model_name_or_path=path,
        max_seq_length=256,
        do_lower_case=False
    )
    # 2) Pooling layer (mean over token embeddings)
    pooling_model = models.Pooling(
        word_embedding_model.get_word_embedding_dimension(),
        pooling_mode="mean"
    )
    # 3) Normalize layer (unit-length vectors)
    normalize_model = models.Normalize()
    return SentenceTransformer(modules=[word_embedding_model, pooling_model, normalize_model])

class nlpManager:
    def __init__(self):
        import spacy
        self.spacy = spacy
        self.nlp = self.spacy.load("en_core_web_sm")
class KeyBERTManager:
    """
    Manages a SentenceTransformer-backed KeyBERT model.
    """
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self._sbert = load_sentence_bert_model(model_path=self.model_path)
        self._keybert = KeyBERT(self._sbert)
        
    @property
    def sbert(self) -> SentenceTransformer:
        return self._sbert

    @property
    def keybert(self) -> KeyBERT:
        return self._keybert
    

def get_keybert_model(model_path: str = None) -> SentenceTransformer:
    """
    Convenience function to return the underlying SBERT model
    from a KeyBERTManager. If no manager exists, create one.

    Args:
        model_path (str): Optional override for the SBERT checkpoint path.

    Returns:
        SentenceTransformer: The SBERT model used by KeyBERT.
    """
    manager = KeyBERTManager(model_path=model_path)
    return manager.sbert


def encode_sentences(
    model: SentenceTransformer = None,
    sentences: list[str] = None,
    model_path: str = None
) -> torch.Tensor:
    """
    Encode a list of sentences (or documents) into normalized sentence embeddings.

    Args:
        model (SentenceTransformer): Pre-loaded SBERT model. If None, will load via get_keybert_model().
        sentences (list[str]): List of text strings to encode.
        model_path (str): Optional path override for SBERT.

    Returns:
        torch.Tensor: A [len(sentences) x D] tensor of embeddings, normalized to unit length.
    """
    m = model or get_keybert_model(model_path=model_path)
    return m.encode(
        sentences,
        convert_to_tensor=True,
        show_progress_bar=True,
        normalize_embeddings=True
    )


def compute_cosine_similarity(embeddings: torch.Tensor) -> torch.Tensor:
    """
    Given a batch of normalized embeddings, compute the full cosine similarity matrix.

    Args:
        embeddings (torch.Tensor): Tensor of shape [N, D], assumed L2-normalized.

    Returns:
        torch.Tensor: [N x N] matrix of cosine similarities.
    """
    return cos_sim(embeddings, embeddings)


def extract_keywords(
    text: str | list[str] = None,
    top_n: int = 5,
    diversity: float = 0.7,
    use_mmr: bool = True,
    stop_words: str = "english",
    keyphrase_ngram_range: tuple[int, int] = (1, 2),
    model: SentenceTransformer = None,
    model_path: str = None
) -> list[tuple[str, float]] | list[list[tuple[str, float]]]:
    """
    Extract keywords using KeyBERT over SBERT embeddings.

    Args:
        text (str or list[str]): A document (string) or a list of documents.
        top_n (int): Number of keywords to return (per document if list). Defaults to 5.
        diversity (float): MMR diversity (0.0–1.0). Defaults to 0.7.
        use_mmr (bool): Whether to use Maximal Marginal Relevance. Defaults to True.
        stop_words (str): Language for stop words (e.g. 'english'). Defaults to 'english'.
        keyphrase_ngram_range (tuple): Range of n-gram lengths for candidate phrases (min_n, max_n).
        model (SentenceTransformer): Pre-loaded SBERT model to use. If None, loads default via model_path.
        model_path (str): Path to a local SBERT checkpoint if model is None.

    Returns:
        If text is a str: List[ (keyword, score) ].
        If text is a list[str]: List of lists, where each inner list is [ (keyword, score) ] for that document.
    """
    if text is None or (isinstance(text, (str, list)) and not text):
        raise ValueError("No content provided for keyword extraction.")

    sbert_model = model or get_keybert_model(model_path=model_path)
    kw = KeyBERT(sbert_model)

    docs = text if isinstance(text, list) else [text]
    return kw.extract_keywords(
        docs,
        keyphrase_ngram_range=keyphrase_ngram_range,
        stop_words=stop_words,
        top_n=top_n,
        use_mmr=use_mmr,
        diversity=diversity
    )

# ------------------------------------------------------------------------------
# 2. SPACY-BASED RULED KEYWORD + DENSITY
# ------------------------------------------------------------------------------



def extract_keywords_nlp(text: str, top_n: int = 5) -> list[str]:
    """
    A rule-based method to extract high-frequency nouns, proper nouns, and multi-word named entities.

    Args:
        text (str): Input text.
        top_n (int): Number of top keywords to return. Defaults to 5.

    Returns:
        list[str]: The top_n keywords (strings) sorted by frequency.
    """
    if not isinstance(text, str):
        raise ValueError(f"extract_keywords_nlp expects a string, got {type(text)}")
    nlp_mgr = nlpManager()
    
    doc = nlp_mgr.nlp(text)
    # Count nouns/propers longer than 3 characters and not stop words
    word_counts = Counter(
        token.text.lower()
        for token in doc
        if token.pos_ in {"NOUN", "PROPN"} and not token.is_stop and len(token.text) > 3
    )
    # Count multi-word named entities of certain types
    entity_counts = Counter(
        ent.text.lower()
        for ent in doc.ents
        if len(ent.text.split()) >= 2 and ent.label_ in {"PERSON", "ORG", "GPE", "EVENT"}
    )

    # Merge counts, prioritizing entities
    combined = entity_counts + word_counts
    return [kw for kw, _ in combined.most_common(top_n)]


def calculate_keyword_density(text: str, keywords: list[str]) -> dict[str, float]:
    """
    Compute keyword density (%) for each keyword relative to total word count.

    Args:
        text (str): The full document text.
        keywords (list[str]): List of keywords (strings).

    Returns:
        dict[str, float]: Mapping from keyword → percentage of total words.
    """
    if not text:
        return {kw: 0.0 for kw in keywords}

    # Split on whitespace, strip punctuation
    words = [word.strip(".,!?;:()\"'").lower() for word in re.split(r"\s+", text) if word.strip()]
    total_words = len(words)
    if total_words == 0:
        return {kw: 0.0 for kw in keywords}

    density = {}
    for kw in keywords:
        count = words.count(kw.lower())
        density[kw] = (count / total_words) * 100 if total_words > 0 else 0.0
    return density


def refine_keywords(
    full_text: str,
    top_n: int = 10,
    use_mmr: bool = True,
    diversity: float = 0.5,
    keyphrase_ngram_range: tuple[int, int] = (1, 3),
    stop_words: str = "english",
    model: SentenceTransformer = None,
    model_path: str = None,
    info_data: dict = None
) -> dict:
    """
    Combine rule-based (spaCy) and embedding-based (KeyBERT) keywords, plus density statistics.

    Args:
        full_text (str): The full document text.
        top_n (int): Number of top keywords from each method. Defaults to 10.
        use_mmr (bool): Whether KeyBERT uses MMR. Defaults to True.
        diversity (float): MMR diversity parameter. Defaults to 0.5.
        keyphrase_ngram_range (tuple): Range of n-grams for KeyBERT. Defaults to (1, 3).
        stop_words (str): Stop words language for KeyBERT. Defaults to 'english'.
        model (SentenceTransformer): SBERT model for KeyBERT. If None, loaded via model_path.
        model_path (str): Path to SBERT checkpoint if model is None.
        info_data (dict): Optional dict to populate with results. If None, a new dict is created.

    Returns:
        dict containing:
            - "keywords_nlp": list[str]   → top nouns/entities by frequency
            - "keywords_keybert": list[tuple[str, float]] → top KeyBERT keyphrases + scores
            - "combined_keywords": list[str] → deduplicated, lowercase set of keywords (max top_n)
            - "keyword_density": dict[str, float] → density % for each combined keyword
    """
    if info_data is None:
        info_data = {}

    # 1) Rule-based extraction
    nlp_kws = extract_keywords_nlp(full_text, top_n=top_n)
    info_data["keywords_nlp"] = nlp_kws

    # 2) KeyBERT extraction
    keybert_kws = extract_keywords(
        text=full_text,
        top_n=top_n,
        diversity=diversity,
        use_mmr=use_mmr,
        stop_words=stop_words,
        keyphrase_ngram_range=keyphrase_ngram_range,
        model=model,
        model_path=model_path
    )
    # keybert_kws is List[ (phrase, score) ]; extract phrases
    keybert_phrases = [phrase for phrase, _ in keybert_kws]
    info_data["keywords_keybert"] = keybert_kws

    # 3) Merge and dedupe (lowercase)
    merged_set = set([kw.lower() for kw in nlp_kws] + [kp.lower() for kp in keybert_phrases])
    combined = list(merged_set)[:top_n]
    info_data["combined_keywords"] = combined

    # 4) Compute densities
    densities = calculate_keyword_density(full_text, combined)
    info_data["keyword_density"] = densities

    return info_data

# ------------------------------------------------------------------------------
# 3. LONGFORM SUMMARIZATION (T5 / FLAN / LED)
# ------------------------------------------------------------------------------

# 3.1. FLAN-BASED (google/flan-t5-xl) SUMMARIZER
class flanManager:
    def __init__(self,model_name:str=None):
        self.model_name = model or FLAN_MODEL_NAME
        self.flan_tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.flan_model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        self.flan_device = 0 if torch.cuda.is_available() else -1
        self.flan_summarizer = pipeline(
            "text2text-generation",
            model=self.flan_model,
            tokenizer=self.flan_tokenizer,
            device=self.flan_device
        )

def get_flan_sumarizer(model_name:str=None):
    flan_mgr = flanManager(model_name=model_name)
    return flan_mgr.flan_summarizer
def get_flan_summary(
    text: str,
    max_chunk: int = 512,
    max_length: int | None = None,
    min_length: int | None = None,
    do_sample: bool = False,
    model_name: str=None
) -> str:
    """
    Use google/flan-t5-xl to generate a human-like summary of an input text.

    Args:
        text (str): Input text to summarize.
        max_chunk (int): Maximum tokens for each chunk. Defaults to 512.
        max_length (int | None): Max tokens for generated summary. Defaults to 512.
        min_length (int | None): Min tokens for generated summary. Defaults to 100.
        do_sample (bool): Whether to sample. Defaults to False.

    Returns:
        str: The generated summary.
    """
    max_length = max_length or 512
    min_length = min_length or 100
    prompt = (
        f"Summarize the following text in a coherent, concise paragraph:\n\n{text}"
    )
    flan_sumarizer = get_flan_sumarizer(model_name=model_name)
    output = flan_summarizer(
        prompt,
        max_length=max_length,
        min_length=min_length,
        do_sample=do_sample
    )[0]["generated_text"]
    return output.strip()

class falconsManager:
    def __init__(self):
        self.falcons_summarizer = pipeline("summarization",model="Falconsai/text_summarization",device=0 if torch.cuda.is_available() else -1)
def get_falcons_sumarizer():
    falcons_mgr = falconsManager()
    return falcons_mgr.falcons_summarizer

def chunk_falcons_summaries(chunks, max_length=160, min_length=40, truncation=True):
    """
    Summarize each chunk using Falconsai/text_summarization.
    Returns a list of summary strings.
    """
    summaries = []
    falcons_sumarizer = get_falcons_sumarizer()
    for chunk in chunks:
        # The pipeline returns a list of dicts; [0]["summary_text"] is our text.
        out = falcons_summarizer(
            chunk,
            max_length=max_length,
            min_length=min_length,
            truncation=truncation
        )
        summaries.append(out[0]["summary_text"].strip())
    return summaries

class t5Manager:
    def __init__(self,model_directory:str=None):
        self.model_directory = model_directory or SUMMARIZER_DIR
        self.t5_tokenizer = AutoTokenizer.from_pretrained(self.model_directory)
        self.t5_model = AutoModelForSeq2SeqLM.from_pretrained(self.model_directory)
def get_t5_manager(model_directory:str=None):
    t5_mgr = t5Manager(model_directory=model_directory)
    return t5_mgr
def get_t5__tokenizer(model_directory:str=None):
    t5_mgr = get_t5_manager(model_directory=model_directory)
    return t5_mgr.t5_tokenizer
def get_t5_model(model_directory:str=None):
    t5_mgr = get_t5_manager(model_directory=model_directory)
    return t5_mgr.t5_model
# 3.2. CHUNK-BASED T5 SUMMARIZER (for arbitrarily long text)



def split_to_chunk(full_text: str, max_words: int = 300) -> list[str]:
    """
    Break a long text into smaller chunks (approximately max_words per chunk),
    splitting on sentence-like boundaries (". ").

    Args:
        full_text (str): The entire document text.
        max_words (int): Maximum words allowed in each chunk. Defaults to 300.

    Returns:
        list[str]: List of text chunks.
    """
    sentences = full_text.split(". ")
    chunks = []
    buffer = ""
    for sent in sentences:
        candidate = (buffer + sent).strip()
        if len(candidate.split()) <= max_words:
            buffer = candidate + ". "
        else:
            if buffer:
                chunks.append(buffer.strip())
            buffer = sent + ". "
    if buffer:
        chunks.append(buffer.strip())
    return chunks


def chunk_summaries(
    chunks: list[str],
    max_length: int = 160,
    min_length: int = 40,
    truncation: bool = False,
    model_directory:str=None
) -> list[str]:
    """
    Summarize each chunk individually using a T5-based summarizer,
    then return a list of summary strings.

    Args:
        chunks (list[str]): List of text chunks.
        max_length (int): Max output tokens per chunk summary.
        min_length (int): Min output tokens per chunk summary.
        truncation (bool): If True, enforce truncation of inputs that exceed model length.

    Returns:
        list[str]: Summaries for each chunk.
    """
    summaries = []
    t5_tokenizer = get_t5__tokenizer(model_directory=model_directory)
    t5_model = get_t5__tokenizer(model_directory=model_directory)
    for chunk in chunks:
        inputs = t5_tokenizer(
            chunk,
            return_tensors="pt",
            truncation=truncation,
            max_length=512
        )
        with torch.no_grad():
            outputs = t5_model.generate(
                inputs["input_ids"],
                max_length=max_length,
                min_length=min_length,
                num_beams=4,
                early_stopping=True
            )
        summary_text = t5_tokenizer.decode(outputs[0], skip_special_tokens=True)
        summaries.append(summary_text.strip())
    return summaries


def get_summary(
    full_text: str,
    max_words: int = 300,
    max_length: int = 160,
    min_length: int = 40,
    truncation: bool = False
) -> str:
    """
    Create a summary of arbitrarily long text by:
      1) Splitting into ~300-word chunks
      2) Summarizing each chunk individually (T5)
      3) Stitching chunk summaries back together into one paragraph

    Args:
        full_text (str): The entire document text.
        max_words (int): Maximum words per chunk. Defaults to 300.
        max_length (int): Max tokens per chunk summary. Defaults to 160.
        min_length (int): Min tokens per chunk summary. Defaults to 40.
        truncation (bool): If True, force-truncate over-length inputs.

    Returns:
        str: Full stitched summary.
    """
    if not full_text:
        return ""

    chunks = split_to_chunk(full_text, max_words=max_words)
    summaries = chunk_summaries(
        chunks,
        max_length=max_length,
        min_length=min_length,
        truncation=truncation
    )
    return " ".join(summaries).strip()


# ------------------------------------------------------------------------------
# 4. BIGBIRD-BASED “GPT”-STYLE REFINEMENT
# ------------------------------------------------------------------------------
def get_content_length(text: str) -> list[int]:
    """
    Given a text snippet containing hints like "into a X-Y word ...",
    extract numerical values (X, Y) and multiply by 10 to get a rough
    min/max length estimate for generation.

    E.g.: "Generate into a 5-10 word title" → returns [50, 100].

    Args:
        text (str): Instructional snippet containing numeric hints.

    Returns:
        list[int]: [min_length*10, max_length*10] (if found), else empty list.
    """
    # Look for patterns like "into a {num}-{num} word"
    for marker in ["into a "]:
        if marker in text:
            text = text.split(marker, 1)[1]
            break
    for ending in [" word", " words"]:
        if ending in text:
            text = text.split(ending, 1)[0]
            break

    numbers = []
    for part in text.split("-"):
        digits = "".join(ch for ch in part if ch.isdigit())
        numbers.append(int(digits) * 10 if digits else None)
    # Filter out None
    return [n for n in numbers if n is not None]


def generate_with_bigbird(
    text: str,
    task: str = "title",
    model_dir: str = "allenai/led-base-16384"
) -> str:
    """
    Use LED (Longformer-Encoder-Decoder) to generate a prompt or partial summary.
    Typically called internally by refine_with_gpt().

    Args:
        text (str): Input text to condition on.
        task (str): One of {"title", "caption", "description", "abstract"}. Defaults to "title".
        model_dir (str): HuggingFace checkpoint for LED. Defaults to "allenai/led-base-16384".

    Returns:
        str: The generated text from LED.
    """
    try:
        tokenizer = LEDTokenizer.from_pretrained(model_dir)
        model = LEDForConditionalGeneration.from_pretrained(model_dir)

        # Build a task-specific prompt
        if task in {"title", "caption", "description"}:
            prompt = f"Generate a concise, SEO-optimized {task} for the following content: {text[:1000]}"
        else:
            # Defaults to an "abstract"/summary style prompt
            prompt = f"Summarize the following content into a 100-150 word SEO-optimized abstract: {text[:4000]}"

        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model.generate(
                inputs["input_ids"],
                max_length=200 if task in {"title", "caption"} else 300,
                num_beams=5,
                early_stopping=True
            )
        return tokenizer.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        print(f"Error in BigBird processing: {e}")
        return ""


def refine_with_gpt(
    full_text: str,
    task: str = None,
    generator_fn=None
) -> str:
    """
    A two‐step “refinement” that:
      1) Calls generate_with_bigbird(...) to craft a prompt or initial summary.
      2) Passes that prompt into a causal‐LM generator (e.g. GPT2, GPT-Neo, or a custom 'generator' function).

    Args:
        full_text (str): The text to refine.
        task (str): One of {"title", "caption", "description", "abstract"}. Defaults to "title".
        generator_fn (callable): A text‐generation function that takes (prompt, min_length, max_length), returns a list of dicts with "generated_text".

    Returns:
        str: The final refined text.
    """
    if not generator_fn:
        raise ValueError("You must supply a generator_fn (e.g. pipeline('text-generation') or a custom function).")

    # Step 1: Let BigBird draft a prompt or partial summary
    prompt = generate_with_bigbird(full_text, task=task)
    if not prompt:
        return ""

    # Step 2: Parse length hints from full_text and fallback to defaults
    lengths = get_content_length(full_text)
    min_length, max_length = 100, 200
    if lengths:
        # lengths may be [min_hint, max_hint], if both present
        min_length = lengths[0] if len(lengths) > 0 else min_length
        max_length = lengths[-1] if len(lengths) > 1 else max_length

    # Step 3: Run the generator function on the prompt
    # Expect generator_fn to return a list of dicts like: [{"generated_text": "..."}, ...]
    out = generator_fn(prompt, min_length=min_length, max_length=max_length, num_return_sequences=1)
    if isinstance(out, list) and "generated_text" in out[0]:
        return out[0]["generated_text"].strip()
    else:
        return ""


# ------------------------------------------------------------------------------
# 5. UTILITY: MEDIA URL BUILDER
# ------------------------------------------------------------------------------
EXT_TO_PREFIX = {
    ".png": "images",
    ".jpg": "images",
    ".jpeg": "images",
    ".gif": "images",
    ".mp4": "videos",
    ".mp3": "audio",
    ".wav": "audio",
    ".pdf": "documents",
    # add more as needed
}


def generate_media_url(
    fs_path: str,
    domain: str = None,
    repository_dir: str = None
) -> str | None:
    """
    Convert a local filesystem path (fs_path) inside repository_dir into a public URL.
    E.g., if domain="https://example.com", repository_dir="/home/user/repo",
    and fs_path="/home/user/repo/assets/img.png",
    returns "https://example.com/images/assets/img.png".

    Args:
        fs_path (str): Absolute or relative file path.
        domain (str): Base domain (including protocol), e.g. "https://mydomain.com".
        repository_dir (str): The root of the repo, so that fs_path starts with repository_dir.

    Returns:
        str | None: The constructed URL, or None if fs_path not under repository_dir.
    """
    if not repository_dir or not domain:
        return None

    fs_path_abs = os.path.abspath(fs_path)
    repo_abs = os.path.abspath(repository_dir)
    if not fs_path_abs.startswith(repo_abs):
        return None

    # Compute relative path under repository_dir
    rel_path = fs_path_abs[len(repo_abs) :].lstrip(os.sep)
    rel_path_unix = quote(rel_path.replace(os.sep, "/"))
    ext = os.path.splitext(fs_path_abs)[1].lower()
    prefix = EXT_TO_PREFIX.get(ext, "repository")

    return f"{domain.rstrip('/')}/{prefix}/{rel_path_unix}"



class generatorManager:
    def __init__(self):
        self.generator = pipeline('text-generation', model='distilgpt2', device= -1)
def get_generator():
    generator_mgr = generatorManager()
    return generator_mgr.generator


