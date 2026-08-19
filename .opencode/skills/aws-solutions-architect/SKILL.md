---
name: aws-solutions-architect
description: Applies the AWS Certified Solutions Architect Official Study Guide (Joe Baron et al.) to designing cloud infrastructure: compute, storage, database, and networking services arranged for high availability, scalability, and cost control. Covers the Well-Architected pillars and the core service decisions for each workload. Use when the user says 'design an AWS architecture', 'choose EC2 or Lambda', or 'make this HA on AWS'.
---
# aws-solutions-architect

The AWS Certified Solutions Architect Official Study Guide by Joe Baron and colleagues is the canonical map of AWS services and the design logic behind them. Use this skill to design, deploy, and operate automation infrastructure on AWS with availability, security, and cost as explicit inputs.

## Core principles
- Architect for the five Well-Architected pillars: operational excellence, security, reliability, performance efficiency, and cost optimization.
- Match the service to the workload: EC2 for full control, Lambda for event-driven short tasks, containers for portable services, S3 for object storage, DynamoDB for key-value scale.
- High availability comes from redundancy across availability zones plus elastic scaling and health-checked replacement.
- Security is built in: VPC isolation, IAM least privilege, encryption at rest and in transit, and managed key control.
- Cost is an architecture input: prefer managed services, right-size instances, and spend the free tiers deliberately.
- Availability zones are the building block of high availability; plan for losing one at a time.
- Everything that can fail should fail in a way the system can detect and replace.

## Key patterns
- Three-tier web architecture: a load-balanced web tier, an application tier, and a managed database tier, each independently scalable.
- Stateless compute with state pushed to services (cache, DynamoDB, RDS) so any node can be replaced without data loss.
- Event-driven integration with SQS queues and SNS topics decoupling producers from consumers.
- Serverless data pipelines: S3 event notifications drive Lambda processing.
- Multi-AZ databases with automated backups and point-in-time restore.
- Auto scaling groups with health checks and spread across availability zones.
- Elastic scaling pairs a scaling policy with a health check so replacement happens automatically.

## Applying this to n8n/automation/code
- Deploy the n8n instance on EC2 or ECS behind a load balancer with a multi-AZ managed database, keeping all state external to the box.
- Store workflow artifacts and binary output in S3 buckets with lifecycle rules, and trigger processing with Lambda or SQS.
- Put secrets in Secrets Manager and reference them from workflow credentials, never in the workflow JSON.
- Add CloudWatch alarms on execution failures and instance health, tied to the error budget.
- Use the free tiers and cost explorer to keep a self-hosted automation stack cheap.
- Place the database and worker queues in private subnets so only the app tier reaches them.

## Hard rules
- Never place databases in a public subnet; keep them private behind security groups.
- Always enable encryption on S3 buckets and databases.
- Always apply IAM least privilege; no wildcard permissions on production roles.
- Always design for instance replacement, never for patching a single fragile box.
- Never store access keys in code or instance metadata that a workflow could read.

## Pairs with
infrastructure-as-code, cloud-native-patterns, cloud-resilience-patterns, security-engineering-threat-modeling, agent-arch-system-design
