# Spec: Scroll the Arcade Hub game list with a Mac trackpad

## Problem Statement

On the affected MacBook Air, a two-finger trackpad gesture does not move the Arcade Hub game list. The list is taller than the window and the vertical scrollbar works, but the user cannot scroll naturally while pointing at the list, a game card, or its controls. The same project scrolls on another device. Previous changes to wheel-delta handling and widget bindings passed synthetic event checks without fixing the physical gesture.

## Solution

The user can launch the Arcade Hub on the affected Mac and scroll the game list up and down with a two-finger trackpad gesture wherever the pointer rests within the list. The scrollbar and supported mouse wheels continue to work, and game controls remain usable. The implementation is chosen only after observing the actual event path from the user's gesture to the list.

## User Stories

1. As a Mac trackpad user, I want to scroll down the game list with two fingers, so that I can reach games below the window.
2. As a Mac trackpad user, I want to scroll up the game list with two fingers, so that I can return to earlier games.
3. As a Mac trackpad user, I want scrolling to work over empty list space, so that I do not have to aim at a particular control.
4. As a Mac trackpad user, I want scrolling to work over a game card, so that I can browse while reading game details.
5. As a Mac trackpad user, I want scrolling to work over a game title, so that text does not interrupt browsing.
6. As a Mac trackpad user, I want scrolling to work over a game description, so that text does not interrupt browsing.
7. As a Mac trackpad user, I want scrolling to work over Play and Read Me buttons, so that I can browse without moving the pointer away from controls.
8. As a user, I want the scrollbar thumb to track the visible portion of the list, so that I can see my position.
9. As a user, I want to drag or click the vertical scrollbar, so that I can navigate without a trackpad gesture.
10. As a mouse user, I want a supported wheel to keep scrolling the list, so that the Mac fix does not regress other input devices.
11. As a user, I want Play and Read Me clicks to keep working, so that scrolling support does not interfere with actions.
12. As a user, I want keyboard interaction to keep working, so that the hub remains usable through its existing controls.
13. As a user, I want scrolling to work after refreshing the game list, so that newly created cards respond to the same gesture.
14. As a maintainer, I want a reproducible record of the physical gesture's event path, so that the fix targets the observed failure.
15. As a maintainer, I want the fix verified through the normal Mac launcher, so that a synthetic wheel event cannot be mistaken for user-visible success.

## Implementation Decisions

- Observe a real two-finger gesture on the affected Mac before choosing a Tk event binding, event translation, or alternate input mechanism. Capture event type, button number, delta, modifier state, target widget, pointer coordinates, and whether the list position changes.
- Compare gestures over the canvas, a card, text, buttons, and the scrollbar. Record whether an event is absent, intercepted, or handled without moving the canvas.
- Keep the existing canvas and scrollbar as the game list's scroll surface. Change the hub's input handling only as far as the observed behavior requires.
- Preserve click, launch, README, and keyboard behavior. Avoid application-wide bindings that affect unrelated windows.
- Reapply any required input handling when the game list is refreshed.
- Treat the installed Tk version and macOS input behavior as diagnostic facts to verify, not as an assumed root cause.

## Testing Decisions

- The primary acceptance seam is the running Arcade Hub opened through its normal launcher on the affected Mac. A real two-finger gesture must visibly move the list in both directions over the canvas, cards, text, and buttons.
- At the same seam, check that the scrollbar moves with the list and still navigates it, and that Play, Read Me, and keyboard actions still respond.
- Check scrolling again after Refresh Games and check a supported mouse wheel where available.
- Automated event tests may protect a discovered input translation, but generated Tk events alone do not prove physical trackpad support. Prefer tests of visible list position and control behavior over assertions about internal binding calls.
- The repository has interaction and rules tests for another game, but no existing Arcade Hub GUI test seam. Add a focused automated check only if the chosen fix creates a meaningful repeatable seam; keep physical Mac verification mandatory.

## Out of Scope

- Redesigning the game list or replacing its toolkit without evidence that the existing toolkit cannot receive the gesture.
- Changing game discovery or launch behavior beyond preventing a scrolling regression.
- General changes to macOS accessibility or system input settings.
- Declaring the issue fixed from synthetic events alone.

## Further Notes

- The ticket remains open until the user confirms the real gesture works on the affected Mac.
- Automated coverage now verifies that wheel events from another window do not
  move the list and that refreshed game controls still scroll it. These checks
  do not establish physical trackpad support.
- Physical event-path observation over the canvas, cards, labels, and buttons,
  followed by verification through `arcade_hub.command`, is still required.
  Record the runtime and Tk version used; do not treat synthetic events as a
  substitute.
- Prior investigation measured a 929 × 483 viewport and a 929 × 4296 scroll region. Direct canvas scrolling worked, as did synthetic positive and negative wheel events on child widgets.
- The investigated environments included Xcode Python 3.9.6 with Tk 8.5.9 and a project environment using Python 3.14.10 with Tk 9.1. The launcher selects an available runtime, so record the runtime used for the final physical check.
- The earlier sign-based delta change and recursive widget bindings are already present. Repeat them only if physical-event evidence shows they need adjustment.
