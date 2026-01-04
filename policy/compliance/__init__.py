"""
Compliance Policy Modules

Pre-built policy templates for major compliance standards:
- GDPR (General Data Protection Regulation)
- HIPAA (Health Insurance Portability and Accountability Act)
- SOC 2 (Service Organization Control 2)
- PCI-DSS (Payment Card Industry Data Security Standard)
"""

from policy.compliance.loader import ComplianceLoader

__all__ = ["ComplianceLoader"]
