import os
import chainlit as cl
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams
from agents import Agent, OpenAIChatCompletionsModel, Runner
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
from openai import AsyncOpenAI
import traceback

# Load environment variables
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

external_client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)
model = OpenAIChatCompletionsModel(
    openai_client=external_client,
    model="google/gemini-2.0-flash-001"
)

# Initialize Firecrawl
firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
if not firecrawl_api_key:
    raise ValueError("FIRECRAWL_API_KEY environment variable is not set")
firecrawl = FirecrawlApp(api_key=firecrawl_api_key)

MCP_SERVER_URL = "http://localhost:3000/mcp"


@cl.on_chat_start
async def on_chat_start():
    await cl.Message(
        content="Hello! I'm your research assistant. What would you like to research today?"
    ).send()
    
    try:
        # Initialize MCP server connection
        mcp_params = MCPServerStreamableHttpParams(url=MCP_SERVER_URL)
        mcp_server_client = MCPServerStreamableHttp(params=mcp_params, name="MySharedMCPServerClient")
        await mcp_server_client.connect()

        # Store MCP client in session
        cl.user_session.set("mcp_server_client", mcp_server_client)
        
    except Exception as e:
        error_msg = f"❌ Failed to initialize MCP server: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


@cl.on_message
async def main(message: cl.Message):
    # Get MCP client from session
    mcp_server_client = cl.user_session.get("mcp_server_client")
    
    if not mcp_server_client:
        await cl.Message(content="Error: MCP server not initialized. Please refresh the page.").send()
        return

    # Create a status message that we'll update throughout the process
    status_msg = cl.Message(content="🚀 Starting research process...")
    await status_msg.send()
    await cl.sleep(2)  

    try:
        
        # STEP 1: INITIAL RESEARCH
        
        status_msg.content = "🔍 Step 1/4: Conducting initial research...\nSearching for relevant sources..."
        await status_msg.update()
        
        
        initial_research_agent = Agent(
            name="Initial Research Agent",
            instructions="""You are an expert initial research agent. Your role is to:
            1. Understand the user's research query thoroughly
            2. Call the firecrawl_search tool EXACTLY ONCE to find relevant information sources
            3. Analyze the search results you receive
            4. Identify the most relevant sources from the results
            5. Return your findings in the structured output format
            
            CRITICAL: You must call firecrawl_search ONLY ONCE, then immediately analyze those 
            results and provide your structured output. Do not call the tool multiple times.
            
            After calling the tool once and receiving results, structure your response with:
            - The original query
            - List of findings from the search results
            - Key topics identified
            - Areas recommended for deeper investigation
            
            Once you have the search results and have created your structured output, you are done.""",
            mcp_servers=[mcp_server_client],
            model=model
        )

        initial_result = await Runner.run(
            initial_research_agent,
            f"Conduct initial research on: {message.content}",
            max_turns=3
        )
        
        print(f"✓ Initial research complete")
        status_msg.content = "✅ Step 1/4: Initial research completed!\n🔍 Found relevant sources and identified key topics."
        await status_msg.update()
        await cl.sleep(2)

        
        # STEP 2: DEEP RESEARCH
        
        status_msg.content = "📊 Step 2/4: Conducting deep research...\nScraping and analyzing key sources..."
        await status_msg.update()
        await cl.sleep(2)
        
        deep_research_agent = Agent(
            name="Deep Research Agent",
            instructions="""You are a deep research specialist. Your role is to:
            1. Review the URLs and topics provided to you
            2. Select 2-3 most important URLs to investigate deeply
            3. Call firecrawl_scrape for each selected URL (maximum 3 calls total)
            4. Analyze the scraped content thoroughly
            5. Return your findings in the structured output format
            
            CRITICAL: Limit yourself to scraping 2-3 URLs maximum. After scraping these URLs
            and analyzing the content, immediately provide your structured output and stop.
            
            Your output should include:
            - The topic being researched
            - Detailed findings from scraped content
            - Key insights extracted
            - Important data points discovered
            
            Once you have scraped the URLs and created your structured output, you are done.""",
            mcp_servers=[mcp_server_client],
            model=model
        )

        deep_research_input = f"""
        Based on the initial research findings for: {message.content}
        **Initial Findings:**
        {initial_result.final_output}
        Identify 2-3 key areas or URLs that require deeper investigation.
        Conduct deep research on those areas and sources.
        """
        
        deep_result = await Runner.run(
            deep_research_agent,
            deep_research_input,
            max_turns=5
        )
        
        
        print(f"✓ Deep research complete")
        status_msg.content = "✅ Step 2/4: Deep research completed!\n📊 Extracted detailed insights and key data points."
        await status_msg.update()
        await cl.sleep(2)

        
        # STEP 3: CONTENT ENHANCEMENT
        
        status_msg.content = "✨ Step 3/4: Enhancing content...\nAdding examples and simplifying complex concepts..."
        await status_msg.update()
        await cl.sleep(2)
        
        enhancer_agent = Agent(
            name="Enhancer Agent",
            instructions="""You are a content enhancement specialist. Your role is to:
            1. Take the deep research findings and improve their quality and clarity
            2. Identify complex concepts and explain them in simple terms
            3. Provide practical examples and use cases for key findings
            4. Add context and real-world applications
            5. Make the content more accessible and actionable
            
            Focus on:
            - Breaking down complex technical concepts into understandable explanations
            - Providing concrete examples that illustrate abstract ideas
            - Highlighting practical use cases and applications
            - Adding analogies and comparisons where helpful
            - Ensuring the content is engaging and easy to understand
            
            Transform dense research into clear, actionable insights.""",
            model=model
        )

        enhancement_input = f"""
        Enhance the following research findings for: {message.content}
        **Deep Research Findings:**
        {deep_result.final_output}
        
        Please enhance this research finding with additional information, examples, case studies, 
        and deeper insights while maintaining its academic rigor and factual accuracy.
        Key Insights:
        """
        
        enhanced_result = await Runner.run(
            enhancer_agent,
            enhancement_input,
            max_turns=2
        )
        
        print(f"✓ Content enhancement complete")
        status_msg.content = "✅ Step 3/4: Content enhancement completed!\n✨ Added examples and simplified explanations."
        await status_msg.update()
        await cl.sleep(2)

        
        # STEP 4: FINAL REPORT GENERATION
        
        status_msg.content = "📝 Step 4/4: Generating final report...\nCompiling comprehensive research document..."
        await status_msg.update()
        await cl.sleep(2)
        
        reporter_agent = Agent(
            name="Reporter Agent",
            instructions="""You are a professional report writer. Your role is to:
            1. Synthesize all previous research and enhanced content
            2. Create a well-structured, comprehensive report
            3. Organize information logically with clear sections
            4. Write in a professional, clear, and engaging style
            5. Include all key findings, insights, and recommendations
            
            Your report should include:
            - Executive Summary: Brief overview of key findings
            - Key Findings: Main discoveries from the research
            - Detailed Analysis: In-depth exploration of the topic
            - Examples and Use Cases: Practical applications
            - Conclusions: Summary and recommendations
            - Sources: List of references
            
            Write in a professional tone suitable for business or academic audiences.
            Ensure the report is comprehensive, well-organized, and actionable.""",
            model=model
        )

        report_input = f"""
        Generate a comprehensive research report for: {message.content}
        
        Initial Research Summary:
        {initial_result.final_output}
            
        Deep Research Insights:
        {deep_result.final_output}
        
        Enhanced Content:
        {enhanced_result.final_output}    
        
        Create a professional, comprehensive report incorporating all this information.
        """
        
        final_result = await Runner.run(
            reporter_agent,
            report_input,
            max_turns=2
        )
        
        print("✓ Final report generated successfully!")
        status_msg.content = "✅ Step 4/4: Final report generated successfully!"
        await status_msg.update()

        # Send the final report
        await cl.Message(content=f"# Research Report: {message.content}\n\n{final_result.final_output}").send()
        
        # Send completion message
        await cl.Message(content="✅ **Research completed successfully!**\n\nYou can ask follow-up questions or start a new research query.").send()

    except Exception as e:
        # Detailed error handling
        error_details = traceback.format_exc()
        error_msg = f"""❌ **An error occurred during the research process**

**Error Type:** {type(e).__name__}
**Error Message:** {str(e)}

**What you can try:**
1. Check if the MCP server is running at {MCP_SERVER_URL}
2. Verify your API keys are set correctly in the .env file
3. Try rephrasing your query
4. Refresh the page and try again

If the problem persists, please check the console logs for more details."""

        print(f"Error occurred: {error_details}")
        
        # Update status message with error
        status_msg.content = "❌ Research process failed. See error details below."
        await status_msg.update()
        
        # Send error message
        await cl.Message(content=error_msg).send()

    finally:
        # Clean up or final logging
        print("Research process completed or terminated")