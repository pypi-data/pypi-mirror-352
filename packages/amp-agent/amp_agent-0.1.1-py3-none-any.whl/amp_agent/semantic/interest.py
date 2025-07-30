"""
Interest model system supporting multiple methods for determining agent interest in messages.
Supports both classifier-based and hybrid approaches.
"""
import os
import json
# import torch
import logging
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional
# from sentence_transformers import SentenceTransformer
# from torch import nn

# Configure logging
logger = logging.getLogger(__name__)

class InterestMethod(ABC):
    """Abstract base class for interest checking methods"""
    
    @abstractmethod
    def is_interested(self, content: str) -> bool:
        """Check if the method determines interest in the content"""
        pass

class HeuristicRule(ABC):
    """Abstract base class for heuristic rules"""
    
    @abstractmethod
    def check(self, content: str) -> bool:
        """Check if the content matches the rule"""
        pass

class QuestionMarkRule(HeuristicRule):
    """Rule that checks for presence of question marks"""
    
    def check(self, content: str) -> bool:
        return "?" in content

class MinLengthRule(HeuristicRule):
    """Rule that checks if content meets minimum word length"""
    
    def __init__(self, min_words: int):
        self.min_words = min_words
    
    def check(self, content: str) -> bool:
        words = content.split()
        return len(words) >= self.min_words

class HeuristicMethod(InterestMethod):
    """Method that uses a collection of heuristic rules"""
    
    def __init__(self, rules_config: List[Dict[str, Any]]):
        self.rules: List[HeuristicRule] = []
        for rule_config in rules_config:
            rule_type = rule_config["type"]
            if rule_type == "question_mark":
                self.rules.append(QuestionMarkRule())
            elif rule_type == "min_length":
                self.rules.append(MinLengthRule(rule_config["min_words"]))
            else:
                logger.warning(f"Unknown heuristic rule type: {rule_type}")
    
    def is_interested(self, content: str) -> bool:
        # Consider interested if any rule matches
        return any(rule.check(content) for rule in self.rules)

class KeywordMethod(InterestMethod):
    """Method that checks for presence of keywords"""
    
    def __init__(self, config: Dict[str, Any]):
        self.keywords = set(config.get("keywords", []))
        self.match_type = config.get("match_type", "any")
        
        # Load additional keywords from file if specified
        keywords_file = config.get("keywords_file")
        if keywords_file and os.path.exists(keywords_file):
            with open(keywords_file, "r") as f:
                file_keywords = {line.strip().lower() for line in f if line.strip() and not line.startswith('#')}
                self.keywords.update(file_keywords)
    
    def is_interested(self, content: str) -> bool:
        content_lower = content.lower()
        if self.match_type == "any":
            return any(keyword in content_lower for keyword in self.keywords)
        elif self.match_type == "all":
            return all(keyword in content_lower for keyword in self.keywords)
        return False

# Commenting out torch-based classifier method
# class InterestClassificationHead(nn.Module):
#     """Classification head for determining if a message is relevant"""
#     
#     def __init__(self, input_dim: int, dropout_prob: float = 0.1):
#         super().__init__()
#         self.dropout = nn.Dropout(dropout_prob)
#         self.linear = nn.Linear(input_dim, 1)
#         self.sigmoid = nn.Sigmoid()
#         
#     def forward(self, embeddings):
#         x = self.dropout(embeddings)
#         x = self.linear(x)
#         return self.sigmoid(x)
# 
# class ClassifierMethod(InterestMethod):
#     """Method that uses a trained classifier to determine interest"""
#     
#     def __init__(self, config: Dict[str, Any]):
#         """
#         Initialize the classifier method
#         
#         Args:
#             config: Configuration dictionary containing model settings
#         """
#         self.model_path = config["model_path"]
#         self.threshold = config.get("threshold", 0.5)
#         model_config = config.get("config", {})
#         
#         # Set device
#         self.device = model_config.get("device")
#         if self.device is None:
#             self.device = "cuda" if torch.cuda.is_available() else "cpu"
#             
#         # Load base model
#         logger.info("Loading base model...")
#         self.base_model = SentenceTransformer(model_config.get("base_model", "all-MiniLM-L6-v2"))
#         
#         # Create and load classification head
#         logger.info("Loading classification head...")
#         self.classification_head = InterestClassificationHead(
#             model_config.get("embedding_dim", 384),
#             dropout_prob=model_config.get("dropout", 0.1)
#         )
#         
#         head_path = os.path.join(self.model_path, "classification_head.pt")
#         if not os.path.exists(head_path):
#             raise FileNotFoundError(f"Classification model not found at {head_path}")
#             
#         self.classification_head.load_state_dict(
#             torch.load(head_path, map_location=self.device)
#         )
#         self.classification_head.to(self.device)
#         self.classification_head.eval()
#         
#     def is_interested(self, content: str) -> bool:
#         # Get embedding
#         embedding = self.base_model.encode(content, convert_to_tensor=True).to(self.device)
#         
#         # Predict
#         with torch.no_grad():
#             score = self.classification_head(embedding.unsqueeze(0)).item()
#             
#         return score > self.threshold

class HybridInterestModel:
    """
    Main interest model that combines multiple methods.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the interest model based on configuration.
        
        Args:
            config: Configuration dictionary from agents.yaml
        """
        model_type = config.get("type", "hybrid")
        
        # Always use keywords or heuristic methods only, ignoring classifier methods
        self.methods = []
        
        if model_type == "classifier":
            # Instead of using classifier, log warning and use keywords if defined
            logger.warning("Classifier method disabled - using keywords or heuristic instead")
            if "keywords" in config:
                keyword_config = {"keywords": config.get("keywords", []), "match_type": "any"}
                self.methods.append(KeywordMethod(keyword_config))
            else:
                # Fallback to simple heuristic
                self.methods = [HeuristicMethod([{"type": "question_mark"}])]
        
        elif model_type == "hybrid":
            # Use only keyword and heuristic methods
            for method_config in config.get("methods", []):
                method_type = method_config["type"]
                
                if method_type == "heuristic":
                    self.methods.append(HeuristicMethod(method_config["rules"]))
                elif method_type == "keywords":
                    self.methods.append(KeywordMethod(method_config))
                else:
                    logger.warning(f"Method type {method_type} is disabled - skipping")
                    
            if not self.methods:
                # Fallback to simple heuristic if no valid methods
                logger.warning("No valid methods found, using fallback heuristic")
                self.methods = [HeuristicMethod([{"type": "question_mark"}])]
        else:
            logger.warning(f"Unknown model type: {model_type}, using fallback heuristic")
            self.methods = [HeuristicMethod([{"type": "question_mark"}])]
    
    def is_interested(self, content: Union[str, Dict[str, Any]]) -> bool:
        """
        Check if the agent is interested in the message.
        
        Args:
            content: Either a string message or a Message object
            
        Returns:
            bool: True if any method indicates interest
        """
        # Extract content if a Message object is passed
        if isinstance(content, dict):
            content = content.get("content", "")
            
        # Consider interested if any method indicates interest
        return any(method.is_interested(content) for method in self.methods)

def create_interest_model(agent_config: Dict[str, Any]) -> HybridInterestModel:
    """
    Factory function to create an interest model from agent config.
    
    Args:
        agent_config: Agent configuration from agents.yaml
        
    Returns:
        An initialized interest model
    """
    interest_config = agent_config.get("interest_model", {})
    return HybridInterestModel(interest_config)

def check_agent_interest(content: str, agent_config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Check if an agent is interested in a message.
    
    Args:
        content: The message content to check
        agent_config: Optional agent configuration
        
    Returns:
        bool: True if the agent is interested
    """
    if agent_config and "interest_model" in agent_config:
        model = create_interest_model(agent_config)
        return model.is_interested(content)
    else:
        # Fallback to simple heuristic
        return "?" in content

# Commenting out the main function and remaining torch-based classes
# def main():
#     # Define test sentences
#     test_sentences = [
#         "What is the capital of France?",
#         "I love eating pizza",
#         "Can you help me with my homework?",
#         "The weather is nice today",
#         "How do I solve this math problem?"
#     ]
#     
#     try:
#         # Load model once
#         logger.info("Loading model...")
#         agent_dir = os.path.dirname(os.path.abspath(__file__))
#         model = InterestModel(agent_dir, threshold=0.5)
#         
#         # Test each sentence
#         print("\nTesting interest model predictions:")
#         print("-" * 50)
#         
#         for sentence in test_sentences:
#             result = model.predict(sentence)
#             
#             print(f"\nText: {sentence}")
#             print(f"Score: {result['score']:.4f}")
#             print(f"Is Interested: {result['is_interested']}")
#             print("-" * 50)
#             
#     except Exception as e:
#         print(f"Error testing model: {e}")
#         logger.error(f"Error details: {e}", exc_info=True)
# 
# class InterestModel:
#     """Wrapper class to load and use the trained interest model"""
#     
#     def __init__(self, agent_dir: str, threshold: float = 0.5, device: Optional[str] = None):
#         """
#         Initialize the interest model
#         
#         Args:
#             agent_dir: Directory containing the trained model
#             threshold: Classification threshold
#             device: Device to use for inference
#         """
#         if device is None:
#             device = "cuda" if torch.cuda.is_available() else "cpu"
#         self.device = device
#         
#         # Load model configuration
#         model_dir = os.path.join(agent_dir,"")
#         config_path = os.path.join(model_dir, "config.json")
#         
#         if not os.path.exists(config_path):
#             raise FileNotFoundError(f"Model not found at {config_path}")
#         
#         with open(config_path, "r") as f:
#             self.config = json.load(f)
#         
#         # Load base model
#         logger.info("Loading base model...")
#         self.base_model = SentenceTransformer(self.config["base_model"])
#         
#         # Create and load classification head
#         logger.info("Loading classification head...")
#         self.classification_head = InterestClassificationHead(
#             self.config["embedding_dim"], 
#             dropout_prob=self.config["dropout"]
#         )
#         head_path = os.path.join(model_dir, "classification_head.pt")
#         self.classification_head.load_state_dict(torch.load(head_path, map_location=device))
#         self.classification_head.to(device)
#         self.classification_head.eval()
#         
#         self.threshold = threshold
#         logger.info("Model loaded successfully")
#     
#     def predict(self, text: str) -> Dict[str, Any]:
#         """
#         Predict if a text is of interest
#         
#         Args:
#             text: Text to predict interest for
#             
#         Returns:
#             Dictionary with prediction results
#         """
#         # Get embedding
#         embedding = self.base_model.encode(text, convert_to_tensor=True).to(self.device)
#         
#         # Predict
#         with torch.no_grad():
#             score = self.classification_head(embedding.unsqueeze(0)).item()
#         
#         # Create result
#         prediction = score > self.threshold
#         
#         return {
#             "text": text,
#             "score": score,
#             "threshold": self.threshold,
#             "is_interested": prediction
#         }
# 
# class EmbeddingEngine_old:
#     """
#     Handles text embedding using sentence transformers.
#     """
#     def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
#         self.model = SentenceTransformer(model_name)
#         
#     def embed(self, text: str) -> np.ndarray:
#         """
#         Generate embeddings for the given text.
#         """
#         return self.model.encode(text, convert_to_numpy=True)

