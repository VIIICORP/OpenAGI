"""
Example: Plugin Development

This example shows how to create custom plugins for OpenAGI
to extend its capabilities with new AI features.
"""

import asyncio
from typing import Dict, Any
from openagi.plugins.manager import Plugin, PluginManager
from openagi.config.settings import Config


class AdvancedMathPlugin(Plugin):
    """Advanced mathematical operations plugin."""
    
    name = "advanced_math"
    version = "1.0.0"
    description = "Advanced mathematical computations and analysis"
    capabilities = ["mathematics", "calculations", "statistics", "optimization"]
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute mathematical operations."""
        operation = task.get("operation", "calculate")
        data = task.get("data", {})
        
        if operation == "prime_factorization":
            number = data.get("number", 1)
            factors = self._prime_factors(number)
            return {
                "number": number,
                "prime_factors": factors,
                "is_prime": len(factors) == 1,
                "factor_count": len(factors)
            }
        
        elif operation == "fibonacci":
            n = data.get("n", 10)
            sequence = self._fibonacci_sequence(n)
            return {
                "sequence": sequence,
                "length": len(sequence),
                "golden_ratio_approximation": sequence[-1] / sequence[-2] if len(sequence) > 1 else 0
            }
        
        elif operation == "matrix_operations":
            matrix_a = data.get("matrix_a", [[1, 2], [3, 4]])
            matrix_b = data.get("matrix_b", [[5, 6], [7, 8]])
            
            return {
                "matrix_a": matrix_a,
                "matrix_b": matrix_b,
                "sum": self._matrix_add(matrix_a, matrix_b),
                "product": self._matrix_multiply(matrix_a, matrix_b),
                "determinant_a": self._determinant_2x2(matrix_a),
                "determinant_b": self._determinant_2x2(matrix_b)
            }
        
        else:
            return {"error": f"Unknown operation: {operation}"}
    
    def _prime_factors(self, n: int) -> list:
        """Find prime factors of a number."""
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        return factors
    
    def _fibonacci_sequence(self, n: int) -> list:
        """Generate Fibonacci sequence."""
        if n <= 0:
            return []
        elif n == 1:
            return [0]
        elif n == 2:
            return [0, 1]
        
        sequence = [0, 1]
        for _ in range(2, n):
            sequence.append(sequence[-1] + sequence[-2])
        return sequence
    
    def _matrix_add(self, a: list, b: list) -> list:
        """Add two matrices."""
        if len(a) != len(b) or len(a[0]) != len(b[0]):
            return None
        
        result = []
        for i in range(len(a)):
            row = []
            for j in range(len(a[0])):
                row.append(a[i][j] + b[i][j])
            result.append(row)
        return result
    
    def _matrix_multiply(self, a: list, b: list) -> list:
        """Multiply two matrices."""
        if len(a[0]) != len(b):
            return None
        
        result = []
        for i in range(len(a)):
            row = []
            for j in range(len(b[0])):
                sum_val = 0
                for k in range(len(b)):
                    sum_val += a[i][k] * b[k][j]
                row.append(sum_val)
            result.append(row)
        return result
    
    def _determinant_2x2(self, matrix: list) -> float:
        """Calculate determinant of 2x2 matrix."""
        if len(matrix) != 2 or len(matrix[0]) != 2:
            return 0
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


class WeatherAnalysisPlugin(Plugin):
    """Weather data analysis plugin."""
    
    name = "weather_analysis"
    version = "1.0.0"
    description = "Weather pattern analysis and prediction"
    capabilities = ["weather", "meteorology", "forecasting", "climate_analysis"]
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze weather data."""
        analysis_type = task.get("analysis_type", "temperature_trends")
        data = task.get("data", {})
        
        if analysis_type == "temperature_trends":
            temperatures = data.get("temperatures", [20, 22, 25, 23, 21, 19, 18])
            
            avg_temp = sum(temperatures) / len(temperatures)
            max_temp = max(temperatures)
            min_temp = min(temperatures)
            temp_range = max_temp - min_temp
            
            # Simple trend analysis
            trend = "stable"
            if temperatures[-1] > temperatures[0] + 2:
                trend = "warming"
            elif temperatures[-1] < temperatures[0] - 2:
                trend = "cooling"
            
            return {
                "temperature_data": temperatures,
                "average_temperature": round(avg_temp, 2),
                "max_temperature": max_temp,
                "min_temperature": min_temp,
                "temperature_range": temp_range,
                "trend": trend,
                "volatility": round(temp_range / avg_temp, 3)
            }
        
        elif analysis_type == "precipitation_forecast":
            humidity = data.get("humidity", 65)
            pressure = data.get("pressure", 1013.25)
            temperature = data.get("temperature", 22)
            
            # Simple precipitation probability model
            rain_probability = 0
            if humidity > 80:
                rain_probability += 0.4
            if pressure < 1010:
                rain_probability += 0.3
            if temperature > 25:
                rain_probability += 0.2
            
            rain_probability = min(1.0, rain_probability)
            
            return {
                "humidity": humidity,
                "pressure": pressure,
                "temperature": temperature,
                "rain_probability": round(rain_probability, 2),
                "forecast": "Rain likely" if rain_probability > 0.6 else "Clear skies expected",
                "confidence": 0.75
            }
        
        else:
            return {"error": f"Unknown analysis type: {analysis_type}"}


class CreativeWritingPlugin(Plugin):
    """Creative writing and text generation plugin."""
    
    name = "creative_writing"
    version = "1.0.0"
    description = "Creative text generation and writing assistance"
    capabilities = ["creativity", "writing", "text_generation", "storytelling"]
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate creative content."""
        content_type = task.get("content_type", "story")
        data = task.get("data", {})
        
        if content_type == "story":
            theme = data.get("theme", "adventure")
            length = data.get("length", "short")
            
            stories = {
                "adventure": "In a distant land filled with mysteries, a brave explorer discovered an ancient artifact that would change the course of history...",
                "mystery": "The old mansion had been empty for decades, but tonight, strange lights flickered in the windows, and Detective Morgan knew the case was far from closed...",
                "romance": "Under the starlit sky, two souls met by chance at a small café, unaware that their lives were about to intertwine in the most beautiful way...",
                "science_fiction": "The year was 2157, and humanity had just received its first message from an alien civilization. Dr. Chen stared at the decoded text with wonder and fear..."
            }
            
            story = stories.get(theme, "Once upon a time, in a place far away, something extraordinary happened...")
            
            return {
                "theme": theme,
                "length": length,
                "story": story,
                "word_count": len(story.split()),
                "estimated_reading_time": f"{len(story.split()) // 200 + 1} minutes",
                "creativity_score": 0.8
            }
        
        elif content_type == "poem":
            style = data.get("style", "free_verse")
            topic = data.get("topic", "nature")
            
            poems = {
                "nature": "Whispering winds through ancient trees,\nDancing leaves in morning breeze,\nSunlight paints the forest floor,\nNature's beauty evermore.",
                "technology": "Silicon dreams and digital streams,\nCode that flows like rivers gleams,\nIn virtual worlds we find our way,\nTomorrow's born from yesterday.",
                "love": "Hearts that beat in perfect time,\nSouls that dance in pantomime,\nLove's sweet song fills the air,\nTwo hearts, one dream to share."
            }
            
            poem = poems.get(topic, "Words flow like water,\nThoughts take flight,\nPoetry illuminates\nThe darkest night.")
            
            return {
                "style": style,
                "topic": topic,
                "poem": poem,
                "line_count": len(poem.split('\n')),
                "meter": "varied",
                "artistic_score": 0.85
            }
        
        else:
            return {"error": f"Unknown content type: {content_type}"}


async def plugin_example():
    """Demonstrate custom plugin development and usage."""
    print("🔌 OpenAGI Plugin Development Example")
    print("=" * 50)
    
    # Initialize plugin manager
    config = Config()
    plugin_manager = PluginManager(config)
    
    # Register custom plugins
    math_plugin = AdvancedMathPlugin()
    weather_plugin = WeatherAnalysisPlugin()
    writing_plugin = CreativeWritingPlugin()
    
    await plugin_manager.register_plugin(math_plugin)
    await plugin_manager.register_plugin(weather_plugin)
    await plugin_manager.register_plugin(writing_plugin)
    
    print(f"📊 Registered {len(plugin_manager.plugins)} custom plugins")
    
    # Test Math Plugin
    print("\n1. Testing Advanced Math Plugin...")
    math_task = {
        "operation": "fibonacci",
        "data": {"n": 10}
    }
    
    result = await plugin_manager.execute_with_plugin("advanced_math", math_task)
    print(f"   📈 Fibonacci Result: {result['result']['sequence']}")
    print(f"   🔢 Golden Ratio Approx: {result['result']['golden_ratio_approximation']:.4f}")
    
    # Test Weather Plugin
    print("\n2. Testing Weather Analysis Plugin...")
    weather_task = {
        "analysis_type": "precipitation_forecast",
        "data": {
            "humidity": 85,
            "pressure": 1008.5,
            "temperature": 28
        }
    }
    
    result = await plugin_manager.execute_with_plugin("weather_analysis", weather_task)
    print(f"   🌧️  Rain Probability: {result['result']['rain_probability']*100:.0f}%")
    print(f"   📡 Forecast: {result['result']['forecast']}")
    
    # Test Creative Writing Plugin
    print("\n3. Testing Creative Writing Plugin...")
    writing_task = {
        "content_type": "poem",
        "data": {
            "style": "free_verse",
            "topic": "technology"
        }
    }
    
    result = await plugin_manager.execute_with_plugin("creative_writing", writing_task)
    print("   ✍️  Generated Poem:")
    print("   " + result['result']['poem'].replace('\n', '\n   '))
    print(f"   🎨 Artistic Score: {result['result']['artistic_score']}")
    
    # Show plugin statistics
    print("\n4. Plugin Statistics...")
    stats = plugin_manager.get_plugin_stats()
    print(f"   🔌 Total Plugins: {stats['total_plugins']}")
    print("   📊 Capabilities:")
    for capability, count in sorted(stats['capabilities_distribution'].items()):
        print(f"      {capability}: {count} plugins")
    
    # Cleanup
    await plugin_manager.cleanup()
    print("\n✅ Plugin example completed!")


if __name__ == "__main__":
    asyncio.run(plugin_example())