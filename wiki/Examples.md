# Examples and Use Cases

Real-world examples and code samples for OpenAGI's 14,000+ features.

## 📚 Table of Contents

- [Quick Examples](#quick-examples)
- [Text Analysis](#text-analysis)
- [Computer Vision](#computer-vision)
- [Machine Learning](#machine-learning)
- [Data Analysis](#data-analysis)
- [Automation](#automation)
- [Complete Applications](#complete-applications)

## ⚡ Quick Examples

### Basic Feature Usage

```python
from openagi import OpenAGI

# Initialize OpenAGI
agi = OpenAGI()

# Text sentiment analysis
sentiment = agi.run('text_sentiment_analysis', text="I love this product!")
print(f"Sentiment: {sentiment['sentiment']} ({sentiment['confidence']:.2%})")

# Image object detection
objects = agi.run('image_object_detection', image_path="photo.jpg")
print(f"Found {len(objects['objects'])} objects")

# Machine learning model training
model = agi.run('ml_train_classifier', 
                data=X_train, target=y_train, algorithm="random_forest")
print(f"Model trained with {model['accuracy']:.2%} accuracy")
```

### Feature Chaining

```python
# Chain multiple features together
text = "The new iPhone 15 Pro is amazing! Apple has outdone themselves."

# Clean the text
cleaned = agi.run('text_cleaner', text=text, remove_punctuation=False)

# Extract entities
entities = agi.run('text_entity_extraction', text=cleaned)

# Analyze sentiment
sentiment = agi.run('text_sentiment_analysis', text=cleaned)

# Extract keywords
keywords = agi.run('text_keyword_extraction', text=cleaned, num_keywords=5)

print(f"Entities: {entities['entities']}")
print(f"Sentiment: {sentiment['sentiment']}")
print(f"Keywords: {[kw['word'] for kw in keywords['keywords']]}")
```

## 📝 Text Analysis

### Social Media Monitoring

```python
def analyze_social_posts(posts):
    """Analyze multiple social media posts."""
    results = []
    
    for post in posts:
        analysis = {
            'post': post,
            'sentiment': agi.run('text_sentiment_analysis', text=post),
            'entities': agi.run('text_entity_extraction', text=post),
            'keywords': agi.run('text_keyword_extraction', text=post, num_keywords=3),
            'language': agi.run('text_language_detection', text=post)
        }
        results.append(analysis)
    
    return results

# Example usage
posts = [
    "Just tried the new restaurant downtown. Food was incredible! 🍕",
    "Terrible customer service at @CompanyX. Very disappointed.",
    "Beautiful sunset at Central Park today #NYC #photography"
]

analyses = analyze_social_posts(posts)

for analysis in analyses:
    print(f"Post: {analysis['post']}")
    print(f"Sentiment: {analysis['sentiment']['sentiment']}")
    print(f"Entities: {[e['text'] for e in analysis['entities']['entities']]}")
    print("-" * 50)
```

### Content Moderation System

```python
def moderate_content(text):
    """Comprehensive content moderation."""
    
    # Basic analysis
    sentiment = agi.run('text_sentiment_analysis', text=text)
    language = agi.run('text_language_detection', text=text)
    
    # Toxicity detection (if available)
    try:
        toxicity = agi.run('text_toxicity_detection', text=text)
        is_toxic = toxicity['is_toxic']
        toxicity_score = toxicity['score']
    except:
        is_toxic = False
        toxicity_score = 0.0
    
    # Spam detection
    try:
        spam = agi.run('text_spam_detection', text=text)
        is_spam = spam['is_spam']
        spam_score = spam['confidence']
    except:
        is_spam = False
        spam_score = 0.0
    
    # Content classification
    try:
        classification = agi.run('text_topic_classification', text=text)
        topic = classification['topic']
        topic_confidence = classification['confidence']
    except:
        topic = "unknown"
        topic_confidence = 0.0
    
    # Determine if content should be approved
    should_approve = (
        not is_toxic and 
        not is_spam and 
        sentiment['sentiment'] != 'negative' or sentiment['confidence'] < 0.8
    )
    
    return {
        'approved': should_approve,
        'sentiment': sentiment,
        'language': language['language'],
        'toxic': is_toxic,
        'toxicity_score': toxicity_score,
        'spam': is_spam,
        'spam_score': spam_score,
        'topic': topic,
        'topic_confidence': topic_confidence,
        'reason': 'Auto-approved' if should_approve else 'Flagged for review'
    }

# Example usage
comments = [
    "Great article! Thanks for sharing.",
    "This is complete garbage and waste of time!",
    "Buy cheap watches now! Click here for amazing deals!"
]

for comment in comments:
    result = moderate_content(comment)
    print(f"Comment: {comment}")
    print(f"Status: {'✅ Approved' if result['approved'] else '❌ Flagged'}")
    print(f"Reason: {result['reason']}")
    print()
```

### Document Summarization Service

```python
def create_document_summary(file_path, summary_length="medium"):
    """Create comprehensive document summary."""
    
    # Read document
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Configure summary length
    length_map = {
        "short": 50,
        "medium": 150,
        "long": 300
    }
    max_length = length_map.get(summary_length, 150)
    
    # Generate summary
    summary = agi.run('text_summarization', text=content, max_length=max_length)
    
    # Extract key information
    entities = agi.run('text_entity_extraction', text=content)
    keywords = agi.run('text_keyword_extraction', text=content, num_keywords=10)
    sentiment = agi.run('text_sentiment_analysis', text=content)
    
    # Create structured summary
    result = {
        'document': file_path,
        'word_count': len(content.split()),
        'character_count': len(content),
        'summary': summary['summary'],
        'key_entities': {
            'people': [e['text'] for e in entities['entities'] if e['type'] == 'PERSON'],
            'organizations': [e['text'] for e in entities['entities'] if e['type'] == 'ORG'],
            'locations': [e['text'] for e in entities['entities'] if e['type'] == 'GPE']
        },
        'top_keywords': [kw['word'] for kw in keywords['keywords'][:5]],
        'overall_sentiment': sentiment['sentiment'],
        'sentiment_confidence': sentiment['confidence']
    }
    
    return result

# Example usage
summary = create_document_summary('research_paper.txt', 'medium')

print(f"📄 Document Summary: {summary['document']}")
print(f"📊 Stats: {summary['word_count']} words, {summary['character_count']} characters")
print(f"📝 Summary: {summary['summary']}")
print(f"👥 People: {', '.join(summary['key_entities']['people'][:3])}")
print(f"🏢 Organizations: {', '.join(summary['key_entities']['organizations'][:3])}")
print(f"🔤 Keywords: {', '.join(summary['top_keywords'])}")
print(f"😊 Sentiment: {summary['overall_sentiment']} ({summary['sentiment_confidence']:.1%})")
```

## 🖼️ Computer Vision

### Image Analysis Pipeline

```python
def analyze_image_comprehensive(image_path):
    """Comprehensive image analysis."""
    
    results = {}
    
    # Basic image info
    from PIL import Image
    img = Image.open(image_path)
    results['image_info'] = {
        'size': img.size,
        'format': img.format,
        'mode': img.mode
    }
    
    # Object detection
    objects = agi.run('image_object_detection', image_path=image_path)
    results['objects'] = objects['objects']
    
    # Face detection
    try:
        faces = agi.run('image_face_detection', image_path=image_path)
        results['faces'] = faces['faces']
    except:
        results['faces'] = []
    
    # Scene classification
    try:
        scene = agi.run('image_scene_classification', image_path=image_path)
        results['scene'] = scene['scene']
        results['scene_confidence'] = scene['confidence']
    except:
        results['scene'] = 'unknown'
        results['scene_confidence'] = 0.0
    
    # Color analysis
    try:
        colors = agi.run('image_dominant_colors', image_path=image_path, num_colors=5)
        results['dominant_colors'] = colors['colors']
    except:
        results['dominant_colors'] = []
    
    # Quality assessment
    try:
        quality = agi.run('image_quality_assessment', image_path=image_path)
        results['quality_score'] = quality['score']
    except:
        results['quality_score'] = 0.0
    
    return results

# Example usage
analysis = analyze_image_comprehensive('vacation_photo.jpg')

print(f"📸 Image: {analysis['image_info']['size']} ({analysis['image_info']['format']})")
print(f"🎬 Scene: {analysis['scene']} ({analysis['scene_confidence']:.1%})")
print(f"👥 Faces detected: {len(analysis['faces'])}")
print(f"🎯 Objects found: {len(analysis['objects'])}")

for obj in analysis['objects'][:5]:
    print(f"   • {obj['class']} ({obj['confidence']:.1%})")

print(f"🎨 Dominant colors: {len(analysis['dominant_colors'])}")
print(f"⭐ Quality score: {analysis['quality_score']:.2f}")
```

### Batch Image Processing

```python
import os
from pathlib import Path

def process_image_batch(input_dir, output_dir, operations):
    """Process multiple images with specified operations."""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Supported image formats
    image_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    
    results = []
    
    for image_file in input_path.iterdir():
        if image_file.suffix.lower() in image_formats:
            print(f"Processing: {image_file.name}")
            
            result = {'file': image_file.name, 'operations': {}}
            
            for operation in operations:
                try:
                    if operation == 'resize':
                        output = agi.run('image_resize', 
                                       image_path=str(image_file),
                                       width=800, height=600)
                        # Save resized image
                        output_file = output_path / f"resized_{image_file.name}"
                        # Implementation would save the image
                        result['operations']['resize'] = 'success'
                    
                    elif operation == 'enhance':
                        output = agi.run('image_enhance',
                                       image_path=str(image_file),
                                       brightness=1.1, contrast=1.1)
                        result['operations']['enhance'] = 'success'
                    
                    elif operation == 'detect_objects':
                        objects = agi.run('image_object_detection',
                                        image_path=str(image_file))
                        result['operations']['objects'] = len(objects['objects'])
                    
                    elif operation == 'extract_text':
                        text = agi.run('image_ocr', image_path=str(image_file))
                        result['operations']['text_length'] = len(text['text'])
                
                except Exception as e:
                    result['operations'][operation] = f'error: {str(e)}'
            
            results.append(result)
    
    return results

# Example usage
operations = ['resize', 'enhance', 'detect_objects', 'extract_text']
results = process_image_batch('./input_images', './output_images', operations)

for result in results:
    print(f"📸 {result['file']}:")
    for op, status in result['operations'].items():
        print(f"   • {op}: {status}")
```

## 🤖 Machine Learning

### Automated ML Pipeline

```python
import pandas as pd
from sklearn.model_selection import train_test_split

def create_ml_pipeline(data_path, target_column, problem_type='classification'):
    """Create automated machine learning pipeline."""
    
    # Load data
    data = pd.read_csv(data_path)
    X = data.drop(columns=[target_column])
    y = data[target_column]
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    results = {}
    
    # Data preprocessing
    print("🔧 Preprocessing data...")
    
    # Handle missing values
    if X_train.isnull().sum().sum() > 0:
        X_train_clean = agi.run('ml_missing_value_imputation', 
                               data=X_train, method='median')
        X_test_clean = agi.run('ml_missing_value_imputation',
                              data=X_test, method='median')
    else:
        X_train_clean = X_train
        X_test_clean = X_test
    
    # Feature scaling
    X_train_scaled = agi.run('ml_feature_scaling', 
                            data=X_train_clean, method='standard')
    X_test_scaled = agi.run('ml_feature_scaling',
                           data=X_test_clean, method='standard')
    
    # Feature selection
    if X_train_scaled.shape[1] > 10:
        X_train_selected = agi.run('ml_feature_selection',
                                  data=X_train_scaled, target=y_train,
                                  method='mutual_info', k=10)
        X_test_selected = X_test_scaled[X_train_selected.columns]
    else:
        X_train_selected = X_train_scaled
        X_test_selected = X_test_scaled
    
    results['preprocessing'] = {
        'original_features': X_train.shape[1],
        'selected_features': X_train_selected.shape[1],
        'training_samples': X_train_selected.shape[0]
    }
    
    # Model training
    print("🎯 Training models...")
    
    algorithms = ['random_forest', 'svm', 'gradient_boosting']
    if problem_type == 'regression':
        algorithms = ['random_forest_regressor', 'svm_regressor', 'linear_regression']
    
    models = {}
    for algorithm in algorithms:
        print(f"   Training {algorithm}...")
        
        if problem_type == 'classification':
            model = agi.run('ml_train_classifier',
                           data=X_train_selected, target=y_train,
                           algorithm=algorithm)
        else:
            model = agi.run('ml_train_regressor',
                           data=X_train_selected, target=y_train,
                           algorithm=algorithm)
        
        # Make predictions
        predictions = agi.run('ml_predict',
                             model=model, data=X_test_selected)
        
        # Evaluate model
        if problem_type == 'classification':
            evaluation = agi.run('ml_evaluate_classifier',
                                model=model, test_data=X_test_selected,
                                test_labels=y_test)
        else:
            evaluation = agi.run('ml_evaluate_regressor',
                                model=model, test_data=X_test_selected,
                                test_labels=y_test)
        
        models[algorithm] = {
            'model': model,
            'predictions': predictions,
            'evaluation': evaluation
        }
    
    # Select best model
    if problem_type == 'classification':
        best_algorithm = max(models.keys(), 
                           key=lambda x: models[x]['evaluation']['accuracy'])
        best_metric = 'accuracy'
    else:
        best_algorithm = min(models.keys(),
                           key=lambda x: models[x]['evaluation']['mse'])
        best_metric = 'mse'
    
    results['models'] = models
    results['best_model'] = best_algorithm
    results['best_score'] = models[best_algorithm]['evaluation'][best_metric]
    
    return results

# Example usage
pipeline_results = create_ml_pipeline('customer_data.csv', 'churn', 'classification')

print(f"📊 Dataset: {pipeline_results['preprocessing']['training_samples']} samples")
print(f"🔧 Features: {pipeline_results['preprocessing']['selected_features']}")
print(f"🏆 Best model: {pipeline_results['best_model']}")
print(f"⭐ Best score: {pipeline_results['best_score']:.3f}")

for algorithm, results in pipeline_results['models'].items():
    accuracy = results['evaluation']['accuracy']
    print(f"   {algorithm}: {accuracy:.3f}")
```

### Anomaly Detection System

```python
def detect_anomalies(data, method='isolation_forest', contamination=0.1):
    """Detect anomalies in data using various methods."""
    
    results = {}
    
    # Preprocessing
    print("🔧 Preprocessing data...")
    data_scaled = agi.run('ml_feature_scaling', data=data, method='standard')
    
    # Apply anomaly detection
    print(f"🔍 Detecting anomalies using {method}...")
    
    if method == 'isolation_forest':
        anomalies = agi.run('ml_isolation_forest',
                           data=data_scaled,
                           contamination=contamination)
    elif method == 'one_class_svm':
        anomalies = agi.run('ml_one_class_svm',
                           data=data_scaled,
                           nu=contamination)
    elif method == 'local_outlier_factor':
        anomalies = agi.run('ml_local_outlier_factor',
                           data=data_scaled,
                           contamination=contamination)
    
    # Analyze results
    anomaly_indices = anomalies['anomaly_indices']
    anomaly_scores = anomalies['anomaly_scores']
    
    results['total_samples'] = len(data)
    results['anomalies_detected'] = len(anomaly_indices)
    results['anomaly_rate'] = len(anomaly_indices) / len(data)
    results['anomaly_indices'] = anomaly_indices
    results['anomaly_scores'] = anomaly_scores
    
    # Statistical analysis of anomalies
    if len(anomaly_indices) > 0:
        anomaly_data = data.iloc[anomaly_indices]
        normal_data = data.drop(anomaly_indices)
        
        # Compare distributions
        comparison = agi.run('data_distribution_comparison',
                           data1=normal_data, data2=anomaly_data)
        results['distribution_comparison'] = comparison
    
    return results

# Example usage
import numpy as np
import pandas as pd

# Generate sample data with anomalies
np.random.seed(42)
normal_data = np.random.normal(0, 1, (1000, 5))
anomaly_data = np.random.normal(3, 1, (50, 5))  # Shifted anomalies
data = pd.DataFrame(np.vstack([normal_data, anomaly_data]))

detection_results = detect_anomalies(data, method='isolation_forest')

print(f"📊 Total samples: {detection_results['total_samples']}")
print(f"🚨 Anomalies detected: {detection_results['anomalies_detected']}")
print(f"📈 Anomaly rate: {detection_results['anomaly_rate']:.2%}")
```

## 📊 Data Analysis

### Business Intelligence Dashboard

```python
def create_business_report(sales_data):
    """Create comprehensive business intelligence report."""
    
    report = {}
    
    # Descriptive statistics
    print("📊 Calculating descriptive statistics...")
    stats = agi.run('data_descriptive_stats', data=sales_data)
    report['statistics'] = stats
    
    # Trend analysis
    print("📈 Analyzing trends...")
    if 'date' in sales_data.columns:
        trends = agi.run('data_trend_analysis', 
                        data=sales_data['revenue'],
                        dates=sales_data['date'])
        report['trends'] = trends
    
    # Correlation analysis
    print("🔗 Analyzing correlations...")
    numeric_columns = sales_data.select_dtypes(include=[np.number]).columns
    if len(numeric_columns) > 1:
        correlations = agi.run('data_correlation_analysis',
                              data=sales_data[numeric_columns])
        report['correlations'] = correlations
    
    # Customer segmentation
    if 'customer_id' in sales_data.columns:
        print("👥 Performing customer segmentation...")
        customer_features = sales_data.groupby('customer_id').agg({
            'revenue': ['sum', 'mean', 'count'],
            'date': ['min', 'max']
        }).reset_index()
        
        segments = agi.run('ml_kmeans_clustering',
                          data=customer_features.select_dtypes(include=[np.number]),
                          n_clusters=4)
        report['customer_segments'] = segments
    
    # Forecasting
    if 'date' in sales_data.columns and len(sales_data) > 30:
        print("🔮 Generating forecasts...")
        forecast = agi.run('data_arima_forecasting',
                          data=sales_data['revenue'],
                          periods=30)
        report['forecast'] = forecast
    
    # Visualizations
    print("📊 Creating visualizations...")
    
    # Revenue trend
    if 'date' in sales_data.columns:
        trend_plot = agi.run('data_line_plot',
                           x=sales_data['date'],
                           y=sales_data['revenue'],
                           title='Revenue Trend Over Time')
        report['visualizations'] = {'trend_plot': trend_plot}
    
    # Revenue by category (if applicable)
    if 'category' in sales_data.columns:
        category_plot = agi.run('data_bar_chart',
                               data=sales_data.groupby('category')['revenue'].sum(),
                               title='Revenue by Category')
        report['visualizations']['category_plot'] = category_plot
    
    return report

# Example usage
sample_data = pd.DataFrame({
    'date': pd.date_range('2023-01-01', periods=365),
    'revenue': np.random.normal(10000, 2000, 365),
    'customer_id': np.random.randint(1, 1000, 365),
    'category': np.random.choice(['A', 'B', 'C'], 365)
})

business_report = create_business_report(sample_data)

print("📊 BUSINESS INTELLIGENCE REPORT")
print("=" * 40)
print(f"📈 Average daily revenue: ${business_report['statistics']['mean']:.2f}")
print(f"📊 Revenue standard deviation: ${business_report['statistics']['std']:.2f}")

if 'trends' in business_report:
    print(f"📈 Trend direction: {business_report['trends']['direction']}")

if 'customer_segments' in business_report:
    print(f"👥 Customer segments identified: {business_report['customer_segments']['n_clusters']}")
```

### Time Series Analysis

```python
def analyze_time_series(data, date_column, value_column):
    """Comprehensive time series analysis."""
    
    # Prepare data
    ts_data = data.set_index(date_column)[value_column]
    
    analysis = {}
    
    # Basic statistics
    print("📊 Computing time series statistics...")
    stats = agi.run('data_descriptive_stats', data=ts_data.values)
    analysis['statistics'] = stats
    
    # Decomposition
    print("🔄 Decomposing time series...")
    decomposition = agi.run('data_seasonal_decomposition', data=ts_data)
    analysis['decomposition'] = decomposition
    
    # Stationarity test
    print("📈 Testing stationarity...")
    stationarity = agi.run('data_stationarity_test', data=ts_data)
    analysis['stationarity'] = stationarity
    
    # Anomaly detection
    print("🚨 Detecting anomalies...")
    anomalies = agi.run('data_anomaly_detection', data=ts_data)
    analysis['anomalies'] = anomalies
    
    # Forecasting
    print("🔮 Generating forecasts...")
    
    # ARIMA forecast
    arima_forecast = agi.run('data_arima_forecasting',
                            data=ts_data, periods=30)
    
    # Prophet forecast (if available)
    try:
        prophet_forecast = agi.run('data_prophet_forecasting',
                                  data=ts_data, periods=30)
        analysis['forecasts'] = {
            'arima': arima_forecast,
            'prophet': prophet_forecast
        }
    except:
        analysis['forecasts'] = {'arima': arima_forecast}
    
    # Change point detection
    print("📍 Detecting change points...")
    change_points = agi.run('data_change_point_detection', data=ts_data)
    analysis['change_points'] = change_points
    
    return analysis

# Example usage
dates = pd.date_range('2023-01-01', periods=365, freq='D')
values = np.cumsum(np.random.randn(365)) + 100  # Random walk with drift

ts_data = pd.DataFrame({
    'date': dates,
    'value': values
})

ts_analysis = analyze_time_series(ts_data, 'date', 'value')

print("📊 TIME SERIES ANALYSIS RESULTS")
print("=" * 40)
print(f"📈 Mean value: {ts_analysis['statistics']['mean']:.2f}")
print(f"📊 Trend: {ts_analysis['decomposition']['trend_direction']}")
print(f"🔄 Seasonality: {'Yes' if ts_analysis['decomposition']['has_seasonality'] else 'No'}")
print(f"📈 Stationary: {'Yes' if ts_analysis['stationarity']['is_stationary'] else 'No'}")
print(f"🚨 Anomalies detected: {len(ts_analysis['anomalies']['anomaly_dates'])}")
print(f"📍 Change points: {len(ts_analysis['change_points']['change_points'])}")
```

## ⚡ Automation

### Automated Data Pipeline

```python
import schedule
import time
from datetime import datetime

class DataPipeline:
    """Automated data processing pipeline."""
    
    def __init__(self, config):
        self.agi = OpenAGI()
        self.config = config
        self.pipeline_logs = []
    
    def extract_data(self):
        """Extract data from various sources."""
        print(f"🔄 [{datetime.now()}] Starting data extraction...")
        
        extracted_data = {}
        
        for source in self.config['sources']:
            try:
                if source['type'] == 'api':
                    data = self.agi.run('api_data_extractor',
                                       url=source['url'],
                                       headers=source.get('headers', {}))
                
                elif source['type'] == 'database':
                    data = self.agi.run('database_query',
                                       connection=source['connection'],
                                       query=source['query'])
                
                elif source['type'] == 'file':
                    data = self.agi.run('file_reader',
                                       path=source['path'],
                                       format=source.get('format', 'csv'))
                
                elif source['type'] == 'web_scraping':
                    data = self.agi.run('web_scraper',
                                       url=source['url'],
                                       selectors=source['selectors'])
                
                extracted_data[source['name']] = data
                print(f"✅ Extracted {len(data)} records from {source['name']}")
                
            except Exception as e:
                print(f"❌ Failed to extract from {source['name']}: {e}")
                self.log_error(f"Extraction failed for {source['name']}", str(e))
        
        return extracted_data
    
    def transform_data(self, raw_data):
        """Transform and clean the extracted data."""
        print(f"🔧 [{datetime.now()}] Starting data transformation...")
        
        transformed_data = {}
        
        for name, data in raw_data.items():
            try:
                # Data cleaning
                cleaned = self.agi.run('data_cleaner',
                                      data=data,
                                      remove_duplicates=True,
                                      handle_missing='interpolate')
                
                # Data validation
                validation = self.agi.run('data_validator',
                                         data=cleaned,
                                         schema=self.config.get('schema', {}))
                
                if validation['is_valid']:
                    # Feature engineering
                    if self.config.get('feature_engineering'):
                        engineered = self.agi.run('feature_engineer',
                                                 data=cleaned,
                                                 operations=self.config['feature_engineering'])
                        transformed_data[name] = engineered
                    else:
                        transformed_data[name] = cleaned
                    
                    print(f"✅ Transformed {name}: {len(transformed_data[name])} records")
                else:
                    print(f"❌ Data validation failed for {name}")
                    self.log_error(f"Validation failed for {name}", 
                                  str(validation['errors']))
            
            except Exception as e:
                print(f"❌ Transformation failed for {name}: {e}")
                self.log_error(f"Transformation failed for {name}", str(e))
        
        return transformed_data
    
    def load_data(self, processed_data):
        """Load processed data to destinations."""
        print(f"💾 [{datetime.now()}] Starting data loading...")
        
        for destination in self.config['destinations']:
            try:
                for name, data in processed_data.items():
                    if destination['type'] == 'database':
                        result = self.agi.run('database_insert',
                                             connection=destination['connection'],
                                             table=destination['table'],
                                             data=data)
                    
                    elif destination['type'] == 'file':
                        result = self.agi.run('file_writer',
                                             data=data,
                                             path=f"{destination['path']}/{name}.csv",
                                             format='csv')
                    
                    elif destination['type'] == 'api':
                        result = self.agi.run('api_data_sender',
                                             url=destination['url'],
                                             data=data,
                                             headers=destination.get('headers', {}))
                    
                    print(f"✅ Loaded {name} to {destination['type']}")
            
            except Exception as e:
                print(f"❌ Loading failed to {destination['type']}: {e}")
                self.log_error(f"Loading failed to {destination['type']}", str(e))
    
    def run_pipeline(self):
        """Execute the complete pipeline."""
        start_time = datetime.now()
        print(f"🚀 Pipeline started at {start_time}")
        
        try:
            # ETL process
            raw_data = self.extract_data()
            transformed_data = self.transform_data(raw_data)
            self.load_data(transformed_data)
            
            # Generate report
            self.generate_report(start_time, len(raw_data), len(transformed_data))
            
            # Send notifications
            self.send_notifications("Pipeline completed successfully")
            
        except Exception as e:
            error_msg = f"Pipeline failed: {e}"
            print(f"❌ {error_msg}")
            self.log_error("Pipeline execution", str(e))
            self.send_notifications(error_msg, is_error=True)
    
    def generate_report(self, start_time, input_records, output_records):
        """Generate pipeline execution report."""
        end_time = datetime.now()
        duration = end_time - start_time
        
        report = {
            'start_time': start_time,
            'end_time': end_time,
            'duration': str(duration),
            'input_records': input_records,
            'output_records': output_records,
            'success_rate': output_records / input_records if input_records > 0 else 0,
            'errors': len(self.pipeline_logs)
        }
        
        # Save report
        report_path = f"pipeline_report_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
        import json
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📊 Pipeline report saved to {report_path}")
        return report
    
    def send_notifications(self, message, is_error=False):
        """Send notifications about pipeline status."""
        try:
            if self.config.get('notifications', {}).get('email'):
                self.agi.run('automation_send_email',
                            to=self.config['notifications']['email'],
                            subject=f"Data Pipeline {'Error' if is_error else 'Success'}",
                            body=message)
            
            if self.config.get('notifications', {}).get('slack'):
                self.agi.run('automation_slack_notification',
                            webhook=self.config['notifications']['slack'],
                            message=message,
                            channel='#data-pipeline')
        
        except Exception as e:
            print(f"⚠️ Failed to send notification: {e}")
    
    def log_error(self, operation, error):
        """Log pipeline errors."""
        self.pipeline_logs.append({
            'timestamp': datetime.now(),
            'operation': operation,
            'error': error
        })
    
    def schedule_pipeline(self, schedule_type='daily', time='09:00'):
        """Schedule automated pipeline execution."""
        if schedule_type == 'daily':
            schedule.every().day.at(time).do(self.run_pipeline)
        elif schedule_type == 'hourly':
            schedule.every().hour.do(self.run_pipeline)
        elif schedule_type == 'weekly':
            schedule.every().week.do(self.run_pipeline)
        
        print(f"📅 Pipeline scheduled to run {schedule_type} at {time}")
        
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)

# Example configuration
pipeline_config = {
    'sources': [
        {
            'name': 'sales_api',
            'type': 'api',
            'url': 'https://api.company.com/sales',
            'headers': {'Authorization': 'Bearer token'}
        },
        {
            'name': 'customer_db',
            'type': 'database',
            'connection': 'postgresql://user:pass@localhost:5432/db',
            'query': 'SELECT * FROM customers WHERE updated_at > NOW() - INTERVAL 1 DAY'
        }
    ],
    'destinations': [
        {
            'type': 'database',
            'connection': 'postgresql://user:pass@warehouse:5432/dw',
            'table': 'fact_sales'
        }
    ],
    'feature_engineering': [
        'calculate_revenue',
        'normalize_dates',
        'create_customer_segments'
    ],
    'notifications': {
        'email': 'admin@company.com',
        'slack': 'https://hooks.slack.com/services/...'
    }
}

# Usage
pipeline = DataPipeline(pipeline_config)

# Run once
pipeline.run_pipeline()

# Or schedule for automated execution
# pipeline.schedule_pipeline('daily', '09:00')
```

## 🏗️ Complete Applications

### AI-Powered Content Management System

```python
class AIContentManager:
    """AI-powered content management and optimization system."""
    
    def __init__(self):
        self.agi = OpenAGI()
        self.content_database = {}
    
    def analyze_content(self, content, content_type='article'):
        """Comprehensive content analysis."""
        
        analysis = {
            'content_type': content_type,
            'length': len(content),
            'word_count': len(content.split())
        }
        
        # Basic NLP analysis
        analysis['sentiment'] = self.agi.run('text_sentiment_analysis', text=content)
        analysis['language'] = self.agi.run('text_language_detection', text=content)
        analysis['keywords'] = self.agi.run('text_keyword_extraction', 
                                           text=content, num_keywords=10)
        analysis['entities'] = self.agi.run('text_entity_extraction', text=content)
        
        # Content quality assessment
        analysis['readability'] = self.agi.run('text_readability_scoring', text=content)
        analysis['quality'] = self.agi.run('text_quality_assessment', text=content)
        
        # SEO analysis
        analysis['seo_score'] = self.calculate_seo_score(content)
        
        # Content classification
        analysis['category'] = self.agi.run('text_topic_classification', text=content)
        
        # Generate summary
        if len(content) > 500:
            analysis['summary'] = self.agi.run('text_summarization', 
                                              text=content, max_length=100)
        
        return analysis
    
    def optimize_content(self, content, target_audience='general', platform='web'):
        """Optimize content for specific audience and platform."""
        
        optimizations = {}
        
        # Tone adjustment
        if target_audience == 'professional':
            optimized_tone = self.agi.run('text_style_transfer',
                                         text=content, target_style='formal')
        elif target_audience == 'casual':
            optimized_tone = self.agi.run('text_style_transfer',
                                         text=content, target_style='casual')
        else:
            optimized_tone = content
        
        optimizations['tone_adjusted'] = optimized_tone
        
        # Platform-specific optimization
        if platform == 'social_media':
            # Shorten for social media
            shortened = self.agi.run('text_summarization',
                                    text=optimized_tone, max_length=280)
            optimizations['social_media'] = shortened
            
            # Generate hashtags
            hashtags = self.agi.run('text_hashtag_generation', text=optimized_tone)
            optimizations['hashtags'] = hashtags
        
        elif platform == 'email':
            # Optimize for email
            subject_line = self.agi.run('text_email_subject_generation', 
                                       text=optimized_tone)
            optimizations['subject_line'] = subject_line
        
        # SEO optimization
        seo_optimized = self.optimize_for_seo(optimized_tone)
        optimizations['seo_optimized'] = seo_optimized
        
        return optimizations
    
    def generate_content_variants(self, original_content, num_variants=3):
        """Generate multiple variants of content."""
        
        variants = []
        
        for i in range(num_variants):
            variant = self.agi.run('text_paraphrasing', 
                                  text=original_content,
                                  diversity=0.7 + (i * 0.1))
            
            # Analyze variant
            variant_analysis = self.analyze_content(variant)
            
            variants.append({
                'text': variant,
                'analysis': variant_analysis,
                'variant_number': i + 1
            })
        
        return variants
    
    def schedule_content(self, content, publish_times, platforms):
        """Schedule content for publication across platforms."""
        
        scheduled_posts = []
        
        for platform in platforms:
            # Optimize for each platform
            optimized = self.optimize_content(content, 
                                            target_audience='general',
                                            platform=platform)
            
            for publish_time in publish_times:
                post = {
                    'content': optimized.get(platform, content),
                    'platform': platform,
                    'scheduled_time': publish_time,
                    'status': 'scheduled'
                }
                
                # Schedule using automation
                self.agi.run('automation_schedule_task',
                            task=f'publish_to_{platform}',
                            schedule_time=publish_time,
                            parameters=post)
                
                scheduled_posts.append(post)
        
        return scheduled_posts
    
    def calculate_seo_score(self, content):
        """Calculate SEO score for content."""
        score = 0
        
        # Basic SEO factors
        word_count = len(content.split())
        if 300 <= word_count <= 2000:
            score += 20
        
        # Keyword density (simplified)
        keywords = self.agi.run('text_keyword_extraction', 
                               text=content, num_keywords=5)
        if keywords['keywords']:
            score += 15
        
        # Readability
        readability = self.agi.run('text_readability_scoring', text=content)
        if readability['score'] > 60:
            score += 25
        
        # Structure (headers, lists, etc.)
        if '\n' in content:  # Simplified check for structure
            score += 20
        
        # Length
        if len(content) > 1000:
            score += 20
        
        return min(score, 100)
    
    def optimize_for_seo(self, content):
        """Optimize content for SEO."""
        
        # Extract keywords
        keywords = self.agi.run('text_keyword_extraction', 
                               text=content, num_keywords=5)
        
        # Generate SEO-friendly title
        title = self.agi.run('text_title_generation', 
                            text=content, style='seo')
        
        # Generate meta description
        meta_description = self.agi.run('text_summarization',
                                       text=content, max_length=160)
        
        return {
            'optimized_content': content,
            'title': title,
            'meta_description': meta_description,
            'keywords': [kw['word'] for kw in keywords['keywords']],
            'seo_score': self.calculate_seo_score(content)
        }

# Example usage
cms = AIContentManager()

# Original article
article = """
Artificial Intelligence is transforming the way businesses operate in the modern world. 
From automating routine tasks to providing deep insights through data analysis, AI has 
become an essential tool for companies looking to stay competitive. Machine learning 
algorithms can process vast amounts of data to identify patterns and make predictions 
that would be impossible for humans to discover manually. Natural language processing 
enables computers to understand and generate human language, opening up new possibilities 
for customer service and content creation. Computer vision allows machines to interpret 
and understand visual information, revolutionizing industries from healthcare to 
autonomous vehicles. As AI technology continues to advance, we can expect to see even 
more innovative applications that will reshape how we work and live.
"""

# Analyze content
analysis = cms.analyze_content(article)
print("📊 CONTENT ANALYSIS")
print(f"Sentiment: {analysis['sentiment']['sentiment']}")
print(f"Quality Score: {analysis['quality']['score']:.2f}")
print(f"SEO Score: {analysis['seo_score']}")
print(f"Top Keywords: {', '.join([kw['word'] for kw in analysis['keywords']['keywords'][:3]])}")

# Generate variants
variants = cms.generate_content_variants(article, num_variants=2)
print(f"\n📝 Generated {len(variants)} content variants")

# Optimize for different platforms
social_optimization = cms.optimize_content(article, 
                                         target_audience='casual',
                                         platform='social_media')
print(f"\n📱 Social Media Version:")
print(social_optimization['social_media']['summary'])
print(f"Hashtags: {', '.join(social_optimization['hashtags']['hashtags'][:3])}")

# Schedule content
from datetime import datetime, timedelta
publish_times = [
    datetime.now() + timedelta(hours=1),
    datetime.now() + timedelta(days=1),
    datetime.now() + timedelta(days=2)
]

scheduled = cms.schedule_content(article, publish_times, ['web', 'social_media', 'email'])
print(f"\n📅 Scheduled {len(scheduled)} posts across platforms")
```

This comprehensive wiki provides extensive documentation for OpenAGI, covering everything from basic usage to advanced applications. Each example demonstrates real-world use cases and provides practical code that users can adapt for their own projects.

---

For more detailed information on specific features, see the [Feature Categories](Feature-Categories.md) page or check the [API Reference](API-Reference.md) for complete documentation.