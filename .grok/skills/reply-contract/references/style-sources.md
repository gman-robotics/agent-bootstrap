# Style sources (reply-contract)

House style wins. These guides change **voice and marks**, not the six required slots, the show-me pairing, or Photon/iMessage bans.

Applied 2026-08-18 from Google’s developer documentation style guide plus the two “other editorial resources” it names (Apple, Red Hat).

## Hierarchy

1. This skill + channel constraints + the project in front of the human
2. [Google developer documentation style guide](https://developers.google.com/style)
3. [Apple Style Guide](https://support.apple.com/guide/applestyleguide/welcome/web) (June 2026) and [Red Hat supplementary style guide](https://redhat-documentation.github.io/supplementary-style-guide/)
4. Merriam-Webster (spelling), Chicago (nontechnical)

Google lists Apple and Red Hat as other resources, not peers. Red Hat sits under IBM Style for RH product docs — do not import IBM.

Break a rule sooner than write something barbarous. Stay consistent inside one reply.

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
