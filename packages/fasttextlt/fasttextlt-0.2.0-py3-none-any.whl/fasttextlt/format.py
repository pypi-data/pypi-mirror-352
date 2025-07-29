# Original:
# Authors: Michael Penkov <m@penkov.dev>
# Copyright (C) 2019 RaRe Technologies s.r.o.
# Licensed under the GNU LGPL v2.1

"""Load models from the native binary format released by Facebook.

See Also
--------

`FB Implementation <https://github.com/facebookresearch/fastText/blob/master/src/matrix.cc>`_.

"""

# NOTE: see end of file for a description of the binary format

import collections
import io
import logging
import struct
from typing import Any, BinaryIO, Literal, NamedTuple, cast

import numpy as np

_END_OF_WORD_MARKER = b"\x00"

# FastText dictionary data structure holds elements of type `entry` which can have `entry_type`
# either `word` (0 :: int8) or `label` (1 :: int8). Here we deal with unsupervised case only
# so we want `word` type.
# See https://github.com/facebookresearch/fastText/blob/master/src/dictionary.h

_DICT_WORD_ENTRY_TYPE_MARKER = b"\x00"


logger = logging.getLogger(__name__)

# Constants for FastText version and FastText file format magic (both int32)
# https://github.com/facebookresearch/fastText/blob/master/src/fasttext.cc#L25

_FASTTEXT_FILEFORMAT_MAGIC = b"\xba\x16\x4f\x2f"  # 793712314 as int32
_FASTTEXT_VERSION = 12


# NOTE: everywhere in this file, we assume we are try to load a model saved on a little-endian
# platform
_HEADER_FORMAT: list[tuple[str, Literal["<i", "<d"]]] = [
    ("dim", "<i"),
    ("ws", "<i"),
    ("epoch", "<i"),
    ("min_count", "<i"),
    ("neg", "<i"),
    ("word_ngrams", "<i"),
    ("loss", "<i"),
    ("model", "<i"),
    ("bucket", "<i"),
    ("minn", "<i"),
    ("maxn", "<i"),
    ("lr_update_rate", "<i"),
    ("t", "<d"),
]

_INT_SIZE = struct.calcsize("<i")
_FLOAT_SIZE = struct.calcsize("<f")


# FIXME: make this a dataclass instead?
class Model(NamedTuple):
    # TODO: sort docstring
    """Holds data loaded from the Facebook binary.

    Parameters
    ----------
    dim : int
        The dimensionality of the vectors.
    ws : int
        The window size.
    epoch : int
        The number of training epochs.
    neg : int
        If non-zero, indicates that the model uses negative sampling.
    loss : int
        If equal to 1, indicates that the model uses hierarchical sampling.
    model : int
        If equal to 2, indicates that the model uses skip-grams.
    bucket : int
        The number of buckets.
    min_count : int
        The threshold below which the model ignores terms.
    t : float
        The sample threshold.
    minn : int
        The minimum ngram length.
    maxn : int
        The maximum ngram length.
    raw_vocab : collections.OrderedDict
        A map from words (str) to their frequency (int).  The order in the dict
        corresponds to the order of the words in the Facebook binary.
    nwords : int
        The number of words.
    vocab_size : int
        The size of the vocabulary.
    vectors_ngrams : np.ndarray
        This is a matrix that contains vectors learned by the model.
        Each row corresponds to a vector.
        The number of vectors is equal to the number of words plus the number of buckets.
        The number of columns is equal to the vector dimensionality.
    hidden_output : np.ndarray
        This is a matrix that contains the shallow neural network output.
        This array has the same dimensions as vectors_ngrams.
        May be None - in that case, it is impossible to continue training the model.
    """

    dim: int
    ws: int
    epoch: int
    min_count: int
    neg: int
    word_ngrams: int
    loss: int
    model: int
    bucket: int
    minn: int
    maxn: int
    lr_update_rate: int
    t: float
    raw_vocab: collections.OrderedDict
    nwords: int
    vocab_size: int
    vectors_ngrams: np.ndarray[tuple[int, int], np.dtype[np.floating]]
    hidden_output: np.ndarray[tuple[int, int], np.dtype[np.floating]]
    ntokens: int


def read_unpack(in_stream: BinaryIO, fmt: str) -> tuple[Any, ...]:
    num_bytes = struct.calcsize(fmt)
    data = in_stream.read(num_bytes)
    return struct.unpack(fmt, data)


def _load_vocab(
    in_stream: BinaryIO, new_format: bool, encoding: str = "utf-8"
) -> tuple[collections.OrderedDict[str, int], int, int, int]:
    """Load a vocabulary from a FB binary.

    Before the vocab is ready for use, call the prepare_vocab function and pass
    in the relevant parameters from the model.

    Parameters
    ----------
    in_stream : file
        An open file pointer to the binary.
    new_format: boolean
        True if the binary is of the newer format.
    encoding : str
        The encoding to use when decoding binary data into words.

    Returns
    -------
    tuple
        The loaded vocabulary.  Keys are words, values are counts.
        The vocabulary size.
        The number of words.
        The number of tokens.
    """
    vocab_size, nwords, nlabels = cast(tuple[int, int, int], read_unpack(in_stream, "<3i"))

    # Vocab stored by [Dictionary::save](https://github.com/facebookresearch/fastText/blob/master/src/dictionary.cc)
    if nlabels > 0:
        raise NotImplementedError("Supervised fastText models are not supported")
    logger.info(f"loading {vocab_size} words for fastText model from {in_stream.name}")

    (ntokens,) = cast(tuple[int], read_unpack(in_stream, "<q"))  # number of tokens

    if new_format:
        (pruneidx_size,) = cast(tuple[int], read_unpack(in_stream, "<q"))
    else:
        pruneidx_size = 0

    raw_vocab = collections.OrderedDict()
    for _ in range(vocab_size):
        word_bytes = io.BytesIO()
        char_byte = in_stream.read(1)

        while char_byte != _END_OF_WORD_MARKER:
            word_bytes.write(char_byte)
            char_byte = in_stream.read(1)

        word_bytes = word_bytes.getvalue()
        try:
            word = word_bytes.decode(encoding)
        except UnicodeDecodeError:
            word = word_bytes.decode(encoding, errors="backslashreplace")
            logger.error(
                f"failed to decode invalid unicode bytes {word_bytes!r};"
                f" replacing invalid characters, using {word!r}",
            )
        count, _ = cast(tuple[int, bytes], read_unpack(in_stream, "<qb"))
        raw_vocab[word] = count

    if pruneidx_size > 0:
        in_stream.seek(pruneidx_size * 2 * _INT_SIZE, 1)
        # TODO: why are we skipping these
        # for _ in range(pruneidx_size):
        #     first, second = read_unpack(in_stream, "<2i")
    else:
        if pruneidx_size != -1:
            raise ValueError(f"Invalid pruneidx_size: {pruneidx_size}")

    return raw_vocab, vocab_size, nwords, ntokens


def _load_matrix(
    in_stream: BinaryIO,
    new_format: bool = True,
    safe_load: bool = False,
) -> np.ndarray[tuple[int, int], np.dtype[np.floating]]:
    """Load a matrix from fastText native format.

    Interprets the matrix dimensions and type from the file stream.

    Parameters
    ----------
    - `in_stream`: A file handle opened for reading.
    - `new_format`: True if the quant_input variable precedes the matrix declaration, which should
      be the case for newer versions of fastText.
    - `safe_load`: if `False`, loading will use `np.fromfile`, set to `True` if `in_stream` is
      incompatible with that.
    """
    if new_format:
        _quantized = read_unpack(in_stream, "<?")  # bool quant_input in fasttext.cc

    num_vectors, dim = cast(tuple[int, int], read_unpack(in_stream, "<2q"))
    count = num_vectors * dim

    # TODO: check that the sizes/endianness are ok here. What does np enforce?
    if safe_load:
        logger.warning(
            "Using a safe loading routine. This can be slow."
            " This is a work-around for a bug in NumPy: <https://github.com/numpy/numpy/issues/13470>."
            " Consider decompressing your model file for a faster load. "
        )
        matrix = np.frombuffer(in_stream.read(count * _FLOAT_SIZE), dtype=np.float32)
    else:
        matrix = np.fromfile(in_stream, np.float32, count)

    if matrix.shape != (count,):
        raise ValueError(f"Wrong matrix size: expected `{(count,)}`,  got `{matrix.shape!r}`")

    return cast(
        np.ndarray[tuple[int, int], np.dtype[np.floating]],
        matrix.reshape((num_vectors, dim), copy=False),
    )


# TODO: supporting supervised would not be that hard actually
# TODO: can we detect early that if a file is not in a compatible format?
def load(
    in_stream: BinaryIO, encoding: str = "utf-8", full_model: bool = False, safe_load: bool = False
) -> Model:
    """Load a model from a binary stream.

    Reverse-engineered from
    [FastText](https://github.com/facebookresearch/fastText/blob/1142dc4c4ecbc19cc16eee5cdd28472e689267e6/src/dictionary.cc#L500)
    and Gensim.

    Parameters
    ----------
    - `in_stream` : file
        The readable binary stream.
    - `encoding` : str, optional
        The encoding to use for decoding text
    - `full_model` : boolean, optional
        If False, skips loading the hidden output matrix. This saves a fair bit of CPU time and RAM,
        but prevents training continuation.
    - `safe_load`: use a slightly slower array reading routine in place of `np.fromfile`. You need
      to set this to `True` if `in_stream` is something lie `gzip.GzipFile` that's incompatible with
      `np.fromfile`. See [the corresponding NumPy
      issue](https://github.com/numpy/numpy/issues/13470>.
    """
    first_field = in_stream.read(_INT_SIZE)
    new_format = first_field == _FASTTEXT_FILEFORMAT_MAGIC

    # Old format doesn't have magic and version, so we have to differentiate here
    if new_format:
        # FIXME: actually Model doesn't use this, dump them?
        model = {
            "magic": first_field,
            "version": cast(tuple[int], read_unpack(in_stream, "<i")[0]),
        }
        # TODO: warn on wrong version?
        # TODO: make this faster by reading all fields at once
        model = {name: read_unpack(in_stream, fmt)[0] for (name, fmt) in _HEADER_FORMAT}
    else:
        model = {
            "dim": int.from_bytes(first_field, byteorder="little", signed=True),
        }
        # Skipping dim and version since we already read thme
        model = {name: read_unpack(in_stream, fmt)[0] for (name, fmt) in _HEADER_FORMAT[1:]}

    raw_vocab, vocab_size, nwords, ntokens = _load_vocab(in_stream, new_format, encoding=encoding)
    model.update({
        "raw_vocab": raw_vocab,
        "vocab_size": vocab_size,
        "nwords": nwords,
        "ntokens": ntokens,
    })

    model["vectors_ngrams"] = _load_matrix(in_stream, new_format=new_format, safe_load=safe_load)

    if full_model:
        model["hidden_output"] = _load_matrix(in_stream, new_format=new_format, safe_load=safe_load)
        if in_stream.read() != b"":
            raise ValueError("expected to reach EOF")
    else:
        model["hidden_output"] = None

    return Model(**model)


def _sign_model(out_stream: BinaryIO):
    """
    Write signature of the file in Facebook's native fastText `.bin` format
    to the binary output stream `out_stream`. Signature includes magic bytes and version.

    Name mimics original C++ implementation, see
    [FastText::signModel](https://github.com/facebookresearch/fastText/blob/master/src/fasttext.cc)

    Parameters
    ----------
    out_stream: writeable binary stream
    """
    out_stream.write(_FASTTEXT_FILEFORMAT_MAGIC)
    out_stream.write(struct.pack("<i", _FASTTEXT_VERSION))


def _args_save(out_stream: BinaryIO, model: Model):
    """
    Saves header with `model` parameters to the binary stream `out_stream` containing a model in the
    Facebook's native fastText `.bin` format.

    Name mimics original C++ implementation, see
    [Args::save](https://github.com/facebookresearch/fastText/blob/master/src/args.cc)

    Parameters
    ----------
    out_stream: writeable binary stream
        stream to which model is saved
    model: Model
        saved model
    """
    for field, field_type in _HEADER_FORMAT:
        out_stream.write(struct.pack(field_type, getattr(model, field)))


def _dict_save(out_stream: BinaryIO, model: Model, encoding: str = "utf-8"):
    """
    Saves the dictionary from `model` to the binary stream `out_stream` containing a model in the
    Facebook's native fastText `.bin` format.

    Name mimics the original C++ implementation
    [Dictionary::save](https://github.com/facebookresearch/fastText/blob/master/src/dictionary.cc)

    Parameters
    ----------
    out_stream: writeable binary stream
        stream to which the dictionary from the model is saved
    model: gensim.models.fasttext.FastText
        the model that contains the dictionary to save
    encoding: str
        string encoding used in the output
    """

    # In the FB format the dictionary can contain two types of entries, i.e.
    # words and labels. The first two fields of the dictionary contain
    # the dictionary size (size_) and the number of words (nwords_).
    # In the unsupervised case we have only words (no labels). Hence both fields
    # are equal.

    out_stream.write(struct.pack("<i", model.nwords))
    out_stream.write(struct.pack("<i", model.nwords))

    # nlabels=0 <- no labels  we are in unsupervised mode
    out_stream.write(struct.pack("<i", 0))

    # Number of training steps
    out_stream.write(struct.pack("<q", model.ntokens))

    # no prune_idx in unsupervised mode. Use -1 as a flag.
    # (why not 0, why not use unsigned long long who knows)
    out_stream.write(struct.pack("<q", -1))

    for word, count in model.raw_vocab.items():
        out_stream.write(word.encode(encoding))
        out_stream.write(_END_OF_WORD_MARKER)
        out_stream.write(struct.pack("<q", count))
        out_stream.write(_DICT_WORD_ENTRY_TYPE_MARKER)

    # We are in unsupervised case, therefore prune_idx is empty, so we do not need to write
    # anything else


def _save_array(
    array: np.ndarray[tuple[int, ...], np.dtype[np.floating]],
    out_stream: BinaryIO,
    quantized: bool | None = False,
):
    """Save a numpy array to `out_stream` in FastText format.

    - If `quantized` is not `None`, a corresponding bool will be prepended.
    - The array shape are simple packed together before the data (as C long longs).
    """
    if quantized is not None:  # New format
        out_stream.write(struct.pack("<?", quantized))

    out_stream.write(struct.pack(f"<{len(array.shape)}q", *array.shape))
    out_stream.write(array.tobytes())


def save(model: Model, out_stream: BinaryIO, encoding: str = "utf-8"):
    """
    Saves word embeddings to the Facebook's native fasttext `.bin` format.

    Parameters
    ----------
    out_stream: writeable binary stream
        stream to which model is saved
    model: Model
        saved model
    encoding: str
        encoding used in the output file

    Notes
    -----
    Unfortunately, there is no documentation of the Facebook's native fasttext `.bin` format

    This is just reimplementation of
    [FastText::saveModel](https://github.com/facebookresearch/fastText/blob/da2745fcccb848c7a225a7d558218ee4c64d5333/src/fasttext.cc)

    Code follows the original C++ code naming.
    """
    _sign_model(out_stream)
    _args_save(out_stream, model)
    _dict_save(out_stream, model, encoding)

    # Save words and ngrams vectors
    if model.vectors_ngrams.shape != (model.nwords + model.bucket, model.dim):
        raise ValueError(
            f"Corrupted model: the input matrix has shape {model.vectors_ngrams.shape}"
            f" but the metadata says {(model.nwords + model.bucket, model.dim)}."
        )
    _save_array(model.vectors_ngrams, out_stream, quantized=False)

    if model.hidden_output is not None:
        # TODO: also check shape for this guy
        _save_array(model.hidden_output, out_stream, quantized=False)


# It would have been amazing if FastText had provided this somewhere but :))

# Technically FastText use native endianness, which is silly, but in practice means
# little-endianness for virtually all existing models. So let's say that's the standard for the file
# format.

# floats are typed
# [`real`](https://github.com/facebookresearch/fastText/blob/1142dc4c4ecbc19cc16eee5cdd28472e689267e6/src/real.h)
# but they should be float32 on all relevant platforms (famous last words). The only case where that
# would be an issue is if someone saves a FastText model on platform where float is something else
# and then try to load *that* in fasttextlt. This would be silly (famous last words) so let's not
# support that now.

# (New) File format:
# - Prelude:  # Absent in old format
#   - 32b: int32 magic  # _FASTTEXT_FILEFORMAT_MAGIC = np.int32(793712314)
#   - 32b: int32 version  # _FASTTEXT_VERSION = np.int32(12)
# - Header:
#   - 32b: int32 dim  # The dimensionality of the vectors.
#   - 32b: int32 ws  # The window size.
#   - 32b: int32 epoch  # The number of training epochs.
#   - 32b: int32 min_count  # The threshold below which the model ignores terms.
#   - 32b: int32 neg  # If non-zero, indicates that the model uses negative sampling.
#   - 32b: int32 word_ngram
#   - 32b: int32 loss  # If equal to 1, indicates that the model uses hierarchical sampling.
#   - 32b: int32 model  # If equal to 2, indicates that the model uses skip-grams.
#   - 32b: int32 bucket  # The number of buckets.
#   - 32b: int32 minn  # The minimum ngram length.
#   - 32b: int32 maxn  # The maximum ngram length.
#   - 32b: int32 lr_update_rate
#   - 64b: float64 t  # # The sample threshold.
# - Vocab:
#   - Prelude:
#     - 64b: int64 pruneidx_size  # -1 stands for None. Absent in old format
#     - 32b: int32 size  # == nwords + nlabels
#     - 32b: int32 nwords   # number of full words in the vocabulary
#     - 32b: int32 nlabels  # 0 for unsupervised models
#     - 64b: int64 ntokens  # number of training steps
#   - Content:
#     - nwords*
#       - Word:  # 0x00-terminated string
#         - *
#           - 8b: char c
#         - 8b: 0x00  # (_END_OF_WORD_MARKER)
#       - 64b: int64 count
#       - 8b: int8 entry_type  # 0x00 (_DICT_WORD_ENTRY_TYPE_MARKER) for words
#     - nlabels*
#       - Label:  # 0x00-terminated string
#         - *
#           - 8b: char c  # Most likely a utf-8 byte
#         - 8b: 0x00
#       - 64b: int64 count
#       - 8b: int8 entry_type  # 0x01 for labels
#    - Pruned Index:  # Absent in old format
#      - pruneidx_size*
#        - 32b: int32 first
#        - 32b: int32 second
# TODO: this is only dense matrices, figure out how quant ones work
# - Input Vectors:  # aka vectors_ngrams/input_hidden
#   - 8b: bool quant_input  # absent in old format
#   - 64b: int64 m   # == num_vectors
#   - 64b: int64 n   # == dim
#   - (m*n*float_size)b: float32* data  # numpy-compatible don't worry about it kitten
# - Output Vectors:  # aka hidden_output
#   - 8b: bool quant_input  # absent in old format
#   - 64b: int64 m
#   - 64b: int64 n
#   - (m*n*float_size)b: float32* data
