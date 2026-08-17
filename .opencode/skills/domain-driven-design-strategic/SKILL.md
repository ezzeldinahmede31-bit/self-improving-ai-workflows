---
name: domain-driven-design-strategic
description: "Applies Eric Evans' Domain-Driven Design to n8n workflows and code: the Ubiquitous Language shared with the domain experts, strategic design with Bounded Contexts, Context Maps, the Core Domain, and Anti-Corruption Layers. Enforces that automation node names, expressions, and messages speak the business language - never generic tech vocabulary - and that contexts stay isolated with explicit integration points. Use when the user says 'bounded context', 'ubiquitous language', 'core domain', 'context map', 'DDD', 'domain modeling', 'model the business', 'domain expert', 'anti-corruption layer', or when workflow terms contradict business terms. Pairs with: domain-modeling-functional, clarify-before-execute, abstraction-quality-gate, proactive-spec-expander."
---
# Domain-Driven Design (Strategic)

Eric Evans' DDD: the model must serve the domain, and the language of the model must be the language of the business. This skill applies strategic DDD to automation design so the workflow's vocabulary matches the business's vocabulary, and contexts stay cleanly bounded.

## Strategic Design Elements (applied to automation)

### 1. Ubiquitous Language
- Every node name, expression variable, and error message must use the business term (e.g. 'OrderApproved' not 'WebhookEvent14').
- When the business says 'lead', the workflow says 'lead' - everywhere, with no synonyms.
- Test: read the workflow aloud to a domain expert. Every term they hear must be one they use.

### 2. Bounded Context
- Each context owns its model; the same word may mean different things in different contexts (e.g. 'Order' in Sales vs 'Order' in Shipping).
- In n8n this maps to SUB-WORKFLOWS: one context = one sub-workflow with its own vocabulary and responsibilities.
- Integration across contexts happens through explicit, minimal contracts - not shared nodes.

### 3. Context Map
- Draw (or document) the relationships: Partnership, Shared Kernel, Customer-Supplier, Conformist, Anticorruption Layer, Open Host Service.
- For each pair of contexts, name the relationship type. This drives which nodes can couple.

### 4. Core Domain (the strategic priority)
- The subdomain that differentiates the business gets the BEST modeling and the most rigorous gate passes.
- Generic subdomains (email sending, logging) get commodity solutions (existing nodes) - do not over-model them.
- Supporting subdomains get adequate but not heroic modeling.

### 5. Anti-Corruption Layer (ACL)
- When integrating with an external/legacy system whose model is ugly, insert a translation boundary (a Code node or HTTP adapter) so the ugliness never leaks into the core model.
- The ACL converts foreign terms and structures into the Ubiquitous Language.

## DDD Gate (pre-build checklist)

- [ ] Every node name uses the business term, verb-first and consistent across the whole workflow
- [ ] No two different terms used for the same concept, no same term for two concepts
- [ ] Each bounded context is a sub-workflow with an explicit interface
- [ ] Context relationships are documented (partnership, ACL, etc.)
- [ ] Core domain nodes carry the highest testing/verification rigor
- [ ] External system integration flows through an Anti-Corruption Layer, never raw

## Violations (severity)

- **V1 - Vocabulary drift** (HIGH): 'customer' in one node, 'client' in another, 'user' in a third. Fix: unify to the business term.
- **V2 - Context bleed** (HIGH): Sales nodes reading Shipping's private state directly. Fix: define the integration contract.
- **V3 - Missing ACL** (HIGH): Raw external API fields (snake_case, foreign codes) flowing into core nodes. Fix: insert a translation boundary.
- **V4 - Generic vocabulary for core terms** (MEDIUM): 'data', 'record', 'object' where the business says 'invoice'. Fix: rename.
- **V5 - Over-modeling commodity** (LOW): A bespoke modeled 'email infrastructure' context. Fix: use the standard node.

## Verification

Run the build gates on any workflow with business vocabulary and require READY_FOR_DEPLOYMENT. Confirm naming consistency by reading node names in sequence like a sentence in the business language.
