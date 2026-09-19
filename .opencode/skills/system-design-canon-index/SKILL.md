---
name: system-design-canon-index
description: "Index of 120+ system-design books mapped to skills: find which book covers what and which skill applies it. Use when the user says 'best books', 'reading list', 'which book for X', 'فهرس الكتب', 'what should I read', or needs the canon behind any design decision."
---

# System Design Canon Index

120+ vetted books (106 from the community canon mhadidg/
software-architecture-books, Goodreads >= 3.5, plus modern essentials
through 2026) mapped to the skill that applies each one. Books teach;
skills execute. When a design cites a book, load its skill.

## How to use

1. Find the book by topic below. 2. Load the mapped skill — it encodes
the book's actionable core. 3. Books marked (E) already have a
dedicated skill; (M) are distilled into a master skill; (I) live only
in this index with their one-line lesson.

## System architecture

- Clean Architecture (Martin) -> `clean-architecture` (E)
- Patterns of Enterprise Application Architecture (Fowler) -> `enterprise-application-architecture` (E)
- Building Evolutionary Architectures -> `evolutionary-architecture` (E)
- Fundamentals of Software Architecture -> `fundamentals-of-software-architecture` (E)
- Software Architecture in Practice (Bass: scenarios, tactics, ATAM) -> `quality-attribute-scenarios-tactics` (M)
- Architecting for Scale -> `finops-cost-architecture` + `production-capacity-planning` (M)
- Software Architecture for Developers Vol 1+2 (Brown: leadership, C4) -> `architect-elevator-staff` + `c4-architecture-communication` (M)
- Software Systems Architecture: Viewpoints (Rozanski/Woods) -> `quality-attribute-scenarios-tactics` + `c4-architecture-communication` (M)
- Design It! (Fairbanks) -> `architect-elevator-staff` (M)
- Software Architect Elevator (Hohpe) -> `architect-elevator-staff` (M)
- Righting Software (Checinski) -> `architect-elevator-staff` (M)
- Analysis Patterns (Fowler) -> `domain-modeling-functional` (M)
- 12 Essential Skills for Software Architects -> `architect-elevator-staff` (M)
- Documenting Software Architectures: Views and Beyond -> `c4-architecture-communication` (M)
- 97 Things Every Software Architect -> `c4-architecture-communication` (M)
- 37 Things One Architect Knows -> `architect-elevator-staff` (M)
- Software Architecture: The Hard Parts -> `software-architecture-hard-parts` (E)
- Software Architecture: Foundations, Theory, and Practice -> `fundamentals-of-software-architecture` (M)
- SOA Principles of Service Design / SOA Concepts (Erl) -> `enterprise-service-bus` + `integration-architecture-frameworks` (M)
- Head First Software Architecture (2024) -> `fundamentals-of-software-architecture` + `c4-architecture-communication` (M)
- Beyond Software Architecture (Brown) -> `architect-elevator-staff` (M)

## Design patterns

- Design Patterns GoF / Head First DP / Dive Into DP / Refactoring to Patterns -> `gof-design-patterns` + `refactoring-catalog-recipes` (E)
- Reactive Design Patterns -> `event-driven-ai-workflows` + `resilient-design-prompt-injection-v2` (M)
- Design Patterns Explained / PPP of DDD -> `domain-driven-design-strategic` (M)

## Domain-driven design

- DDD: Tackling Complexity (Evans) -> `domain-driven-design-strategic` (E)
- Implementing DDD (Vernon) / DDD Distilled / DDD Quickly -> `ddd-tactical-aggregates` (E)
- Domain Modeling Made Functional (Wlaschin) -> `domain-modeling-functional` (E)

## Microservices

- Building Microservices (Newman) -> `microservices-boundary-design` (E)
- Monolith to Microservices (Newman) -> `monolith-to-microservices` (E)
- Microservice Patterns (Richardson) -> `microservices-patterns` (E)
- Production-Ready Microservices (Fowler) -> `production-microservices-standards` (M)
- Microservices AntiPatterns and Pitfalls -> `production-microservices-standards` (M)
- Tao of Microservices -> `production-microservices-standards` (M)
- Reactive Microservices Architecture -> `event-driven-architecture-async-patterns` (M)
- Microservice Architecture: Principles/Practices/Culture -> `team-topologies` + `production-microservices-standards` (M)
- Microservices From Design to Deployment -> `microservices-up-and-running` (M)

## Data + streaming

- Designing Data-Intensive Applications (Kleppmann; 2e 2026 w/ Riccomini adds cloud-service design) -> `data-intensive-applications` + `ddia-replication-partitioning` (E)
- Database Internals (Petrov) -> `database-internals-engines` + `petrov-lsm-storage-compaction` (E)
- Big Data Principles (Marz/Warren) -> `streaming-systems-akidau` (M)
- Data Modeling Made Simple -> `database-system-concepts` + `fundamentals-database-systems` (M)
- Model Thinker / Beautiful Data (I) -> mental models for data work; no dedicated skill — pair `data-analysis`
- Enterprise Integration Patterns -> `enterprise-integration-patterns` + `eip-message-routing` + `eip-message-transformation` (E)
- Streaming Systems (Akidau) -> `streaming-systems-akidau` (E)
- Designing Event-Driven Systems (Stopford) -> `designing-event-driven-systems` (E)
- Making Sense of Stream Processing (I) -> pairs `streaming-systems-akidau`

## Distributed systems

- Designing Distributed Systems (Burns: sidecar/ambassador/adapters) -> `designing-distributed-systems` (E)
- Distributed Systems for Fun and Profit -> `distributed-systems-field-manual` (M)
- Understanding Distributed Systems (Vitillo, practical) -> `distributed-systems-field-manual` (M)
- Distributed Systems: Concepts and Design (Coulouris) -> `distributed-systems-concepts-design` (E)
- Distributed Systems (Tanenbaum/van Steen) -> `distributed-systems-tanenbaum` (E)
- Security Engineering (Anderson: threat model, platform, crypto) -> `security-engineering-threat-modeling` + `security-engineering-platform-security` + `applied-cryptography-engineering` (E)

## Cloud + web scalability

- Infrastructure as Code (Morris) -> `infrastructure-as-code` + `immutable-infrastructure` (E)
- Cloud Native Infrastructure / Patterns (Davis) -> `cloud-native-patterns` + `cloud-resilience-patterns` (E)
- Practice of Cloud System Administration -> `practice-of-cloud-system-administration` (E)
- Beyond the Twelve-Factor App -> `cloud-native-patterns` (M)
- Kubernetes Patterns -> `kubernetes-operations` + `kubernetes-deployment-strategies` (E)
- Cloud Design Patterns (Azure) -> `cloud-native-patterns` (M)
- Art of Scalability (AKF cube; people/process/tech) -> `akf-scalability-cube` (E)
- Web Scalability for Startup Engineers (Ejsmont) -> `web-scalability-startup-playbook` (M)
- Scalability Rules (Abbott, 50 principles) -> `web-scalability-startup-playbook` (M)
- Building Scalable Web Sites / Scalable Internet Architectures -> `web-scalability-startup-playbook` (M)
- Art of Capacity Planning (Allspaw) -> `production-capacity-planning` (M)
- High Performance Web Sites (Souders) -> `web-scalability-startup-playbook` (M)
- High Performance Browser Networking (Grigorik) -> `high-performance-browser-networking` (E)
- Chaos Engineering (Rosenthal/Basiri) -> `chaos-resilience-practice` (M)
- Observability Engineering (Majors et al) -> `observability-engineering-design` (M)
- Cloud FinOps (Storment) -> `finops-cost-architecture` (M)

## Agile / DevOps / general

- DevOps Handbook / Continuous Delivery / Continuous Integration -> `devops-handbook-flow` + `continuous-delivery-pipeline` (E)
- DevOps: A Software Architect's Perspective -> `devops-automation` (M)
- SRE (Google) / SRE Workbook -> `sre-workbook-practices` + `sre-devops-automation` (E)
- Release It! (Nygard: stability patterns) -> `release-it-production-hardening` (E)
- Software Engineering at Google -> `software-engineering-at-google` (E)
- Team Topologies -> `team-topologies` (E)
- Staff Engineer (Larson) -> `staff-engineer-leadership` (E)
- Pragmatic Programmer (DRY/orthogonality/reversibility/tracer) -> `pragmatic-programmer` + `orthogonality-guard` + `reversibility-engine` (E)
- Mythical Man-Month (Brooks) -> `mythical-man-month-leadership` (E)
- Philosophy of Software Design (Ousterhout) -> `philosophy-software-design-ousterhout` + `abstraction-quality-gate` (E)
- Clean Agile / Agile PPP / Art of Agile / Balancing Agility -> `clean-agile` + `agile-principles-patterns-practices` (E)
- Software Estimation (McConnell) -> `production-capacity-planning` (M)
- Software Requirements / Waltzing with Bears (risk) -> `proactive-spec-expander` + `thinking-pre-mortem` (M)
- Software Design X-Rays (Tornhill, behavioral analysis) -> `code-smell-detector` + `code-execution-guided-swemaster` (M)
- System Design Interview Vol 1+2 (Alex Xu) -> `alex-xu-system-design` (E)
- Hacking the System Design Interview (Chiang) -> `alex-xu-system-design` (M)
- Software Security: Building Security In (McGraw) -> `secure-software-lifecycle` (M)
- Container Security -> `linux-security-hardening` + `docker-deep-dive` (M)

## Verification

Every book above resolves to a named loadable skill; (M) rows are
covered by the master skill named, (E) rows by a dedicated skill, (I)
rows name their pair. A book with no row is a gap — report it via
`find-skills` flow instead of guessing.

## Pairs with

- `system-design-production-blueprint` (execute the design),
  `find-skills` (fill gaps), `fable-5-playbook` (frontier behavior).
