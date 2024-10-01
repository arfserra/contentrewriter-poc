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

# Function to scrape the main body content, excluding header, footer, and navigation
def scrape_content(url):
    try:
        # Use certifi to verify SSL certificates
        response = requests.get(url, verify=certifi.where())
        response.raise_for_status()  # Raise an error for bad responses (4XX, 5XX)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to extract content within the <main> tag or specific <div> sections
        main_content = soup.find('main') or soup.find('div', {'class': 'content'})
        
        if main_content is None:
            # If no <main> or <div> is found, fall back to other methods
            main_content = soup.find('article') or soup.find('section')
        
        # Remove unwanted elements like <nav>, <aside>, <footer>, and ads
        for element in main_content.find_all(['nav', 'footer', 'aside', 'header']):
            element.decompose()  # Remove the unwanted elements

        # Extract and clean the remaining text
        content = ' '.join(main_content.get_text(separator=' ').split())
        return content

    except requests.exceptions.RequestException as e:
        # Handle request errors
        return f"Error occurred: {e}"

# Function to clean up unnecessary spaces and line breaks from content
def clean_content(content):
    # Replace newlines with spaces and remove extra spaces
    content = ' '.join(content.split())  # Split by any whitespace and join with a single space
    return content
    

# Function to rewrite the content using OpenAI's ChatCompletion API via the client
def rewrite_content(content, audience, context, channel):
    prompt = f"""
    You are an expert in {context} communication. Please rewrite the following content for a {audience} audience in a way that is optimized for {channel}. The content should be adapted to be clear, engaging, and suitable for this audience, providing information at the appropriate depth and complexity.
    
    Original Content:
    {content}
    
    Consider the following:
    - Audience: {audience} (e.g., healthcare professionals, patients, layperson)
    - Context: {context} (e.g., patient education, a medical research paper, public awareness)
    - Channel: {channel} (e.g., social media, a website article, a professional report)
    
    """
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant skilled in content rewriting."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
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
    context = st.selectbox('Select the context:', ('large hospital group', 'small practice', 'trade publication', 'general publication'))

        # Select channel
    channel = st.selectbox('Select the channel:', ('mobile', 'desktop', 'podcast', 'conversational agent'))

    if st.button('Rewrite Content'):
        if url:
            try:
                with st.spinner('Scraping content...'):
                    original_content = scrape_content(url)
                with st.spinner('Rewriting content using LLM...'):
                    rewritten_content = rewrite_content(original_content, audience, context, channel)
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
