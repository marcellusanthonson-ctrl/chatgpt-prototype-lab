# Evidence — Phase 4 Accessibility Normative and Assistive Technology Research

- Evidence ID: `EVD-LAB-DK-003`
- Authorization: `AUTHORIZATION_LAB_PHASE_4_ACCESSIBILITY_RESEARCH_044`
- Research date: 2026-07-20
- Status: `DOCUMENTED_AND_VALIDATED_NOT_INTEGRATED`
- Runtime effect: `NONE`
- Symphonie structure effect: `NONE`
- Product conformance effect: `NONE`

## 1. Research question

What normative accessibility requirements, official implementation guidance, component patterns and assistive-technology testing disciplines should strengthen the LAB design-knowledge package without overstating conformance or modifying Symphonie?

## 2. Primary findings

### 2.1 WCAG 2.2 is the normative web-content baseline

WCAG 2.2 is a W3C Recommendation. Its success criteria are testable, technology-independent statements. WCAG 2.2 extends WCAG 2.1 and W3C advises using the current version when developing or updating accessibility policy. It covers a broad range of disability needs but explicitly does not address every user need.

Governed consequence:

- normative requirements must point to WCAG 2.2 itself;
- conformance levels and requirements must not be reconstructed from blogs or summaries;
- claims must state scope and level;
- accessibility must not be reduced to a checklist that guarantees absence of barriers.

### 2.2 Supporting W3C documents have different authority

The following distinctions are mandatory:

- WCAG 2.2: normative W3C Recommendation;
- WAI-ARIA 1.2: normative W3C Recommendation for accessibility semantics;
- Understanding WCAG: informative explanation, examples, sufficient and advisory techniques, and failures;
- ARIA APG: informative patterns and examples, explicitly not a normative standard and not a UI design system;
- ACT Rules: informative rules that improve testing transparency but are not required for conformance;
- WCAG-EM 1.0: supporting Working Group Note for structured evaluation, not an additional WCAG requirement;
- WCAG-EM 2.0: draft during this research and therefore not final authority.

Failure to preserve these classes creates false requirements and false assurance.

### 2.3 ARIA provides semantics, not complete accessibility

WAI-ARIA can expose roles, states and properties to assistive technologies, especially for dynamic interfaces. It does not automatically provide keyboard support, usable interaction, focus management or correct behavior. APG states that authors of custom components must implement the required keyboard behavior.

Governed consequence:

- prefer native HTML when it supplies appropriate semantics and behavior;
- custom widgets require a complete behavioral contract;
- role, name, state and value must match visible behavior and update dynamically;
- ARIA must not be used to disguise inaccessible interaction architecture.

### 2.4 Automated tools cannot determine accessibility alone

W3C evaluation guidance states that no tool alone can determine whether a site meets accessibility standards; knowledgeable human evaluation is required. ACT supports automated, semi-automated and manual rules, but ACT coverage is partial and informative.

Governed consequence:

- automated findings are one evidence layer;
- a zero-error scan does not establish WCAG conformance;
- every report must state manual, semi-automated and untested coverage;
- tool output must be reproducible and linked to the evaluated build.

### 2.5 Conformance evaluation and disabled-user evaluation answer different questions

WCAG-EM structures conformance evaluation through scope definition, exploration, representative sampling, evaluation and reporting. W3C separately recommends involving disabled users to discover real-world barriers and evaluate solutions. User evaluation does not prove conformance; conformance does not prove a frictionless or complete experience.

Governed consequence:

- reports must separate standards findings from usability findings;
- representative disabled-user involvement should be planned for material workflows;
- a single successful session must not be generalized to all users or technologies.

### 2.6 Accessibility must cover diverse functional needs

W3C human-context guidance covers auditory, cognitive, physical, speech and visual disabilities, including combinations, age-related changes, temporary impairments, health conditions and situational limitations. The examples are not exhaustive.

Governed consequence:

- testing cannot be limited to screen readers;
- keyboard, magnification, zoom, text resizing, reflow, alternative pointer input, captions, cognitive load, errors, timing and motion are part of the baseline;
- medical labels should not replace functional-needs analysis.

## 3. Minimum test architecture

The governed testing architecture contains five layers:

1. structural and static automation;
2. manual evaluation without assistive technology;
3. accessibility-tree and platform inspection;
4. assistive-technology task testing;
5. evaluation with disabled users.

Every assistive-technology result must record:

- product build or commit;
- operating system and version;
- browser and version;
- assistive technology and version;
- relevant settings and input mode;
- viewport, zoom and language;
- task, preconditions and expected result;
- observed result, status and evidence;
- applicable WCAG or pattern reference;
- limitations and known support differences.

The full protocol is `ASSISTIVE_TECHNOLOGY_TEST_PROTOCOL.json`.

## 4. Priority interaction families

The minimum families for future product validation are:

- orientation, language, headings, landmarks and reading order;
- keyboard operation, focus visibility, focus order and focus recovery;
- accessible name, role, state and value;
- forms, instructions, autocomplete purpose and error recovery;
- status messages, notifications and asynchronous changes;
- text resize, zoom, reflow, text spacing and magnification;
- target size, pointer cancellation, drag alternatives and touch;
- captions, audio alternatives, flashing and reduced motion;
- authentication, timing and high-impact submission recovery.

## 5. False or unsupported claims

The evidence does not support the following claims:

- `An automated scanner can certify WCAG conformance.`
- `A page with no scanner errors is accessible.`
- `ARIA automatically makes a custom component accessible.`
- `Following APG is itself a normative WCAG requirement.`
- `Passing WCAG AA proves that no user will encounter barriers.`
- `One screen-reader and browser combination proves universal support.`
- `Testing only with a screen reader is sufficient assistive-technology testing.`
- `One disabled participant can validate conformance.`
- `All cognitive accessibility guidance is normative WCAG.`
- `WCAG 2.2 addresses every need of every disabled user.`

## 6. Principles derived

Ten principles were documented as `DKP-019` through `DKP-028`:

- normative and informative guidance must be separated;
- automation cannot establish accessibility alone;
- native semantics before ARIA;
- keyboard access is a behavioral contract;
- accessible name, role, state and value must match behavior;
- reflow, zoom and text resizing are layout requirements;
- pointer interaction requires non-drag and target alternatives;
- errors require identification, guidance and recovery;
- assistive-technology testing requires a recorded environment;
- conformance and usability are complementary, not equivalent.

These principles are documented and validated as knowledge artifacts only. They are not integrated into Symphonie or product gates.

## 7. Gap result

`GAP-DK-001 — ACCESSIBILITY` moves from `PARTIALLY_COVERED` to `FOUNDATIONAL_COVERAGE_DOCUMENTED_NOT_OPERATIONALLY_VALIDATED`.

Covered:

- WCAG 2.2 normative baseline;
- official informative interpretation boundary;
- WAI-ARIA and APG component-pattern boundary;
- evaluation methodology;
- automated, manual and assistive-technology testing layers;
- broader functional-needs framing;
- disabled-user evaluation boundary.

Remaining:

- execute the protocol against representative products;
- establish supported browser and assistive-technology matrices by product;
- validate native mobile and desktop application accessibility separately;
- define procurement and third-party component evidence requirements;
- add localization and bidirectional accessibility testing;
- add sector-specific evidence for high-stakes products;
- determine how and whether these principles enter Symphonie gates under a future authorization.

## 8. Validation and authority boundaries

Validation performed:

- official-source classification;
- normative versus informative separation;
- principle identifier uniqueness;
- source-reference closure within Phase 4 files;
- false-claim inventory;
- protocol completeness review;
- authorization-scope review;
- runtime, RAG, Symphonie and product boundaries.

Not performed:

- browser execution;
- assistive-technology execution;
- product audit;
- user research;
- legal conformance determination;
- Symphonie integration.

No product or interface may claim WCAG conformance based on this research package alone.
