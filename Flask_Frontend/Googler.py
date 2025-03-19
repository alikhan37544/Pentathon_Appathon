import requests
from bs4 import BeautifulSoup
from googlesearch import search  # Alternatively, use serpapi
from langchain.llms import Ollama

# Step 1: Perform Web Search
def search_web(query, num_results=5):
    results = []
    for url in search(query, num_results=num_results):
        results.append(url)
    return results

# Step 2: Scrape Website Content
def scrape_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = ' '.join([p.get_text() for p in paragraphs])
        return content
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

# Step 3: Summarize with Ollama
def summarize_content(content, model="tinyllama" ):
    llm = Ollama(model=model, num_thread=8)
    prompt = f"Summarize the following content:\n{content}"
    summary = llm(prompt)
    return summary

# Step 4: Main Function
def research_and_summarize(query):
    print(f"Searching for: {query}")
    urls = search_web(query)
    summaries = []
    sources = []

    for url in urls:
        content = scrape_content(url)
        if content:
            summary = summarize_content(content)
            summaries.append(summary)
            sources.append(url)

    # Combine summaries and sources
    combined_summary = "\n\n".join(summaries)
    source_list = "\n".join(sources)
    return combined_summary, source_list

# Example Usage
if __name__ == "__main__":
    query = input("Enter your query: ")
    summary, sources = research_and_summarize(query)
    print("Summary:\n", summary)
    print("\nSources:\n", sources)
