"""LLM client for interacting with different LLM providers."""

import logging
from typing import Dict, Any, Optional, AsyncContextManager

from ..providers import create_provider
from .models import LLMGenerationConfig

logger = logging.getLogger('gollm.orchestrator.llm_client')

class LLMClient(AsyncContextManager):
    """Client for interacting with LLM providers."""
    
    def __init__(self, config: Dict[str, Any], provider_name: Optional[str] = None):
        """Initialize the LLM client.
        
        Args:
            config: Configuration dictionary
            provider_name: Name of the provider to use (default: from config)
        """
        self.config = config
        self.provider_name = provider_name or config.llm_integration.api_provider.lower()
        self.provider = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        # Get provider config
        provider_config = self._get_provider_config()
        
        # Create and initialize provider
        self.provider = create_provider(self.provider_name, provider_config)
        await self.provider.__aenter__()
        
        logger.info(f"Initialized LLM provider: {self.provider_name}")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.provider:
            await self.provider.__aexit__(exc_type, exc_val, exc_tb)
    
    def _get_provider_config(self) -> Dict[str, Any]:
        """Get the configuration for the current provider."""
        # Get base config from llm_integration
        base_config = {
            'model': self.config.llm_integration.model_name,
            'temperature': 0.1,
            'max_tokens': self.config.llm_integration.token_limit,
        }
        
        # Merge with provider-specific config
        provider_config = self.config.llm_integration.providers.get(self.provider_name, {})
        return {**base_config, **provider_config}
    
    async def generate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        generation_config: Optional[LLMGenerationConfig] = None
    ) -> Dict[str, Any]:
        """Generate a response using the configured LLM provider.
        
        Args:
            prompt: The prompt to generate a response for
            context: Additional context for the generation
            generation_config: Configuration for the generation
            
        Returns:
            Dictionary containing the generated response and metadata
        """
        if not self.provider:
            raise RuntimeError("LLM provider not initialized. Use 'async with' context manager.")
        
        # Prepare generation parameters
        params = {
            'temperature': generation_config.temperature if generation_config else 0.1,
            'max_tokens': generation_config.max_tokens if generation_config else 4000,
            # Parameters to encourage simpler, more concise responses
            'top_p': 0.9,  # Focus on high-probability tokens
            'frequency_penalty': 0.7,  # Discourage repetition
            'presence_penalty': 0.7,  # Encourage new content
            'stop': ['```', '---', '===', '##'],  # Stop on common formatting markers
        }
        
        # If the prompt is asking for simple code, be more strict
        if 'simple' in prompt.lower() or 'hello' in prompt.lower() or 'world' in prompt.lower():
            params.update({
                'temperature': 0.1,  # Lower temperature for more focused output
                'max_tokens': 50,  # Limit output length
                'top_p': 0.8,
                'frequency_penalty': 1.0,
                'presence_penalty': 1.0,
            })
        
        # Add any additional context
        if context:
            params['context'] = context
        
        # Generate the response
        try:
            response = await self.provider.generate_response(prompt, **params)
            
            if not response.get('success', False):
                error = response.get('error', 'Unknown error')
                logger.error(f"LLM generation failed: {error}")
                raise RuntimeError(f"LLM generation failed: {error}")
                
            return response
            
        except Exception as e:
            logger.exception(f"Error generating response with {self.provider_name}")
            raise RuntimeError(f"Error generating response: {str(e)}") from e
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the LLM provider.
        
        Returns:
            Dictionary with health check results
        """
        if not self.provider:
            return {
                'status': False,
                'error': 'Provider not initialized'
            }
            
        try:
            return await self.provider.health_check()
        except Exception as e:
            logger.exception("Health check failed")
            return {
                'status': False,
                'error': str(e)
            }
