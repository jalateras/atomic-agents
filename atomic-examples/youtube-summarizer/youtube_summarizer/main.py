import os
from dotenv import load_dotenv
from rich.console import Console

from atomic_agents.agents.base_agent import (
    BaseAgent,
    BaseAgentConfig,
    BaseAgentInputSchema,
    BaseAgentOutputSchema,
)
from atomic_agents.lib.components.agent_memory import AgentMemory

from youtube_summarizer.tools.youtube_transcript_scraper import (
    YouTubeTranscriptTool,
    YouTubeTranscriptToolConfig,
    YouTubeTranscriptToolInputSchema,
)

from youtube_summarizer.agent import YouTubeKnowledgeExtractionInputSchema, youtube_knowledge_extraction_agent, transcript_provider

import openai
import instructor

load_dotenv()

# Initialize a Rich Console for pretty console outputs
console = Console()

# Memory setup
memory = AgentMemory()

# Initialize memory with an initial message from the assistant
initial_message = BaseAgentOutputSchema(
    chat_message="Hello! I can help you fetch YouTube transcripts. How can I assist you today?"
)
memory.add_message("assistant", initial_message)

# Initialize the YouTubeTranscriptTool
transcript_tool = YouTubeTranscriptTool(
    config=YouTubeTranscriptToolConfig(api_key=os.getenv("YOUTUBE_API_KEY"))
)

# Initialize the BaseAgent
agent = BaseAgent(
    config=BaseAgentConfig(
        client=instructor.from_openai(openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))),
        model="gpt-4o-mini",
        memory=memory,
    )
)

# Remove the infinite loop and perform a one-time transcript extraction
video_url = "https://www.youtube.com/watch?v=iHwptVCfxyg"

transcript_input = YouTubeTranscriptToolInputSchema(
    video_url=video_url, language="en"
)
try:
    transcript_output = transcript_tool.run(transcript_input)
    console.print(f"[bold green]Transcript:[/bold green] {transcript_output.transcript}")
    console.print(f"[bold green]Duration:[/bold green] {transcript_output.duration} seconds")

    # Update transcript_provider with the scraped transcript data
    transcript_provider.transcript = transcript_output.transcript
    transcript_provider.duration = transcript_output.duration
    transcript_provider.metadata = transcript_output.metadata  # Assuming metadata is available in transcript_output

    # Run the transcript through the agent
    transcript_input_schema = YouTubeKnowledgeExtractionInputSchema(video_url=video_url)
    agent_response = youtube_knowledge_extraction_agent.run(transcript_input_schema)

    # Print the output schema in a formatted way
    console.print("[bold blue]Agent Output Schema:[/bold blue]")
    console.print(agent_response)
except Exception as e:
    console.print(f"[bold red]Error:[/bold red] {str(e)}")
