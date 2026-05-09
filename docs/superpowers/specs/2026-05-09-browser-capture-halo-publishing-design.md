# Browser Capture and Halo Publishing Design

## Purpose

SOP Generator should become an agent-powered Problem Steps Recorder for modern MSP workflows. The first useful shape is human-led browser capture: a technician explicitly starts recording, performs the real workflow in their normal compliant browser profile, and the tool quietly captures enough context to draft a usable SOP with screenshots.

The goal is to reduce documentation effort without moving sensitive raw capture into cloud storage. Raw sessions stay machine-local. Only reviewed SOP payloads are published through Bifrost into Halo KB.

## V1 Scope

V1 focuses on browser workflows only. The browser extension records meaningful browser activity while a session is explicitly running:

- meaningful clicks
- navigation and title changes
- form submissions and page transitions
- screenshots
- optional user notes
- pause, resume, and stop markers

The extension is ambient but visible. It should fade into the background during work, but the recording state must always be explicit.

Out of scope for V1:

- autonomous clicking or agent-driven browser control
- whole-desktop capture
- remote access tool capture
- direct IT Glue, Hudu, or Autotask publishing
- Markdown wiki export as a primary path
- learning from approved SOP examples
- multi-author review or formal approval workflows

## Future Scope

The architecture should leave room for additional capture sources:

- remote-window capture for named tools such as Ninja Remote, ScreenConnect, or Quick Assist
- Playwright capture for disposable or reproducible workflows
- whole-desktop capture only if privacy and redaction controls are mature enough

These future sources should feed the same local session, drafting, review, and publishing pipeline.

## Architecture

### Browser Extension

The extension is a thin capture client that runs in the user's normal browser profile. This preserves the real operating environment: organization browser policy, credential manager access, conditional access state, Dark Reader, bookmarks, and other daily-driver browser context.

Responsibilities:

- start, pause, resume, stop, and add-note controls
- visible recording state
- capture browser events from approved tabs
- capture screenshots
- send events to the local companion service over localhost

The extension should not perform heavy drafting, persistence, Bifrost calls, or vendor API work.

### Local Companion Service

The local companion is the main SOP Generator application.

Responsibilities:

- localhost API for extension events
- machine-local session storage under `%LOCALAPPDATA%\MTG\SOPGenerator`
- screenshot storage
- event normalization
- meaningful step detection and deduplication
- draft SOP generation
- MTG house-style application
- local review web UI
- Halo-ready rendering
- explicit publish request to Bifrost

Default storage layout:

```text
%LOCALAPPDATA%\MTG\SOPGenerator\
  sessions\
    2026-05-09_1430_example-workflow\
      raw\
      screenshots\
      events.jsonl
      browser-context.jsonl
      notes.md
      draft.md
      review.json
      export.html
  style\
    house-style.md
  exports\
```

Raw session folders are sensitive and local-only. The tool should not place raw captures in Documents, OneDrive, repo folders, or cloud-synced paths by default.

### Bifrost Publisher

Bifrost owns external publishing and vendor auth.

Responsibilities:

- accept reviewed SOP payloads only
- publish to Halo KB
- upload or attach images
- map customer, category, and KB metadata where available
- return publish status and Halo article URL
- centralize platform credentials and API-specific behavior

SOP Generator should not grow Halo, IT Glue, Hudu, or Autotask auth logic directly.

## Review Experience

The review UI should be mostly automatic. After recording stops, the companion drafts a complete SOP and opens the assembled article first, not the raw event timeline.

Default workflow:

```text
Stop recording
-> draft appears
-> skim and edit title, intro, steps, warnings
-> choose Halo KB target
-> publish
```

Raw events remain available behind an evidence or timeline view for debugging, redaction, or correction.

V1 review actions:

- edit title and summary
- edit step text
- delete noisy steps
- merge adjacent steps
- mark a step as a warning or note
- add a missing manual step
- replace or select the screenshot for a step
- publish to Halo KB

## House Style

V1 uses a local style file only:

```text
%LOCALAPPDATA%\MTG\SOPGenerator\style\house-style.md
```

The drafting pass may use:

- captured browser events
- screenshots and visual/OCR summaries
- user notes
- `house-style.md`
- a built-in SOP structure template

It should not claim to learn from approved examples until there is a useful local corpus of approved SOPs.

The style file should define:

- audience: MTG technicians and internal support operators
- voice: direct, procedural, concise
- step format
- warning and note conventions
- how to refer to credentials and customer-specific values
- what should not appear in final docs
- Halo KB formatting conventions

## Data Model

### CaptureSession

- `id`
- `title`
- `started_at`
- `stopped_at`
- `source`: initially `browser-extension`
- `status`: `recording`, `paused`, `drafting`, `reviewed`, `published`
- `sensitivity`: `raw-local-only`

### CaptureEvent

- `timestamp`
- `url`
- `title`
- `event_type`: `click`, `navigation`, `form_change`, `submit`, `note`, `screenshot`, `pause`, `resume`
- `screenshot_id`
- `context`: page text, element labels, or other safe structured browser context when available
- `note`: optional user note

### DraftSop

- `title`
- `audience`
- `summary`
- `prerequisites`
- `steps`
- `warnings`
- `screenshots`
- `publish_target`

## Privacy And Export Boundary

V1 uses full-fidelity local capture because MSP workflows often require credential forms and secure configuration screens. Partial capture would create incomplete documentation.

Safety comes from boundaries rather than automatic raw redaction:

- raw capture stays machine-local
- raw folders are clearly marked sensitive
- publishing requires explicit review and approval
- only reviewed SOP payloads are sent to Bifrost
- user can pause recording for content that should not even exist locally
- user can delete or replace screenshots before publishing

The final SOP may generalize secrets and customer-specific values while raw evidence remains available locally for drafting accuracy.

## Halo Publishing

Halo KB is the first direct publishing target.

The local companion renders a reviewed SOP into Halo-ready HTML and sends the payload to Bifrost. Bifrost handles Halo details such as article creation or update, image upload, category/customer mapping, retries, and returned article URL.

If Bifrost is unavailable, the tool may still produce local `export.html` and image assets, but direct publishing is unavailable until Bifrost recovers.

## Failure Modes

The tool should fail safely:

- extension disconnect: preserve the session and mark a timeline gap
- drafting failure: keep raw capture and allow retry
- screenshot failure: keep event context and mark missing evidence
- Bifrost unavailable: keep reviewed SOP local and allow publish retry
- Halo publishing failure: surface the exact Bifrost/Halo error and keep the reviewed artifact unchanged
- user deletes a screenshot: remove it from the final payload and retain a local audit marker

## Testing Strategy

- Unit tests for event normalization, step grouping, and renderer output
- Local integration tests with fake browser events and fake screenshots
- Review model tests for delete, merge, note, warning, and screenshot replacement actions
- Bifrost contract tests using a mocked Halo publisher payload
- Manual acceptance workflow: record a browser process, generate a draft, edit one step, publish to a Halo test category, and verify the returned article link

## Implementation Slices

1. Repo modernization and local companion skeleton
2. Local session storage and data model
3. Browser extension minimal capture client
4. Event ingestion and screenshot persistence
5. Draft generation using `house-style.md`
6. Review UI
7. Halo HTML renderer
8. Bifrost publish contract and mocked publisher
9. Halo KB publishing through Bifrost
10. MSI/WinGet packaging once the app has a useful operator entry point
