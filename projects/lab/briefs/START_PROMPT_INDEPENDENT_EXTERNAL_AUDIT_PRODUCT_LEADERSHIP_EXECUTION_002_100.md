Perform an independent external read-only audit of PRODUCT-LEADERSHIP-CLEAN-REPRODUCTION-EXECUTION-002 in marcellusanthonson-ctrl/chatgpt-prototype-lab, branch main.

Canonical authorization:
projects/lab/authorizations/AUTHORIZATION_LAB_INDEPENDENT_EXTERNAL_AUDIT_PRODUCT_LEADERSHIP_EXECUTION_002_100.json

Canonical brief:
projects/lab/briefs/BRIEF_INDEPENDENT_EXTERNAL_AUDIT_PRODUCT_LEADERSHIP_EXECUTION_002_099.json

Audit mode:
INDEPENDENT_EXTERNAL_READ_ONLY

Required inputs:
- projects/lab/test-executions/PRODUCT-LEADERSHIP-CLEAN-REPRODUCTION-EXECUTION-002/
- projects/lab/test-designs/PRODUCT-LEADERSHIP-ACTIVATION-AND-VALUE-DISCRIMINATION-TEST-001/
- foundation-library/product-leadership/PRODUCT-LEADERSHIP-CANDIDATE-PACKAGE-001/
- projects/lab/reconciliations/REC-LAB-PRODUCT-LEADERSHIP-EXECUTION-002-001.json

Audit objectives:
1. Verify role isolation and the blinding chain.
2. Verify exactly 88 outputs, hash coverage and artifact completeness.
3. Verify scores, rationales and mappings were frozen before oracle unblinding.
4. Independently recalculate all declared metrics and gates.
5. Assess divergences PL-CLEAN-028, PL-CLEAN-033 and PL-CLEAN-035.
6. Assess the validity and reproducibility of the closed-scope denominator.
7. Assess the effect of missing optional input paths.
8. Determine whether PL-GATE-VALUE must remain INCONCLUSIVE under the rules declared before execution.
9. Propose a prospective, non-post-hoc value test design without reclassifying this execution.

For every material claim return one of:
CONFIRMED, MODIFIED, REVERSED, INSUFFICIENT_EVIDENCE.

Required outputs outside the repository:
- AUDIT_REPORT.md
- AUDIT_FINDINGS.json

Do not modify the repository. Do not add a post-hoc value threshold. Do not promote, reject, activate or integrate Product Leadership. Do not use real product data, modify Symphonie or products, create runtime/RAG/embeddings/vector storage, or make the final human decision.

Return the audited repository HEAD, methodology, recalculated metrics, per-gate findings, divergence analysis, limitations, prospective test recommendation and SHA-256 hashes of both audit outputs. A separate explicit reconciliation authorization is required before any audit output may be committed to the LAB.