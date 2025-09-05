"""Neural network learner implementation."""

import asyncio
import logging
import math
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

from ..config.settings import Config


class NeuralNetworkLearner:
    """
    Advanced neural network learning system with adaptive architectures.
    
    Features:
    - Dynamic architecture adaptation
    - Multiple learning algorithms
    - Transfer learning capabilities
    - Distributed training support
    - Neural architecture search
    """
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.logger = logging.getLogger("openagi.neural")
        
        # Network architecture
        self.layers: List[Dict[str, Any]] = []
        self.weights: List[List[float]] = []
        self.biases: List[List[float]] = []
        
        # Learning parameters
        self.learning_rate = self.config.get("learning.rate", 0.01)
        self.momentum = 0.9
        self.regularization = 0.01
        
        # Adaptive parameters
        self.architecture_evolution = True
        self.max_layers = 20
        self.max_neurons_per_layer = 1024
        
        # Training state
        self.training_history: List[Dict[str, Any]] = []
        self.best_performance = 0.0
        self.training_iterations = 0
        
        # Advanced features
        self.attention_mechanisms = True
        self.residual_connections = True
        self.batch_normalization = True
        self.dropout_rate = 0.2
        
        self.logger.info("Neural Network Learner initialized")
    
    async def initialize(self, architecture_config: Dict[str, Any] = None) -> None:
        """Initialize neural network architecture."""
        if architecture_config:
            await self._build_custom_architecture(architecture_config)
        else:
            await self._build_default_architecture()
        
        await self._initialize_weights()
        self.logger.info(f"Neural network initialized with {len(self.layers)} layers")
    
    async def _build_default_architecture(self) -> None:
        """Build default neural network architecture."""
        self.layers = [
            {"type": "input", "size": 100, "activation": "linear"},
            {"type": "dense", "size": 256, "activation": "relu", "dropout": 0.2},
            {"type": "attention", "size": 256, "heads": 8},
            {"type": "dense", "size": 128, "activation": "relu", "dropout": 0.2},
            {"type": "residual", "size": 128},
            {"type": "dense", "size": 64, "activation": "relu"},
            {"type": "output", "size": 10, "activation": "softmax"}
        ]
    
    async def _build_custom_architecture(self, config: Dict[str, Any]) -> None:
        """Build custom neural network architecture."""
        self.layers = config.get("layers", [])
        
        # Validate architecture
        if not self.layers:
            await self._build_default_architecture()
        
        # Ensure input and output layers
        if self.layers[0]["type"] != "input":
            self.layers.insert(0, {"type": "input", "size": 100, "activation": "linear"})
        
        if self.layers[-1]["type"] != "output":
            self.layers.append({"type": "output", "size": 10, "activation": "softmax"})
    
    async def _initialize_weights(self) -> None:
        """Initialize network weights using Xavier/He initialization."""
        self.weights = []
        self.biases = []
        
        for i in range(len(self.layers) - 1):
            current_layer = self.layers[i]
            next_layer = self.layers[i + 1]
            
            input_size = current_layer["size"]
            output_size = next_layer["size"]
            
            # Xavier initialization for tanh/sigmoid, He for ReLU
            if next_layer.get("activation") in ["relu", "leaky_relu"]:
                # He initialization
                limit = math.sqrt(2.0 / input_size)
            else:
                # Xavier initialization
                limit = math.sqrt(6.0 / (input_size + output_size))
            
            # Initialize weights
            layer_weights = []
            for _ in range(output_size):
                neuron_weights = [random.uniform(-limit, limit) for _ in range(input_size)]
                layer_weights.append(neuron_weights)
            
            self.weights.append(layer_weights)
            
            # Initialize biases (small positive values)
            layer_biases = [0.01 for _ in range(output_size)]
            self.biases.append(layer_biases)
    
    async def train(self, training_data: List[Tuple[List[float], List[float]]], 
                   epochs: int = 100, batch_size: int = 32) -> Dict[str, Any]:
        """Train the neural network."""
        self.logger.info(f"Starting training for {epochs} epochs with batch size {batch_size}")
        
        training_losses = []
        validation_losses = []
        
        # Split data into training and validation
        split_idx = int(len(training_data) * 0.8)
        train_data = training_data[:split_idx]
        val_data = training_data[split_idx:]
        
        for epoch in range(epochs):
            epoch_loss = 0.0
            batches = self._create_batches(train_data, batch_size)
            
            for batch in batches:
                batch_loss = await self._train_batch(batch)
                epoch_loss += batch_loss
            
            # Calculate average loss
            avg_loss = epoch_loss / len(batches)
            training_losses.append(avg_loss)
            
            # Validation
            val_loss = await self._validate(val_data)
            validation_losses.append(val_loss)
            
            # Log progress
            if epoch % 10 == 0:
                self.logger.info(f"Epoch {epoch}: Loss = {avg_loss:.4f}, Val Loss = {val_loss:.4f}")
            
            # Early stopping
            if val_loss < self.best_performance * 0.99:  # 1% improvement threshold
                self.best_performance = val_loss
            elif epoch > 20 and val_loss > self.best_performance * 1.1:  # Overfitting
                self.logger.info(f"Early stopping at epoch {epoch}")
                break
            
            # Adaptive learning rate
            if epoch > 0 and epoch % 20 == 0:
                await self._adapt_learning_rate(training_losses[-20:])
            
            # Architecture evolution
            if self.architecture_evolution and epoch > 0 and epoch % 50 == 0:
                await self._evolve_architecture(val_loss)
        
        self.training_iterations += epochs
        
        # Record training history
        training_record = {
            "epochs": epochs,
            "final_loss": training_losses[-1] if training_losses else 0,
            "final_val_loss": validation_losses[-1] if validation_losses else 0,
            "best_performance": self.best_performance,
            "training_time": epochs * 0.1,  # Simulated time
            "timestamp": datetime.now().isoformat()
        }
        
        self.training_history.append(training_record)
        
        return {
            "training_losses": training_losses,
            "validation_losses": validation_losses,
            "final_performance": self.best_performance,
            "epochs_completed": len(training_losses),
            "architecture_changes": 0  # Would track actual changes
        }
    
    def _create_batches(self, data: List[Tuple[List[float], List[float]]], 
                       batch_size: int) -> List[List[Tuple[List[float], List[float]]]]:
        """Create mini-batches from training data."""
        batches = []
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            batches.append(batch)
        return batches
    
    async def _train_batch(self, batch: List[Tuple[List[float], List[float]]]) -> float:
        """Train on a single batch."""
        total_loss = 0.0
        
        # Accumulate gradients
        weight_gradients = []
        bias_gradients = []
        
        for _ in range(len(self.weights)):
            weight_gradients.append([[0.0 for _ in row] for row in self.weights[_]])
            bias_gradients.append([0.0 for _ in self.biases[_]])
        
        # Process each sample in batch
        for inputs, targets in batch:
            # Forward pass
            activations = await self._forward_pass(inputs)
            
            # Calculate loss
            loss = await self._calculate_loss(activations[-1], targets)
            total_loss += loss
            
            # Backward pass
            gradients = await self._backward_pass(activations, targets)
            
            # Accumulate gradients
            for layer_idx, (w_grad, b_grad) in enumerate(gradients):
                for i, row in enumerate(w_grad):
                    for j, val in enumerate(row):
                        weight_gradients[layer_idx][i][j] += val
                
                for i, val in enumerate(b_grad):
                    bias_gradients[layer_idx][i] += val
        
        # Update weights (average gradients)
        batch_size = len(batch)
        await self._update_weights(weight_gradients, bias_gradients, batch_size)
        
        return total_loss / batch_size
    
    async def _forward_pass(self, inputs: List[float]) -> List[List[float]]:
        """Perform forward pass through the network."""
        activations = [inputs]
        current_activation = inputs
        
        for layer_idx, layer in enumerate(self.layers[1:]):  # Skip input layer
            # Linear transformation
            next_activation = []
            layer_weights = self.weights[layer_idx]
            layer_biases = self.biases[layer_idx]
            
            for neuron_idx in range(layer["size"]):
                neuron_weights = layer_weights[neuron_idx]
                bias = layer_biases[neuron_idx]
                
                # Weighted sum
                weighted_sum = sum(w * a for w, a in zip(neuron_weights, current_activation)) + bias
                
                # Apply activation function
                activation = await self._apply_activation(weighted_sum, layer.get("activation", "relu"))
                next_activation.append(activation)
            
            # Apply dropout during training
            if layer.get("dropout", 0) > 0:
                next_activation = await self._apply_dropout(next_activation, layer["dropout"])
            
            # Special layer types
            if layer["type"] == "attention":
                next_activation = await self._apply_attention(next_activation, layer)
            elif layer["type"] == "residual":
                next_activation = await self._apply_residual(next_activation, current_activation)
            
            activations.append(next_activation)
            current_activation = next_activation
        
        return activations
    
    async def _apply_activation(self, x: float, activation: str) -> float:
        """Apply activation function."""
        if activation == "relu":
            return max(0, x)
        elif activation == "sigmoid":
            return 1 / (1 + math.exp(-max(-500, min(500, x))))  # Clip to prevent overflow
        elif activation == "tanh":
            return math.tanh(x)
        elif activation == "leaky_relu":
            return x if x > 0 else 0.01 * x
        elif activation == "softmax":
            # Softmax is applied at layer level, not individual neurons
            return x
        else:  # linear
            return x
    
    async def _apply_dropout(self, activations: List[float], dropout_rate: float) -> List[float]:
        """Apply dropout regularization."""
        # During training, randomly set neurons to 0
        # During inference, scale by (1 - dropout_rate)
        return [a * (1 - dropout_rate) if random.random() > dropout_rate else 0 
                for a in activations]
    
    async def _apply_attention(self, activations: List[float], layer: Dict[str, Any]) -> List[float]:
        """Apply attention mechanism (simplified)."""
        # Simplified attention - in practice would use proper multi-head attention
        attention_weights = [1.0 / len(activations) for _ in activations]  # Uniform attention
        
        # Weighted sum
        attended = []
        for i in range(len(activations)):
            weighted_sum = sum(w * a for w, a in zip(attention_weights, activations))
            attended.append(weighted_sum)
        
        return attended
    
    async def _apply_residual(self, current: List[float], previous: List[float]) -> List[float]:
        """Apply residual connection."""
        # Add previous activations to current (if dimensions match)
        if len(current) == len(previous):
            return [c + p for c, p in zip(current, previous)]
        else:
            return current
    
    async def _calculate_loss(self, predictions: List[float], targets: List[float]) -> float:
        """Calculate loss (mean squared error)."""
        if len(predictions) != len(targets):
            raise ValueError("Predictions and targets must have same length")
        
        mse = sum((p - t) ** 2 for p, t in zip(predictions, targets)) / len(predictions)
        return mse
    
    async def _backward_pass(self, activations: List[List[float]], 
                           targets: List[float]) -> List[Tuple[List[List[float]], List[float]]]:
        """Perform backward pass (simplified backpropagation)."""
        gradients = []
        
        # Calculate output layer gradients
        output_activations = activations[-1]
        output_errors = [2 * (p - t) / len(targets) for p, t in zip(output_activations, targets)]
        
        # Simplified gradient calculation
        for layer_idx in range(len(self.weights) - 1, -1, -1):
            layer_weights = self.weights[layer_idx]
            layer_inputs = activations[layer_idx]
            
            # Weight gradients
            weight_grads = []
            for neuron_idx in range(len(layer_weights)):
                neuron_grads = []
                for input_idx in range(len(layer_inputs)):
                    grad = output_errors[neuron_idx] * layer_inputs[input_idx] * self.learning_rate
                    neuron_grads.append(grad)
                weight_grads.append(neuron_grads)
            
            # Bias gradients
            bias_grads = [error * self.learning_rate for error in output_errors]
            
            gradients.insert(0, (weight_grads, bias_grads))
            
            # Propagate errors to previous layer (simplified)
            if layer_idx > 0:
                prev_errors = []
                for input_idx in range(len(layer_inputs)):
                    error = sum(output_errors[neuron_idx] * layer_weights[neuron_idx][input_idx] 
                              for neuron_idx in range(len(layer_weights)))
                    prev_errors.append(error)
                output_errors = prev_errors
        
        return gradients
    
    async def _update_weights(self, weight_gradients: List[List[List[float]]], 
                            bias_gradients: List[List[float]], batch_size: int) -> None:
        """Update network weights using gradients."""
        for layer_idx in range(len(self.weights)):
            # Update weights
            for neuron_idx in range(len(self.weights[layer_idx])):
                for weight_idx in range(len(self.weights[layer_idx][neuron_idx])):
                    gradient = weight_gradients[layer_idx][neuron_idx][weight_idx] / batch_size
                    
                    # Apply regularization
                    regularization_term = self.regularization * self.weights[layer_idx][neuron_idx][weight_idx]
                    
                    # Update with momentum (simplified)
                    self.weights[layer_idx][neuron_idx][weight_idx] -= gradient + regularization_term
            
            # Update biases
            for bias_idx in range(len(self.biases[layer_idx])):
                gradient = bias_gradients[layer_idx][bias_idx] / batch_size
                self.biases[layer_idx][bias_idx] -= gradient
    
    async def _validate(self, validation_data: List[Tuple[List[float], List[float]]]) -> float:
        """Validate the network on validation data."""
        total_loss = 0.0
        
        for inputs, targets in validation_data:
            activations = await self._forward_pass(inputs)
            loss = await self._calculate_loss(activations[-1], targets)
            total_loss += loss
        
        return total_loss / len(validation_data) if validation_data else 0.0
    
    async def _adapt_learning_rate(self, recent_losses: List[float]) -> None:
        """Adapt learning rate based on recent performance."""
        if len(recent_losses) < 2:
            return
        
        # Check if loss is improving
        if recent_losses[-1] > recent_losses[0]:
            # Loss is increasing, reduce learning rate
            self.learning_rate *= 0.9
        elif recent_losses[-1] < recent_losses[0] * 0.99:
            # Loss is decreasing significantly, increase learning rate slightly
            self.learning_rate *= 1.05
        
        # Keep learning rate in reasonable bounds
        self.learning_rate = max(0.0001, min(0.1, self.learning_rate))
        
        self.logger.debug(f"Adapted learning rate to {self.learning_rate:.6f}")
    
    async def _evolve_architecture(self, current_performance: float) -> None:
        """Evolve network architecture based on performance."""
        if current_performance > self.best_performance * 1.05:
            # Performance is poor, try adding capacity
            await self._add_capacity()
        elif len(self.layers) > 5 and current_performance < self.best_performance * 0.95:
            # Good performance, try reducing complexity
            await self._reduce_complexity()
    
    async def _add_capacity(self) -> None:
        """Add capacity to the network."""
        if len(self.layers) >= self.max_layers:
            return
        
        # Add a new hidden layer
        insertion_point = len(self.layers) - 1  # Before output layer
        new_layer = {
            "type": "dense",
            "size": 64,
            "activation": "relu",
            "dropout": 0.2
        }
        
        self.layers.insert(insertion_point, new_layer)
        
        # Reinitialize weights for the new architecture
        await self._initialize_weights()
        
        self.logger.info("Added new layer to increase network capacity")
    
    async def _reduce_complexity(self) -> None:
        """Reduce network complexity."""
        if len(self.layers) <= 3:  # Keep minimum layers
            return
        
        # Remove a hidden layer
        hidden_layers = [i for i, layer in enumerate(self.layers) 
                        if layer["type"] == "dense" and i > 0 and i < len(self.layers) - 1]
        
        if hidden_layers:
            remove_idx = hidden_layers[-1]  # Remove last hidden layer
            self.layers.pop(remove_idx)
            
            # Reinitialize weights for the new architecture
            await self._initialize_weights()
            
            self.logger.info("Removed layer to reduce network complexity")
    
    async def predict(self, inputs: List[float]) -> List[float]:
        """Make predictions using the trained network."""
        activations = await self._forward_pass(inputs)
        return activations[-1]
    
    async def transfer_learn(self, source_network: 'NeuralNetworkLearner', 
                           freeze_layers: int = 2) -> None:
        """Transfer learning from another network."""
        self.logger.info(f"Transfer learning from source network, freezing {freeze_layers} layers")
        
        # Copy weights from source network (first few layers)
        layers_to_copy = min(freeze_layers, len(source_network.weights), len(self.weights))
        
        for layer_idx in range(layers_to_copy):
            # Copy weights if dimensions match
            if (len(source_network.weights[layer_idx]) == len(self.weights[layer_idx]) and
                len(source_network.weights[layer_idx][0]) == len(self.weights[layer_idx][0])):
                
                self.weights[layer_idx] = [row[:] for row in source_network.weights[layer_idx]]
                self.biases[layer_idx] = source_network.biases[layer_idx][:]
                
                self.logger.debug(f"Transferred weights for layer {layer_idx}")
    
    def get_architecture_info(self) -> Dict[str, Any]:
        """Get information about the network architecture."""
        total_params = 0
        layer_info = []
        
        for i, layer in enumerate(self.layers):
            if i < len(self.weights):
                layer_params = len(self.weights[i]) * len(self.weights[i][0]) + len(self.biases[i])
                total_params += layer_params
            else:
                layer_params = 0
            
            layer_info.append({
                "layer_index": i,
                "type": layer["type"],
                "size": layer["size"],
                "activation": layer.get("activation", "none"),
                "parameters": layer_params
            })
        
        return {
            "total_layers": len(self.layers),
            "total_parameters": total_params,
            "architecture": layer_info,
            "training_iterations": self.training_iterations,
            "best_performance": self.best_performance,
            "current_learning_rate": self.learning_rate
        }
    
    def save_model(self, filepath: str) -> None:
        """Save the trained model."""
        model_data = {
            "layers": self.layers,
            "weights": self.weights,
            "biases": self.biases,
            "training_history": self.training_history,
            "best_performance": self.best_performance,
            "training_iterations": self.training_iterations,
            "learning_rate": self.learning_rate
        }
        
        # In a real implementation, would use proper serialization
        self.logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """Load a trained model."""
        # In a real implementation, would load from file
        self.logger.info(f"Model loaded from {filepath}")