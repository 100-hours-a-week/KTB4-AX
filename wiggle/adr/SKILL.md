---
name: adr
description: Guide students through technical choices using their project constraints and priorities, compare evidence, and record the agreed decision in an ADR.
disable-model-invocation: true
---

# ADR

Help the student make a technical choice grounded in their project and leave a credible rationale for their portfolio. The student supplies what matters to them; the agent develops the criteria, investigates alternatives, recommends, and writes. Reach the decision together before recording it.

Keep participation lightweight. Do not require the student to generate every option, perform the analysis, repeat explanations, or pass an understanding check. Explain unfamiliar concepts briefly when needed and adapt depth to their interest. Agreement with a clearly explained recommendation is a valid decision; silence is not.

Read [TEMPLATE.md](./TEMPLATE.md) when ready to draft; it owns the section structure and section-specific writing guidance.

## Reaching the decision

### 1. Start with the student's drivers

Ask first what matters in this choice: requirements, constraints, priorities, and any reasons they want to share. Accept everyday language rather than demanding finished Decision Drivers. If the conversation already contains this, reuse it rather than asking again.

For example: “이번 선택에서 중요하게 생각하는 게 뭐야? 일정, 비용, 성능, 팀의 익숙함, 새로운 기술 학습 같은 것 중 편하게 이야기해 줘. 반드시 지켜야 하는 조건도 알려 줘.”

If they are unsure, offer examples or a tentative framing based on the project. Do not invent their priorities or present your preferred technology as their starting point.

Read available project context: `CONTEXT.md` or `CONTEXT-MAP.md`, `docs/agents/domain.md`, relevant implementation/configuration, and existing ADRs. Missing documents do not block a decision before implementation. State the decision as one question with an explicit scope. Flag contradictions with existing decisions as potential supersedes.

Turn the student's input and verified project constraints into drivers. Distinguish mandatory requirements from preferences; clarify priority only where it affects the choice. Ask only consequential questions you cannot resolve from available evidence, usually one or two at a time. Drivers may evolve as facts emerge: make changes visible and compare against the final agreed set.

### 2. Develop realistic options

Use any candidates the student already mentioned, then supply realistic alternatives yourself. Include the conventional approach or keeping the current system when relevant. Do not require the student to list candidates or invent alternatives to fill a quota.

Describe how each option would actually work in this project: the request/data flow, component responsibilities, and extra infrastructure. Compare concrete designs, not just technology names. Briefly explain non-obvious exclusions so the student can bring them back.

### 3. Gather decisive evidence

Use project artifacts and current primary sources to verify claims that could change the choice, including API support, limits, versions, and pricing. Use available research tools or a suitable research skill; the workflow does not require Orca. If evidence cannot be obtained, state the gap and its effect on confidence instead of silently substituting model knowledge.

Where a measurement could change the recommendation, propose the smallest useful check. Perform feasible checks within the authorized environment; state a plan for checks that cannot yet run. Do not require a benchmark for every ADR or make the student conduct it personally.

Define what is measured, under which conditions, and what requirement it tests. Record actual execution, results, and limits. Keep requirements/targets, measured results, estimates, and unverified assumptions distinct. Do not manufacture numbers, arbitrary scores, or thresholds to make the ADR look rigorous. Structural criteria such as ownership and added components can be assessed directly without numerical scoring.

Missing measurements do not block writing: identify remaining uncertainty and follow-up verification. If it prevents a responsible final choice, recommend a provisional option or small experiment and leave the status Proposed until the student accepts a decision with its limits.

### 4. Compare and recommend

Check mandatory constraints first, then compare viable options using the agreed drivers and priorities. Use a compact comparison table when helpful, and explain the decisive trade-off in prose. General advantages matter only when relevant to this project.

Give your recommendation, why the strongest alternative loses under these conditions, the downsides being accepted, and what remains uncertain. Do not require the student to analyze the table before you help. Offer brief explanations where needed rather than quizzing them.

### 5. Settle the scoped decision

Let the student accept the recommendation, choose another option, or adjust the drivers. An informed preference different from yours is valid; flag factual mistakes and explain the trade-off without insisting on agreement.

Finish when the scope, main alternatives, decisive reasons, accepted downsides, and material uncertainty are clear and the student confirms the choice. Do not demand a restatement or explore every downstream design branch. Capture follow-up implementation decisions separately instead of expanding this ADR indefinitely.

## Recording it

Offer an ADR when a real project choice has alternatives and trade-offs worth recording. Hard-to-reverse decisions, surprising choices, and recurring debates are especially useful, but small reversible choices also qualify for student learning and portfolios. Typical subjects include architectural shape, integration patterns, technology selection, ownership/scope boundaries, and constraints or rejected alternatives that are not obvious from code.

Do not manufacture alternatives or achievements. If there is no meaningful choice, suggest a lighter project note; if the user wants an ADR, honestly explain why the choice was constrained. Do not add an eligibility approval gate.

Draft from the discussion and evidence using the template's sections. Write in the language of the discussion, using sentences that connect project conditions, evidence, and judgment. Preserve the section structure, adapt the candidate count to real options, and remove empty bullets and writing instructions. Mark unresolved content and needed follow-up explicitly. Link consequential claims to primary sources, relevant code, or experiment artifacts beside the claim.

For an unresolved draft use Proposed and describe the tentative choice explicitly; only mark Accepted after confirmation. For retrospective ADRs separate the reasons known at the original decision from analysis performed now. Never present agent analysis as work or experiments the student personally performed.

Show the complete draft for review. Save when the user requests saving or existing instructions already authorize it; do not ask for the same permission again. Apply project placement rules:

1. **Place it.** Use `docs/adr/` at the project root for system-wide decisions, or `src/<context>/docs/adr/` when `CONTEXT-MAP.md` assigns it to that context. Respect a supplied destination. Without a repository, use the intended project directory.
2. **Number it.** Create the directory only when saving its first ADR. Scan the target directory for the highest number and increment. Use `0001-slug.md` and `# ADR-0001: <제목>` consistently.
3. **Supersede.** Reference the previous ADR in the new Context. Update its Status to `Superseded by ADR-NNNN` only when the accepted replacement is saved, not while drafting a proposal.

Before delivery, check that reasons trace to the final drivers, evidence supports the claims, missing measurements remain visible, and accepted downsides and reconsideration conditions are explicit. Do not fill gaps with invented discussion or results.

## After

Mention follow-up implementation or verification that matters to the decision. If vocabulary changed, suggest updating the project's context document. Do not automatically start a teaching workspace or write unrelated notes.
