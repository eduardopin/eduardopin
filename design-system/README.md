# Pin Open design system

Version: see `VERSION` (1.0.0). This directory is the source of truth for the four pages: the profile hub (this repository), agenfk-squad, AgentCenter and the AWS IaC Enterprise Library.

## Files

- `tokens.json`: every colour (light and dark), type style, space, radius, shadow, opacity, duration and easing.
- `bundle.css`: the component styles. It reads only token names, never a raw colour.
- `VERSION`: the semantic version of the pair above.
- `../scripts/build_ds_css.py`: compiles both into `site/assets/pin-open-<version>.css`, tokens first, components second. The first line names the version, the hub commit that last touched this directory, and the sha256 of the rest of the file.

## How a page uses it

Each page commits its own copy at `site/assets/pin-open-<version>.css` and loads its `site/styles.css` after it. That file holds only the page's overrides: the `accent`, `accent-fill` and `on-accent` re-point, and the page's own sections. Pages never link this file across repositories at runtime: each repository deploys alone, and its checks run against the CSS in its own commit.

Check a vendored copy against this directory:

```
python3 scripts/build_ds_css.py check <repo>/site/assets/pin-open-1.0.0.css --ref pin-open-1.0.0
```

It fails when the vendored body no longer matches its own sha256, when its version is not the hub's version at that ref, or when its body differs from what the hub compiles at that ref. Change this directory only with a version bump in `VERSION`.

## Fonts and licences

| Family | Use | Licence | Source |
|---|---|---|---|
| Archivo (variable: width 62–125, weight 100–900) | display and body | SIL Open Font License 1.1. Copyright 2020 The Archivo Project Authors (Omnibus-Type) | Google Fonts `ofl/archivo/OFL.txt` and `METADATA.pb` (`license: "OFL"`), read 2026-11-13 |
| Martian Mono (variable: width 75–112.5, weight 100–800) | labels, code, readouts | SIL Open Font License 1.1. Copyright 2021 The Martian Mono Project Authors (Roman Shamin, Evil Martians) | Google Fonts `ofl/martianmono/OFL.txt` and `METADATA.pb` (`license: "OFL"`), read 2026-11-13 |

Pages load both from Google Fonts with `display=swap` and a `preconnect`. Self-hosting the woff2 files (about 120 KB per site) is the alternative if no third-party request is wanted; the OFL allows it.

## Changes from the Design System artifact (first publish, 2026-11-13)

`tokens.json` is byte-identical to the artifact (sha256 `da2cef49…946696`). `bundle.css` started from the artifact (sha256 `1f9e1fcf…2f4a`) with two changes, both taken from the chosen direction A ("Trace") in the directions prototype:

1. The dark multipliers of the light layer read theme variables (`--art-line-filter`, `--haze-mult`, `--sweep-strength`) instead of `[data-theme="dark"]` selectors, so they also apply when dark comes from `prefers-color-scheme` and no `data-theme` is set. The compiler emits those three variables per theme from the `opacity` notes (lines ×1.65, haze ×0.8, sweep at `sweep-dark`).
2. The three trails read their strengths `art-trail-1`/`-2`/`-3` (0.5, 0.38, 0.3) through `stroke-opacity`, as the light-and-motion rules state.

---

Four pages share this system: the profile hub (Eduardo Pin), agenfk-squad, AgentCenter and the AWS IaC Enterprise Library. They share one ground, one type pair, one set of components and one light layer. A visitor tells the pages apart by their project hue and their real mark. Build every page from the tokens below. Components read the alias `accent` and never name a hue directly.

## Voice

The pages say what the code does today, how it was measured, and what it does not do yet. Keep that register.

- **State limits next to claims.** For example: "Useful to try. Not ready to trust blindly." (AgentCenter), "Current work, with status and licensing stated plainly." (hub).
- **Use short declarative headlines, sentence case, ending with a full stop.** For example: "Small modules. Explicit interfaces. Reviewable foundations." (IaC), "Parallel Claude Code, with someone watching the blind spots." (agenfk-squad), "Know what every coding agent costs your machine." (AgentCenter). Never use Title Case For Headings.
- **Name the source of every picture and number.** For example: "Example output from the hook over a synthetic transcript with an artificial 550k context value, generated in a throwaway home." Only print a number that a file or a command in the repository can reproduce (58 Terraform modules, twelve role-limited agents). Never invent a star count, user count or testimonial.
- **Speak to the reader as "you".** Use "I" or "we" rarely, and never as "our community". For example: "The first machine is documented. The next data point could be yours."
- **Write status and licence the way the repository's LICENSE and README write them:** "Free software (AGPL-3.0), see LICENSE. Built for Linux. Pre-alpha." The hub card repeats the repository's licence word for word, or says that none is claimed.
- **Spell product names the way the repository does.** In the header and cards, use the repository's own spelling: `agenfk-squad`, `AgentCenter`, `AWS IaC Library`. In prose, use the full name: AgenFK Squad, AWS IaC Enterprise Library.
- **Never use emoji, exclamation marks, "blazing", "seamless" or "powerful".** Use `↗` only after a link that leaves the site.
- **Keep each page in its current language.** All four are English today.

## Colour

- **Grounds.** Use `ground` for the page background. Use `surface` for cards and the stuck header. Use `sunk` for inset panels: the hero trace panel, StatBadge and the CrossLinks strip. Use `terminal` for code and command panels; it stays dark in both themes on purpose.
- **Text.** Use `ink` for headings and body text on `ground`, `surface` and `sunk` (13.9:1 or better in both themes). Use `ink-muted` for ledes, captions and metadata on the same three grounds (6.2:1 or better). On `terminal`, write only in `term-ink`, `term-muted` and `term-prompt`.
- **Project hues.** Each page owns one hue: hub `rust`, agenfk-squad `green`, AgentCenter `amber`, IaC `violet`. Re-point the three aliases once, on `:root` of the page:
  - hub: `accent` → `rust`, `accent-fill` → `rust`, `on-accent` → `on-rust`
  - agenfk-squad: `green` / `green` / `on-green`
  - AgentCenter: `accent` → `amber-text`, `accent-fill` → `amber`, `on-accent` → `on-amber`. Never set small text in `amber` on light grounds.
  - IaC: `violet` / `violet` / `on-violet`
- **Hue roles.** Use `accent` for eyebrows, inline links (`link` is its alias) and the active anchor. Use `accent-fill` for the primary button and the hero trails. Put text on `accent-fill` only in `on-accent`. Every hue is a solid colour. Never use a hue in a gradient, and never set two project hues side by side, except in CrossLinks and the hub's trace panel, where each project appears in its own hue.
- **Star.** The star call-to-action is `star` with `on-star` on every page. It is the same neutral button everywhere, so a visitor learns it once. Never tint it with the page hue.
- **Lines.** Use `line` for hairlines that only separate. Use `line-strong` for every border that marks a control: ghost button, copy button, input (3:1 or better on all three grounds).
- **Signal.** Use `signal` only for the "pre-alpha" dot and word, and always next to the word. Never use colour alone to carry a meaning.
- **Hero light.** Use `art-haze-b` only for the second haze ellipse, and never as text.

## Type

- **Families.** Set everything in Archivo (`display`, `body`), plus Martian Mono (`mono`) for the instrument layer. Load both from Google Fonts with `display=swap`. Never substitute Inter, Roboto or a system stack as the identity face.
- **`display-xl` (88px, 0.94, 780).** Use it once per page, for an h1 that is a name (hub). It clamps to 48px at 400px.
- **`display-l` (56px, 1.0, 760).** Use it for an h1 that is a sentence (agenfk-squad, AgentCenter, IaC). It clamps down on phones, as `bundle.css` sets it. Keep a sentence h1 to three lines at 1280.
- **`heading` (32px).** Section h2, one per section. It clamps to 26px at 400px.
- **`title` (20px, 680).** h3 for ProjectCard and FeatureGrid cells.
- **`lede` (20px, 1.5).** The hero's one supporting line, in `ink-muted`, at most 54ch wide.
- **`body` (16px, 1.6).** Everything else.
- **`small` (14px).** Licence notes, figcaptions and the footer.
- **`label` (Martian Mono 12px, 500, +0.06em).** Uppercase is allowed only here: eyebrows, status words, card toplines and StatBadge words.
- **`code` (14px).** InstallSnippet, inline code and terminal blocks.
- **`readout` (24px, 600).** One measured number with tabular figures, only in StatBadge.
- **Headings.** Keep one h1 per page and never skip a level.

## Spacing and layout

- **Grid.** The base unit is 4px. Use `space-1`…`space-9` only, and never a free value in between. The one exception is the button's 18px side padding.
- **Page shell.** Width is `min(1180px, 100%)`. The side gutter is `space-4` (16px) below 720px and `space-6` (32px) from 720px, always as `max(gutter, env(safe-area-inset-*))`. Allow no horizontal scroll from 320px up.
- **Rhythm.** Pad sections by `space-9` on desktop and `space-8` on phone. Leave `space-6` from a heading to its content, and `space-7` between the hero copy and its actions.
- **Hero.** At 720px and up, use two columns: the copy is left-aligned on the left, the trace panel or the product picture on the right. Below 720px, use one column, with the actions full width.
- **Alignment.** Never centre a whole page. Centre only a button's label.
- **Cards and grids.** Card padding is `space-5` on desktop and `space-4` on phone. Join FeatureGrid cells by 1px of `line`, with no gaps and no numbering. Use `auto-fit` columns of at least 240px (features) and 220px (cross-links).
- **Touch targets.** Make every target 44px tall or more. The copy button is 36×72px inside a 44px bar.

## Borders, radii and shadows

- **Borders, not shadows.** Use `shadow-panel` only on `terminal` and InstallSnippet frames. Nothing else casts a shadow.
- **Radii.** Use `radius-sm` (6px) on buttons, inputs, the copy button and StatBadge, and `radius-md` (10px) on ProjectCard, FeatureGrid and the InstallSnippet frame. Use `radius-0` on the trace panel, section rules and terminal panels. Use `radius-pill` only on the status dot: there are no pill buttons.

## States and focus

- **Focus.** Use `outline: 3px solid` `focus` with a 3px offset on every focusable element. That is 3:1 or better on `ground`, `surface`, `sunk` and `terminal` in both themes. Where an outline cannot follow the shape, use `focus-ring`. Never remove focus without replacing it.
- **Hover.** The border turns `ink`. On the star button, the border turns `accent-fill`.
- **Press.** Scale to 0.97 over `dur-press`.
- **Disabled.** Set `aria-disabled="true"` and 0.55 opacity, keep the label, and add no motion.
- **Copy button.** It reads "Copy". On success it reads "Copied" in `term-prompt` for 1.8s, with only a colour change over `dur-ui`. On failure it reads "Select text" and selects the command. A polite live region announces "Command copied." or "Copy unavailable; command selected."
- **Skip link.** "Skip to content" is the first focusable element on every page.

## Light and motion

Light and motion live in the Hero and the star button. Nothing else moves.

- **Haze.** Two radial ellipses: `accent-fill` at the top right and `art-haze-b` at the bottom left, each at `art-haze` alpha (0.11–0.16). They drift by 1–2% over `dur-haze` with `ease-ambient`, alternating. In dark, multiply the haze by 0.8. On phones, multiply the whole layer by 0.78.
- **Traces.** Three paths cross the hero behind the copy. Each is drawn as a 30-unit band at `art-band` and a 1-unit line whose gradient peaks at `art-line`. In dark, the lines brighten (×1.65), because the haze dims.
- **Trails.** Three short dashes of `accent-fill` travel the traces, using `ease-constant` with `dur-trail-1` (delay 0), `dur-trail-2` (−8s) and `dur-trail-3` (−17s), at strengths `art-trail-1`/`-2`/`-3`. Never synchronise them.
- **Veil.** A `ground` wash at 98% behind the copy keeps every hero text pair at its stated contrast while the light moves.
- **Star sweep.** A 72px band of `on-star` at 34% passes behind the label once every `dur-sweep`, with `ease-constant`, from −400px to 400px. Most of that travel falls outside the button, which gives the pause. In dark, the band runs at `sweep-dark`.
- **UI timing.** Keep UI motion under 300ms: `dur-press` 120ms, `dur-ui` 180ms. Use `ease-out` for anything entering or leaving, and `ease-move` for something crossing the screen. Never use ease-in.
- **Reduced motion.** Under `prefers-reduced-motion: reduce`, stop every loop, hide the trails and the sweep, keep the haze still at its resting position, and turn off transitions and the press scale.
- **Complete at rest.** The page is complete at rest: nothing starts at opacity 0 or off-screen and waits for script. Never add a scroll-triggered reveal.

## Iconography and marks

- **Marks.** Each page's mark is its own `favicon.svg`, used unchanged: the hub's EP monogram, the squad's watcher ring, AgentCenter's site icon, IaC's hexagon graph. Show it at 28px in SiteHeader and CrossLinks with `alt=""`, because the name sits beside it. Never draw a new logo or redraw a mark. The squad's text mark `A/` is retired in favour of its ring.
- **Social images.** Each page has one 1200×630 PNG (`og.png`), with its mark, its h1 and its hue on `ground`.
- **Icons.** Use only two inline SVG glyphs: the GitHub mark (fill `currentColor`) and the outlined star (1.6 stroke, `currentColor`), at 18px inside buttons, with `aria-hidden="true"`. There is no icon library, there are no emoji, and there are no decorative icons beside headings.
- **Product pictures.** These are real captures only: the app screenshots, the CLI output and the watcher output. Give each one alt text that says what it shows, and a caption that says how it was made. Diagrams are SVG, drawn in the page's tokens.

## Components

| Component | Use it for |
|---|---|
| SiteHeader | Mark, name, up to four anchors that exist on the page, and the GitHub link. |
| Hero | The h1, one lede, the actions (star, primary, ghost) and the light layer. |
| Button | `primary` (one per view, `accent-fill`), `ghost` (`line-strong` border), `star` (`star`, with the live count when available). |
| ProjectCard | The hub's card for one project: mark, name, status, one sentence, licence, star and source. |
| InstallSnippet | The one-line install, exactly as the README gives it, with a copy button. |
| FeatureGrid | Three to six things the code does today, joined by hairlines. |
| StatBadge | A status word, or one measured number with its unit. |
| CrossLinks | The other three pages, in the order hub, agenfk-squad, AgentCenter, AWS IaC Library, right before the footer. |
| SiteFooter | Licence and status in one sentence, then three to five links. |
