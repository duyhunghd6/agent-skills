---
name: abcjs
description: JavaScript library for rendering ABC music notation as SVG and playing it as audio. Use when implementing music notation rendering, audio playback, interactive music editors, or animation synchronized with music. Triggers on tasks involving ABC notation, sheet music display, music synthesis, or MIDI generation.
argument-hint: <abc-notation-string-or-file>
metadata:
  author: paulrosen
  version: "6.6.0"
  license: MIT
  docs: https://docs.abcjs.net
  repo: https://github.com/paulrosen/abcjs
---

# abcjs - Music Notation Library

JavaScript library for rendering standard music notation in the browser using ABC notation format. Provides SVG rendering, audio synthesis, live editing, and playback animation.

## Reference Implementation

Full source code: `reference/abcjs/`

## Installation

```bash
npm install abcjs
```

CDN:

```html
<script src="https://cdn.jsdelivr.net/npm/abcjs@6/dist/abcjs-basic-min.js"></script>
```

---

## ABC Notation Reference

ABC is a text-based music notation format. Full standard: [abcnotation.com](http://abcnotation.com/learn)

### Header Fields

```abc
X: 1                    % Reference number (required)
T: Tune Title           % Title
C: Composer Name        % Composer
M: 4/4                  % Meter (time signature)
L: 1/8                  % Default note length
Q: 1/4=120              % Tempo (quarter=120 bpm)
K: G                    % Key signature (required, last header)
```

### Notes

| Notation        | Description            |
| --------------- | ---------------------- |
| `C D E F G A B` | Notes in lower octave  |
| `c d e f g a b` | Notes in middle octave |
| `C, D,`         | Octave down (comma)    |
| `c' d'`         | Octave up (apostrophe) |
| `^C`            | Sharp                  |
| `_B`            | Flat                   |
| `=C`            | Natural                |

### Note Lengths

| Notation      | Description   |
| ------------- | ------------- |
| `C2`          | Double length |
| `C/2` or `C/` | Half length   |
| `C3/2`        | Dotted (1.5x) |
| `C4`          | 4x length     |

### Rests

| Notation | Description           |
| -------- | --------------------- |
| `z`      | Rest (default length) |
| `z2`     | Rest (double length)  |
| `x`      | Invisible rest        |

### Chords and Groupings

| Notation | Description                |
| -------- | -------------------------- |
| `[CEG]`  | Chord (simultaneous notes) |
| `"Am"C`  | Chord symbol above note    |
| `(CDE)`  | Slur                       |
| `C-C`    | Tie                        |
| `{g}A`   | Grace note                 |

### Bar Lines

| Notation | Description   |
| -------- | ------------- | -------------------- |
| `\|`     | Single bar    |
| `\|\|`   | Double bar    |
| `\|:`    | Start repeat  |
| `:\|`    | End repeat    |
| `\|1`    | First ending  |
| `\|2`    | Second ending |
| `[       | `             | Thick-thin bar       |
| `        | ]`            | Thin-thick bar (end) |

### Decorations

| Notation           | Description          |
| ------------------ | -------------------- |
| `!p!` `!f!` `!ff!` | Dynamics             |
| `!>!`              | Accent               |
| `!fermata!`        | Fermata              |
| `!trill!`          | Trill                |
| `!mark!`           | Add "mark" CSS class |

### Alternate Note Heads

In `K:` or `V:` lines:

```abc
K:C style=rhythm      % Rhythm slashes
K:C style=harmonic    % Diamond heads
K:C style=x           % X note heads
K:C style=triangle    % Triangle heads
```

Or as decoration: `!style=rhythm!C`

---

## ABC Notation v2.1 Writing Guidelines

This section provides comprehensive guidance for writing ABC notation conforming to the **ABC Standard v2.1 (Dec 2011)**. Following these guidelines ensures your notation is portable, correctly rendered, and properly played back.

### File Structure

Every ABC file should begin with a version identifier:

```abc
%abc-2.1
```

An **abc tune** consists of:

1. **Tune header** - Information fields (must start with `X:`, followed by `T:`, and end with `K:`)
2. **Tune body** - Music code

Tunes are separated by **empty lines**.

### Required Header Fields

The minimal valid tune requires these fields in order:

```abc
X:1                    % Reference number (first, required)
T:My Tune Title        % Title (second, required)
K:C                    % Key signature (last, required)
```

**Complete tune header example:**

```abc
X:1
T:The Irish Washerwoman
C:Trad.
R:Jig
M:6/8
L:1/8
Q:1/4=120
K:G
```

### Pitch Notation (v2.1 Standard)

ABC uses letters to represent pitches on the treble clef:

| Notation        | Pitch    | Octave Description                 |
| --------------- | -------- | ---------------------------------- |
| `C D E F G A B` | C4 to B4 | Lower octave (middle C to B above) |
| `c d e f g a b` | C5 to B5 | Middle octave                      |
| `c' d' e'`      | C6+      | One octave up (apostrophe)         |
| `c'' d''`       | C7+      | Two octaves up                     |
| `C, D, E,`      | C3 to B3 | One octave down (comma)            |
| `C,, D,,`       | C2+      | Two octaves down                   |

**⚠️ CRITICAL (v2.1):** Combining `,` and `'` on the same note is legal but NOT recommended:

```abc
% Legal but confusing - avoid this:
C,',   % Same as C,
C'     % Same as c (uppercase C + apostrophe = lowercase c)
```

**Recommended practice:**

```abc
% Clear octave notation:
C, D, E, F, G, A, B,  | % Octave 3
C D E F G A B         | % Octave 4 (middle C = C)
c d e f g a b         | % Octave 5
c' d' e' f' g' a' b'  | % Octave 6
```

### Accidentals (v2.1 Standard)

Accidentals are placed **before** the note letter:

| Symbol | Meaning                           |
| ------ | --------------------------------- |
| `^C`   | C sharp                           |
| `^^C`  | C double sharp                    |
| `_B`   | B flat                            |
| `__B`  | B double flat                     |
| `=C`   | C natural (cancels key signature) |

**Example - Chromatic scale:**

```abc
K:C
C ^C D ^D E F ^F G ^G A ^A B | c |
```

**⚠️ IMPORTANT (v2.1):** By default, accidentals apply to **all notes of the same pitch in all octaves** until the end of the bar. Use `=` natural to explicitly cancel:

```abc
K:C
^C c =C |  % First C is sharp, second c (octave up) is also sharp, third C is natural
```

### Note Lengths (v2.1 Standard)

Note length is relative to the **unit note length** set by `L:`:

| L:1/8 Setting  | Notation       | Duration               |
| -------------- | -------------- | ---------------------- |
| eighth note    | `C` or `C1`    | 1 unit                 |
| quarter note   | `C2`           | 2 units                |
| dotted quarter | `C3`           | 3 units (1.5x quarter) |
| half note      | `C4`           | 4 units                |
| dotted half    | `C6`           | 6 units                |
| sixteenth note | `C/2` or `C/`  | 0.5 units              |
| thirty-second  | `C/4` or `C//` | 0.25 units             |
| dotted eighth  | `C3/2`         | 1.5 units              |

**Example - Mixed note lengths:**

```abc
L:1/8
K:C
C2 D E/2F/2 G4 | A// B// c/ d | % quarter, eighth, 2 sixteenths, half | 32nds, 16ths, 8th
```

**Default L: when not specified:**

- If meter ≥ 0.75 (e.g., 4/4, 6/8, 3/4): `L:1/8`
- If meter < 0.75 (e.g., 2/4): `L:1/16`

### Broken Rhythm (v2.1 Standard)

Use `>` and `<` for dotted rhythms (common in jigs, hornpipes, strathspeys):

| Notation | Meaning                             |
| -------- | ----------------------------------- |
| `A>B`    | A is dotted, B is halved (A3/2 B/2) |
| `A<B`    | A is halved, B is dotted (A/2 B3/2) |
| `A>>B`   | A is double-dotted, B is quartered  |
| `A<<B`   | A is quartered, B is double-dotted  |

**Example - Hornpipe rhythm:**

```abc
M:4/4
L:1/8
K:G
G>A B>c d>e f>g | a>g f>e d>c B>A |
```

**⚠️ WARNING:** Do not use broken rhythm between notes of unequal lengths - results are undefined.

### Rests (v2.1 Standard)

| Notation    | Description                           |
| ----------- | ------------------------------------- |
| `z`         | Visible rest (uses unit note length)  |
| `z2`, `z4`  | Rest with length multiplier           |
| `z/2`, `z/` | Half-length rest                      |
| `x`         | Invisible rest (spacing, not printed) |
| `Z`         | Multi-measure rest (whole bar)        |
| `Z4`        | 4-bar rest                            |
| `X`         | Multi-measure invisible rest          |

**Example:**

```abc
M:4/4
L:1/4
K:C
C D z E | z4 | Z2 | c d e f |
%       rest  whole bar  2-bar rest
```

### Beaming (v2.1 Standard)

Notes are beamed together when written **without spaces**:

```abc
L:1/8
K:C
CDEF GABc |  % Two beamed groups of 4
C D E F G A B c |  % All notes separate (no beams)
CD EF GA Bc |  % Four beamed groups of 2
```

**Back quotes** (`` ` ``) can be used between notes for readability without breaking beams:

```abc
A2`B`C  % Same as A2BC - beamed together
```

### Bar Lines and Repeats (v2.1 Standard)

| Symbol            | Meaning                       |
| ----------------- | ----------------------------- |
| `\|`              | Bar line                      |
| `\|\|`            | Double bar line (thin-thin)   |
| `\|]`             | Thin-thick double bar (end)   |
| `[\|`             | Thick-thin double bar (start) |
| `\|:`             | Start repeat                  |
| `:\|`             | End repeat                    |
| `::`              | End and start repeat          |
| `:\|:`, `::\|\|:` | Also valid repeat variants    |
| `.\|`             | Dotted bar line               |
| `[\|]`            | Invisible bar line            |

**First/second endings:**

```abc
K:G
|: G A B c | d e f g |1 a g f e | d c B A :|2 a b c' d' | g4 |]
```

**Multiple endings (with P: parts):**

```abc
P:A4
K:C
|: C D E F |[1 G2 G2 :|[2 A2 A2 :|[3 B2 B2 :|[4 c4 |]
```

**Ending ranges:**

```abc
[1,3 G2 G2 :|   % Play on 1st and 3rd repeat
[1-3 G2 G2 :|   % Play on 1st, 2nd, and 3rd repeat
```

### Ties and Slurs (v2.1 Standard)

**⚠️ CRITICAL:** Ties and slurs are **different**:

| Symbol | Purpose                  | Usage                    |
| ------ | ------------------------ | ------------------------ |
| `-`    | Tie: connects same pitch | `c4-c4` (played as c8)   |
| `()`   | Slur: phrasing/legato    | `(cdef)` (legato phrase) |

**Tie rules:**

```abc
% Tie must be adjacent to first note:
c4-c4    % Correct
c4- c4   % WRONG - space before second note is OK, but not after tie
c4 -c4   % WRONG - space before tie is NOT allowed

% Tie across bar lines:
abc-|cba  % Correct
abc|-cba  % WRONG
```

**Slur examples:**

```abc
(CDEF) | (C D E F) |  % Both valid - spaces allowed inside slurs
((c d e) f g a)       % Nested slurs allowed
(c d (e) f g a)       % Slur starting and ending on same note
```

**Dotted ties/slurs** (for optional phrasing):

```abc
C.-C     % Dotted tie
.(cde)   % Dotted slur
```

### Grace Notes (v2.1 Standard)

Grace notes are enclosed in `{}`:

```abc
{g}A    % Single grace note before A
{gab}c  % Multiple grace notes before c
```

**Acciaccatura** (slashed grace note) - use `/` after opening brace:

```abc
{/g}C      % Single slashed grace note
{/gagab}C  % Multiple slashed grace notes
```

**Example - Highland bagpipe gracing:**

```abc
K:D
{gcd}c<{e}A {gAGAG}A2 | {gef}e>A {gAGAG}Ad |
```

### Tuplets (v2.1 Standard)

Basic syntax: `(p` where p = number of notes in tuplet

| Symbol     | Meaning                            |
| ---------- | ---------------------------------- |
| `(2ab`     | Duplet: 2 notes in time of 3       |
| `(3abc`    | Triplet: 3 notes in time of 2      |
| `(4abcd`   | Quadruplet: 4 notes in time of 3   |
| `(5abcde`  | Quintuplet: 5 notes in time of n\* |
| `(6abcdef` | Sextuplet: 6 notes in time of 2    |

\*n = 3 for compound meters (6/8, 9/8, 12/8), otherwise 2

**Extended syntax:** `(p:q:r` = p notes in time of q, for next r notes

```abc
(3abc         % 3 notes in time of 2, for 3 notes (standard triplet)
(3:2:2 G4c2   % 3 notes in time of 2, but only for 2 notes
(3::4 G2A2Bc  % 3 notes in time of 2, for 4 notes
(5:4:5 GABAB  % 5 notes in time of 4
```

**Example:**

```abc
M:4/4
L:1/8
K:C
(3cde (3fga | (3:2:4 c2d2ef | (6GABcde f2 |
```

### Decorations (v2.1 Standard)

**Short-form decorations:**

| Symbol | Meaning       |
| ------ | ------------- |
| `.`    | Staccato      |
| `~`    | Irish roll    |
| `H`    | Fermata       |
| `L`    | Accent        |
| `M`    | Lower mordent |
| `P`    | Upper mordent |
| `T`    | Trill         |
| `u`    | Up-bow        |
| `v`    | Down-bow      |

**Long-form decorations** using `!...!`:

```abc
!trill!c    !fermata!c    !accent!c    !staccato!c
!pp!c2      !mf!c2        !ff!c2       !sfz!c2
!crescendo(!cdef!crescendo)!
!>!c        !upbow!c      !downbow!c
!segno!|    !coda!|       !D.S.!|      !D.C.!|
!0!c !1!d !2!e !3!f !4!g  % Fingerings
```

**Decoration placement:** Always **before** the note:

```abc
!f! .~^c'3   % forte, staccato, roll, C# octave up, dotted quarter
```

### Chord Symbols (v2.1 Standard)

Chord symbols are placed in double quotes before the note:

```abc
"Am"A2 "G"G2 | "C"c4 | "Dm7"d2 "G7"G2 | "C"c4 |
```

**Chord format:** `<note><accidental><type></bass>`

```abc
"C"       % C major
"Cm"      % C minor
"C7"      % C dominant 7th
"Cmaj7"   % C major 7th
"Cdim"    % C diminished
"Caug"    % C augmented (also "C+")
"Csus4"   % C suspended 4th
"C/E"     % C major with E bass (first inversion)
"C/G"     % C major with G bass (second inversion)
"Am7/G"   % A minor 7th with G bass
"G(Em)"   % Alternate chord in parentheses (print only)
```

### Annotations (v2.1 Standard)

Text annotations with placement specifiers:

| Prefix    | Placement       |
| --------- | --------------- |
| `"^text"` | Above the staff |
| `"_text"` | Below the staff |
| `"<text"` | Left of note    |
| `">text"` | Right of note   |
| `"@text"` | Program decides |

```abc
"^Allegro" C2 | "^rit." G2 "_sotto voce" | "<(" ">)" c |
```

### Lyrics (v2.1 Standard)

**`W:` field** - Lyrics printed after the tune
**`w:` field** - Lyrics aligned with notes

**Alignment symbols:**

| Symbol | Meaning                                           |
| ------ | ------------------------------------------------- |
| `-`    | Syllable break within word                        |
| `_`    | Hold syllable for extra note                      |
| `*`    | Skip one note                                     |
| `~`    | Non-breaking space (one syllable, multiple words) |
| `\-`   | Print hyphen, stay on same note                   |
| `\|`   | Advance to next bar                               |

**Example:**

```abc
C D E F | G A B c |
w: doh re mi fa | sol la ti doh |
```

**Multi-syllable words:**

```abc
G2 A2 | B2 c2 |
w: hap-py | birth-day |
```

**Held syllables:**

```abc
c4 D2 E2 | F4 G4 |
w: lo----ng_ | no---te |
```

**Multiple verses:**

```abc
C D E F | G4 |
w: First verse words here
w: Se-cond verse words go
w: Third verse ly-rics too
```

**Verse numbering:**

```abc
C D E F | G4 |
w: 1.~First verse words
w: 2.~Se-cond verse here
```

### Multi-Voice Music (v2.1 Standard)

Define voices in header with `V:`, then use `[V:ID]` in body:

```abc
X:1
T:Two-Part Example
M:4/4
L:1/4
%%score (S A)
V:S clef=treble name="Soprano"
V:A clef=treble name="Alto"
K:C
%
[V:S] c d e f | g2 g2 |
[V:A] E F G A | B2 c2 |
```

**Voice properties:**

```abc
V:T1 clef=treble-8 name="Tenor" snm="T"
V:B1 clef=bass middle=d name="Bass" transpose=-24
```

**Voice overlay** (`&`) - multiple voices in one measure:

```abc
c d e f | g a b c' &\
E F G A | B c d e |]
```

### Order of ABC Constructs (v2.1 Standard)

**⚠️ CRITICAL:** Elements must appear in this order:

1. Grace notes `{}`
2. Chord symbols `"Am"`
3. Annotations/Decorations `"^text"`, `!trill!`
4. Accidentals `^`, `_`, `=`
5. Note letter `C`, `c`
6. Octave modifier `'`, `,`
7. Note length `2`, `/2`
8. Tie `-`

**Correct order:**

```abc
{g}"Am"!f!^c'2-   % grace, chord, decoration, sharp, note, octave up, length, tie
```

### Common Mistakes to Avoid

**❌ WRONG - Tie not adjacent to first note:**

```abc
c4 -c4   % Space before tie
```

**✓ CORRECT:**

```abc
c4-c4    % Tie immediately follows note
c4- c4   % Space after tie is OK
```

**❌ WRONG - Accidental after note:**

```abc
C^ D     % Sharp should be before C
```

**✓ CORRECT:**

```abc
^C D     % Sharp before the note
```

**❌ WRONG - Decoration inside chord:**

```abc
[C!trill!E G]   % Decoration should be before chord or on individual note
```

**✓ CORRECT:**

```abc
!trill![CEG]    % Decoration on whole chord
[!trill!CEG]    % Decoration on C only
```

**❌ WRONG - Inline field spacing:**

```abc
[M: 4/4]   % No space after bracket
```

**✓ CORRECT:**

```abc
[M:4/4]    % No spaces around field identifier
```

### Complete Example (v2.1 Compliant)

```abc
%abc-2.1
X:1
T:Amazing Grace
C:John Newton
M:3/4
L:1/4
Q:1/4=90
K:G
D/2 | "G"G2 B/2G/2 | "C"B2 A/2G/2 | "G"G2 E | "G"D2 D/2 |
"G"G2 B/2G/2 | "C"B2 "D7"A | "G"B3- | B2 d |
"G"d2 B/2d/2 | "Em"d/2B/2 G2 | "C"E2 D/2E/2 | "G/D"G2 E |
"G"D2 G | "C"G/2B/2 G/2E/2 "D7"D | "G"G3- | G2 |]
w: A-ma-zing grace, how sweet the sound that saved a wretch like me!
+: I once was lost, but now am found, was blind but now I see.
```

---

## Visual Rendering

### renderAbc()

Main entry point for rendering ABC notation to SVG:

```javascript
import ABCJS from "abcjs";

// Basic usage
const visualObj = ABCJS.renderAbc("paper", abcString)[0];

// With options
const visualObj = ABCJS.renderAbc("paper", abcString, {
  responsive: "resize",
  add_classes: true,
  staffwidth: 740,
  wrap: { minSpacing: 1.8, maxSpacing: 2.7, preferredMeasuresPerLine: 4 },
})[0];

// Multiple tunes to multiple elements
ABCJS.renderAbc(["target1", "target2"], abcString);

// Invisible rendering (audio/analysis only)
const visualObj = ABCJS.renderAbc("*", abcString)[0];
```

### Render Options Reference

| Option            | Default           | Description                           |
| ----------------- | ----------------- | ------------------------------------- |
| `responsive`      | undefined         | `"resize"` for responsive SVG sizing  |
| `staffwidth`      | 740               | Staff width in pixels                 |
| `scale`           | 1                 | Scale factor (0-1 smaller, >1 larger) |
| `add_classes`     | false             | Add CSS classes for styling           |
| `paddingtop`      | 15                | Top padding in pixels                 |
| `paddingbottom`   | 30                | Bottom padding                        |
| `paddingleft`     | 15                | Left padding                          |
| `paddingright`    | 50                | Right padding                         |
| `visualTranspose` | 0                 | Transpose by semitones                |
| `foregroundColor` | currentColor      | Color for all elements                |
| `selectionColor`  | "#ff0000"         | Color for clicked notes               |
| `dragColor`       | same as selection | Color during drag                     |

**Layout Options:**

| Option           | Default   | Description                                                           |
| ---------------- | --------- | --------------------------------------------------------------------- |
| `wrap`           | null      | Line wrapping: `{ minSpacing, maxSpacing, preferredMeasuresPerLine }` |
| `lineBreaks`     | undefined | Array of measure numbers for line breaks                              |
| `oneSvgPerLine`  | false     | Separate SVG per staff system                                         |
| `expandToWidest` | false     | Expand all lines to widest line                                       |
| `stafftopmargin` | 0         | Extra space above each staff                                          |
| `minPadding`     | 0         | Minimum pixels between elements                                       |
| `print`          | false     | Print mode (margins, headers)                                         |

**Feature Options:**

| Option           | Default       | Description                             |
| ---------------- | ------------- | --------------------------------------- |
| `clickListener`  | null          | Callback for note clicks                |
| `dragging`       | false         | Enable note dragging                    |
| `selectTypes`    | false         | Array or `true` for selectable elements |
| `tablature`      | undefined     | Add tablature staff                     |
| `chordGrid`      | undefined     | `"noMusic"` or `"withMusic"`            |
| `jazzchords`     | false         | Jazz-style chord formatting             |
| `germanAlphabet` | false         | German notation (H for B)               |
| `hint_measures`  | false         | Show next measure at line end           |
| `initialClef`    | false         | Show clef only on first line            |
| `accentAbove`    | false         | Place accents above notes               |
| `ariaLabel`      | "Sheet Music" | Accessibility label                     |

**Wrap Option Details:**

```javascript
{
  wrap: {
    minSpacing: 1.8,              // 1 = tight, 2 = double spacing
    maxSpacing: 2.7,              // Max spacing before line break
    preferredMeasuresPerLine: 4,  // Target measures per line
    lastLineLimit: 0.5            // Min fill ratio for last line
  }
}
```

### Return Value (visualObj)

`renderAbc()` returns an array of tune objects. Key properties:

```javascript
const visualObj = ABCJS.renderAbc("paper", abc)[0];

// Data properties
visualObj.formatting; // Fonts and formatting commands
visualObj.lines; // Array of staff systems
visualObj.metaText; // Title, composer, etc.
visualObj.version; // Format version
visualObj.visualTranspose; // Applied transposition

// Methods
visualObj.getBarLength(); // Bar duration (1 = whole note)
visualObj.getBeatLength(); // Beat duration
visualObj.getBeatsPerMeasure(); // Beats per measure
visualObj.getBpm(); // Tempo in BPM
visualObj.getMeter(); // Meter object
visualObj.getMeterFraction(); // { num: 4, den: 4 }
visualObj.getKeySignature(); // Key signature object
visualObj.getPickupLength(); // Pickup measure length
visualObj.getTotalBeats(); // Total beats (after setUpAudio)
visualObj.getTotalTime(); // Total seconds (after setUpAudio)
visualObj.millisecondsPerMeasure(); // Ms per measure
visualObj.setUpAudio(); // Initialize audio data
visualObj.getElementFromChar(idx); // Element at char position
visualObj.findSelectableElement(el); // Find selectable for element
visualObj.getSelectableArray(); // All selectable elements
```

---

## CSS Classes

When `add_classes: true`, elements get classes for styling:

```css
/* Staff lines */
.abcjs-staff { stroke: #ccc; }

/* Notes */
.abcjs-note { fill: black; }
.abcjs-note.abcjs-v0 { } /* Voice 0 */
.abcjs-note.abcjs-l0 { } /* Line 0 */
.abcjs-note.abcjs-mm0 { } /* Measure 0 */

/* Highlight during playback */
.abcjs-note.highlight {
  fill: #00bcd4;
  stroke: #00bcd4;
}

/* Hide finished measures */
.abcjs-mm0.hidden {
  opacity: 0;
  transition: opacity 0.3s;
}

/* Cursor line */
.abcjs-cursor {
  stroke: blue;
  stroke-width: 2;
}

/* Other classes */
.abcjs-bar          /* Bar lines */
.abcjs-clef         /* Clef */
.abcjs-key-sig      /* Key signature */
.abcjs-time-sig     /* Time signature */
.abcjs-title        /* Title */
.abcjs-rhythm       /* Rhythm notation */
.abcjs-annotation   /* Text annotations */
.abcjs-chord        /* Chord symbols */
.abcjs-lyric        /* Lyrics */
.abcjs-beam         /* Note beams */
.abcjs-slur         /* Slurs */
.abcjs-tie          /* Ties */
```

---

## Click Listener

Handle user clicks on notation:

```javascript
function clickListener(
  abcelem,
  tuneNumber,
  classes,
  analysis,
  drag,
  mouseEvent,
) {
  console.log("Clicked:", {
    line: analysis.line, // Zero-based line number
    measure: analysis.measure, // Measure number on line
    voice: analysis.voice, // Voice number
    name: analysis.name, // Element type ("note", etc.)
    clickedName: analysis.clickedName, // Specific clicked part
    parentClasses: analysis.parentClasses,
    selectableElement: analysis.selectableElement,
  });
}

ABCJS.renderAbc("paper", abc, {
  clickListener: clickListener,
  add_classes: true, // Required for classes info
});
```

---

## Selecting and Dragging

Enable selection and dragging of notes:

```javascript
ABCJS.renderAbc("paper", abc, {
  dragging: true,
  selectTypes: ["note"], // Or true for all types
  selectionColor: "#0066cc",
  dragColor: "#ff6600",
  clickListener: function (abcelem, tuneNumber, classes, analysis, drag) {
    if (drag && drag.step !== 0) {
      // drag.step: visual positions moved (negative = down)
      // Update ABC string and re-render
      console.log("Dragged by", drag.step, "positions");
    }
  },
});
```

**Selectable Types:**
`"note"`, `"bar"`, `"clef"`, `"keySignature"`, `"timeSignature"`, `"title"`, `"subtitle"`, `"composer"`, `"author"`, `"tempo"`, `"part"`, `"dynamicDecoration"`, `"ending"`, `"slur"`, `"rhythm"`, `"voiceName"`, `"freeText"`, `"extraText"`, `"unalignedWords"`, `"brace"`, `"partOrder"`

---

## Tablature

Add guitar/violin tablature below standard notation:

```javascript
ABCJS.renderAbc("paper", abc, {
  tablature: [
    {
      instrument: "guitar", // "guitar", "violin", "mandolin", "fiveString"
      label: "Guitar (%T)", // %T = tuning
      tuning: ["E,", "A,", "D", "G", "B", "e"], // Low to high
      capo: 0, // Fret number
      highestNote: "a'", // Highest playable note
      hideTabSymbol: false, // Hide "TAB" clef
    },
  ],
});
```

**Default Tunings:**

- Guitar: `["E,", "A,", "D", "G", "B", "e"]`
- Violin/Mandolin/Fiddle: `["G,", "D", "A", "e"]`

---

## Audio Synthesis

### CreateSynth - Low-level Audio

```javascript
const synth = new ABCJS.synth.CreateSynth();

// Must be called from user gesture (click handler)
const audioContext = new AudioContext();

await synth.init({
  visualObj: visualObj,
  audioContext: audioContext,
  millisecondsPerMeasure: visualObj.millisecondsPerMeasure(),
  options: {
    soundFontUrl: "https://paulrosen.github.io/midi-js-soundfonts/abcjs/",
    pan: [-0.3, 0.3], // Stereo panning per track
    program: 0, // MIDI instrument (0 = piano)
    midiTranspose: 0, // Transpose MIDI output
  },
});

// Prime the audio buffer
const response = await synth.prime();
console.log("Duration:", response.duration, "seconds");

// Playback control
synth.start();
synth.pause();
synth.resume();
synth.seek(0.5); // 50% position
synth.seek(30, "seconds"); // 30 seconds in
synth.seek(16, "beats"); // 16 beats in
synth.stop();

// Get audio data
const buffer = synth.getAudioBuffer(); // AudioBuffer
const wav = synth.download(); // WAV blob
```

### SynthController - UI Controls

Built-in audio control widget:

```javascript
const synthController = new ABCJS.synth.SynthController();

// Create UI in element
synthController.load("#audio-controls", cursorControl, {
  displayRestart: true,
  displayPlay: true,
  displayProgress: true,
  displayClock: true,
  displayWarp: true,
  displayLoop: true,
});

// Load tune (userAction = true if from user gesture)
synthController.setTune(visualObj, userAction, {
  qpm: 120, // Override tempo
  program: 0, // MIDI instrument
  chordsOff: false, // Disable chord playback
  voicesOff: false, // Disable voice playback
  drumIntro: 2, // Drum intro measures
  drum: "dd 76 77 54 50 100", // Custom drum pattern
  soundFontUrl: "https://...",
});

// Programmatic control
synthController.play();
synthController.pause();
synthController.restart();
synthController.toggleLoop();
synthController.setWarp(150); // 150% speed
synthController.download("tune.wav");
```

CSS for audio controls:

```html
<link rel="stylesheet" href="abcjs-audio.css" />
```

### MIDI File Generation

```javascript
// From visualObj
const midiBlob = ABCJS.synth.getMidiFile(visualObj, {
  midiOutputType: "binary", // Returns Blob
});

// As download link
const linkHtml = ABCJS.synth.getMidiFile(abc, {
  midiOutputType: "link",
  downloadLabel: "Download MIDI for %T",
  fileName: "tune.mid",
});

// As encoded string
const encoded = ABCJS.synth.getMidiFile(visualObj, {
  midiOutputType: "encoded",
});
```

---

## Timing Callbacks (Animation)

Synchronize animations with music timing:

```javascript
const visualObj = ABCJS.renderAbc("paper", abc, { add_classes: true })[0];

const timingCallbacks = new ABCJS.TimingCallbacks(visualObj, {
  qpm: 120, // Tempo override
  extraMeasuresAtBeginning: 0, // Count-in measures
  beatSubdivisions: 1, // Callbacks per beat

  beatCallback: (beatNumber, totalBeats, totalTime, position, debugInfo) => {
    // Called every beat
    // position: { left, top, height } - cursor position
    console.log(`Beat ${beatNumber}/${totalBeats}`);
  },

  eventCallback: (ev) => {
    if (!ev) {
      // End of tune
      return; // or return "continue" to loop
    }

    // Highlight current notes
    ev.elements.forEach((group) => {
      group.forEach((el) => el.classList.add("highlight"));
    });

    // ev properties:
    // milliseconds, millisecondsPerMeasure, line, measureNumber
    // top, height, left, width, elements
    // midiPitches: [{ pitch, durationInMeasures, volume, instrument }]
  },

  lineEndCallback: (info) => {
    // Called when reaching end of each line
    // Useful for scrolling
    console.log("Line ended:", info);
  },

  lineEndAnticipation: 500, // Call lineEndCallback 500ms early
});

// Control methods
timingCallbacks.start(); // Start from beginning
timingCallbacks.start(0.5); // Start at 50%
timingCallbacks.start(10, "seconds"); // Start at 10s
timingCallbacks.start(8, "beats"); // Start at beat 8
timingCallbacks.pause();
timingCallbacks.stop();
timingCallbacks.reset();
timingCallbacks.setProgress(0.25); // Jump to 25%
timingCallbacks.replaceTarget(newVisualObj); // Change tune
```

---

## Interactive Editor

Live-updating ABC editor:

```javascript
const editor = new ABCJS.Editor("abc-textarea", {
  canvas_id: "paper", // Render target
  warnings_id: "warnings", // Error display
  generate_warnings: true,
  abcjsParams: {
    responsive: "resize",
    add_classes: true,
  },

  // Audio integration
  synth: {
    el: "#audio-controls",
    cursorControl: cursorControlObject,
    options: {
      displayPlay: true,
      displayProgress: true,
    },
  },

  // Callbacks
  onchange: function () {}, // Called on ABC changes
  selectionChangeCallback: function () {}, // Called on selection change
  indicate_changed: true, // Add class when dirty
});

// Methods
editor.setReadOnly(true);
editor.paramChanged({ responsive: "resize" }); // Update render options
editor.synthParamChanged({ qpm: 140 }); // Update synth options
editor.millisecondsPerMeasure();
editor.getTunes(); // Get parsed tunes
editor.isDirty();
editor.setNotDirty();
editor.pause(true); // Pause real-time updates
```

HTML structure:

```html
<textarea id="abc-textarea">
X:1
T: My Tune
M: 4/4
K: C
CDEF|GABc|</textarea
>
<div id="warnings"></div>
<div id="paper"></div>
<div id="audio-controls"></div>
```

---

## Tune Book Analysis

Work with collections of tunes:

```javascript
// Count tunes in string
const count = ABCJS.numberOfTunes(tunebookString);

// Create TuneBook object
const tuneBook = new ABCJS.TuneBook(tunebookString);

// Access tunes
const allTunes = tuneBook.tunes; // Array of tune info
const tune = tuneBook.getTuneById("1"); // By X: number
const tune = tuneBook.getTuneByTitle("Cooley's");

// Extract measures
const measures = ABCJS.extractMeasures(tunebookString);

// Render specific tune from tunebook
ABCJS.renderAbc("paper", tunebookString, { startingTune: 2 });
```

---

## Transposition

```javascript
// Visual transposition (during render)
ABCJS.renderAbc("paper", abc, { visualTranspose: 5 }); // Up 5 semitones

// String transposition (returns new ABC)
const transposedAbc = ABCJS.strTranspose(abc, -3); // Down 3 semitones
```

---

## Examples

See `reference/abcjs/examples/` for complete working examples:

| File                   | Description             |
| ---------------------- | ----------------------- |
| `basic.html`           | Simple rendering        |
| `basic-synth.html`     | Audio playback          |
| `full-synth.html`      | Complete audio control  |
| `editor.html`          | Live editor             |
| `animation.html`       | Cursor and highlighting |
| `tablatures.html`      | Guitar/instrument tabs  |
| `basic-transpose.html` | Key transposition       |
| `dragging.html`        | Note editing            |
| `karaoke-synth.html`   | Karaoke-style display   |

---

## TypeScript Support

```typescript
import ABCJS, {
  TuneObject,
  SynthController,
  TimingCallbacks,
  Editor,
} from "abcjs";
```

---

## Full Documentation

https://docs.abcjs.net
