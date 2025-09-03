from django.shortcuts import render, redirect
import requests
import os


# Store your API key safely (ideally use environment variables, not plain text)
api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")

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
    prompt_template = """You are a professional news analyst AI. Create a concise, well-structured point-wise summary of the following article. Follow these guidelines strictly:

1. **Format Requirements**:
   - Begin with a 1-sentence overview in bold
   - Use clear bullet points (•) for key facts
   - Group related points under subheadings
   - Keep each bullet point under 15 words
   - Maintain neutral, factual tone

2. **Content Structure**:
   **Overview**: [Main point of article]

   • [Key fact 1]
   • [Key fact 2]
   • [Key fact 3]

   **Key Entities**:
   • [Person/Organization 1]: [Role/relevance]
   • [Person/Organization 2]: [Role/relevance]

   **Additional Context**:
   • [Background info if needed]
   • [Statistics/numbers if present]

3. **Special Instructions**:
   - Prioritize factual information over opinions
   - Include numbers/dates when available
   - Skip introductory fluff
   - Use simple, direct language

Article to summarize:
{user_input}

Your summary:"""+"query"

    full_prompt = prompt_template.format(user_input=query)
    
    if not api_key:
        return "Error: Missing API key. Please set GOOGLE_API_KEY in environment."

    api = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": full_prompt  # Using the formatted prompt with user input
                    }
                ]
            }
        ]
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(api, json=payload, headers=headers)

    print("Status Code:", response.status_code)  # Debugging

    if response.status_code == 200:
        data = response.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return "Error: Unexpected response format."
    else:
        return f"Error: {response.text}"
    
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


    prompt_template = """Act as professional article analyzer and detect the bias facts while comparing with other websites. Mention in point-wise format:
    
1. **Bias Detection**:
   - Identify potential biases in the content
   - Compare with neutral sources
   - Highlight any one-sided arguments

2. **Fact Verification**:
   - Point out unsupported claims
   - Note any missing context
   - Flag emotional language

3. **Source Comparison**:
   - Contrast with alternative viewpoints
   - Note any factual discrepancies

Article to analyze:
{user_input}

Your analysis:"""
    
    full_prompt = prompt_template.format(user_input=query2)  # Changed from 'query' to 'query2'
    
    if not api_key:
        return "Error: Missing API key. Please set GOOGLE_API_KEY in environment."

    api = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
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
        response = requests.post(api, json=payload, headers=headers, timeout=10)
        print("Status Code:", response.status_code)

        if response.status_code == 200:
            data = response.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError) as e:
                print(f"Error parsing response: {str(e)}")
                return "Error: Could not process the API response format."
        else:
            error_msg = response.text if response.text else "No error details provided"
            print(f"API Error {response.status_code}: {error_msg}")
            return f"Error: API request failed with status {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")
        return f"Error: Failed to connect to the API service"
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
    prompt_template = """act professional data analyst, I provide article you highlight important facts"""
    
    full_prompt = prompt_template.format(user_input=query3)
    
    if not api_key:
        return "Error: Missing API key. Please set GOOGLE_API_KEY in environment."

    api = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
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
        response = requests.post(api, json=payload, headers=headers, timeout=10)
        print("Status Code:", response.status_code)

        if response.status_code == 200:
            data = response.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError) as e:
                print(f"Error parsing response: {str(e)}")
                return "Error: Could not process the API response format."
        else:
            error_msg = response.text if response.text else "No error details provided"
            print(f"API Error {response.status_code}: {error_msg}")
            return f"Error: API request failed with status {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")
        return f"Error: Failed to connect to the API service"