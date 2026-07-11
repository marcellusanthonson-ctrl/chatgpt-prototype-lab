# Waypoint — Project State

Project-ID: `waypoint`
Status: `REFERENCED_CONCEPT`
Last-Updated: `2026-07-11`

## Authority boundary

This file records product-strategy decisions for continuity inside the LAB
repository. It does not authorize product implementation, repository changes
outside `marcellusanthonson-ctrl/chatgpt-prototype-lab`, release, integration,
deployment, or code execution.

Structured source of truth for this project note:
`projects/waypoint/PROJECT_STATE.json`.

## Current thesis

Waypoint should be treated as a B2B-oriented operations platform for guides,
agencies, tourism operators and mixed travel groups, not as a motorcycle-first
consumer convoy app.

Positioning:

```text
Plan routes on web. Execute in mobile app. Monitor operations in real time.
```

## Product surfaces

### Web planner and live operations view

The web version is valuable because it provides screen space to organize routes,
checkpoints, notes, QR/link generation, agency workflow and active-trip
monitoring.

The web is not the primary trusted tracking surface for moving participants.

### Android-first field app

The mobile app is for guides, drivers, staff and tracked operational units. Any
unit expected to share reliable movement/location during a trip should use the
mobile app.

Android is the preferred MVP target for LATAM/Chile validation.

### Guest web link

Tourists or viewers can receive a web link or QR to see itinerary, meeting
points, external navigation links, manual check-in/help actions and guide contact
information. Tourists are not primary tracked units in the MVP.

## Decisions recorded

### WAYPOINT-D-001 — Native mobile app required for reliable tracked units

Any unit expected to share reliable movement/location during a trip should use
the mobile app. Browser/web users should be treated as viewers, planners, admins
or low-reliability participants, not as core tracked units.

### WAYPOINT-D-002 — Web is for planning and operations

The web version is for route planning, checkpoint organization, link/QR
generation, agency workflow and monitoring active groups from a larger screen.

### WAYPOINT-D-003 — Motorcycle-first positioning is deprioritized

Do not use motorcycle clubs as the primary beachhead until RISER/Cardo Ride,
REVER, Detecht and Convoy Tracker are tested in the field and clear gaps are
verified. Motos remain a secondary or benchmark segment.

### WAYPOINT-D-004 — Primary validation shifts to guides/agencies

Initial validation should focus on guides, small agencies, tourism adventure,
mixed vehicle groups and operators who currently depend on WhatsApp, radios and
manual protocols.

### WAYPOINT-D-005 — MVP scope becomes web planner/live view plus Android app

The MVP should be reduced to one minimal web surface with plan/live views, one
Android-first field app for guides/staff/tracked units, and a web guest link.

### WAYPOINT-D-006 — Safety automation remains out of commercial MVP

Manual help/report actions, last known location, stopped/no-signal states and
basic operational alerts may exist. Automatic accident detection, sensor fusion
and precise road-ice claims remain research or shadow-mode only.

## MVP definition

### Web MVP

- Create route or tour.
- Define origin, destination and checkpoints.
- Add notes per checkpoint.
- Generate QR/link.
- View one active trip live.
- Show guide, vehicle or staff location.
- Show passive state: active, stopped, late, no signal, arrived.
- Close trip.

### Android MVP

- Join assigned trip.
- Start/end tracking.
- Share location with low-power mode.
- View route/checkpoints.
- Report problem/manual help.
- Pause tracking.
- Queue state updates when connectivity degrades.

### Guest web MVP

- View itinerary and meeting point.
- Open navigation externally.
- Manual check-in or help action.
- Contact guide/operator.

## Explicitly out of MVP

- Motorcycle-first product.
- iOS MVP.
- Free-form chat.
- Push-to-talk/audio.
- Automatic crash detection.
- Road-ice precision claims.
- Advanced weather/traffic.
- Replay/history product.
- Full multi-agency dashboard.
- Tracking every tourist by default.

## Validation plan

Before implementation commitment:

1. Interview 3-5 guides or agencies with concrete pricing in hand.
2. Validate whether monitoring guides, vehicles or staff is enough without
   tracking every tourist.
3. Test willingness to pay around USD 29 per guide or USD 79 per small agency
   per month.
4. Document current WhatsApp/radio/manual failures with timestamps from real
   tours.
5. Benchmark RISER/Cardo Ride, REVER, Detecht and Convoy Tracker before
   re-opening motorcycle-first positioning.
6. Estimate map and location infrastructure cost per active tour.

Primary B2B validation metric:

```text
Guide or agency uses Waypoint-like workflow in three or more tours within
30 days and expresses willingness to pay.
```

## Open questions

- Will agencies accept tracking only guides/vehicles/staff instead of every
  tourist?
- Is one live trip view enough for the first paying pilot?
- What is the real willingness to pay for small agencies in LATAM?
- What map provider keeps cost per tour acceptable?
- Can low-power Android tracking stay reliable for 4-8 hour tours?
- Which legal disclaimer is required for manual help/SOS actions?
