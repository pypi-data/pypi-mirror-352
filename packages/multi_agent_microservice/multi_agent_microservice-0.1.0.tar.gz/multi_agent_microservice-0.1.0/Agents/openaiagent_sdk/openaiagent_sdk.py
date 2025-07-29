import os
import uuid
import asyncio
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

from agents import (
    Agent,
    Runner,
    WebSearchTool,
    function_tool,
    handoff,
    trace,
)

from pydantic import BaseModel, Field
from typing import List, Dict, Optional

# Load environment variables
load_dotenv()

# Set up page configuration
st.set_page_config(
    page_title="Egg Price Researcher",
    page_icon="🥚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Make sure API key is set
if not os.environ.get("OPENAI_API_KEY"):
    st.error("Please set your OPENAI_API_KEY environment variable")
    st.stop()

# App title and description
st.title("🥚 Egg Price Analyzer")
st.subheader("Powered by OpenAI Agents SDK")
st.markdown("""
This app researches current egg prices in your specified city, comparing different brands, 
types (organic, free-range, etc.), and retailers to help you find the best deals.
""")

# Define data models
class EggResearchPlan(BaseModel):
    city: str
    search_queries: List[str]
    focus_areas: List[str]

class EggPriceData(BaseModel):
    store_name: str
    egg_type: str
    price: float
    unit: str  # dozen, half-dozen, etc.
    date_found: str

class EggPriceReport(BaseModel):
    title: str = Field(..., description="The title of the report")
    city: str = Field(..., description="The city researched")
    summary: str = Field(..., description="A summary of the findings")
    price_breakdown: str = Field(..., description="A textual breakdown of price findings")
    cheapest_option: str = Field(..., description="Description of the cheapest egg option found")
    premium_options: List[str] = Field(..., description="List of premium egg options")
    price_comparison: str = Field(..., description="Comparison of different egg prices")
    shopping_recommendations: List[str] = Field(..., description="List of shopping recommendations")
    sources: List[str] = Field(..., description="List of sources used in research")
    full_report: str = Field(..., description="The complete markdown report")

# Custom tool for saving egg price data
@function_tool
def save_egg_price(store_name: str, egg_type: str, price: float, unit: str, source: str = None) -> str:
    """Save egg price data discovered during research.

    Args:
        store_name: Name of the store or retailer
        egg_type: Type of eggs (regular, organic)
        price: Price in local currency
        unit: Unit of sale (dozen, half-dozen, etc.)
        source: Optional source of the price information

    Returns:
        Confirmation message
    """
    if "collected_prices" not in st.session_state:
        st.session_state.collected_prices = []

    st.session_state.collected_prices.append({
        "store_name": store_name,
        "egg_type": egg_type,
        "price": price,
        "unit": unit,
        "source": source or "Not specified",
        "date_found": datetime.now().strftime("%Y-%m-%d")
    })

    return f"Price saved: {egg_type} eggs at {store_name} - ${price} per {unit}"

# Define the agents
# Updated price_research_agent to focus on finding the cheapest egg options
price_research_agent = Agent(
    name="Price Research Agent",
    instructions="""You are a specialized egg price researcher. Your task is to capture atleast six prices for a dozen eggs in a specific city and collect detailed information by scraping retail websites.
    
    PRIORITY FOCUS:
    - Find the absolute cheapest eggs available in the city
    - DO NOT collect or report average prices across the city
    - Focus only on the prices for a dozen eggs with two types: regular and organic
    
    PRIORITY WEBSITES TO CHECK:
    - Walmart.com: Search for the store location in the target city, navigate to grocery/dairy/eggs
    - Target.com: Find stores in the target city and check their egg inventory and pricing
    - Local grocery chain websites: Check weekly ads/circulars for egg specials and promotions
    
    SCRAPING INSTRUCTIONS:
    1. Check store brand/generic options which are typically cheaper
    2. For each specific store location and egg type found, record:
       - Store name and location 
       - Exact egg type and size
       - Date of the pricing and exact URL source
    4. Use the save_egg_price tool to record atleast 10 actual prices with 7 cheapest and 3 most expensive from specific stores.

    QUALITY REQUIREMENTS:
    - All prices must be current (within the past week ONLY)
    - Each price must be verifiable with a direct link where possible

    Return the response in the most concise folrmat withoout using extra words and capturing minimum six prices.
    """,
    model="gpt-4o-mini",
    tools=[
        WebSearchTool(),
        save_egg_price
    ],
)

analysis_agent = Agent(
    name="Price Analysis Agent",
    handoff_description="An analyst who identifies trends, compares prices, and makes recommendations",
    instructions="""You are an egg price analyst tasked with making sense of collected egg price data.
    
    Your analysis should include:
    1. Identification of the cheapest options available in the city
    2. Comparison of different egg types (organic vs. regular, etc.)
    3. Price range analysis across different retailers
    4. Value assessment (factoring in quality, egg type, and price)
    5. Shopping recommendations based on different consumer priorities (budget, quality, etc.)
    
    Create a comprehensive report that includes all required fields:
    - title: A descriptive title for the report
    - city: The city researched
    - summary: Brief overview of findings (1-2 paragraphs)
    - price_breakdown: Detailed textual breakdown of prices found
    - cheapest_option: Description of the cheapest egg option found
    - premium_options: List of premium egg options with details
    - price_comparison: Text comparing prices across stores and egg types
    - shopping_recommendations: List of actionable recommendations
    - sources: List of all sources used in research
    - full_report: The complete analysis in markdown format
    
    Use markdown formatting for clarity. Avoid the dollar sign in your response. Your analysis should be detailed but accessible to
    regular consumers looking to make informed purchasing decisions.
    """,
    model="gpt-4o-mini",
    output_type=EggPriceReport,
)

Master_agent = Agent(
    name="Master Agent",
    instructions="""You are the coordinator of this egg price research operation. Your job is to:
    1. Understand the user's city of interest
    2. Create a research plan with the following elements:
       - city: The target city for egg price research
       - search_queries: A list of 3-5 specific search queries that will help gather price information
       - focus_areas: A list of 3-5 key areas to investigate (types of stores, egg varieties, etc.)
    3. Hand off to the Price Research Agent to collect price data
    4. After research is complete, hand off to the Price Analysis Agent to analyze findings and write a report
    
    Make sure to return your plan in the expected structured format with city, search_queries, and focus_areas.
    Be specific in your search queries, including the city name and current year to ensure recent data.
    """,
    handoffs=[
        handoff(price_research_agent),
        handoff(analysis_agent)
    ],
    model="gpt-4o-mini",
    output_type=EggResearchPlan,
)

# Create sidebar for input and controls
with st.sidebar:
    st.header("Egg Price Research")
    user_city = st.text_input(
        "Enter a city to research egg prices:",
        placeholder="e.g., Chicago, IL"
    )

    start_button = st.button("Start Research", type="primary", disabled=not user_city)

    st.divider()
    st.subheader("Example Cities")
    example_cities = [
        "New York City, NY",
        "Raleigh, NC",
        "Seattle, WA",
        "Miami, FL"
    ]

    for city in example_cities:
        if st.button(city):
            user_city = city
            start_button = True

# Main content area with three tabs
tab1, tab2, tab3 = st.tabs(["Research Process", "Price Data", "Final Report"])

# Initialize session state for storing results
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4().hex[:16])
if "collected_prices" not in st.session_state:
    st.session_state.collected_prices = []
if "research_done" not in st.session_state:
    st.session_state.research_done = False
if "report_result" not in st.session_state:
    st.session_state.report_result = None

# Main research function
async def run_egg_price_research(city):
    # Reset state for new research
    st.session_state.collected_prices = []
    st.session_state.research_done = False
    st.session_state.report_result = None

    with tab1:
        message_container = st.container()

    # Create error handling container
    error_container = st.empty()

    # Create a trace for the entire workflow
    with trace("Egg Price Research", group_id=st.session_state.conversation_id):
        # Start with the Master agent
        with message_container:
            st.write("🔍 **Master Agent**: Planning research approach...")

        Master_result = await Runner.run(
            Master_agent,
            f"Research current egg prices in {city}. Find prices for different types of eggs (regular, organic, etc.) at various retailers."
        )

        # Check if the result is an EggResearchPlan object or a string
        if hasattr(Master_result.final_output, 'city'):
            research_plan = Master_result.final_output
            plan_display = {
                "city": research_plan.city,
                "search_queries": research_plan.search_queries,
                "focus_areas": research_plan.focus_areas
            }
        else:
            # Fallback if we don't get the expected output type
            research_plan = {
                "city": city,
                "search_queries": [f"Current egg prices in {city}", f"Organic egg prices {city}", f"Cheapest eggs in {city}"],
                "focus_areas": ["Supermarket prices", "Farmers market eggs", "Organic vs conventional comparison"]
            }
            plan_display = research_plan

        with message_container:
            st.write("📋 **Research Plan**:")
            st.json(plan_display)

        # Display prices as they're collected
        price_placeholder = message_container.empty()

        # Check for new prices periodically
        previous_price_count = 0
        for i in range(20):  # Check more times to allow for more comprehensive research
            current_prices = len(st.session_state.collected_prices)
            if current_prices > previous_price_count:
                with price_placeholder.container():
                    st.write("🥚 **Collected Prices**:")
                    for price in st.session_state.collected_prices:
                        st.info(f"**Store**: {price['store_name']}\n\n**Type**: {price['egg_type']}\n\n**Price**: ${price['price']} per {price['unit']}\n\n**Source**: {price['source']}")
                previous_price_count = current_prices
            await asyncio.sleep(1)

        # Analysis Agent phase
        with message_container:
            st.write("📊 **Price Analysis Agent**: Creating comprehensive price report...")

        try:
            report_result = await Runner.run(
                analysis_agent,
                Master_result.to_input_list()
            )

            st.session_state.report_result = report_result.final_output

            with message_container:
                st.write("✅ **Research Complete! Price Report Generated.**")

                # Preview a snippet of the report
                if hasattr(report_result.final_output, 'summary'):
                    report_preview = report_result.final_output.summary
                else:
                    report_preview = str(report_result.final_output)[:300] + "..."

                st.write("📄 **Report Preview**:")
                st.markdown(report_preview)
                st.write("*See the Final Report tab for the full analysis.*")

        except Exception as e:
            st.error(f"Error generating report: {str(e)}")
            # Fallback to display raw agent response
            if hasattr(Master_result, 'new_items'):
                messages = [item for item in Master_result.new_items if hasattr(item, 'content')]
                if messages:
                    raw_content = "\n\n".join([str(m.content) for m in messages if m.content])
                    st.session_state.report_result = raw_content

                    with message_container:
                        st.write("⚠️ **Research completed but there was an issue generating the structured report.**")
                        st.write("Raw research results are available in the Final Report tab.")

    st.session_state.research_done = True

# Run the research when the button is clicked
if start_button:
    with st.spinner(f"Researching egg prices in: {user_city}"):
        try:
            asyncio.run(run_egg_price_research(user_city))
        except Exception as e:
            st.error(f"An error occurred during research: {str(e)}")
            # Set a basic report result so the user gets something
            st.session_state.report_result = f"# Egg Price Research for {user_city}\n\nUnfortunately, an error occurred during the research process. Please try again later or with a different city.\n\nError details: {str(e)}"
            st.session_state.research_done = True

# Display collected price data in the Price Data tab
with tab2:
    if "collected_prices" in st.session_state and st.session_state.collected_prices:
        st.header(f"Egg Prices in {user_city}")

        # Create a dataframe for better visualization
        import pandas as pd
        price_data = pd.DataFrame(st.session_state.collected_prices)

        # Display the raw data
        st.subheader("Raw Price Data")
        st.dataframe(price_data)

        # Add some visualizations if we have enough data
        if len(price_data) >= 3:
            st.subheader("Price Comparisons")

            # Group by store and egg type
            try:
                # Bar chart by store
                st.bar_chart(price_data.groupby('store_name')['price'].mean())

                # Bar chart by egg type
                st.bar_chart(price_data.groupby('egg_type')['price'].mean())
            except:
                st.write("Not enough data for meaningful visualizations.")

        # Add download button for the raw data
        csv = price_data.to_csv(index=False)
        st.download_button(
            label="Download Price Data (CSV)",
            data=csv,
            file_name=f"egg_prices_{user_city.replace(' ', '_')}.csv",
            mime="text/csv"
        )

# Display results in the Final Report tab
with tab3:
    if st.session_state.research_done and st.session_state.report_result:
        report = st.session_state.report_result

        # Handle different possible types of report results
        if hasattr(report, 'title'):
            # We have a properly structured EggPriceReport object
            st.title(report.title)

            # Display city and summary
            # st.header(f"Egg Prices in {report.city}")
            st.markdown(report.summary)

            # Display price breakdown in a more visual way
            st.subheader("Price Breakdown")
            st.markdown(report.price_breakdown)

            col1, col2 = st.columns(2)
            with col1:
                st.write("**Cheapest Option:**")
                st.success(report.cheapest_option)
            with col2:
                st.write("**Premium Options:**")
                for option in report.premium_options:
                    st.info(option)

            # Price comparison section
            st.subheader("Price Comparison")
            st.markdown(report.price_comparison)

            # Shopping recommendations
            st.subheader("Shopping Recommendations")
            for i, rec in enumerate(report.shopping_recommendations):
                st.markdown(f"{i+1}. {rec}")


            # Display the full report in markdown
            st.subheader("Full Analysis")
            if hasattr(report, 'full_report'):
                report_content = report.full_report
                st.markdown(report_content)
            else:
                report_content = str(report)
                st.markdown(report_content)

            # Display sources if available
            if hasattr(report, 'sources') and report.sources:
                with st.expander("Sources"):
                    for i, source in enumerate(report.sources):
                        st.markdown(f"{i+1}. {source}")

            # Add download button for the report
            st.download_button(
                label="Download Full Report",
                data=report_content,
                file_name=f"Egg_Price_Report_{report.city.replace(' ', '_')}.md",
                mime="text/markdown"
            )
        else:
            # Handle string or other type of response
            report_content = str(report)
            title = f"Egg Price Report for {user_city}"

            st.title(title)
            st.markdown(report_content)

            # Add download button for the report
            st.download_button(
                label="Download Report",
                data=report_content,
                file_name=f"Egg_Price_Report_{user_city.replace(' ', '_')}.md",
                mime="text/markdown"
            )