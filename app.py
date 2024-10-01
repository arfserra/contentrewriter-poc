import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
import openai
import certifi
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Load API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to scrape content from the webpage with SSL verification using certifi
def scrape_content(url):
    try:
        # Use certifi to verify SSL certificates
        response = requests.get(url, verify=certifi.where())
        response.raise_for_status()  # Raise an error for bad responses (4XX, 5XX)
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text content from the page
        content = soup.get_text(separator='\n')

        # Clean up content: remove extra spaces and newlines
        cleaned_content = clean_content(content)
        return cleaned_content

    except requests.exceptions.RequestException as e:
        # Handle request errors
        return f"Error occurred: {e}"

# Function to clean up unnecessary spaces and line breaks from content
def clean_content(content):
    # Replace newlines with spaces and remove extra spaces
    content = ' '.join(content.split())  # Split by any whitespace and join with a single space
    return content
    

# Function to rewrite the content using OpenAI's ChatCompletion API via the client
def rewrite_content(originalContent, audience, context):
    prompt = f"""
    Rewrite the following content for a {audience} audience that's accessing this content on {context}:
    
    {originalContent}
    """
    
    # Use ChatCompletion with the OpenAI client to call GPT-3.5-turbo or GPT-4
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # Or "gpt-4" if desired
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1500,
        temperature=0.7
    )
    return response.choices[0].message.content


# Streamlit app
def main():
    st.title('Content Rewriter')

    # Input field for URL
    url = st.text_input('Enter a URL to scrape content from:', '')

    # Select audience type
    audience = st.selectbox('Select the audience:', ('imaging technicians', 'procurement', 'journalist'))

    # Select context
    context = st.selectbox('Select the context:', ('mobile', 'desktop', 'podcast'))

    if st.button('Rewrite Content'):
        if url:
            try:
                with st.spinner('Scraping content...'):
                    original_content = scrape_content(url)
                with st.spinner('Rewriting content using LLM...'):
                    rewritten_content = rewrite_content(original_content, audience, context)
                st.subheader('Original Content:')
                st.text_area('Original Content', original_content, height=200)
                st.subheader('Rewritten Content:')
                st.text_area('Rewritten Content', rewritten_content, height=400)
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning('Please enter a valid URL.')

if __name__ == '__main__':
    main()
