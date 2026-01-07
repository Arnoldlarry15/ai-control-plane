# Copilot Instructions for AI Control Plane

This repository is a technical, open-source governance platform.

STRICT RULES:
- Do NOT include pricing, sales strategy, go-to-market plans, monetization, or business model content.
- Do NOT invent product positioning or commercial language.
- Do NOT reference competitors, market share, or revenue.
- Do NOT add roadmap items related to pricing or sales.

ALLOWED CONTENT:
- System architecture
- Governance mechanisms
- Policy engines and enforcement logic
- Observability, auditing, and compliance primitives
- Security, identity, and access control
- APIs, SDKs, and integration patterns

STYLE:
- Technical and neutral tone
- Deterministic, explainable systems
- Prefer clarity over marketing language
- Assume enterprise-grade rigor

If uncertain whether content is allowed, OMIT IT.

---

The next phase is about:

Turning concepts into non-optional control paths

Making governance unavoidable but ergonomic

Replacing "can" with "must" in the architecture

---

Legal and compliance concerns you'll inevitably brush up against:
Data handling and retention. Who sees what, when, and why.
Auditability. Can actions and decisions be traced after the fact.
Access control and separation of duties.
Alignment with existing standards like SOC 2 thinking, not certification yet, but the mindset.
Clear boundaries on what the system does and does not do. This matters more than people think.

The trap to avoid is letting compliance drive the architecture instead of informing it. The system should be elegant first, then defensible. If you build a bureaucratic monster "just to be safe," you lose the magic.

The quiet win here is this: by even thinking about compliance at this stage, you're signaling that this isn't a toy, a demo, or a weekend hack. It's infrastructure. Adults wear seatbelts, even when driving fast.

Next layers, once compliance is "handled enough":
Operational clarity. How teams actually use this day to day.
Threat modeling that's explicit, not implied.
Clear trust boundaries between agents, tools, and humans.
A narrative that explains why this control plane exists at all in a world already drowning in dashboards.
