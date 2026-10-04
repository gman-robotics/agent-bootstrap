# Style sources (reply-contract)

House slots win. Voice is ASD-STE100 unless the information cannot be expressed any other way. These guides do not change the six required slots, the show-me pairing, or Photon/iMessage bans.

Applied 2026-10-03: ASD-STE100 is the writing standard. Google, Apple, and Red Hat apply only where STE has no rule.

## Hierarchy

1. This skill + channel constraints + the project in front of the human
2. ASD-STE100 (Simplified Technical English). Required. Exception only when the fact cannot be said with an approved word or a permitted technical name.
3. [Google developer documentation style guide](https://developers.google.com/style)
4. [Apple Style Guide](https://support.apple.com/guide/applestyleguide/welcome/web) (June 2026) and [Red Hat supplementary style guide](https://redhat-documentation.github.io/supplementary-style-guide/)
5. Merriam-Webster (spelling), Chicago (nontechnical)

Google lists Apple and Red Hat as other resources, not peers. Red Hat sits under IBM Style for RH product docs — do not import IBM.

Break a rule sooner than write something barbarous. Stay consistent inside one reply.

## ASD-STE100

Use the licensed dictionary as the word check. Do not copy the dictionary into this repo.

- One topic per sentence. Procedural max 20 words. Descriptive max 25 words.
- Imperative procedures. Active voice. Write the condition before the action.
- Approved word when one exists. Technical name only when no approved word keeps the meaning. Define that name once, then reuse it.
- Noun cluster of 3 nouns maximum. No slang. No synonym for an approved word.
- Different words must not mean the same thing in one reply.

## Imported (behavior)


| Rule | Source |
|------|--------|
| You / active voice; conditions before instructions | Google |
| No please / simply / easy / quickly / let’s / ! / please note | Google |
| ~26-word sentences; serial commas; no `&` for “and” | Google |
| Bold labeled UI; `code` for code-like tokens | Google + Red Hat |
| Prefer replace jargon; define once then reuse | Google jargon |
| Numbered lists for sequences — **except** when a show-me tree is the sequence | Google, house exception |
| Single-step procedure = one bullet, not `1.` | Red Hat |
| Don’t put new facts only in a diagram | Google a11y |
| Descriptive links; never “click here”; `See` is OK | Google + Apple + Red Hat |
| No pre-announce; no promised ship date for a leftover | Google + Red Hat future |
| Cut fluff; action first; include how to verify / recover | Red Hat minimalism |
| Placeholder: `<value_name>` in code font | Red Hat form; iMessage trees don’t italicize |
| Don’t verb a function name | Apple |
| No idioms; describe the event, not a sense | Apple |
| No color/position as the only cue | Google + Red Hat a11y |
| Inclusive write-arounds | All three |
| Don’t use *basically* or *as expected* | Red Hat word list |

Word lists stay on the live sites. Do not dump A–Z into a reply.

## Not imported

Heading hierarchy, notices, HTML/aria, Red Hat “avoid contractions”, Apple A–Z product catalog, RH/IBM module machinery.

## Placeholder conflict (decided)

Google `ALL_CAPS` vs Apple italics/`volumeName` vs Red Hat `<value_name>`. **House:** `<value_name>` in code font.
