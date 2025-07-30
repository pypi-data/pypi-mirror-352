"""
OpenAI client for TestIndex.

This module provides a client for the OpenAI API.
It is only imported when the --llm flag is used, so it's an optional dependency.
"""

import json
import os
from decimal import Decimal
from typing import List, Dict, Any, Optional

from testindex.core.logging import get_logger

# Set up logger
logger = get_logger(__name__)


class OpenAIError(Exception):
    """Raised when there's an error with the OpenAI API."""
    pass


class OpenAIClient:
    """Client for the OpenAI API."""
    
    def __init__(self, model: str = "gpt-4o", budget: Decimal = Decimal("0.03")):
        """Initialize the OpenAI client.
        
        Args:
            model: OpenAI model to use
            budget: Maximum cost per suggestion in dollars
        """
        self.model = model
        # Ensure budget is a Decimal object
        self.budget = Decimal(str(budget)) if not isinstance(budget, Decimal) else budget
        self.cumulative_cost = Decimal("0.0")  # Track cumulative spending
        self.api_key = os.environ.get("OPENAI_API_KEY")
        
        # Token pricing (per 1K tokens)
        self.pricing = {
            "gpt-4o": {"input": Decimal("0.005"), "output": Decimal("0.015")},
            "gpt-4-turbo": {"input": Decimal("0.01"), "output": Decimal("0.03")},
            "gpt-3.5-turbo": {"input": Decimal("0.0005"), "output": Decimal("0.0015")}
        }
        
        # Check if OpenAI is available
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise OpenAIError("OpenAI package not installed. Install with: pip install openai")
        
        # Check if API key is set
        if not self.api_key:
            raise OpenAIError("OpenAI API key not set. Set OPENAI_API_KEY environment variable.")
    
    def generate_test_suggestions(self, prompt: str, name: str, 
                                 file_path: str) -> List[Dict[str, Any]]:
        """Generate test suggestions using the OpenAI API.
        
        Args:
            prompt: Prompt for the model
            name: Function name
            file_path: File path
            
        Returns:
            List of test suggestions
        """
        try:
            # Estimate cost
            prompt_tokens = len(prompt.split())
            estimated_tokens = prompt_tokens * 2  # Conservative estimate
            estimated_cost = self._estimate_cost(estimated_tokens)
            
            # Check budget with cost guard
            if not self.enforce_budget(estimated_cost):
                return []
            
            # Call API
            logger.info(f"Calling OpenAI API with model {self.model}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a test expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            # Process response
            content = response.choices[0].message.content
            
            # Try to parse as JSON
            if "[" in content and "]" in content:
                # Extract JSON array
                start = content.find("[")
                end = content.rfind("]") + 1
                json_str = content[start:end]
                
                try:
                    suggestions = json.loads(json_str)
                    
                    # Add metadata to suggestions
                    for suggestion in suggestions:
                        suggestion["test_name"] = suggestion.get("test_name", f"test_{name}")
                        suggestion["target_node"] = f"{file_path}::{name}"
                        suggestion["estimated_coverage_gain"] = 3.0  # Default value
                        suggestion["prompt_tokens"] = prompt_tokens
                        suggestion["completion_tokens"] = len(content.split())
                        suggestion["estimated_cost"] = float(estimated_cost)
                    
                    # Update cumulative cost tracking
                    self.cumulative_cost += estimated_cost
                    logger.info(f"Cumulative LLM cost: ${self.cumulative_cost:.4f}")
                    
                    return suggestions[:3]  # Limit to 3 suggestions
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse response as JSON: {json_str}")
                    return []
            else:
                logger.error(f"Response does not contain a JSON array: {content}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to generate test suggestions: {e}")
            return []
    
    def enforce_budget(self, estimated_cost: Decimal) -> bool:
        """Enforce budget constraints before API calls."""
        if estimated_cost > self.budget:
            logger.warning(f"Estimated cost ${estimated_cost:.4f} exceeds budget ${self.budget:.4f}")
            return False
        
        # Track cumulative cost with safety margin
        if self.cumulative_cost + estimated_cost > self.budget * 10:  # Safety margin
            logger.error(f"Cumulative cost ${self.cumulative_cost + estimated_cost:.4f} exceeds safety limit")
            return False
        
        return True
    
    def _estimate_cost(self, tokens: int) -> Decimal:
        """Estimate the cost of a request.
        
        Args:
            tokens: Estimated token count
            
        Returns:
            Estimated cost in dollars
        """
        model_pricing = self.pricing.get(self.model, {"input": Decimal("0.01"), "output": Decimal("0.03")})
        
        # Conservative estimate: 1/3 input, 2/3 output
        input_tokens = tokens // 3
        output_tokens = tokens - input_tokens
        
        # Ensure decimal arithmetic is used throughout
        input_cost = (Decimal(input_tokens) / Decimal("1000")) * model_pricing["input"]
        output_cost = (Decimal(output_tokens) / Decimal("1000")) * model_pricing["output"]
        
        total_cost = input_cost + output_cost
        
        logger.debug(f"Estimated cost: {total_cost} ({input_tokens} input, {output_tokens} output)")
        
        return total_cost 