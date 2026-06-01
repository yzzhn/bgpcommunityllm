# Community Categorization Pipeline

This document describes the rule-based pipeline used to categorize communities based on the extracted semantics stored in our dictionary. The pipeline combines lightweight NLP-based verb extraction with regular-expression and keyword matching to assign each community to one predefined category.

## Overview

For each community, the pipeline takes a semantic description as input and assigns a single category label. The categorization process is deterministic and follows a fixed priority order: the first matching rule determines the final category.

At a high level, the pipeline performs three steps:

1. **Extract verbs from the semantic description** using the `en_core_web_sm` spaCy NLP model.
2. **Normalize and scan the text** for category-specific keywords, abbreviations, and spelling variants.
3. **Assign a category** using an ordered set of rule-based checks.

The extracted verbs are mainly used as a fallback signal. If no category-specific rules match and the description contains no verbs, the community is treated as informational.

## Input and Output

### Input

The categorization function expects:

- `x`: a semantic description string for a community.
- `verb`: a list of verb lemmas extracted from the semantic description.

In practice, `verb` is produced by applying the helper function `get_verbs(text)` to the same semantic description.

### Output

The function returns one category label as a string, such as:

- `Act-Blackhole`
- `Act-Permissive`
- `Info-RouteStatus`
- `Info`
- `Other`

Only one category is assigned per community.

## Verb Extraction

The pipeline uses spaCy’s `en_core_web_sm` model to extract verbs from each semantic description.

```python
nlp = spacy.load("en_core_web_sm")

def get_verbs(text):
    doc = nlp(text)
    verbs_lemma = [token.lemma_ for token in doc if token.pos_ == "VERB"]
    return verbs_lemma
```

For each token in the parsed document, the pipeline keeps the token lemma if its part-of-speech tag is `VERB`. For example, descriptions containing words such as “advertise,” “announce,” “drop,” or “reject” may produce verb lemmas that help determine whether the description represents an action.

The verb list is not used to distinguish most specific categories. Instead, it is used near the end of the pipeline to decide whether an otherwise unmatched description should default to `Info` or `Other`.

## Rule-Based Matching

The pipeline defines a set of helper functions, each detecting one semantic pattern. These functions use keyword, substring, and regular-expression based matching.

Before applying the rules, descriptions should be lowercased and normalized consistently so that substring checks behave as expected.

## Category Precedence

The categorization function applies rules in the following order:

```python
def categorization(x, verb):
    if isblackhole(x): 
        return "Act-Blackhole"
    if isShutdown(x):
        return "Act-Shutdown"
    if isPermissive(x):
        return "Act-Permissive"
    if isSuppressive(x):
        return "Act-Suppressive"
    if isRedistribute(x):
        return "Act-GeneralRedistribute"
    if isPrepend(x):
        return "Act-Prepend"
    if isPREF(x):
        return "Act-Local Pref."
    if isFiltering(x):
        return "Act-Filtering"
    if isDrop(x):
        return "Act-Drop"
    if isAgg(x):
        return "Act-Aggregation"
    if isRouteStatus(x):
        return "Info-RouteStatus"
    if isMED(x):
        return "MED"
    if isNoPeer(x):
        return "NOPEER"
    if infomation(x):
        return "Info"
    if isLLSG(x):
        return "LLSG"
    if len(verb) == 0:
        return "Info"
    return "Other"
```

Because the rules are evaluated sequentially, earlier categories have higher priority. For example, a description that contains both a blackhole-related keyword and a prepend-related keyword will be assigned to `Act-Blackhole`, because blackhole detection is checked first.

## Category Rules

### `Act-Blackhole`

A community is categorized as `Act-Blackhole` if the description contains blackhole or DDoS-related terms.

Matched keywords include:

- `blackhole`
- `rtbh`
- `blackh`
- `black h`
- `ddos`

This rule captures communities used for blackholing, remote triggered blackholing, or DDoS mitigation.

### `Act-Shutdown`

A community is categorized as `Act-Shutdown` if the description suggests route shutdown or graceful shutdown behavior.

Matched keywords include:

- `shutd`
- `shut down`
- `graceful`
- `g shut`

### `Act-Permissive`

A community is categorized as `Act-Permissive` when the description indicates that routes should be advertised, announced, exported, sent, leaked, reported, or distributed, unless the same text contains a suppressive negation.

Permissive action keywords include:

- `advertis`
- `announ`
- `export`
- `send`
- `leak`
- `report`
- `distribute`

The rule excludes descriptions containing:

- `no`
- `don't`
- `stop`

The rule also treats the following phrases as permissive:

- `always to`
- `do not modify`

### `Act-Suppressive`

A community is categorized as `Act-Suppressive` when the description contains an advertisement, announcement, export, send, leak, report, or distribution keyword together with a suppressive modifier.

Action keywords include:

- `advertis`
- `announ`
- `export`
- `send`
- `leak`
- `report`
- `distribut`

Suppressive modifiers include:

- `no`
- `don't`
- `stop`
- `restrict`

### `Act-GeneralRedistribute`

A community is categorized as `Act-GeneralRedistribute` if the description contains:

- `distribut`

This rule is evaluated after permissive and suppressive rules. Therefore, descriptions with redistribution-related terms and explicit permissive or suppressive signals are assigned to those more specific action categories first.

### `Act-Prepend`

A community is categorized as `Act-Prepend` if the description indicates AS-path prepending or similar path modification behavior.

Matched keywords include:

- `prepen`
- `append`
- `pre pend`
- `add `
- `prepand`

### `Act-Local Pref.`

A community is categorized as `Act-Local Pref.` if the description refers to local preference.

Matched keywords include:

- `local pref`
- `local-pref`
- `prf`
- `localpref`
- `pref`

### `Act-Filtering`

A community is categorized as `Act-Filtering` if the description contains either an accept-related or reject-related keyword.

Accept keywords:

- `accept`

Reject keywords:

- `reject`
- `deny`
- `block`

### `Act-Drop`

A community is categorized as `Act-Drop` if the description contains:

- `drop`
- `discard`

This rule is checked after filtering, so descriptions containing both `reject` and `drop` are categorized as `Act-Filtering`.

### `Act-Aggregation`

A community is categorized as `Act-Aggregation` if the description contains:

- `aggregat`

This captures variants such as “aggregate,” “aggregated,” or “aggregation.”

### `Info-RouteStatus`

A community is categorized as `Info-RouteStatus` if the description refers to route validation, routing databases, or route status.

Matched keywords include:

- `valid`
- `unknown`
- `found`
- `rpki`
- `irr`

### `MED`

A community is categorized as `MED` if the description refers to Multi-Exit Discriminator or metric-related behavior.

Matched keywords include:

- `med`
- `metric`

### `NOPEER`

A community is categorized as `NOPEER` if the description explicitly refers to no-peer behavior.

Matched keywords include:

- `no peer`
- `nopeer`

### `Info`

A community is categorized as `Info` if the description appears to provide informational metadata rather than describing a routing action.

The informational rule checks for:

- point of presence terms via `isPoP`
- `customer`
- downstream or upstream relationship terms
- learned, received, imported, origin, ownership, or source-related terms
- peer-related descriptions, unless they explicitly match `NOPEER`
- `uplink`
- `it`
- `country`
- `region`
- region or country identifiers
- `ix`

The helper function `isRegion` splits the description using the following delimiters:

```python
delimiters = r"[;,.-_| :]"
```

It then checks whether any token belongs to ISO-3166 [`countries and regions`](https://github.com/lukes/ISO-3166-Countries-with-Regional-Codes/blob/master/all/all.csv).

If a region or country token is found, the description is treated as informational.

If none of the rule-based checks match and the extracted verb list is empty, the description is also categorized as `Info`.

### `LLSG`

A community is categorized as `LLSG` if the description contains:

- `llsg`
- `restart`

This rule is evaluated after the general informational rule.

### `Other`

A community is categorized as `Other` only when:

1. No category-specific rule matches, and
2. The description contains at least one extracted verb.

This means the description likely expresses some action, but the action is not covered by the predefined rule set.

## Helper Rule Summary

| Helper function | Purpose | Example matched terms |
|---|---|---|
| `isblackhole` | Detect blackhole or DDoS mitigation communities | `blackhole`, `rtbh`, `ddos` |
| `isShutdown` | Detect shutdown-related communities | `shutd`, `shut down`, `graceful` |
| `isPermissive` | Detect route advertisement/export permission | `advertis`, `announ`, `export`, `send` |
| `isSuppressive` | Detect route advertisement/export suppression | `no`, `don't`, `stop`, `restrict` with action terms |
| `isRedistribute` | Detect general redistribution | `distribut` |
| `isPrepend` | Detect AS-path prepending | `prepen`, `append`, `pre pend` |
| `isPREF` | Detect local preference | `local pref`, `local-pref`, `pref` |
| `isFiltering` | Detect accept/reject filtering | `accept`, `reject`, `deny`, `block` |
| `isDrop` | Detect route dropping | `drop`, `discard` |
| `isAgg` | Detect aggregation | `aggregat` |
| `isRouteStatus` | Detect route status or validation information | `valid`, `rpki`, `irr` |
| `isMED` | Detect MED or metric-related communities | `med`, `metric` |
| `isNoPeer` | Detect no-peer communities | `no peer`, `nopeer` |
| `infomation` | Detect informational communities | `customer`, `peer`, `country`, `region`, `ix` |
| `isLLSG` | Detect long-lived graceful restart / shutdown-related terms | `llsg`, `restart` |
| `isRegion` | Detect country or region codes | entries in `COUNTRYSET`, plus `uk`, `wa` |

## Notes and Assumptions

- The pipeline assumes that input text has been normalized before categorization, especially lowercased.
- Matching is substring-based, so short patterns may match unintended words. For example, `pref` may match any string containing that substring.
- Category assignment is order-sensitive. Changing the order of rules may change the output labels.
- The function name `infomation` appears to be a typo of `information`, but the behavior is unchanged.
- Some spelling variants are intentionally included, such as `prepand`, `lerned`, and `receie`, to make the rule set robust to noisy semantic descriptions.

