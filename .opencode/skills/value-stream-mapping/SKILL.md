---
name: value-stream-mapping
description: Applies the First Way of The DevOps Handbook (Kim, Humble, Debois, Willis) to accelerate flow: map the end-to-end value stream from request to deployed, quantify wait time versus active time at each step, shrink batch sizes, and remove handoffs and queues that lengthen lead time. Use when the user says 'value stream', 'value stream mapping', 'why is delivery slow', 'reduce lead time', 'flow efficiency', 'batch size', 'handoffs', 'queues', 'First Way', 'DevOps Handbook', 'optimize the flow', or when delivery speed is throttled by hand-offs and waiting. Pairs with: devops-handbook-flow, continuous-delivery-pipeline, the-goal-constraints, accelerate-dora-metrics.
---

# Value Stream Mapping

Transfers the First Way of The DevOps Handbook to any delivery pipeline: see the whole flow, find where value waits, and shrink the batch sizes that multiply delay.

## When to use
- Delivery is slow even though every individual step looks fast.
- Work sits in queues and handoffs longer than anyone works on it.
- A pipeline needs a shared picture that every team agrees on.

## Map the end-to-end stream
- Walk the path a single request travels from the moment it is requested to the moment it is deployed and used.
- Name every step, queue, and handoff; include the steps that are invisible to the requester.
- Draw the map with the team that owns each step so the picture is the real process, not the documented one.

## Quantify flow
- Measure wait time and active time per step; flow efficiency is active time as a share of total elapsed time.
- A low flow-efficiency number is the symptom that queues and handoffs dominate.
- Measure lead time and deployment frequency as the external outcomes the stream must improve.

## Shrink batch sizes
- Smaller batches move through the stream faster and reveal problems sooner.
- Split large features into shippable increments; each increment travels the full stream.
- Reduce handoffs by letting one team own a larger slice of the stream.

## Remove queues and waste
- Name the constraint that holds the flow; subordinate everything else to it.
- Cut steps that add no value to the request — approvals, rework loops, and partial handoffs.
- Make waiting visible; a visible queue is the first step toward eliminating it.

## Verification discipline
- Re-measure flow efficiency after each change; a higher flow-efficiency number is the only proof that flow improved.
- Track lead time before and after to confirm the improvement reached the customer.

## Pairs with
devops-handbook-flow, continuous-delivery-pipeline, the-goal-constraints, accelerate-dora-metrics.