# Arcade Hub trackpad scrolling does not work on macOS

## Status

Open. The previous scrolling fix was not confirmed by the user; do not close
this ticket based only on synthetic Tk events.

## Problem

On the user's Mac, the arcade hub game list cannot be scrolled with the
trackpad. The same project can be used on another device where scrolling works.
The visible list is longer than the window, and the vertical scrollbar is
present, but trackpad scrolling does not move the list.

## Reproduction

1. Use macOS with the repository's launcher:

   ```bash
   ./arcade_hub.command
   ```

2. Move the pointer over the game list, a game card, or a button.
3. Use a two-finger trackpad scroll gesture.
4. Observe that the list does not scroll.

The issue must be tested with actual trackpad input. Synthetic
`event_generate("<MouseWheel>")` tests are not sufficient because they pass
even though the user's physical gesture remains broken.

## Environment

- macOS on a MacBook Air
- macOS appearance was Dark during investigation
- Xcode Python: 3.9.6 with Tk 8.5.9
- Current launcher environment: Homebrew Python 3.14.10 in `.venv`
- Current Tk in `.venv`: 9.1
- Current Pygame package: `pygame-ce` 2.5.8
- Entry point: `arcade_hub.py`

## Verified facts

- The canvas is larger than its viewport. In the investigated run:
  - viewport: `929 x 483`
  - scroll region: `0 0 929 4296`
- Calling `Canvas.yview_scroll()` directly moves the list.
- Synthetic positive and negative `<MouseWheel>` events generated on a child
  widget move the canvas in both directions.
- Therefore, the remaining failure is specifically the path from the physical
  macOS trackpad gesture to Tk's event system, or a platform-specific Tk event
  sequence not covered by the current bindings.

## Current implementation

Relevant code is in [`arcade_hub.py`](../arcade_hub.py):

- The canvas and scrollbar are created around lines 147-157.
- `_on_mousewheel` handles `<MouseWheel>`, `<Button-4>`, and `<Button-5>` around
  lines 165-175.
- `_bind_scroll_events` recursively binds those sequences to widgets around
  lines 177-181.
- `refresh_games()` reapplies bindings after creating cards around lines
  187-230.

The current handler treats any positive `event.delta` as one upward unit and
any negative delta as one downward unit. It ignores events whose delta is zero
or absent.

## Changes already attempted

1. Changed `int(-event.delta / 40)` to sign-based scrolling so small macOS
   deltas would not round to zero.
2. Replaced `bind_all()` with recursive bindings on the root and its child
   widgets so events over cards and buttons should reach the handler.
3. Confirmed both changes with synthetic events, but the user reports that the
   real trackpad remains unusable.

Do not repeat these changes without first observing the actual event sequence.

## Investigation guidance

Instrument a temporary diagnostic build or use Tk event inspection to record,
while performing a real two-finger gesture:

- whether `<MouseWheel>`, `<Button-4>`, `<Button-5>`, or another event is
  generated;
- the event's `type`, `num`, `delta`, `state`, `widget`, and `x/y` values;
- whether the callback runs when the pointer is over the canvas, a `Frame`,
  `Label`, or `Button`;
- whether the scrollbar thumb moves when the callback is invoked from the
  observed physical event.

Also compare behavior when the pointer is directly over the scrollbar. Avoid
swallowing events needed by buttons or introducing a global binding that
affects unrelated applications.

Potential platform-specific causes to evaluate, rather than assume:

- Tk 8.5 versus Tk 9.1 event behavior on macOS;
- Tk/Aqua not exposing trackpad gestures as `<MouseWheel>`;
- event bindings being replaced or stopped by native Tk buttons;
- macOS accessibility/input settings;
- a need for a platform-specific gesture binding or a different UI toolkit.

## Acceptance criteria

- A real two-finger trackpad gesture scrolls the game list up and down.
- Scrolling works when the pointer is over the canvas, game cards, labels, and
  buttons.
- Mouse-wheel scrolling still works where supported.
- The vertical scrollbar continues to scroll and reflect the canvas position.
- Button clicks, game launching, README opening, and keyboard interaction are
  unchanged.
- The fix is verified on the user's Mac with the same launcher, not only with
  synthetic events.
