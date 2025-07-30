from transformers.tokenization_utils import PreTrainedTokenizer 
from transformers.tokenization_utils_base import BatchEncoding


SEP = "ꙮ"

def consolidate(text: str) -> str:
    """
    Remove the separators (multiocular.SEP) from the text.
    """
    text = text.replace(SEP, "")
    return text

def split(text: str) -> list[str]:
    """
    Split the text by the separators (multiocular.SEP) and return a list of segments.
    """
    return text.split(SEP)

def tokenize(tok: PreTrainedTokenizer, text: str, **kwargs) -> tuple[BatchEncoding, list[int | None]]:
    """
    Remove the separators (multiocular.SEP) from the text and tokenize it.
    
    Return a tuple containing:
    - A BatchEncoding object with the tokenized text.
    - A list of (int | None) representing the split points in the tokenized text.
      Each integer is the index of the token that corresponds to the end of a segment.
      If a split point is not at an exact token boundary, it will be None.
    """
    consolidated_text = consolidate(text)
    segments = split(text)
    lengths = [len(seg) for seg in segments[:-1]]
    split_points = []
    for i, length in enumerate(lengths):
        if i == 0:
            split_points.append(length)
        else:
            split_points.append(split_points[-1] + length)

    
    tokens: BatchEncoding = tok(consolidated_text, **kwargs)
    pairs = [
        (
            tokens.char_to_token(sp - 1) + 1,
            tokens.char_to_token(sp)
        )
        for sp in split_points
    ]
        
    points = [
        a if (a == b) else None
        for a, b in pairs
    ]

    return (tokens, points)
