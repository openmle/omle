# omle.text — Operators

_Text preprocessing, tokenization, vectorization, and embedding operators for OMLE v0.1._

**Registry version:** 0.1

## Operators

| Operator | Category | Kind | Summary |
|----------|----------|------|---------|
| [`Lowercase`](#lowercase) | normalization | generic | Convert text to lowercase. |
| [`Trim`](#trim) | normalization | generic | Remove leading and trailing whitespace. |
| [`NormalizeWhitespace`](#normalizewhitespace) | normalization | generic | Collapse repeated whitespace to single spaces. |
| [`StringReplace`](#stringreplace) | normalization | generic | Replace string occurrences. |
| [`RegexReplace`](#regexreplace) | normalization | generic | Replace text matched by a regular expression. |
| [`Tokenizer`](#tokenizer) | tokenization | generic | Split each input string into a token sequence using whitespace tokenization. |
| [`RegexTokenizer`](#regextokenizer) | tokenization | generic | Split each input string into a token sequence using a regular expression. |
| [`NGram`](#ngram) | sequence | generic | Produce token n-grams for sizes in the inclusive range [n_min, n_max]. |
| [`StopWordsRemover`](#stopwordsremover) | sequence | generic | Remove stop words from token sequences. |
| [`CountVectorizer`](#countvectorizer) | vectorization | generic | Convert token sequences to sparse count vectors. |
| [`HashingVectorizer`](#hashingvectorizer) | vectorization | generic | Convert token sequences to sparse hashed feature vectors. |
| [`TfIdfTransformer`](#tfidftransformer) | weighting | generic | Apply inverse-document-frequency weighting to count vectors. |
| [`Word2Vec`](#word2vec) | embedding | generic | Convert token sequences to dense document embeddings using a learned word embedding table. |

---

## Lowercase

**Category:** normalization  ·  **Since:** 0.1  ·  **Kind:** generic

Convert text to lowercase.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `x` | yes | no | string_tensor | rank = 1 |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | string | same_shape(x) | TEXT |  |

### Attributes

_(none)_

### Converter Notes

- Equivalent source operators: the lowercase=True preprocessing step inside sklearn.feature_extraction.text.CountVectorizer/TfidfVectorizer/HashingVectorizer.
- Coverage notes: exact. No converter emits this operator standalone today — sklearn folds case-folding into its vectorizers, so it is currently produced only as part of lowering a vectorizer's preprocessing chain.
- Lowering notes: emit this before Tokenizer when the source vectorizer had lowercase enabled, rather than baking case-folding into the vocabulary.

---

## Trim

**Category:** normalization  ·  **Since:** 0.1  ·  **Kind:** generic

Remove leading and trailing whitespace.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `x` | yes | no | string_tensor | rank = 1 |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | string | same_shape(x) | TEXT |  |

### Attributes

_(none)_

### Converter Notes

- Equivalent source operators: leading and trailing whitespace stripping in text preprocessing chains.
- Coverage notes: exact. No converter emits this operator today; it exists so a preprocessing chain can be represented explicitly rather than implied.
- Lowering notes: use together with NormalizeWhitespace when the source pipeline normalized surrounding whitespace before tokenization.

---

## NormalizeWhitespace

**Category:** normalization  ·  **Since:** 0.1  ·  **Kind:** generic

Collapse repeated whitespace to single spaces.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `x` | yes | no | string_tensor | rank = 1 |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | string | same_shape(x) | TEXT |  |

### Attributes

_(none)_

### Converter Notes

- Equivalent source operators: whitespace collapsing in text preprocessing chains, including the default whitespace splitting behaviour that precedes tokenization.
- Coverage notes: exact. No converter emits this operator today; it exists so a preprocessing chain can be represented explicitly rather than implied.
- Lowering notes: collapses runs of whitespace to a single space; pair with Trim to fully normalize surrounding whitespace before Tokenizer.

---

## StringReplace

**Category:** normalization  ·  **Since:** 0.1  ·  **Kind:** generic

Replace string occurrences.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `x` | yes | no | string_tensor | rank = 1 |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | string | same_shape(x) | TEXT |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `old` | string | yes |  |  |
| `new` | string | yes |  |  |
| `replace_all` | bool | no | True |  |

### Validation Rules

- String matching and replacement operate on Unicode code points. Input strings are treated as UTF-8 encoded.

### Converter Notes

- Equivalent source operators: literal substring replacement in text preprocessing chains.
- Coverage notes: exact for literal replacement. No converter emits this operator today. Use RegexReplace when the source step used a pattern rather than a literal.
- Lowering notes: literal replacement only — the pattern is not interpreted as a regular expression.

---

## RegexReplace

**Category:** normalization  ·  **Since:** 0.1  ·  **Kind:** generic

Replace text matched by a regular expression.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `x` | yes | no | string_tensor | rank = 1 |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | string | same_shape(x) | TEXT |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `pattern` | string | yes |  |  |
| `replacement` | string | yes |  |  |

### Validation Rules

- pattern must be a valid RE2 syntax regular expression.
- Pattern matching and replacement operate on Unicode code points. Input strings are treated as UTF-8 encoded.
- Converters from scikit-learn or Spark must verify that source patterns are RE2-compatible and must reject or flag patterns that rely on unsupported constructs such as backreferences or lookarounds.

### Converter Notes

- Equivalent source operators: regular-expression substitution in text preprocessing chains, including custom preprocessor callables in sklearn vectorizers.
- Coverage notes: exact for the stored pattern. No converter emits this operator today, because sklearn preprocessor callables are arbitrary Python and cannot be extracted automatically.
- Lowering notes: the pattern must be written in a portable regular-expression syntax; avoid engine-specific constructs, since consumers use their own regex implementations.

---

## Tokenizer

**Category:** tokenization  ·  **Since:** 0.1  ·  **Kind:** generic

Split each input string into a token sequence using whitespace tokenization.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `x` | yes | no | string_tensor | rank = 1 |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | string | token_sequence_variable | TEXT |  |

### Attributes

_(none)_

### Validation Rules

- Splits on any Unicode whitespace character as defined by Unicode property White_Space = yes.
- Consecutive whitespace characters are treated as a single separator.
- Leading and trailing whitespace produce no empty tokens.

### Converter Notes

- Equivalent source operators: pyspark.ml.feature.Tokenizer.
- Coverage notes: exact for simple whitespace tokenization. sklearn vectorizers tokenize with a regular expression rather than plain whitespace and therefore lower to RegexTokenizer.
- Lowering notes: produces a per-row token sequence rather than a fixed-width tensor; downstream operators must accept token_sequence.

---

## RegexTokenizer

**Category:** tokenization  ·  **Since:** 0.1  ·  **Kind:** generic

Split each input string into a token sequence using a regular expression.

### Inputs

| Name | Required | Variadic | Kind(s) | Shape Constraints |
|------|----------|----------|---------|-------------------|
| `x` | yes | no | string_tensor | rank = 1 |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | string | token_sequence_variable | TEXT |  |

### Attributes

| Name | Type | Required | Default | Enum Values | Description |
|------|------|----------|---------|-------------|-------------|
| `pattern` | string | yes |  |  |  |
| `gaps` | bool | no | True |  | If true, pattern matches separators between tokens (split on match). If false, pattern matches tokens themselves (keep matches). Mirrors Spark RegexTokenizer.gaps semantics. |
| `min_token_length` | int | no | 1 |  |  |

### Validation Rules

- pattern must be a valid RE2 syntax regular expression.
- If gaps = false, tokens are the non-overlapping regex matches of pattern.
- If gaps = true, tokens are the non-empty spans between regex matches of pattern.
- min_token_length must be >= 1.
- Converters from scikit-learn or Spark must verify that source patterns are RE2-compatible and must reject or flag patterns that rely on unsupported constructs such as backreferences or lookarounds.

### Converter Notes

- Equivalent source operators: pyspark.ml.feature.RegexTokenizer; the token_pattern tokenization step inside sklearn.feature_extraction.text.CountVectorizer/TfidfVectorizer/HashingVectorizer.
- Coverage notes: exact for the stored pattern. sklearn's default token_pattern of (?u)\b\w\w+\b is carried across verbatim rather than approximated by whitespace splitting.
- Lowering notes: produces a per-row token sequence rather than a fixed-width tensor; downstream operators must accept token_sequence.

---

## NGram

**Category:** sequence  ·  **Since:** 0.1  ·  **Kind:** generic

Produce token n-grams for sizes in the inclusive range [n_min, n_max].

Output token count per row is the sum over n in [n_min, n_max] of max(0, len(row) - n + 1). Tokens within each n-gram are joined with a single space character U+0020.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `x` | yes | no | token_sequence |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | string | token_sequence_variable | TEXT |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `n_min` | int | no | 1 |  |
| `n_max` | int | yes |  |  |

### Validation Rules

- n_min must be >= 1.
- n_max must be >= n_min.
- Tokens within each n-gram are joined with a single space character U+0020.

### Converter Notes

- Equivalent source operators: pyspark.ml.feature.NGram; the ngram_range expansion inside sklearn.feature_extraction.text.CountVectorizer/TfidfVectorizer/HashingVectorizer.
- Coverage notes: exact. A single node covers a range of n, so scikit-learn and Spark style n-gram ranges do not require multiple NGram nodes plus Concat.
- Lowering notes: use n_min = n_max for single-n behaviour, matching Spark's NGram; use n_min < n_max for a sklearn ngram_range.

---

## StopWordsRemover

**Category:** sequence  ·  **Since:** 0.1  ·  **Kind:** generic

Remove stop words from token sequences.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `x` | yes | no | token_sequence |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | string | token_sequence_variable | TEXT |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `stop_words` | tensor_ref | yes |  |  |
| `case_sensitive` | bool | no | False |  |

### Validation Rules

- stop_words must reference a STRING tensor of shape [K].

### Converter Notes

- Equivalent source operators: pyspark.ml.feature.StopWordsRemover; the stop_words filtering step inside sklearn.feature_extraction.text.CountVectorizer/TfidfVectorizer.
- Coverage notes: exact for an explicit stop-word list. sklearn's stop_words='english' resolves to its built-in list, which converters must materialize into an explicit list rather than referencing by name.
- Lowering notes: apply after tokenization and before vectorization, matching the source pipeline's order.

---

## CountVectorizer

**Category:** vectorization  ·  **Since:** 0.1  ·  **Kind:** generic

Convert token sequences to sparse count vectors.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `x` | yes | no | token_sequence |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | same_type(attr:output_dtype) | matrix(n_rows=N,n_cols=K) | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `vocabulary` | tensor_ref | yes |  |  |
| `binary` | bool | no | False |  |
| `output_dtype` | string | no | FLOAT32 | `FLOAT32`, `FLOAT64`, `INT32`, `INT64` |

### Validation Rules

- Tokens not present in vocabulary are silently ignored.
- vocabulary must reference a STRING tensor of shape [K].
- If binary = false, y[i, vocab_index(token)] is incremented by 1 for each occurrence of token in row i.
- If binary = true, y[i, vocab_index(token)] is set to 1 regardless of occurrence count.
- Output y is typically represented as SparseTensor in runtime implementations when sparse materialization is available.

### Converter Notes

- Equivalent source operators: sklearn.feature_extraction.text.CountVectorizer; pyspark.ml.feature.CountVectorizerModel.
- Coverage notes: exact for the fitted vocabulary and term counts. sklearn's TfidfVectorizer lowers to CountVectorizer followed by TfIdfTransformer, since it is the composition of the two.
- Lowering notes: store the fitted vocabulary in its fitted index order; the column order of the output depends on it.

---

## HashingVectorizer

**Category:** vectorization  ·  **Since:** 0.1  ·  **Kind:** generic

Convert token sequences to sparse hashed feature vectors.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `x` | yes | no | token_sequence |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | same_type(attr:output_dtype) | matrix(n_rows=N,n_cols=K) | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `num_features` | int | yes |  |  |
| `binary` | bool | no | False |  |
| `alternate_sign` | bool | no | False |  |
| `hash_function` | string | no | murmurhash2 | `murmurhash2`, `murmurhash3` |
| `output_dtype` | string | no | FLOAT32 | `FLOAT32`, `FLOAT64`, `INT32`, `INT64` |

### Validation Rules

- K = num_features.
- num_features must be >= 1.
- Tokens are encoded as UTF-8 bytes before hashing.
- If hash_function = 'murmurhash2', index = murmurhash2_unsigned(token_bytes) % num_features.
- If hash_function = 'murmurhash3', index = murmurhash3_x86_32(token_bytes, seed=0) % num_features.
- If alternate_sign = false, each token contributes a positive unit or count to its hashed index.
- If alternate_sign = true and hash_function = 'murmurhash2', let h = murmurhash2_unsigned(token_bytes). The feature sign is +1 if ((h >> 31) & 1) = 0, else -1.
- If alternate_sign = true and hash_function = 'murmurhash3', let h = murmurhash3_x86_32(token_bytes, seed=0). The feature sign is +1 if ((h >> 31) & 1) = 0, else -1.
- Converters must record which hash_function the source framework used.

### Converter Notes

- Equivalent source operators: sklearn.feature_extraction.text.HashingVectorizer; pyspark.ml.feature.HashingTF.
- Coverage notes: exact given a matching hash function. It is stateless — there is no fitted vocabulary — so the hash function and feature count fully determine the output.
- Lowering notes: record the hash function and n_features exactly; a consumer using a different hash produces silently wrong columns rather than an error.

---

## TfIdfTransformer

**Category:** weighting  ·  **Since:** 0.1  ·  **Kind:** generic

Apply inverse-document-frequency weighting to count vectors.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `x` | yes | no | numeric_tensor, sparse_tensor |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | promote_to_float(x) | same_shape(x) | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `idf` | tensor_ref | yes |  |  |

### Validation Rules

- idf must reference a floating-point tensor of shape [K] where K matches the trailing feature dimension of x.
- Output is computed elementwise: y[i, j] = x[i, j] * idf[j].
- Output dtype follows promote_to_float(x) regardless of the stored dtype of idf.

### Converter Notes

- Equivalent source operators: sklearn.feature_extraction.text.TfidfTransformer and the IDF half of TfidfVectorizer; pyspark.ml.feature.IDFModel.
- Coverage notes: exact for precomputed IDF weights. The two frameworks use different smoothing — sklearn's default smooth IDF is idf[i] = log((1 + n) / (1 + df[i])) + 1, while Spark's IDFModel uses idf[i] = log((N + 1) / (df[i] + 1)) — so the idf tensor must match the source framework's fitted formula.
- Lowering notes: extract the fitted idf array directly rather than recomputing it from document frequencies.
- Lowering notes: TfIdfTransformer does not normalize. Apply an explicit omle.feature.Normalizer node after it when the source used L1 or L2 normalization, as sklearn's TfidfVectorizer does by default.

---

## Word2Vec

**Category:** embedding  ·  **Since:** 0.1  ·  **Kind:** generic

Convert token sequences to dense document embeddings using a learned word embedding table.

### Inputs

| Name | Required | Variadic | Kind(s) |
|------|----------|----------|---------|
| `x` | yes | no | token_sequence |

### Outputs

| Name | Type Rule | Shape Rule | Measure Level Rule | Role Rule |
|------|-----------|------------|--------------------|-----------|
| `y` | floating_type(attr:output_dtype) | matrix(n_rows=N,n_cols=K) | CONTINUOUS |  |

### Attributes

| Name | Type | Required | Default | Enum Values |
|------|------|----------|---------|-------------|
| `vocabulary` | tensor_ref | yes |  |  |
| `embeddings` | tensor_ref | yes |  |  |
| `pooling` | string | no | mean | `mean`, `sum` |
| `unknown_token_policy` | string | no | ignore | `ignore`, `zero` |
| `output_dtype` | string | no | FLOAT32 | `FLOAT32`, `FLOAT64` |

### Validation Rules

- vocabulary must reference a STRING tensor of shape [V].
- embeddings must reference a floating-point tensor of shape [V, K].
- The leading dimension of embeddings must equal len(vocabulary).
- K is the embedding dimension derived from embeddings.
- unknown_token_policy = 'ignore': unknown tokens contribute nothing to pooling; for mean pooling they are excluded from the denominator.
- unknown_token_policy = 'zero': unknown tokens contribute a zero vector; for mean pooling they are included in the denominator.
- If pooling = 'sum' and no tokens in a row are matched, output row is the zero vector.
- If pooling = 'mean' and no tokens in a row are matched, whether because the row is empty or all tokens are unknown, output row is the zero vector.

### Converter Notes

- Equivalent source operators: pyspark.ml.feature.Word2VecModel.
- Coverage notes: exact for the fitted vocabulary and embedding matrix. Inference averages the embeddings of the tokens in each row, matching Spark's transform semantics; training is out of scope.
- Lowering notes: preserve the learned token-to-row alignment between vocabulary and embeddings — the vocabulary order indexes the embedding matrix.

---
