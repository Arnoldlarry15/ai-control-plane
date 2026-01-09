# Copyright 2024 AI Control Plane Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Shared service instances.

This module provides singleton instances of all services to ensure
state is shared across the application.
"""

import logging

from registry.service import RegistryService
from kill_switch.service import KillSwitchService
from policy.evaluator import PolicyEvaluator
from observability.logger import ObservabilityLogger
from approval.service import ApprovalService

logger = logging.getLogger(__name__)

# Singleton instances
_registry: RegistryService = None
_kill_switch: KillSwitchService = None
_policy_evaluator: PolicyEvaluator = None
_obs_logger: ObservabilityLogger = None
_approval_service: ApprovalService = None


def get_registry() -> RegistryService:
    """Get singleton registry service instance."""
    global _registry
    if _registry is None:
        _registry = RegistryService()
        logger.info("Registry service initialized (singleton)")
    return _registry


def get_kill_switch() -> KillSwitchService:
    """Get singleton kill switch service instance."""
    global _kill_switch
    if _kill_switch is None:
        _kill_switch = KillSwitchService()
        logger.info("Kill switch service initialized (singleton)")
    return _kill_switch


def get_policy_evaluator() -> PolicyEvaluator:
    """Get singleton policy evaluator instance."""
    global _policy_evaluator
    if _policy_evaluator is None:
        _policy_evaluator = PolicyEvaluator()
        logger.info("Policy evaluator initialized (singleton)")
    return _policy_evaluator


def get_observability_logger() -> ObservabilityLogger:
    """Get singleton observability logger instance."""
    global _obs_logger
    if _obs_logger is None:
        _obs_logger = ObservabilityLogger()
        logger.info("Observability logger initialized (singleton)")
    return _obs_logger


def get_approval_service() -> ApprovalService:
    """Get singleton approval service instance."""
    global _approval_service
    if _approval_service is None:
        _approval_service = ApprovalService()
        logger.info("Approval service initialized (singleton)")
    return _approval_service
