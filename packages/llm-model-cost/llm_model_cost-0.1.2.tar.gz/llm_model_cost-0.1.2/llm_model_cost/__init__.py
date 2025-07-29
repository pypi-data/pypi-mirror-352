from .calculator import ModelCostCalculator

class modelCost:
    _calculator = ModelCostCalculator()
    
    def __new__(cls, name: str, input_tokens: int = 0, output_tokens: int = 0):
        """
        Calculate the cost for a given model and token counts.
        
        Args:
            name: Name of the model
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Dictionary containing input cost, output cost, and total cost
        """
        return cls._calculator.calculate_cost(name, input_tokens, output_tokens)
    
    @classmethod
    def get_model_info(cls, name: str):
        """Get detailed information about a specific model."""
        return cls._calculator.get_model_info(name)
    
    @classmethod
    def list_models(cls):
        """List all available models."""
        return cls._calculator.list_models()
    
    @classmethod
    def get_models_by_provider(cls, provider: str):
        """Get all models from a specific provider."""
        return cls._calculator.get_models_by_provider(provider)
    
    @classmethod
    def get_models_by_mode(cls, mode: str):
        """Get all models of a specific mode."""
        return cls._calculator.get_models_by_mode(mode)

__version__ = "0.1.2" 