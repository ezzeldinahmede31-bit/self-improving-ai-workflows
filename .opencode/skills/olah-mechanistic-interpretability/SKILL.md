---
name: olah-mechanistic-interpretability
description: "Reverse-engineers neural networks: features, circuits, and causal attribution. Use when the user says 'mechanistic interpretability', 'induction heads', 'superposition', 'sparse autoencoders', 'feature visualization', 'circuit', 'attribution', 'Olah', 'what does this neuron do', or when a model must be understood, not just measured."
---

# Olah Mechanistic Interpretability

Distilled from the Circuits/distill.pub program (Olah et al.) and the
Anthropic interpretability lineage: treat the network as compiled code and
decompile it — features are variables, weights are the operations, circuits
are the subroutines.

## Purpose

Replace "the model just does that" with a causal story: which internal
structures compute the behavior, verified by intervention.

## The method (observe -> hypothesize -> intervene)

1. **Find candidate features.** Visualization (optimize inputs for
   activation), dataset exemplars (what inputs excite it most), dimensionality
   probes. One method lies; agreement across methods is the signal.
2. **Expect superposition.** Networks store MORE features than neurons
   (nearly-orthogonal directions in activation space). Single neurons are
   usually polysemantic — analyze DIRECTIONS, not neurons. Sparse
   autoencoders disentangle superposed features into interpretable ones.
3. **Trace circuits.** Follow weights from feature to feature (e.g.
   previous-token + induction heads implementing in-context copying).
   Minimality test: ablate everything outside the proposed circuit — behavior
   must survive; ablate inside — behavior must break.
4. **Attribute causally.** Activation patching (swap activations from a
   contrastive run to localize), path patching (which edges carry the
   effect), gradient-based attribution as a cheap first pass. Correlation of
   activation with behavior is a hypothesis, patching is the verdict.
5. **Close the loop.** A complete explanation predicts: novel inputs where
   the behavior appears/disappears per the circuit story. Test the
   prediction; update the story. Publish the falsifiable version.

## Honesty constraints

- Interpretability claims are about the TRAINED artifact, not the
  architecture in general — re-verify per checkpoint/scale.
- Toy models transfer partially; state what was shown in small models vs
  production scale.
- "The probe found it" ≠ "the model uses it" — probes detect presence,
  interventions prove use.

## Verification

Each claim ships with: feature definition (exemplars + decoder), circuit
diagram (nodes/edges), ablation/patching numbers, and a novel prediction
tested. Missing intervention = unconfirmed hypothesis, labeled as such.

## Pairs with

- `interpretable-machine-learning`/`model-explanations-shap-lime`
  (behavioral explanations), `neural-networks-and-deep-learning` (substrate),
  `evaluation` (behavioral evals the circuits must predict),
  `experiment-code` (patching harnesses).
