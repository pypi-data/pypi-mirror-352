# Twi Phonology Guide for TTS Development

This guide provides detailed information about Twi phonology specifically for text-to-speech (TTS) development. Understanding the phonological system of Twi is essential for creating a high-quality TTS system.

## Table of Contents

1. [Introduction to Twi](#introduction-to-twi)
2. [Vowel System](#vowel-system)
3. [Consonant System](#consonant-system)
4. [Tone System](#tone-system)
5. [Syllable Structure](#syllable-structure)
6. [Phonological Processes](#phonological-processes)
7. [Orthography and Pronunciation](#orthography-and-pronunciation)
8. [Challenges for TTS](#challenges-for-tts)
9. [Phoneme Inventory for Implementation](#phoneme-inventory-for-implementation)

## Introduction to Twi

Twi (also known as Akan) is a language spoken in Ghana and parts of Côte d'Ivoire. It belongs to the Kwa language family within the Niger-Congo language group. Twi has several dialects, including Asante, Akuapem, and Fante.

Key characteristics:
- Tonal language with two main tones (high and low)
- SVO (Subject-Verb-Object) word order
- Agglutinative morphology
- Rich vowel system with ATR (Advanced Tongue Root) harmony

## Vowel System

Twi has a 9-vowel system with ATR harmony.

### Vowel Phonemes

| Vowel | IPA | Description | Example | Meaning |
|-------|-----|-------------|---------|---------|
| a | /a/ | Open front unrounded | papa | good |
| e | /e/ | Close-mid front unrounded [+ATR] | efi | from |
| ɛ | /ɛ/ | Open-mid front unrounded [-ATR] | ɛdan | house |
| i | /i/ | Close front unrounded [+ATR] | didi | eat |
| ɪ | /ɪ/ | Near-close front unrounded [-ATR] | pɪ | many |
| o | /o/ | Close-mid back rounded [+ATR] | boro | beat |
| ɔ | /ɔ/ | Open-mid back rounded [-ATR] | ɔhɔ | there |
| u | /u/ | Close back rounded [+ATR] | buu | break |
| ʊ | /ʊ/ | Near-close back rounded [-ATR] | pʊ | sea |

### Vowel Length

Vowel length is phonemic in Twi. Long vowels are typically written as doubled vowels:

- Short: da /da/ (sleep)
- Long: daa /daː/ (always)

### ATR Harmony

Twi exhibits ATR (Advanced Tongue Root) harmony, where vowels in a word tend to agree in their ATR feature:

- [+ATR] vowels: /i e o u/
- [-ATR] vowels: /ɪ ɛ ɔ ʊ/
- Neutral: /a/

Words typically contain vowels from only one set (plus the neutral /a/).

## Consonant System

Twi has approximately 20 consonant phonemes.

### Consonant Phonemes

| Consonant | IPA | Description | Example | Meaning |
|-----------|-----|-------------|---------|---------|
| b | /b/ | Voiced bilabial plosive | ba | come |
| d | /d/ | Voiced alveolar plosive | di | eat |
| f | /f/ | Voiceless labiodental fricative | fa | take |
| g | /g/ | Voiced velar plosive | gye | receive |
| h | /h/ | Voiceless glottal fricative | hu | see |
| k | /k/ | Voiceless velar plosive | ka | bite |
| l | /l/ | Alveolar lateral approximant | lɔ | love |
| m | /m/ | Bilabial nasal | ma | give |
| n | /n/ | Alveolar nasal | na | and |
| p | /p/ | Voiceless bilabial plosive | pa | good |
| r | /r/ | Alveolar trill/tap | bra | come |
| s | /s/ | Voiceless alveolar fricative | sa | dance |
| t | /t/ | Voiceless alveolar plosive | to | buy |
| w | /w/ | Labial-velar approximant | wo | you |
| y | /j/ | Palatal approximant | ye | do |

### Consonant Clusters

Twi has several consonant clusters, particularly those involving palatalization and labialization:

| Cluster | IPA | Description | Example | Meaning |
|---------|-----|-------------|---------|---------|
| ky | /tʃ/ | Voiceless palatal affricate | kyɛ | share |
| gy | /dʒ/ | Voiced palatal affricate | gye | receive |
| hy | /ç/ | Voiceless palatal fricative | hyɛ | force |
| ny | /ɲ/ | Palatal nasal | nyɛ | press |
| tw | /tɥ/ | Labialized voiceless alveolar plosive | twa | cut |
| dw | /dɥ/ | Labialized voiced alveolar plosive | dwom | song |
| kw | /kɥ/ | Labialized voiceless velar plosive | kwan | path |
| gw | /gɥ/ | Labialized voiced velar plosive | gwam | snore |
| hw | /ɥ/ | Labialized voiceless glottal fricative | hwɛ | look |
| nw | /ɲɥ/ | Labialized palatal nasal | nwa | snail |

## Tone System

Twi is a tonal language with two main tones: high and low. Tone is phonemic and can distinguish between otherwise identical words.

### Tone Types

1. **High tone** (marked with acute accent: á, é, í, ó, ú, ɛ́, ɔ́)
2. **Low tone** (marked with grave accent: à, è, ì, ò, ù, ɛ̀, ɔ̀)
3. **Mid tone** (unmarked: a, e, i, o, u, ɛ, ɔ)

### Tone Functions

Tones in Twi serve several functions:

1. **Lexical**: Distinguishing between words
   - bá (come) vs. bà (child)
   - dá (sleep) vs. dà (day)

2. **Grammatical**: Marking grammatical features
   - Present tense vs. past tense
   - Indicative vs. subjunctive mood

3. **Phrasal**: Marking phrase boundaries and questions

### Tone Rules

Several tone rules operate in Twi:

1. **Tone spreading**: A high tone can spread to adjacent syllables
2. **Downstep**: A high tone is lowered after another high tone
3. **Downdrift**: Gradual lowering of pitch throughout an utterance

## Syllable Structure

The basic syllable structure in Twi is (C)(w/y)V(N), where:
- C = consonant
- w/y = glide
- V = vowel (can be long)
- N = nasal consonant

Common syllable types:
- V: e (you)
- CV: ba (come)
- CVV: daa (always)
- CVN: dan (turn)
- CwV: twa (cut)
- CyV: kyɛ (share)

## Phonological Processes

Several phonological processes occur in Twi:

### 1. Vowel Harmony

Vowels in a word typically agree in their ATR feature:
- edi (it eats) [+ATR]
- ɔdɛ (it is sweet) [-ATR]

### 2. Assimilation

Nasal assimilation:
- /n/ assimilates to the place of articulation of a following consonant
  - /n/ + /p/ → [mp] (e.g., n+pa → mpa)
  - /n/ + /k/ → [ŋk] (e.g., n+ko → ŋko)

### 3. Vowel Elision

Vowel elision occurs when two vowels meet across word boundaries:
- me + ani → m'ani (my eye)

### 4. Tone Sandhi

Tone changes occur when words combine:
- High + High → High-Downstepped High
- Low + High → Low-High

## Orthography and Pronunciation

The standard Twi orthography uses the Latin alphabet with additional characters:

- **ɛ** - represents the open-mid front unrounded vowel /ɛ/
- **ɔ** - represents the open-mid back rounded vowel /ɔ/
- **Tone marks** - acute (´) for high tone, grave (`) for low tone

### Spelling-to-Sound Rules

1. **Vowels**:
   - 'a' → /a/
   - 'e' → /e/
   - 'ɛ' → /ɛ/
   - 'i' → /i/
   - 'o' → /o/
   - 'ɔ' → /ɔ/
   - 'u' → /u/

2. **Consonants**:
   - Most consonants have straightforward pronunciation
   - Digraphs represent single sounds: 'ky' → /tʃ/, 'tw' → /tɥ/

3. **Special Cases**:
   - 'r' is often realized as [ɾ] (tap) between vowels
   - Word-final nasals may be syllabic

## Challenges for TTS

Developing a Twi TTS system presents several challenges:

### 1. Tone Representation

- Tone is often not marked in written Twi
- Contextual tone rules must be implemented
- Tone affects meaning and naturalness

### 2. Vowel Harmony

- ATR harmony affects vowel quality
- Implementation requires morphological analysis

### 3. Consonant Clusters

- Proper pronunciation of palatalized and labialized consonants
- Timing and transitions between elements

### 4. Dialectal Variation

- Differences between Asante, Akuapem, and Fante dialects
- Lexical, phonological, and tonal variations

### 5. Orthographic Inconsistencies

- Inconsistent use of tone marks
- Variation in spelling conventions
- Handling of loan words

## Phoneme Inventory for Implementation

For implementing a Twi TTS system, we recommend the following phoneme inventory:

### Vowels (9 base + 18 toned = 27)
- Base vowels: /a, e, ɛ, i, ɪ, o, ɔ, u, ʊ/
- High-toned vowels: /á, é, ɛ́, í, ɪ́, ó, ɔ́, ú, ʊ́/
- Low-toned vowels: /à, è, ɛ̀, ì, ɪ̀, ò, ɔ̀, ù, ʊ̀/

### Consonants (20)
- Simple consonants: /b, d, f, g, h, k, l, m, n, p, r, s, t, w, y/
- Consonant clusters (treated as single phonemes): /ky, gy, hy, ny, tw/

### Special Symbols
- Silence: /_/
- Word boundary: /#/
- Syllable boundary: /./

### Implementation Notes

1. **Phoneme-to-Acoustic Mapping**:
   - Each phoneme should map to its acoustic realization
   - Context-dependent models may be necessary for tone

2. **Duration Modeling**:
   - Long vowels should have longer duration
   - Tones affect duration patterns

3. **Prosody Modeling**:
   - Implement downdrift across phrases
   - Model question intonation patterns
   - Capture natural rhythm of Twi

4. **G2P Conversion**:
   - Implement comprehensive grapheme-to-phoneme rules
   - Handle tone assignment for unmarked text
   - Account for dialectal variations

---
