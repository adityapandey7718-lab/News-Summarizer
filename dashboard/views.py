from django.shortcuts import render, redirect
import requests
import os
from bs4 import BeautifulSoup
import re


# Store your API key safely (ideally use environment variables, not plain text)
api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

def fetch_article_content(url):
    """Fetch and extract article content from a given URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        
        # Extract text content
        text = soup.get_text()
        
        # Clean up the text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit text length to avoid token limits
        if len(text) > 8000:
            text = text[:8000] + "..."
        
        return text
    except Exception as e:
        print(f"Error fetching article: {str(e)}")
        return None

def dashboard_page(request):
    return render(request, 'dashboard.html')
#_________________________ai_page----------------------------------------

def ai_page(request):
    if request.method == "POST":
        query = request.POST.get("query")
        response = generate_response(query)
        parameters = {
            "response": response
        }
        return render(request, "asked_ai.html", parameters)

    return render(request, 'asked_ai.html', {"response": None})

def generate_response(query):
    # Check API key first
    if not api_key:
        return "Error: Missing API key. Please set GOOGLE_API_KEY in environment."
    
    print(f"API Key available: {'Yes' if api_key else 'No'}")
    print(f"Query length: {len(query) if query else 0}")

    prompt_template = """You are a professional news analyst AI. Create a comprehensive, well-structured summary of the following article. Follow these guidelines:

1. **Format Requirements**:
   - Begin with a 2-3 sentence overview
   - Use clear bullet points (•) for key facts
   - Group related points under subheadings
   - Provide detailed explanations, not just brief points
   - Maintain neutral, factual tone

2. **Content Structure**:
   **Overview**: [Provide a comprehensive summary of the main points]

   **Key Facts**:
   • [Detailed fact 1 with context and explanation]
   • [Detailed fact 2 with context and explanation]
   • [Detailed fact 3 with context and explanation]
   • [Continue with more facts as needed]

   **Key Entities**:
   • [Person/Organization 1]: [Detailed role and relevance with context]
   • [Person/Organization 2]: [Detailed role and relevance with context]

   **Additional Context**:
   • [Background information and historical context]
   • [Statistics, numbers, and supporting data]
   • [Implications and significance]

3. **Special Instructions**:
   - Provide comprehensive analysis, not just surface-level points
   - Include detailed explanations for each fact
   - Add context and background information
   - Explain why each point is important
   - Aim for a detailed, informative summary

Article to summarize:
{user_input}

Your detailed summary:"""

    full_prompt = prompt_template.format(user_input=query)
    print(f"Prompt length: {len(full_prompt)}")
    
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    print(f"API URL: {api_url[:50]}...")
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": full_prompt
                    }
                ]
            }
        ]
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        print("Making API request...")
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        print(f"Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            try:
                result = data["candidates"][0]["content"]["parts"][0]["text"]
                print(f"Success! Response length: {len(result)}")
                return result
            except (KeyError, IndexError) as e:
                print(f"Error parsing response: {str(e)}")
                return "Error: Unexpected response format."
        else:
            error_msg = response.text if response.text else "No error details provided"
            print(f"API Error {response.status_code}: {error_msg}")
            return f"Error: API request failed with status {response.status_code}. Details: {error_msg}"
            
    except requests.exceptions.Timeout:
        print("Request timed out after 30 seconds")
        return "Error: Request timed out. The API service is taking too long to respond."
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {str(e)}")
        return "Error: Cannot connect to the API service. Please check your internet connection."
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")
        return f"Error: Failed to connect to the API service. Details: {str(e)}"
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return f"Error: An unexpected error occurred: {str(e)}"
    
#---------------------Bies detector-------------------------------
def bias_detector(request):  # Renamed from Bies_detector
    if request.method == "POST":
        query2 = request.POST.get("query2")
        response = generate_response2(query2)
        parameters = {
            "response": response
        }
        return render(request, "bies.html", parameters)

    return render(request, 'bies.html', {"response": None})

#---------------------generative ----------------------------
def generate_response2(query2):
    # Check API key first
    if not api_key:
        return "Error: Missing API key. Please set GOOGLE_API_KEY in environment."
    
    print(f"API Key available: {'Yes' if api_key else 'No'}")
    print(f"Query length: {len(query2) if query2 else 0}")

    prompt_template = """Act as a professional article analyzer and provide a comprehensive bias detection analysis. Give detailed, thorough analysis in point-wise format:

1. **Bias Detection Analysis**:
   - Identify and explain potential biases in the content with specific examples
   - Analyze language patterns, word choices, and framing techniques
   - Compare the presentation with neutral, objective reporting standards
   - Highlight any one-sided arguments or selective information use
   - Assess the overall balance of perspectives presented

2. **Fact Verification & Credibility**:
   - Point out unsupported claims and explain why they lack credibility
   - Note any missing context that could change the interpretation
   - Flag emotional language and explain how it affects objectivity
   - Identify potential conflicts of interest or agenda-driven content
   - Assess the quality and reliability of sources cited

3. **Source Comparison & Alternative Views**:
   - Contrast the article's perspective with alternative viewpoints
   - Note any factual discrepancies when compared to other sources
   - Identify what information might be missing or downplayed
   - Suggest additional sources for balanced understanding
   - Provide context on the broader debate or issue

4. **Overall Assessment**:
   - Rate the article's objectivity on a scale (1-10)
   - Summarize the main biases detected
   - Provide recommendations for balanced reading
   - Explain the potential impact on reader understanding

Article to analyze:
{user_input}

Your comprehensive bias analysis:"""
    
    full_prompt = prompt_template.format(user_input=query2)
    print(f"Prompt length: {len(full_prompt)}")
    
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    print(f"API URL: {api_url[:50]}...")
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": full_prompt
                    }
                ]
            }
        ]
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        print("Making API request...")
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        print(f"Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            try:
                result = data["candidates"][0]["content"]["parts"][0]["text"]
                print(f"Success! Response length: {len(result)}")
                return result
            except (KeyError, IndexError) as e:
                print(f"Error parsing response: {str(e)}")
                return "Error: Could not process the API response format."
        else:
            error_msg = response.text if response.text else "No error details provided"
            print(f"API Error {response.status_code}: {error_msg}")
            return f"Error: API request failed with status {response.status_code}. Details: {error_msg}"
            
    except requests.exceptions.Timeout:
        print("Request timed out after 30 seconds")
        return "Error: Request timed out. The API service is taking too long to respond."
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {str(e)}")
        return "Error: Cannot connect to the API service. Please check your internet connection."
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")
        return f"Error: Failed to connect to the API service. Details: {str(e)}"
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return f"Error: An unexpected error occurred: {str(e)}"
#------------------------def-fact------------------------------------
def fact(request):
    if request.method == "POST":
        query3 = request.POST.get("query3")
        response = generate_response3(query3)
        parameters = {
            "response": response
        }
        return render(request, "fact.html", parameters)

    return render(request, 'fact.html', {"response": None})

#----------------------generative_3-----------------
def generate_response3(query3):
    # Check API key first
    if not api_key:
        return "Error: Missing API key. Please set GOOGLE_API_KEY in environment."
    
    print(f"API Key available: {'Yes' if api_key else 'No'}")
    print(f"Query length: {len(query3) if query3 else 0}")

    prompt_template = """Act as a professional data analyst and provide a comprehensive fact extraction analysis. Give detailed, thorough analysis of the important facts in the article:

1. **Key Facts Identification**:
   - Extract and explain the most important factual information
   - Provide context and background for each fact
   - Include specific numbers, dates, statistics, and data points
   - Explain why each fact is significant or newsworthy
   - Identify any trends or patterns in the data presented

2. **Fact Verification & Reliability**:
   - Assess the credibility of each fact presented
   - Identify the sources of information and their reliability
   - Note any facts that need additional verification
   - Flag any claims that appear to be opinions rather than facts
   - Assess the completeness of the factual information

3. **Context & Implications**:
   - Provide historical context for the facts presented
   - Explain the broader significance and implications
   - Connect facts to larger trends or issues
   - Identify any missing context that could change interpretation
   - Suggest additional information needed for full understanding

4. **Factual Summary**:
   - Create a comprehensive summary of all key facts
   - Organize facts by importance and relevance
   - Highlight any contradictions or inconsistencies
   - Provide recommendations for further fact-checking

Article to analyze:
{user_input}

Your comprehensive fact analysis:"""
    
    full_prompt = prompt_template.format(user_input=query3)
    print(f"Prompt length: {len(full_prompt)}")
    
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    print(f"API URL: {api_url[:50]}...")
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": full_prompt
                    }
                ]
            }
        ]
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        print("Making API request...")
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        print(f"Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            try:
                result = data["candidates"][0]["content"]["parts"][0]["text"]
                print(f"Success! Response length: {len(result)}")
                return result
            except (KeyError, IndexError) as e:
                print(f"Error parsing response: {str(e)}")
                return "Error: Could not process the API response format."
        else:
            error_msg = response.text if response.text else "No error details provided"
            print(f"API Error {response.status_code}: {error_msg}")
            return f"Error: API request failed with status {response.status_code}. Details: {error_msg}"
            
    except requests.exceptions.Timeout:
        print("Request timed out after 30 seconds")
        return "Error: Request timed out. The API service is taking too long to respond."
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {str(e)}")
        return "Error: Cannot connect to the API service. Please check your internet connection."
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")
        return f"Error: Failed to connect to the API service. Details: {str(e)}"
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return f"Error: An unexpected error occurred: {str(e)}"

def analyze_article(request):
    """Handle article analysis from dashboard form"""
    if request.method == "POST":
        article_url = request.POST.get("articleUrl")
        
        if not article_url:
            return render(request, "dashboard.html", {"error": "Please provide an article URL"})
        
        # Fetch article content
        article_content = fetch_article_content(article_url)
        
        if not article_content:
            return render(request, "dashboard.html", {"error": "Could not fetch article content. Please check the URL."})
        
        # Generate analysis using real article content
        summary = generate_response(article_content)
        bias_analysis = generate_response2(article_content)
        fact_analysis = generate_response3(article_content)
        
        # Calculate bias score (simple heuristic based on response length and content)
        bias_score = calculate_bias_score(bias_analysis)
        
        context = {
            "article_url": article_url,
            "summary": summary,
            "bias_analysis": bias_analysis,
            "fact_analysis": fact_analysis,
            "bias_score": bias_score,
            "has_results": True
        }
        
        return render(request, "dashboard.html", context)
    
    return render(request, "dashboard.html")

def calculate_bias_score(bias_analysis):
    """Calculate a simple bias score based on analysis content"""
    if not bias_analysis or "Error:" in bias_analysis:
        return 0.5  # Default neutral score
    
    # Simple heuristic: look for bias indicators in the text
    bias_indicators = {
        'high': ['significant bias', 'strong bias', 'clear bias', 'obvious bias', 'heavy bias'],
        'medium': ['some bias', 'moderate bias', 'partial bias', 'slight bias'],
        'low': ['low bias', 'minimal bias', 'balanced', 'objective', 'neutral']
    }
    
    analysis_lower = bias_analysis.lower()
    
    for level, indicators in bias_indicators.items():
        for indicator in indicators:
            if indicator in analysis_lower:
                if level == 'high':
                    return 0.7 + (hash(indicator) % 30) / 100  # 0.7-1.0
                elif level == 'medium':
                    return 0.4 + (hash(indicator) % 30) / 100  # 0.4-0.7
                else:
                    return 0.1 + (hash(indicator) % 30) / 100  # 0.1-0.4
    
    # Default to medium if no clear indicators
    return 0.5