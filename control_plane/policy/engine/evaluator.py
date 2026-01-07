"""
Policy Engine Evaluator - The beating heart of governance.

This is the part that turns words into law.
It answers exactly one question:
"Given this request, under these policies, what must happen?"

And it must answer it deterministically.
Not vibes. Not best effort. Not "probably allowed."

The engine outputs one of three canonical outcomes:
- ALLOW: Proceed automatically
- DENY: Block immediately
- REVIEW: Pause and require human approval
"""

from typing import List
from control_plane.policy.schemas.context import RequestContext
from control_plane.policy.schemas.decision import PolicyDecision, DecisionType
from control_plane.policy.schemas.policy_schema import PolicySchema


def evaluate_policies(
    policies: List[PolicySchema],
    context: RequestContext
) -> PolicyDecision:
    """
    Evaluate policies against a request context.
    
    This is a pure evaluator:
    - No side effects
    - No database writes
    - No API calls
    
    It takes: policies + context → decision
    
    This purity is what makes it trustworthy.
    
    Evaluation algorithm:
    1. Sort policies by priority (highest first)
    2. For each policy:
       a. Check if scope matches
       b. Check if conditions match
       c. If both match, record the match
       d. If effect is DENY, return immediately
       e. If effect is REVIEW, return immediately
    3. If no DENY or REVIEW matched, return ALLOW
    
    Args:
        policies: List of policy definitions
        context: Request context to evaluate
        
    Returns:
        PolicyDecision with outcome, matched policies, and reason
    """
    matched = []
    
    # Sort by priority (higher priority first)
    sorted_policies = sorted(policies, key=lambda p: p.priority, reverse=True)
    
    for policy in sorted_policies:
        # Check if scope matches
        if not _scope_matches(policy.scope, context):
            continue
        
        # Check if conditions match
        if not _conditions_match(policy.conditions, context):
            continue
        
        # Policy matched!
        matched.append(policy.id)
        
        # DENY takes precedence - return immediately
        if policy.effect == "DENY":
            return PolicyDecision(
                decision=DecisionType.DENY,
                matched_policies=matched,
                reason=f"Denied by policy {policy.id}: {policy.description}"
            )
        
        # REVIEW takes precedence over ALLOW - return immediately
        if policy.effect == "REVIEW":
            return PolicyDecision(
                decision=DecisionType.REVIEW,
                matched_policies=matched,
                reason=f"Review required by policy {policy.id}: {policy.description}"
            )
    
    # No blocking policies matched - ALLOW
    return PolicyDecision(
        decision=DecisionType.ALLOW,
        matched_policies=matched,
        reason="No blocking policies matched"
    )


def _scope_matches(scope: dict, context: RequestContext) -> bool:
    """
    Check if policy scope matches request context.
    
    Scope defines what the policy applies to:
    - environment: Which environments (dev, staging, production)
    - resource_type: Which resource types (model, agent, data)
    
    If scope is empty, policy applies to everything.
    If scope has a field, context value must be in allowed list.
    
    Args:
        scope: Policy scope definition
        context: Request context
        
    Returns:
        True if scope matches, False otherwise
    """
    if not scope:
        # Empty scope matches everything
        return True
    
    # Check environment
    if "environment" in scope:
        allowed_envs = scope["environment"]
        if context.environment not in allowed_envs:
            return False
    
    # Check resource_type
    if "resource_type" in scope:
        allowed_types = scope["resource_type"]
        if context.resource_type not in allowed_types:
            return False
    
    # Check actor_role
    if "actor_role" in scope:
        allowed_roles = scope["actor_role"]
        if context.actor_role not in allowed_roles:
            return False
    
    return True


def _conditions_match(conditions: dict, context: RequestContext) -> bool:
    """
    Check if policy conditions match request context.
    
    Conditions define when the policy triggers:
    - tags: Must have at least one of these tags
    - metadata: Must have these metadata key-value pairs
    
    If conditions is empty, policy always triggers.
    If conditions has fields, at least one must match.
    
    Args:
        conditions: Policy conditions
        context: Request context
        
    Returns:
        True if conditions match, False otherwise
    """
    if not conditions:
        # Empty conditions always match
        return True
    
    # Check tags - must have at least one matching tag
    if "tags" in conditions:
        required_tags = conditions["tags"]
        if not any(tag in context.tags for tag in required_tags):
            return False
    
    # Check metadata - must have all required key-value pairs
    if "metadata" in conditions:
        required_metadata = conditions["metadata"]
        for key, value in required_metadata.items():
            if context.metadata.get(key) != value:
                return False
    
    # Check intent
    if "intent" in conditions:
        allowed_intents = conditions["intent"]
        if isinstance(allowed_intents, list):
            if context.intent not in allowed_intents:
                return False
        else:
            if context.intent != allowed_intents:
                return False
    
    return True
