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
Example Custom Risk Engine Plugin

Demonstrates how to create an external risk assessment plugin.
"""

import re
from typing import Dict, Any
from policy.plugins import RiskEnginePlugin


class ContentBasedRiskEngine(RiskEnginePlugin):
    """
    Content-based risk assessment engine.
    
    Analyzes prompts for risky patterns and keywords.
    """
    
    # Risk keyword configuration - externalize in production
    FINANCIAL_KEYWORDS = ['payment', 'transfer', 'credit card', 'bank account', 
                         'bitcoin', 'crypto', 'wire transfer']
    DANGEROUS_KEYWORDS = ['delete', 'drop', 'truncate', 'remove', 'destroy']
    CODE_PATTERNS = ['<script>', 'eval(', 'exec(', 'system(', '`']
    
    @property
    def plugin_id(self) -> str:
        return "content-risk-engine"
    
    @property
    def plugin_name(self) -> str:
        return "Content-Based Risk Engine"
    
    @property
    def plugin_version(self) -> str:
        return "1.0.0"
    
    @property
    def plugin_description(self) -> str:
        return "Assesses risk based on prompt content analysis"
    
    def assess_risk(
        self,
        agent_id: str,
        prompt: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess risk based on content analysis.
        
        Checks for:
        - Financial keywords
        - PII patterns
        - Dangerous operations
        - Code injection attempts
        """
        risk_score = 0.0
        risk_factors = []
        threat_indicators = []
        recommendations = []
        
        prompt_lower = prompt.lower()
        
        # Check for financial keywords
        for keyword in self.FINANCIAL_KEYWORDS:
            if keyword in prompt_lower:
                risk_score += 15
                risk_factors.append(f"Financial keyword detected: {keyword}")
        
        # Check for PII patterns
        if re.search(r'\b\d{3}-\d{2}-\d{4}\b', prompt):  # SSN pattern
            risk_score += 30
            risk_factors.append("SSN pattern detected")
            threat_indicators.append("PII_EXPOSURE")
        
        if re.search(r'\b\d{16}\b', prompt):  # Credit card pattern
            risk_score += 30
            risk_factors.append("Credit card pattern detected")
            threat_indicators.append("PAYMENT_DATA")
        
        # Check for dangerous operations
        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword in prompt_lower:
                risk_score += 20
                risk_factors.append(f"Dangerous operation keyword: {keyword}")
        
        # Check for code injection patterns
        for pattern in self.CODE_PATTERNS:
            if pattern in prompt_lower:
                risk_score += 25
                risk_factors.append(f"Code injection pattern: {pattern}")
                threat_indicators.append("CODE_INJECTION")
        
        # Check prompt length (potential data exfiltration)
        if len(prompt) > 2000:
            risk_score += 10
            risk_factors.append("Unusually long prompt")
            recommendations.append("Review for data exfiltration attempt")
        
        # Determine risk level
        risk_score = min(risk_score, 100)
        
        if risk_score < 20:
            risk_level = "low"
        elif risk_score < 50:
            risk_level = "medium"
            recommendations.append("Monitor execution closely")
        elif risk_score < 75:
            risk_level = "high"
            recommendations.append("Require approval before execution")
        else:
            risk_level = "critical"
            recommendations.append("Block execution and alert security team")
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "threat_indicators": threat_indicators,
            "recommendations": recommendations,
            "external_ref": f"content-risk-{agent_id}"
        }


class MLRiskEngine(RiskEnginePlugin):
    """
    ML-based risk engine (placeholder for real ML model).
    
    In production, this would integrate with your ML risk model.
    """
    
    @property
    def plugin_id(self) -> str:
        return "ml-risk-engine"
    
    @property
    def plugin_name(self) -> str:
        return "ML-Based Risk Engine"
    
    @property
    def plugin_version(self) -> str:
        return "1.0.0"
    
    @property
    def plugin_description(self) -> str:
        return "ML model-based risk assessment (placeholder)"
    
    def assess_risk(
        self,
        agent_id: str,
        prompt: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess risk using ML model.
        
        In production, replace with actual ML model inference.
        """
        # Placeholder: Simple heuristic
        # In production: model.predict(features)
        
        risk_score = len(prompt) / 50  # Simplified scoring
        risk_score = min(risk_score, 100)
        
        if risk_score < 30:
            risk_level = "low"
        elif risk_score < 60:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": ["ML model prediction"],
            "threat_indicators": [],
            "recommendations": ["Based on ML model v1.0"],
            "external_ref": "ml-model-prediction-123"
        }
