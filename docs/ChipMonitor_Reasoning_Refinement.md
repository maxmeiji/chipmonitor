# ChipMonitor reasoning refinement

## Local first

The dashboard uses React + TypeScript (Vinext), not Streamlit. Keep the existing graph interface. Start it with `npm run dev` inside `outputs/chipmonitor-site`; the current preview uses http://localhost:5173. Review locally before further publication.

## C1–C7 are hypotheses

Use the seven beliefs as optional reasoning patterns and candidate-retrieval aids. They are not an exhaustive taxonomy or mandatory conclusions. A story can support several mechanisms, contradict a belief, or introduce an entirely new mechanism.

Keyword matches do not establish model openness, an economic actor, a hardware supplier, or causality. The prototype still uses rule-based routing and scenario templates; it does not yet independently interpret every post.

## Source-led analysis contract

1. Read the summary and every returned tweet, including quoted text. Preserve exact words, author, URL, date and role.
2. Identify the exact model/version, provider, seller, service and price unit. Distinguish downloadable weights and license terms from paid hosted access.
3. Separate reported events, the author's explanations, forecasts and our inferences. Tweets can contribute valuable viewpoints without being verified facts. Reposts and multiple posts by one author are not independent corroboration.
4. Generate mechanisms from the evidence first; consult C1–C7 afterward. Add mechanisms beyond the seven when the sources justify them.
5. Branch when interpretations differ. Each branch needs supporting sources, assumptions, company/hardware links, a TSMC transmission channel and evidence that would invalidate it.
6. Separate total compute demand, supplier share, manufacturing content, shipment timing, revenue and margins. A relationship graph shows exposure; it does not establish causal contagion.
7. Keep unresolved checks explicit. Internal metrics remain deferred. Do not invent adoption, GPU orders or financial validation.

## Tinker / GLM correction

[Tinker's source post](https://x.com/tinkerapi/status/2108670587241697771) attributes price reductions to efficiency improvements for long-context RL. The [supporting post](https://x.com/tinkerapi/status/2108671005132763598) compares GLM-5.3-Flash with GLM-5.3. That different-model comparison is distinct from platform-wide repricing and from a same-model historical cut.

The [official GLM-5.3-Flash model card](https://huggingface.co/zai-org/GLM-5.3-Flash) provides weights and lists an MIT license. This verifies that exact version today; do not automatically generalize to every GLM version or assume historical availability.

- Potential positive: efficiency savings → cheaper service access → more paid RL/training/inference workloads → incremental general-purpose GPU capacity → NVIDIA, if verified or explicitly assumed → TSMC wafers/packaging if additional orders follow.
- Offset: fewer GPU-hours per comparable task can offset workload growth. Net demand remains unresolved.
- Conditional negative: realized service prices fall faster than costs and volume offsets → weaker service-provider returns → reduced procurement. This requires evidence and does not establish reduced GLM-publisher revenue.

Open weights can coexist with paid hosting. Neither openness nor lower prices alone determines TSMC direction.

## Other reasoning checks

A Google release may expand compute, but does not establish open weights or NVIDIA deployment. Check TPU/GPU allocation and manufacturing route.

An open-model release may expand NVIDIA demand, subject to real adoption, spare capacity, efficiency and hardware alternatives.

Tweets about power, memory, packaging, software efficiency, capacity reassignment or financing can introduce mechanisms beyond C1–C7. Preserve attribution and test the manufacturing consequences.

## Implemented locally

Original post excerpts now appear beside the reasoning as attributed source viewpoints. Efficiency-driven service-pricing stories receive distinct adoption, efficiency-offset and conditional service-margin branches, with an unresolved overall direction. Full source-led interpretation for every story remains a subsequent pipeline step.
