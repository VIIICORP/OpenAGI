# Quick Start Tutorial

Build your first AI application with OpenAGI in 15 minutes!

## 🎯 What We'll Build

In this tutorial, we'll create a **Smart Document Analyzer** that:
- Analyzes text sentiment
- Extracts key entities 
- Generates a summary
- Provides insights and recommendations

## 📋 Prerequisites

Make sure you have:
- ✅ OpenAGI installed ([Installation Guide](Installation.md))
- ✅ Python 3.8+ 
- ✅ Basic Python knowledge
- ✅ A text editor or IDE

## 🚀 Step 1: Verify Installation

First, let's make sure OpenAGI is working:

```bash
# Check installation
openagi info

# List available features
openagi list-features --category nlp --limit 5
```

Expected output:
```
OpenAGI Platform v1.0.0
Total Features: 14,000+
Categories: 15
Status: Ready

NLP Features (showing 5 of 2000+):
- text_sentiment_analysis
- text_entity_extraction
- text_summarization
- text_language_detection
- text_keyword_extraction
```

## 🛠️ Step 2: Create the Project

Create a new directory for our project:

```bash
mkdir smart-document-analyzer
cd smart-document-analyzer
```

Create our main script:

```python
# main.py
from openagi import OpenAGI
import json
from pathlib import Path

def main():
    print("🧠 Smart Document Analyzer")
    print("=" * 40)
    
    # Initialize OpenAGI
    agi = OpenAGI()
    
    # Sample document
    document = """
    OpenAGI is an amazing artificial intelligence platform that brings together 
    over 14,000 AI features. The platform makes advanced AI capabilities accessible 
    through a simple, consistent interface. Users love how easy it is to integrate 
    multiple AI features into their applications. The documentation is comprehensive 
    and the community is very supportive. However, some users have mentioned that 
    the initial setup can be time-consuming due to the large number of dependencies.
    Overall, OpenAGI represents a significant advancement in democratizing AI technology.
    """
    
    print(f"📄 Analyzing document ({len(document)} characters)...")
    print()
    
    # Analyze the document
    results = analyze_document(agi, document)
    
    # Display results
    display_results(results)

def analyze_document(agi, text):
    """Analyze a document using multiple OpenAGI features."""
    results = {}
    
    print("🔍 Running analysis...")
    
    # 1. Sentiment Analysis
    print("  • Analyzing sentiment...")
    sentiment = agi.run('text_sentiment_analysis', text=text)
    results['sentiment'] = sentiment
    
    # 2. Entity Extraction
    print("  • Extracting entities...")
    entities = agi.run('text_entity_extraction', text=text)
    results['entities'] = entities
    
    # 3. Text Summarization
    print("  • Generating summary...")
    summary = agi.run('text_summarization', text=text, max_length=100)
    results['summary'] = summary
    
    # 4. Keyword Extraction
    print("  • Extracting keywords...")
    keywords = agi.run('text_keyword_extraction', text=text, num_keywords=10)
    results['keywords'] = keywords
    
    # 5. Language Detection
    print("  • Detecting language...")
    language = agi.run('text_language_detection', text=text)
    results['language'] = language
    
    print("✅ Analysis complete!")
    print()
    
    return results

def display_results(results):
    """Display analysis results in a formatted way."""
    
    print("📊 ANALYSIS RESULTS")
    print("=" * 40)
    
    # Sentiment Analysis
    sentiment = results['sentiment']
    print(f"😊 Sentiment: {sentiment['sentiment'].upper()}")
    print(f"   Confidence: {sentiment['confidence']:.2%}")
    print()
    
    # Language Detection
    language = results['language']
    print(f"🌍 Language: {language['language']} ({language['confidence']:.2%})")
    print()
    
    # Summary
    summary = results['summary']
    print("📝 Summary:")
    print(f"   {summary['summary']}")
    print()
    
    # Keywords
    keywords = results['keywords']
    print("🔤 Key Terms:")
    for keyword in keywords['keywords'][:5]:  # Top 5 keywords
        print(f"   • {keyword['word']} (score: {keyword['score']:.2f})")
    print()
    
    # Entities
    entities = results['entities']
    if entities['entities']:
        print("🏷️  Named Entities:")
        for entity in entities['entities'][:5]:  # Top 5 entities
            print(f"   • {entity['text']} ({entity['type']})")
    else:
        print("🏷️  Named Entities: None detected")
    print()
    
    # Generate insights
    generate_insights(results)

def generate_insights(results):
    """Generate insights based on the analysis."""
    print("💡 INSIGHTS & RECOMMENDATIONS")
    print("=" * 40)
    
    sentiment = results['sentiment']['sentiment']
    confidence = results['sentiment']['confidence']
    
    # Sentiment insights
    if sentiment == 'positive' and confidence > 0.8:
        print("✅ This document expresses strong positive sentiment.")
        print("   Recommendation: Great for marketing or promotional content.")
    elif sentiment == 'negative' and confidence > 0.8:
        print("⚠️  This document expresses strong negative sentiment.")
        print("   Recommendation: Consider addressing concerns raised.")
    else:
        print("ℹ️  This document has mixed or neutral sentiment.")
        print("   Recommendation: Consider balancing positive and negative aspects.")
    
    print()
    
    # Content insights
    word_count = len(results['summary']['summary'].split())
    if word_count > 50:
        print("📏 Document length: Long-form content")
        print("   Recommendation: Consider breaking into sections for better readability.")
    else:
        print("📏 Document length: Concise content")
        print("   Recommendation: Good length for quick consumption.")
    
    print()
    
    # Entity insights
    entity_count = len(results['entities']['entities'])
    if entity_count > 5:
        print("🏷️  Rich in named entities (people, places, organizations)")
        print("   Recommendation: Good for information extraction and knowledge graphs.")
    elif entity_count > 0:
        print("🏷️  Contains some named entities")
        print("   Recommendation: Suitable for basic information extraction.")
    else:
        print("🏷️  Few or no named entities detected")
        print("   Recommendation: Focus on sentiment and topic analysis.")

if __name__ == "__main__":
    main()
```

## ▶️ Step 3: Run the Application

Run your Smart Document Analyzer:

```bash
python main.py
```

Expected output:
```
🧠 Smart Document Analyzer
========================================
📄 Analyzing document (523 characters)...

🔍 Running analysis...
  • Analyzing sentiment...
  • Extracting entities...
  • Generating summary...
  • Extracting keywords...
  • Detecting language...
✅ Analysis complete!

📊 ANALYSIS RESULTS
========================================
😊 Sentiment: POSITIVE
   Confidence: 78.50%

🌍 Language: en (99.80%)

📝 Summary:
   OpenAGI is an AI platform with 14,000+ features, making AI accessible through a simple interface.

🔤 Key Terms:
   • OpenAGI (score: 0.95)
   • platform (score: 0.82)
   • features (score: 0.78)
   • AI (score: 0.75)
   • accessible (score: 0.71)

🏷️  Named Entities:
   • OpenAGI (ORG)
   • 14,000 (CARDINAL)

💡 INSIGHTS & RECOMMENDATIONS
========================================
✅ This document expresses strong positive sentiment.
   Recommendation: Great for marketing or promotional content.

📏 Document length: Concise content
   Recommendation: Good length for quick consumption.

🏷️  Contains some named entities
   Recommendation: Suitable for basic information extraction.
```

## 🎨 Step 4: Add File Processing

Let's enhance our analyzer to process text files:

```python
# file_analyzer.py
from openagi import OpenAGI
import sys
from pathlib import Path

def analyze_file(file_path):
    """Analyze a text file."""
    
    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    print(f"📄 Analyzing file: {file_path}")
    print(f"📏 File size: {len(content)} characters")
    print()
    
    # Initialize OpenAGI
    agi = OpenAGI()
    
    # Analyze content
    results = {}
    
    # Basic analysis
    print("🔍 Running basic analysis...")
    sentiment = agi.run('text_sentiment_analysis', text=content)
    language = agi.run('text_language_detection', text=content)
    
    # Advanced analysis for longer texts
    if len(content) > 500:
        print("📚 Running advanced analysis for long text...")
        summary = agi.run('text_summarization', text=content, max_length=150)
        keywords = agi.run('text_keyword_extraction', text=content, num_keywords=15)
        entities = agi.run('text_entity_extraction', text=content)
    else:
        print("📄 Running basic analysis for short text...")
        keywords = agi.run('text_keyword_extraction', text=content, num_keywords=8)
        entities = agi.run('text_entity_extraction', text=content)
        summary = {'summary': content[:200] + '...' if len(content) > 200 else content}
    
    # Display results
    print()
    print("📊 ANALYSIS RESULTS")
    print("=" * 50)
    
    print(f"😊 Sentiment: {sentiment['sentiment'].upper()} ({sentiment['confidence']:.1%})")
    print(f"🌍 Language: {language['language']} ({language['confidence']:.1%})")
    print()
    
    print("📝 Summary:")
    print(f"   {summary['summary']}")
    print()
    
    print("🔤 Top Keywords:")
    for i, kw in enumerate(keywords['keywords'][:8], 1):
        print(f"   {i}. {kw['word']} ({kw['score']:.2f})")
    print()
    
    if entities['entities']:
        print("🏷️  Named Entities:")
        entity_types = {}
        for entity in entities['entities']:
            entity_type = entity['type']
            if entity_type not in entity_types:
                entity_types[entity_type] = []
            entity_types[entity_type].append(entity['text'])
        
        for entity_type, names in entity_types.items():
            unique_names = list(set(names))[:5]  # Top 5 unique entities
            print(f"   {entity_type}: {', '.join(unique_names)}")
    else:
        print("🏷️  Named Entities: None detected")
    
    # Save results
    save_results(file_path, {
        'sentiment': sentiment,
        'language': language,
        'summary': summary,
        'keywords': keywords,
        'entities': entities
    })

def save_results(file_path, results):
    """Save analysis results to a JSON file."""
    output_file = Path(file_path).stem + '_analysis.json'
    
    try:
        import json
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"💾 Results saved to: {output_file}")
    except Exception as e:
        print(f"⚠️  Could not save results: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python file_analyzer.py <text_file>")
        print()
        print("Example:")
        print("  python file_analyzer.py document.txt")
        return
    
    file_path = sys.argv[1]
    analyze_file(file_path)

if __name__ == "__main__":
    main()
```

Create a sample text file to test:

```bash
# Create sample.txt
cat > sample.txt << 'EOF'
Artificial Intelligence has revolutionized the way we approach complex problems in technology. 
Companies like Google, Microsoft, and OpenAI have made significant breakthroughs in machine learning 
and natural language processing. The development of transformer models has particularly changed 
the landscape of AI applications. However, there are still challenges in ensuring AI safety and 
addressing bias in AI systems. The future of AI looks promising, with potential applications 
in healthcare, education, and scientific research. Nevertheless, we must proceed carefully to 
ensure that AI development benefits all of humanity.
EOF
```

Test the file analyzer:

```bash
python file_analyzer.py sample.txt
```

## 🌐 Step 5: Add Web Interface (Optional)

Create a simple web interface using Streamlit:

```python
# web_app.py
import streamlit as st
from openagi import OpenAGI
import time

# Configure page
st.set_page_config(
    page_title="Smart Document Analyzer",
    page_icon="🧠",
    layout="wide"
)

@st.cache_resource
def get_openagi():
    """Initialize OpenAGI with caching."""
    return OpenAGI()

def main():
    st.title("🧠 Smart Document Analyzer")
    st.markdown("*Powered by OpenAGI*")
    
    # Sidebar
    st.sidebar.header("📋 Analysis Options")
    
    include_summary = st.sidebar.checkbox("Generate Summary", value=True)
    include_entities = st.sidebar.checkbox("Extract Entities", value=True)
    include_keywords = st.sidebar.checkbox("Extract Keywords", value=True)
    num_keywords = st.sidebar.slider("Number of Keywords", 5, 20, 10)
    
    # Main interface
    st.header("📄 Enter Text to Analyze")
    
    # Text input options
    input_method = st.radio("Input Method:", ["Text Area", "File Upload"])
    
    text = ""
    if input_method == "Text Area":
        text = st.text_area("Enter your text:", height=200, 
                           placeholder="Paste your text here...")
    else:
        uploaded_file = st.file_uploader("Choose a text file", type=['txt'])
        if uploaded_file is not None:
            text = uploaded_file.read().decode('utf-8')
            st.text_area("File content:", value=text, height=200, disabled=True)
    
    # Analysis button
    if st.button("🔍 Analyze Document", type="primary"):
        if not text.strip():
            st.error("Please enter some text to analyze.")
            return
        
        # Initialize OpenAGI
        agi = get_openagi()
        
        # Progress tracking
        progress_bar = st.progress(0)
        status = st.empty()
        
        results = {}
        total_steps = 2 + include_summary + include_entities + include_keywords
        current_step = 0
        
        # Basic analysis
        status.text("Analyzing sentiment...")
        results['sentiment'] = agi.run('text_sentiment_analysis', text=text)
        current_step += 1
        progress_bar.progress(current_step / total_steps)
        
        status.text("Detecting language...")
        results['language'] = agi.run('text_language_detection', text=text)
        current_step += 1
        progress_bar.progress(current_step / total_steps)
        
        # Optional analyses
        if include_summary:
            status.text("Generating summary...")
            results['summary'] = agi.run('text_summarization', text=text, max_length=150)
            current_step += 1
            progress_bar.progress(current_step / total_steps)
        
        if include_entities:
            status.text("Extracting entities...")
            results['entities'] = agi.run('text_entity_extraction', text=text)
            current_step += 1
            progress_bar.progress(current_step / total_steps)
        
        if include_keywords:
            status.text("Extracting keywords...")
            results['keywords'] = agi.run('text_keyword_extraction', 
                                        text=text, num_keywords=num_keywords)
            current_step += 1
            progress_bar.progress(current_step / total_steps)
        
        status.text("Analysis complete!")
        progress_bar.progress(1.0)
        time.sleep(0.5)
        progress_bar.empty()
        status.empty()
        
        # Display results
        display_web_results(results, include_summary, include_entities, include_keywords)

def display_web_results(results, include_summary, include_entities, include_keywords):
    """Display analysis results in the web interface."""
    
    st.header("📊 Analysis Results")
    
    # Create columns for layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Sentiment
        sentiment = results['sentiment']
        sentiment_color = {
            'positive': '🟢',
            'negative': '🔴',
            'neutral': '🟡'
        }.get(sentiment['sentiment'], '⚪')
        
        st.metric(
            label=f"{sentiment_color} Sentiment",
            value=sentiment['sentiment'].title(),
            delta=f"{sentiment['confidence']:.1%} confidence"
        )
        
        # Language
        language = results['language']
        st.metric(
            label="🌍 Language",
            value=language['language'].upper(),
            delta=f"{language['confidence']:.1%} confidence"
        )
    
    with col2:
        # Text statistics
        word_count = len(results.get('summary', {}).get('summary', '').split())
        char_count = len(results.get('summary', {}).get('summary', ''))
        
        st.metric("📏 Word Count", word_count)
        st.metric("📝 Character Count", char_count)
    
    # Summary
    if include_summary and 'summary' in results:
        st.subheader("📝 Summary")
        st.info(results['summary']['summary'])
    
    # Keywords
    if include_keywords and 'keywords' in results:
        st.subheader("🔤 Keywords")
        keywords = results['keywords']['keywords']
        
        # Create keyword tags
        keyword_tags = []
        for kw in keywords[:10]:
            keyword_tags.append(f"`{kw['word']}` ({kw['score']:.2f})")
        
        st.markdown(" • ".join(keyword_tags))
    
    # Entities
    if include_entities and 'entities' in results:
        st.subheader("🏷️ Named Entities")
        
        entities = results['entities']['entities']
        if entities:
            # Group entities by type
            entity_groups = {}
            for entity in entities:
                entity_type = entity['type']
                if entity_type not in entity_groups:
                    entity_groups[entity_type] = []
                entity_groups[entity_type].append(entity['text'])
            
            for entity_type, names in entity_groups.items():
                unique_names = list(set(names))
                st.write(f"**{entity_type}:** {', '.join(unique_names[:5])}")
        else:
            st.write("No named entities detected.")
    
    # Export options
    st.subheader("💾 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Copy to Clipboard"):
            # This would require additional JavaScript
            st.info("Copy functionality would be implemented with custom JS")
    
    with col2:
        # JSON download
        import json
        json_data = json.dumps(results, indent=2)
        st.download_button(
            label="📁 Download JSON",
            data=json_data,
            file_name="analysis_results.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()
```

Install Streamlit and run the web app:

```bash
pip install streamlit
streamlit run web_app.py
```

## 🎉 Step 6: What You've Accomplished

Congratulations! You've built a complete Smart Document Analyzer that:

✅ **Analyzes sentiment** - Determines if text is positive, negative, or neutral  
✅ **Extracts entities** - Identifies people, places, organizations  
✅ **Generates summaries** - Creates concise summaries of long text  
✅ **Finds keywords** - Extracts the most important terms  
✅ **Detects language** - Identifies the language of the text  
✅ **Provides insights** - Offers recommendations based on analysis  
✅ **Processes files** - Analyzes text files and saves results  
✅ **Web interface** - Interactive web application (optional)

## 🚀 Next Steps

Now that you've mastered the basics, try these extensions:

### 1. Add More AI Features
```python
# Add image analysis
image_results = agi.run('image_object_detection', image_path='photo.jpg')

# Add audio processing
audio_results = agi.run('audio_transcription', audio_path='speech.wav')

# Add machine learning
model = agi.run('ml_train_classifier', data=X_train, target=y_train)
```

### 2. Create Feature Pipelines
```python
# Create an automated content pipeline
pipeline = agi.create_pipeline([
    ('text_cleaner', {'remove_punctuation': True}),
    ('text_sentiment_analysis', {}),
    ('text_keyword_extraction', {'num_keywords': 10}),
    ('data_confidence_filter', {'min_confidence': 0.8})
])

result = pipeline.run(text="Your content here")
```

### 3. Build Real-World Applications
- **Content Moderation System** - Analyze user-generated content
- **Customer Feedback Analyzer** - Process reviews and feedback
- **Document Classification** - Automatically categorize documents
- **Social Media Monitor** - Analyze social media posts
- **Research Assistant** - Summarize academic papers

### 4. Explore More Categories
- **[Computer Vision](Feature-Categories.md#-computer-vision)** - Image and video processing
- **[Machine Learning](Feature-Categories.md#-machine-learning)** - Model training and prediction
- **[Data Analysis](Feature-Categories.md#-data-analysis)** - Statistical analysis and visualization
- **[Automation](Feature-Categories.md#-automation)** - Workflow automation

## 📚 Learning Resources

- **[User Guide](User-Guide.md)** - Comprehensive feature documentation
- **[API Reference](API-Reference.md)** - Complete API documentation
- **[Examples](Examples.md)** - More real-world examples
- **[Feature Categories](Feature-Categories.md)** - Explore all 14,000+ features

## 🆘 Need Help?

- **Issues?** Check the [Troubleshooting Guide](Troubleshooting.md)
- **Questions?** Visit the [FAQ](FAQ.md)
- **Community?** Join [GitHub Discussions](https://github.com/VIIICORP/OpenAGI/discussions)

---

**🎉 Congratulations!** You've completed the OpenAGI Quick Start Tutorial. You're now ready to build amazing AI applications!