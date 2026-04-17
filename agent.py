import os
import pandas as pd
import requests
import pypdf
import base64
from groq import Groq
from dotenv import load_dotenv
from typing import TypedDict, List, Annotated
from langchain_groq import ChatGroq
from bs4 import BeautifulSoup
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

# llm
llm = ChatGroq(
model='llama-3.3-70b-versatile',
api_key=os.getenv('GROQ_API_KEY'),
temperature=0
)
        
#state
class AgentState(TypedDict):
    query: str
    messages: Annotated[List[AnyMessage], add_messages]


#tools
def read_image_tool(image_path: str) -> str:
    """Extract text and information from an image."""
    client = Groq()

    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    response = client.chat.completions.create(
        model = 'meta-llama/llama-4-scout-17b-16e-instruct',
        messages = [{
            "role": "user",
            'content':[
                {
                    "type": "image_url",
                    "image_url":{
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                },
                {
                    "type": "text",
                    "text": "Describe this image in detail and extract all text visible."
                }
            ]
        }]
    )

    return response.choices[0].message.content

def web_search_tool(query: str) -> str:
    """Search the web for information about a given query."""

    search = TavilySearchResults(
        max_results=5,
        tavily_api_key=os.getenv('TAVILY_API_KEY')
    )

    results = search.invoke(query)

    if results:
        return "\n\n".join([
            f"Source: {r['url']}\n{r['content']}"
            for r in results
        ])

    return "No results found."

def web_fetch_tool(url: str) -> str:
    """Useful for extracting all text content from a specific webpage URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        for tag in soup(['script', 'style', 'nav', 'footer']):
            tag.decompose()


        return soup.get_text(separator='\n', strip=True)[:10000]
    
    except Exception as e:
        return f"Error fetching URL: {e}"
    
        
def file_reader_tool(file_path: str) -> str:
    """Read content from a file. Supports PDF, Excel, CSV, TXT, and images."""
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"
    
    ext = os.path.splitext(file_path)[1].lower()

    try:

        if ext == '.pdf':
            reader = pypdf.PdfReader(file_path)
            text = "\n".join([
                page.extract_text() 
                for page in reader.pages 
                if page.extract_text()
            ])
            return text if text else "Could not extract text from PDF."
        
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
            return df.to_string()
        
        elif ext == '.csv':
            df = pd.read_csv(file_path)
            return df.to_string()
        
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
            
        elif ext in ['.jpg', '.jpeg', '.png']:
            return read_image_tool(file_path)
            
        else:
            return f"Unsupported file type: {ext}"
    
    except Exception as e:
        return f"Error reading file: {e}"
    

def file_downloader_tool(task_id: int) -> str:
    """Downloads a file associated with a task and returns its content."""
    file_url = f"https://agents-course-unit4-scoring.hf.space/files/{task_id}"
    response = requests.get(file_url)

    if response.status_code != 200:
        return f"Failed to download file for task {task_id}. Status code: {response.status_code}"
    
    content_type = response.headers.get('Content-Type', '')

    if 'pdf' in content_type:
        ext = '.pdf'
    elif 'excel' in content_type or 'spreadsheet' in content_type:
        ext = '.xlsx'
    elif 'csv' in content_type:
        ext = '.csv'
    elif 'image/jpeg' in content_type:
        ext = '.jpg'
    elif 'image/png' in content_type:
        ext = '.png'    
    elif 'text/plain' in content_type:
        ext = '.txt'    
    else:
        ext = '.bin'
    
    file_path = f'/tmp/{task_id}{ext}'

    with open(file_path,  'wb') as f:
        f.write(response.content)
    
    return file_reader_tool(file_path)

# def wikipedia_search_tool(query: str) -> str:
#     ...

# def calculator_tool(expression: str) -> str:
#     ...



#assistant
def assistant(state: AgentState):
    query = state['query']
    sys_msg = SystemMessage(content=f"""You are a helpful assistant.
    you have access to tools to perform web search, fetch webpage content, 
    read files whose extension is either pdf, csv, xslx, xls, jpg, jpeg, png or txt.
    you can use these tools to gather information to answer the user's query.
                            
    Current Query: {query}

    First determine if you need to use any tools to answer the query. If yes, use the appropriate tool and then answer the query based on the tool output. If no, answer the query directly.
    And the output should be to the point and concise.


    """)

    return {
        'messages': [llm_with_tools.invoke([sys_msg] + state['messages'])]
    }

    

#tools give
tools = [web_search_tool, web_fetch_tool, file_reader_tool, 
         read_image_tool, file_downloader_tool]

llm_with_tools = llm.bind_tools(tools)

#graph
agent_graph = StateGraph(AgentState)

#add node
agent_graph.add_edge(START, 'assistant')
agent_graph.add_node('assistant', assistant)
agent_graph.add_node('tools', ToolNode(tools))    

#add edge
agent_graph.add_edge(START, 'assistant')
agent_graph.add_conditional_edges(
    'assistant',
    tools_condition,
    {
        'tools': 'tools',
        END: END
    }
)
agent_graph.add_edge('tools', 'assistant')

#compile        
agent_compiled_graph = agent_graph.compile()