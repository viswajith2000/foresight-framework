import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os
from main import DRIForesightProcessor, initialize_processor
from dotenv import load_dotenv
import base64

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="DRI Foresight Framework",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to match the original design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }
    


    /* Hide Streamlit branding but keep sidebar controls */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
   
    /* Keep sidebar toggle visible */
    .css-1rs6os, .css-17ziqus {visibility: visible !important;}
    
    /* Custom Header */
    .main-header {
        background: linear-gradient(135deg, #1a237e 0%, #3f51b5 100%);
        color: white;
        padding: 1rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 10px 10px;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Phase Progress */
    .phase-progress {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .progress-bar {
        background: #e0e0e0;
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .progress-fill {
        background: #4caf50;
        height: 100%;
        transition: width 0.3s ease;
    }
    
    /* AI Cards */
    .ai-card {
        background: #f5f7fa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .ai-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }
    
    .ai-badge {
        background: #673ab7;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    /* Content Cards */
    .content-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .content-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-1px);
        transition: all 0.3s;
    }
    
    /* Signal Cards */
    .signal-card {
        background: #f8f9fa;
        border-left: 4px solid #1976d2;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    
    .signal-card.strong {
        border-left-color: #4caf50;
        background: #f1f8e9;
    }
    
    .signal-card.weak {
        border-left-color: #ff9800;
        background: #fff8e1;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 6px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton > button[kind="primary"] {
        background: #1976d2;
    }
    
    .stButton > button[kind="secondary"] {
        background: #f5f7fa;
        color: #333;
        border: 1px solid #ddd;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
        border-radius: 6px 6px 0 0;
    }
    
    /* Error and success messages */
    .error-message {
        background: #ffebee;
        color: #c62828;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .success-message {
        background: #e8f5e8;
        color: #2e7d32;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if 'current_phase' not in st.session_state:
        st.session_state.current_phase = 1
    if 'completed_phases' not in st.session_state:
        st.session_state.completed_phases = []
    if 'project_data' not in st.session_state:
        st.session_state.project_data = {}
    if 'domain_map' not in st.session_state:
        st.session_state.domain_map = {}
    if 'custom_questions' not in st.session_state:
        st.session_state.custom_questions = []
    if 'signals_data' not in st.session_state:
        st.session_state.signals_data = {}
    if 'steepv_analysis' not in st.session_state:
        st.session_state.steepv_analysis = {}
    # if 'editable_steepv' not in st.session_state:
    #     st.session_state.editable_steepv = {}
    if 'custom_signals' not in st.session_state:
        st.session_state.custom_signals = []
    if 'uploaded_documents' not in st.session_state:
        st.session_state.uploaded_documents = {}
    if 'futures_triangle' not in st.session_state:
        st.session_state.futures_triangle = {}
    if 'editable_futures_triangle' not in st.session_state:
        st.session_state.editable_futures_triangle = {}
    if 'interview_files' not in st.session_state:
        st.session_state.interview_files = {}
    if 'interview_analysis' not in st.session_state:
        st.session_state.interview_analysis = {}
    if 'full_interview_text' not in st.session_state:
        st.session_state.full_interview_text = ""
    if 'groq_api_key' not in st.session_state:
        st.session_state.groq_api_key = os.getenv('GROQ_API_KEY')

initialize_session_state()

# Main Header
st.markdown("""
<div class="main-header">
    <h1>🔮 DRI Foresight Framework</h1>
</div>
""", unsafe_allow_html=True)

with st.sidebar:   
    # Progress Indicator
    progress_percentage = (len(st.session_state.completed_phases) / 2) * 100  # Only 2 phases for now
    st.markdown(f"""
    <div class="phase-progress">
        <h3>Project Progress</h3>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress_percentage}%"></div>
        </div>
        <p style="margin-top: 0.5rem; font-size: 0.9rem; color: #666;">
            {int(progress_percentage)}% Complete
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Phase Navigation
    # Phase Navigation
    st.markdown('<div><h3>Framework Phases</h3>', unsafe_allow_html=True)

    # Add consistent CSS for all phase buttons
    st.markdown("""
    <style>
    div[data-testid="stButton"] button {
        width: 100% !important;
        height: 50px !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        margin-bottom: 8px !important;
    }

    /* Style for current phase (red) */
    div[data-testid="stButton"] button[kind="primary"] {
        background-color: #dc3545 !important;
        border-color: #dc3545 !important;
        color: white !important;
    }

    /* Style for other phases */
    div[data-testid="stButton"] button[kind="secondary"] {
        background-color: #f8f9fa !important;
        border-color: #dee2e6 !important;
        color: #495057 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    phases = [
        (1, "1- Framing", "Define scope and domain"),
        (2, "2- Scanning", "Environmental analysis")
    ]

    for phase_num, phase_name, phase_desc in phases:
        # Determine phase status and styling
        if phase_num == st.session_state.current_phase:
            button_type = "primary"
        else:
            button_type = "secondary"
        
        disabled = False
        
        if st.button(f"{phase_num}. {phase_name}", key=f"phase_{phase_num}", help=phase_desc, disabled=disabled, type=button_type):
            st.session_state.current_phase = phase_num
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)



    # Export Options
    st.markdown("---")
    if st.button("📥 Export Project", type="secondary"):
        export_data = {
            "project_data": st.session_state.project_data,
            "domain_map": st.session_state.domain_map,
            "custom_questions": st.session_state.custom_questions,
            "signals_data": st.session_state.signals_data,
            "steepv_analysis": st.session_state.steepv_analysis,
            "custom_signals": st.session_state.custom_signals,
            "futures_triangle": st.session_state.futures_triangle
        }
        st.download_button(
            label="Download Project Data",
            data=json.dumps(export_data, indent=2),
            file_name=f"dri_foresight_project_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

# Phase 1: Framing
def render_phase_1():
    st.header("Phase 1: Framing")
    st.markdown("<p style='font-size: 1.1rem; color: #555; font-style: italic;'>Define the project scope, domain, and establish baseline understanding</p>", unsafe_allow_html=True)
    #i was comment out this line for solve the col 2 problem.
    # col1, col2 = st.columns([2, 1])
        
    #i was comment out this line for solve the col 2 problem.
    # with col1:
    # Project Setup
    st.subheader("Project Setup")
    st.markdown("<label style='font-size: 1.1rem; font-weight: 500;'>Project Name</label>", unsafe_allow_html=True)
    project_name = st.text_input(
        "Project Name", 
        placeholder="Enter project name",
        value=st.session_state.project_data.get('project_name', ''),
        label_visibility="collapsed"
    )

  
    if project_name:
        st.session_state.project_data['project_name'] = project_name

    # Domain selection with custom option
    domain_options = [
        "Choose a domain...",
        "Food Security & Self-Sufficiency",
        "Human Capital & TVET", 
        "SMEs & Fiscal Policy",
        "Custom Domain"
    ]
 
    st.markdown("<label style='font-size: 1.1rem; font-weight: 500;'>Select Domain Focus</label>", unsafe_allow_html=True)
    selected_domain = st.selectbox(
        "Select Domain Focus", 
        domain_options,
        index=domain_options.index(st.session_state.project_data.get('selected_domain', domain_options[0])) if st.session_state.project_data.get('selected_domain') in domain_options else 0,
        label_visibility="collapsed"
    )

    # Show custom input field when "Custom Domain" is selected
    st.markdown("<label style='font-size: 1.1rem; font-weight: 500;'>Enter Custom Domain</label>", unsafe_allow_html=True)
    if selected_domain == "Custom Domain":
        custom_domain = st.text_input(
            "Enter Custom Domain",
            placeholder="Describe your custom domain focus...",
            help="Specify the domain you want to focus on for this project",
            value=st.session_state.project_data.get('custom_domain', ''),
            label_visibility="collapsed"
        )
        final_domain = custom_domain if custom_domain else "Custom Domain"
        if custom_domain:
            st.session_state.project_data['custom_domain'] = custom_domain
    else:
        final_domain = selected_domain

    # Store domain selection
    st.session_state.project_data['selected_domain'] = selected_domain
    st.session_state.project_data['final_domain'] = final_domain

    # Display the selected domain
    if final_domain and final_domain != "Choose a domain...":
        st.success(f"Selected Domain: {final_domain}")
    
    # PDF Upload
    st.subheader("Upload Draft Domain Map")
    st.markdown("<label style='font-size: 1.1rem; font-weight: 500;'>Choose document files</label>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Choose document files",
        type=['pdf', 'docx', 'doc', 'pptx', 'ppt', 'jpg', 'jpeg', 'png', 'bmp', 'gif'],
        accept_multiple_files=True,
        help="Upload PDF, Word documents, PowerPoint presentations, or images related to your project domain",
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} document file(s) uploaded successfully")
        
        # Store uploaded files in session state
        for file in uploaded_files:
            st.session_state.uploaded_documents[file.name] = file
    
    # AI Domain Map Generation
    st.subheader("Domain Map Development")
    st.markdown("""
    <div class="ai-card">
        <div class="ai-header">
            <div>
                <h4>AI-Generated Domain Map</h4>
                <p style="font-size: 0.9rem; color: #666;">Based on your uploaded documents and selected domain</p>
            </div>
            <span class="ai-badge">AI Assistant</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we can generate domain map
    can_generate = (
        os.getenv('GROQ_API_KEY') and 
        final_domain and 
        final_domain != "Choose a domain..." and
        uploaded_files and 
        project_name
    )
    
    if st.button("🤖 Generate Domain Map", type="primary", disabled=not can_generate):
        if not can_generate:
            if not os.getenv('GROQ_API_KEY'):
                st.error("Groq API key not found. Please add GROQ_API_KEY to your .env file")
            elif not final_domain or final_domain == "Choose a domain...":
                st.error("Please select or enter a domain")
            elif not uploaded_files:
                st.error("Please upload PDF documents")
            elif not project_name:
                st.error("Please enter a project name")
        else:
            try:
                with st.spinner("Generating domain map..."):
                    # Initialize processor
                    processor = initialize_processor()
                    
                    # Extract text from all uploaded PDFs
                    all_text = ""
                    for file in uploaded_files:
                        file.seek(0)  # Reset file pointer
                        text = processor.extract_text_from_file(file)
                        all_text += text + "\n\n"
                    
                    # Generate domain map
                    domain_map = processor.generate_domain_map(
                        final_domain, 
                        all_text, 
                        project_name
                    )
                    
                    if 'error' not in domain_map:
                        st.session_state.domain_map = domain_map
                        st.success("Domain map generated successfully!")
                    else:
                        st.error(f"Error: {domain_map['error']}")
                        
            except Exception as e:
                st.error(f"Failed to generate domain map: {str(e)}")

    # Display generated domain map
    if st.session_state.domain_map and 'error' not in st.session_state.domain_map:
        domain_map = st.session_state.domain_map
        
        # Always show TEXT FORMAT first
        if 'central_domain' in domain_map:
            # Display as formatted text (original style)
            st.markdown(f"""
            <div class="content-card">
                <h4>Central Domain: {domain_map.get('central_domain', 'Domain Analysis')}</h4>
                <p style="font-size: 1.1rem;"><em>{domain_map.get('description', '')}</em></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display sub-domains as text
            #changed the size for the text
            if 'sub_domains' in domain_map and domain_map['sub_domains']:
                st.markdown("### Sub-domains:")
                for sub_domain in domain_map['sub_domains']:
                    st.markdown(f"""
                    <div style="font-size: 1.1rem;">
                    <strong>{sub_domain.get('name', 'Sub-domain')}</strong><br>
                    {sub_domain.get('description', '')}<br>
                    <strong>Relevance: {sub_domain.get('relevance', 'Medium')}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("---")
            
            #changed the size for the text
            # Display interconnections as text
            if 'interconnections' in domain_map and domain_map['interconnections']:
                st.markdown("### Key Interconnections:")
                for interconnection in domain_map['interconnections']:
                    # st.markdown(f"• {interconnection}")
                    st.markdown(f"<div style='font-size: 1.1rem;'>• {interconnection}</div>", unsafe_allow_html=True)
        
        elif 'raw_response' in domain_map:
            # Display raw text response
            raw_response = domain_map['raw_response']
            try:
                import json
                import re
                
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_response, re.DOTALL)
                if json_match:
                    json_data = json.loads(json_match.group(1))
                    
                    st.markdown(f"""
                    <div class="content-card">
                        <h4>Central Domain: {json_data.get('central_domain', 'Domain Analysis')}</h4>
                        <p><em>{json_data.get('description', '')}</em></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if 'sub_domains' in json_data:
                        st.markdown("### Sub-domains:")
                        for sub_domain in json_data['sub_domains']:
                            st.markdown(f"""
                            **{sub_domain.get('name', 'Sub-domain')}**  
                            {sub_domain.get('description', '')}  
                            **Relevance: {sub_domain.get('relevance', 'Medium')}**
                            """)
                            st.markdown("---")
                    
                    if 'interconnections' in json_data:
                        st.markdown("### Key Interconnections:")
                        for interconnection in json_data['interconnections']:
                            st.markdown(f"• {interconnection}")
                else:
                    # Display raw content
                    st.markdown(f"""
                    <div class="content-card">
                        <h4>Domain Analysis</h4>
                        <div style="white-space: pre-wrap; font-size: 0.9rem; line-height: 1.6;">
                            {raw_response}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            except Exception as e:
                st.markdown(f"""
                <div class="content-card">
                    <h4>Domain Analysis</h4>
                    <div style="white-space: pre-wrap; font-size: 0.9rem; line-height: 1.6;">
                        {raw_response}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        else:
            # Display whatever structure exists
            st.json(domain_map)
        #graphic view for domain map start here
        # Single button for graphics view
        st.markdown("---")
        show_graphics_button = st.button("🎨 View Graphic Format", type="primary", key="show_graphics_view")
        
        # Show graphics view if button was clicked
        if show_graphics_button:
            st.markdown("### 🎨 Domain Map Graphic ")
            
            # Prepare data for D3.js visualization
            if 'central_domain' in domain_map:
                central_domain = domain_map.get('central_domain', 'Central Domain')
                sub_domains = domain_map.get('sub_domains', [])
                interconnections = domain_map.get('interconnections', [])
            elif 'raw_response' in domain_map:
                # Try to extract JSON from raw response
                raw_response = domain_map['raw_response']
                
                try:
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_response, re.DOTALL)
                    if json_match:
                        json_data = json.loads(json_match.group(1))
                        central_domain = json_data.get('central_domain', 'Central Domain')
                        sub_domains = json_data.get('sub_domains', [])
                        interconnections = json_data.get('interconnections', [])
                    else:
                        # If no JSON found, create a simple structure
                        central_domain = "Domain Analysis"
                        sub_domains = []
                        interconnections = []
                except:
                    central_domain = "Domain Analysis"
                    sub_domains = []
                    interconnections = []
            else:
                central_domain = "Domain Analysis"
                sub_domains = []
                interconnections = []
            
            # Convert Python data to JSON strings for JavaScript
            import json
            sub_domains_json = json.dumps(sub_domains)
            interconnections_json = json.dumps(interconnections)
            
            # Create D3.js visualization
            # Create D3.js visualization
            # Replace the existing st.components.v1.html() section in your domain map code with this updated version:

            st.components.v1.html(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://d3js.org/d3.v7.min.js"></script>
                <style>

                    body {{
                        margin: 0;
                        padding: 0;
                        font-family: 'Arial', sans-serif;
                        background: white;
                        overflow-x: auto;
                        height: 100%;
                    }}
                    
                    #visualization {{
                        width: 1400px;
                        height: 900px;
                        margin: 10px auto 0 auto;
                        display: block;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                        border-radius: 15px;
                        overflow: hidden;
                        background: white;
                    }}
                    
                    .bubble {{
                        cursor: pointer;
                        stroke: white;
                        stroke-width: 2;
                    }}
                    
                    .bubble:hover {{
                        stroke-width: 4;
                        opacity: 0.9;
                    }}
                    
                    .bubble-text {{
                        text-anchor: middle;
                        dominant-baseline: central;
                        pointer-events: none;
                        font-family: 'Arial', sans-serif;
                        font-weight: bold;
                        fill: white;
                    }}
                    
                    .central-bubble {{
                        stroke-width: 4;
                        stroke: #34495e;
                    }}
                    
                    .central-text {{
                        font-size: 18px;
                        font-weight: 900;
                    }}
                    
                    .tooltip {{
                        position: absolute;
                        padding: 15px;
                        background: rgba(255, 255, 255, 0.98);
                        border: none;
                        border-radius: 12px;
                        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
                        pointer-events: none;
                        font-size: 14px;
                        font-family: 'Arial', sans-serif;
                        max-width: 300px;
                        z-index: 1000;
                        border: 2px solid #3498db;
                    }}
                    
                    .tooltip h4 {{
                        margin: 0 0 10px 0;
                        color: #2c3e50;
                        font-size: 16px;
                        font-weight: bold;
                    }}
                    
                    .tooltip p {{
                        margin: 5px 0;
                        color: #34495e;
                        line-height: 1.4;
                    }}
                    
                    .title {{
                        text-anchor: middle;
                        font-size: 28px;
                        font-weight: bold;
                        fill: #2c3e50;
                        font-family: 'Arial Black', sans-serif;
                    }}
                    
                    .legend {{
                        font-size: 14px;
                        font-weight: 600;
                        font-family: 'Arial', sans-serif;
                    }}
                </style>
            </head>
            <body>
                <div id="visualization"></div>
                <script>
                    // Get data from Python - using your actual domain map data
                    const centralDomain = "{central_domain}";
                    const subDomains = {sub_domains_json};
                    
                    // Function to categorize domains based on keywords and content
                    function categorizeDomain(domainName, description = "") {{
                        const name = domainName.toLowerCase();
                        const desc = description.toLowerCase();
                        const combined = name + " " + desc;
                        
                        // Define keywords for each category
                        const categories = {{
                            "Education & Skills": ["education", "learning", "training", "skill", "university", "school", "curriculum", "teacher", "student", "tvet", "literacy", "stem", "academic", "research", "knowledge"],
                            "Technology & Infrastructure": ["technology", "infrastructure", "digital", "internet", "network", "cloud", "computing", "hardware", "software", "data", "cyber", "tech", "platform", "system"],
                            "Healthcare & Social": ["health", "medical", "healthcare", "hospital", "clinic", "patient", "treatment", "social", "community", "public", "safety", "welfare"],
                            "Economic & Business": ["economic", "business", "economy", "finance", "financial", "market", "trade", "commerce", "investment", "industry", "commercial", "startup", "entrepreneur"],
                            "Environment & Agriculture": ["environment", "climate", "green", "sustainable", "agriculture", "farming", "energy", "renewable", "carbon", "ecological", "nature", "conservation"],
                            "Governance & Policy": ["governance", "government", "policy", "regulation", "law", "legal", "compliance", "ethics", "framework", "standard", "guideline", "strategy"],
                            "Innovation & Research": ["innovation", "research", "development", "patent", "science", "laboratory", "experiment", "discovery", "breakthrough", "advancement"]
                        }};
                        
                        // Check which category has the most keyword matches
                        let bestCategory = "Technology & Infrastructure"; // default
                        let maxMatches = 0;
                        
                        for (const [category, keywords] of Object.entries(categories)) {{
                            const matches = keywords.filter(keyword => combined.includes(keyword)).length;
                            if (matches > maxMatches) {{
                                maxMatches = matches;
                                bestCategory = category;
                            }}
                        }}
                        
                        return bestCategory;
                    }}
                    
                    // Define color scheme for different domain categories
                    const colorScheme = {{
                        "Education & Skills": "#f1c40f",           // Yellow
                        "Technology & Infrastructure": "#27ae60",   // Green  
                        "Healthcare & Social": "#3498db",          // Blue
                        "Economic & Business": "#e67e22",          // Orange
                        "Environment & Agriculture": "#e74c3c",    // Red
                        "Governance & Policy": "#9b59b6",          // Purple
                        "Innovation & Research": "#1abc9c",        // Teal
                        "Central": "#2c3e50"                       // Dark gray for central
                    }};
                    
                    // Set up dimensions
                    const width = 1400;
                    const height = 900;
                    const margin = {{top: 60, right: 40, bottom: 120, left: 40}};
                    
                    // Create SVG
                    const svg = d3.select("#visualization")
                        .append("svg")
                        .attr("width", "70%")
                        .attr("height", "70%")
                        .attr("viewBox", `0 0 ${{width}} ${{height}}`)
                        .style("background", "white");
                    
                    // Add title
                    svg.append("text")
                        .attr("class", "title")
                        .attr("x", width / 2)
                        .attr("y", 40)
                        .text(centralDomain);
                    
                    // Prepare data for bubble chart
                    let bubbleData = [];
                    
                    // Add central domain
                    bubbleData.push({{
                        id: "central",
                        name: centralDomain,
                        category: "Central",
                        relevance: "Central",
                        size: 100,
                        color: colorScheme["Central"],
                        description: "Central Domain - Core focus area",
                        isCentral: true
                    }});
                    
                    // Process sub-domains from your actual data
                    subDomains.forEach((domain, i) => {{
                        const domainName = domain.name || `Sub-domain ${{i+1}}`;
                        const domainDesc = domain.description || "No description available";
                        const domainRelevance = domain.relevance || "Medium";
                        
                        // Automatically categorize based on domain content
                        const category = categorizeDomain(domainName, domainDesc);
                        
                        // Set size based on relevance
                        let size = 45; // Base size
                        if (domainRelevance === "High") size = 65;
                        else if (domainRelevance === "Medium") size = 55;
                        else if (domainRelevance === "Low") size = 40;
                        
                        bubbleData.push({{
                            id: `sub_${{i}}`,
                            name: domainName,
                            category: category,
                            relevance: domainRelevance,
                            size: size,
                            color: colorScheme[category] || "#95a5a6",
                            description: domainDesc,
                            isCentral: false
                        }});
                    }});
                    
                    // Create force simulation for bubble positioning
                    const simulation = d3.forceSimulation(bubbleData)
                        .force("charge", d3.forceManyBody().strength(-80))
                        .force("center", d3.forceCenter(width / 2, (height + margin.top - margin.bottom) / 2))
                        .force("collision", d3.forceCollide().radius(d => d.size + 4).strength(0.8))
                        .force("x", d3.forceX(width / 2).strength(0.1))
                        .force("y", d3.forceY((height + margin.top - margin.bottom) / 2).strength(0.1));
                    
                    // Create tooltip
                    const tooltip = d3.select("body")
                        .append("div")
                        .attr("class", "tooltip")
                        .style("opacity", 0);
                    
                    // Create bubbles
                    const bubbles = svg.selectAll(".bubble")
                        .data(bubbleData)
                        .enter()
                        .append("circle")
                        .attr("class", d => d.isCentral ? "bubble central-bubble" : "bubble")
                        .attr("r", d => d.size)
                        .style("fill", d => d.color)
                        .style("opacity", 0.85)
                        .on("mouseover", function(event, d) {{
                            // Highlight effect
                            d3.select(this)
                                .transition()
                                .duration(200)
                                .style("opacity", 1)
                                .attr("r", d.size * 1.1);
                            
                            // Show tooltip
                            let tooltipContent = `<h4>${{d.name}}</h4>`;
                            tooltipContent += `<p><strong>Category:</strong> ${{d.category}}</p>`;
                            if (!d.isCentral) {{
                                tooltipContent += `<p><strong>Relevance:</strong> ${{d.relevance}}</p>`;
                            }}
                            tooltipContent += `<p><strong>Description:</strong> ${{d.description}}</p>`;
                            
                            tooltip.transition()
                                .duration(200)
                                .style("opacity", 1);
                            tooltip.html(tooltipContent)
                                .style("left", (event.pageX + 15) + "px")
                                .style("top", (event.pageY - 15) + "px");
                        }})
                        .on("mousemove", function(event, d) {{
                            tooltip.style("left", (event.pageX + 15) + "px")
                                .style("top", (event.pageY - 15) + "px");
                        }})
                        .on("mouseout", function(event, d) {{
                            // Remove highlight
                            d3.select(this)
                                .transition()
                                .duration(200)
                                .style("opacity", 0.85)
                                .attr("r", d.size);
                            
                            // Hide tooltip
                            tooltip.transition()
                                .duration(200)
                                .style("opacity", 0);
                        }});
                    
                    // Add text labels with smart sizing
                    const labels = svg.selectAll(".bubble-text")
                        .data(bubbleData)
                        .enter()
                        .append("text")
                        .attr("class", d => d.isCentral ? "bubble-text central-text" : "bubble-text")
                        .style("font-size", d => {{
                            const baseSize = d.isCentral ? 16 : 12;
                            const textLength = d.name.length;
                            if (d.size < 50) return "10px";
                            if (textLength > 15) return Math.max(baseSize - 2, 10) + "px";
                            if (textLength > 10) return Math.max(baseSize - 1, 10) + "px";
                            return baseSize + "px";
                        }})
                        .text(d => {{
                            // Smart text truncation based on bubble size
                            const maxLength = d.size < 50 ? 8 : (d.size < 60 ? 12 : 15);
                            if (d.name.length > maxLength) {{
                                if (d.name.includes(" ")) {{
                                    const words = d.name.split(" ");
                                    return words[0].substring(0, maxLength);
                                }}
                                return d.name.substring(0, maxLength) + "...";
                            }}
                            return d.name;
                        }});
                    
                    // Add second line for wrapped text (for larger bubbles)
                    const labels2 = svg.selectAll(".bubble-text-2")
                        .data(bubbleData.filter(d => d.name.includes(" ") && d.size >= 55))
                        .enter()
                        .append("text")
                        .attr("class", "bubble-text")
                        .style("font-size", d => {{
                            const baseSize = d.isCentral ? 14 : 11;
                            return baseSize + "px";
                        }})
                        .attr("dy", "1.2em")
                        .text(d => {{
                            const words = d.name.split(" ");
                            const remaining = words.slice(1).join(" ");
                            const maxLength = d.size < 60 ? 10 : 12;
                            return remaining.length > maxLength ? remaining.substring(0, maxLength) + "..." : remaining;
                        }});
                    
                    // Update positions on simulation tick
                    simulation.on("tick", () => {{
                        bubbles
                            .attr("cx", d => Math.max(d.size, Math.min(width - d.size, d.x)))
                            .attr("cy", d => Math.max(d.size + margin.top, Math.min(height - d.size - margin.bottom, d.y)));
                        
                        labels
                            .attr("x", d => Math.max(d.size, Math.min(width - d.size, d.x)))
                            .attr("y", d => Math.max(d.size + margin.top, Math.min(height - d.size - margin.bottom, d.y)));
                        
                        labels2
                            .attr("x", d => Math.max(d.size, Math.min(width - d.size, d.x)))
                            .attr("y", d => Math.max(d.size + margin.top, Math.min(height - d.size - margin.bottom, d.y)));
                    }});
                    
                    // Create dynamic legend based on categories actually present in data
                    const categoriesInData = [...new Set(bubbleData.map(d => d.category))];
                    const legendData = categoriesInData.map(category => ({{
                        category: category,
                        color: colorScheme[category] || "#95a5a6",
                        count: bubbleData.filter(d => d.category === category).length
                    }}));
                    
                    const legend = svg.append("g")
                        .attr("class", "legend")
                        .attr("transform", `translate(50, ${{height - 100}})`);
                    
                    const legendItems = legend.selectAll(".legend-item")
                        .data(legendData)
                        .enter()
                        .append("g")
                        .attr("class", "legend-item")
                        .attr("transform", (d, i) => "translate(" + ((i % 4) * 300) + ", " + (Math.floor(i / 4) * 25) + ")");
                    
                    legendItems.append("circle")
                        .attr("r", 8)
                        .style("fill", d => d.color)
                        .style("stroke", "white")
                        .style("stroke-width", 2);
                    
                    legendItems.append("text")
                        .attr("x", 18)
                        .attr("y", 4)
                        .style("font-size", "12px")
                        .style("font-weight", "600")
                        .style("fill", "#2c3e50")
                        .text(d => `${{d.category}} (${{d.count}})`);
                    
                    // Initial animation
                    bubbles
                        .style("opacity", 0)
                        .attr("r", 0)
                        .transition()
                        .duration(1000)
                        .delay((d, i) => i * 50)
                        .style("opacity", 0.85)
                        .attr("r", d => d.size);
                    
                    labels
                        .style("opacity", 0)
                        .transition()
                        .duration(1000)
                        .delay((d, i) => i * 50 + 500)
                        .style("opacity", 1);
                    
                    labels2
                        .style("opacity", 0)
                        .transition()
                        .duration(1000)
                        .delay((d, i) => i * 50 + 500)
                        .style("opacity", 1);
                </script>
            </body>
            </html>
            """, width=1400, height=630)
            
            # Display interconnections below the visualization
            # Display interconnections below the visualization
            if interconnections:
                st.markdown("---")
                st.markdown("### 🔗 Key Interconnections")
                
                # Create enhanced cards for interconnections
                # cols = st.columns(3)  # Always create 3 columns
                cols = st.columns([1, 1, 1], gap="large")

                
                for i, interconnection in enumerate(interconnections):
                    with cols[i % 3]:
                        icon = ["🔄", "⚡", "🎯", "💡", "🚀", "🌟", "🔗", "📊"][i % 8]
                        st.markdown(f"""
                        <div style="
                            background: white;
                            border-radius: 15px;
                            padding: 25px;
                            min-height: 250px;
                            max-height: 250px;
                            box-shadow: 0 8px 25px rgba(0,0,0,0.08);
                            border-left: 5px solid #3498db;
                            transition: all 0.3s ease;
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            margin-bottom: 20px;
                        ">
                            <div style="
                                font-size: 32px; 
                                margin-bottom: 15px;
                                text-align: center;
                                flex-shrink: 0;
                            ">{icon}</div>
                            <div style="
                                overflow-y: auto;
                                overflow-x: hidden;
                                flex: 1;
                                width: 100%;
                                padding-right: 5px;
                            ">
                                <p style="
                                    margin: 0;
                                    color: #2c3e50;
                                    line-height: 1.6;
                                    font-size: 16px;
                                    text-align: center;
                                    font-weight: 500;
                                    padding-right: 5px;
                                ">{interconnection}</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            
            # Add controls info
            st.markdown("---")
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                margin: 20px 0;
            ">
                <h4 style="margin: 0 0 10px 0;">🎮 Interactive Controls</h4>
                <p style="margin: 5px 0;"><strong>🖱️ Hover:</strong> View detailed information</p>
                <p style="margin: 5px 0;"><strong>🖱️ Drag:</strong> Move nodes around</p>
                <p style="margin: 5px 0;"><strong>🔍 Scroll:</strong> Zoom in/out</p>
                <p style="margin: 5px 0;"><strong>🖱️ Pan:</strong> Click and drag background</p>
            </div>
            """, unsafe_allow_html=True)
        #i will place the mind map code here
        #ends here

    elif st.session_state.domain_map and 'error' in st.session_state.domain_map:
        st.error(f"Error generating domain map: {st.session_state.domain_map.get('error')}")
        if 'raw_response' in st.session_state.domain_map:
            with st.expander("View Raw Response (for debugging)"):
                st.text(st.session_state.domain_map['raw_response'])

    # Interview Data Upload
    st.subheader("🎤 Interview Data")
    st.markdown("<label style='font-size: 1.1rem; font-weight: 500;'>Upload interview transcripts or summaries</label>", unsafe_allow_html=True)
    interview_files = st.file_uploader(
        "Upload interview transcripts or summaries",
        type=['pdf', 'doc', 'docx', 'xlsx', 'xls', 'txt', 'mp3', 'wav', 'm4a'],
        accept_multiple_files=True,
        key="interviews",
        help="Upload interview transcripts, audio files, or summaries",
        label_visibility="collapsed"
    )
    
    if interview_files:
        # Store interview files in session state
        if 'interview_files' not in st.session_state:
            st.session_state.interview_files = {}
        
        # Clear existing files and add new ones
        st.session_state.interview_files.clear()
        for file in interview_files:
            st.session_state.interview_files[file.name] = file
        
        st.success(f"📁 {len(interview_files)} interview file(s) uploaded successfully")
        
        # Display uploaded files
        st.write("**Uploaded Interview Files:**")
        for filename in st.session_state.interview_files.keys():
            st.write(f"• {filename}")
        
        if st.button("📊 Analyze Interview Data", type="primary"):
            if os.getenv('GROQ_API_KEY'):
                try:
                    with st.spinner("Analyzing interview data..."):
                        processor = initialize_processor()
                        
                        # Extract text from all interview files
                        all_interview_text = ""
                        for file_name, file in st.session_state.interview_files.items():
                            file.seek(0)
                            if file_name.endswith('.pdf'):
                                text = processor.extract_text_from_file(file)
                            elif file_name.endswith(('.mp3', '.wav', '.m4a')):
                                # For audio files, you'll need to implement audio transcription
                                text = f"Audio file: {file_name} (transcription needed)"
                            else:
                                # For other text files
                                try:
                                    text = file.read().decode('utf-8')
                                except:
                                    text = f"Could not read {file_name}"
                            
                            all_interview_text += f"\n\n--- INTERVIEW FILE: {file_name} ---\n"
                            all_interview_text += text + "\n\n"
                        
                        # Store the FULL extracted text (NEW LINE)
                        st.session_state.full_interview_text = all_interview_text
                        
                        # Generate interview analysis (for display purposes only)
                        interview_analysis = processor.analyze_interview_data(
                            st.session_state.project_data.get('final_domain', ''),
                            all_interview_text
                        )
                        
                        if 'error' not in interview_analysis:
                            st.session_state.interview_analysis = interview_analysis
                            st.success("✅ Interview analysis completed!")
                            st.rerun()
                        else:
                            st.error("Failed to analyze interview data")
                            
                except Exception as e:
                    st.error(f"Failed to analyze interviews: {str(e)}")
            else:
                st.error("Please provide your Groq API key to analyze interviews")
    
    # Display interview analysis
    if st.session_state.get('interview_analysis'):
        st.subheader("📊 Interview Analysis Results")
        
        analysis_data = st.session_state.interview_analysis
        
        # Handle different response formats
        if 'raw_response' in analysis_data:
            try:
                import json
                import re
                
                raw_response = analysis_data['raw_response']
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_response, re.DOTALL)
                
                if json_match:
                    analysis_data = json.loads(json_match.group(1))
                else:
                    analysis_data = json.loads(raw_response)
                    
            except Exception as e:
                st.error(f"Error parsing interview analysis: {str(e)}")
                analysis_data = {}
        
        if analysis_data and 'error' not in analysis_data:
            col_challenges, col_opportunities, col_visions = st.columns([1, 1, 1], gap="large")

            
            with col_challenges:
                st.markdown("""
                <div style="
                    background: #ffebee;
                    border-left: 4px solid #e74c3c;
                    padding: 1rem;
                    border-radius: 4px;
                    margin-bottom: 1rem;
                ">
                    <h4 style="color: #c62828; margin: 0 0 0.5rem 0;">🎯 Top Challenges</h4>
                </div>
                """, unsafe_allow_html=True)
                
                challenges = analysis_data.get('challenges', [])
                for challenge in challenges:
                    st.markdown(f"<div style='font-size: 1.1rem;'>• {challenge}</div>", unsafe_allow_html=True)
            
            with col_opportunities:
                st.markdown("""
                <div style="
                    background: #e3f2fd;
                    border-left: 4px solid #2196f3;
                    padding: 1rem;
                    border-radius: 4px;
                    margin-bottom: 1rem;
                ">
                    <h4 style="color: #1976d2; margin: 0 0 0.5rem 0;">💡 Key Opportunities</h4>
                </div>
                """, unsafe_allow_html=True)
                
                opportunities = analysis_data.get('opportunities', [])
                for opportunity in opportunities:
                    st.markdown(f"<div style='font-size: 1.1rem;'>• {opportunity}</div>", unsafe_allow_html=True)
            
            with col_visions:
                st.markdown("""
                <div style="
                    background: #e8f5e8;
                    border-left: 4px solid #4caf50;
                    padding: 1rem;
                    border-radius: 4px;
                    margin-bottom: 1rem;
                ">
                    <h4 style="color: #2e7d32; margin: 0 0 0.5rem 0;">🔮 Future Visions</h4>
                </div>
                """, unsafe_allow_html=True)
                
                visions = analysis_data.get('visions', [])
                for vision in visions:
                    # st.markdown(f"• {vision}")
                    st.markdown(f"<div style='font-size: 1.1rem;'>• {vision}</div>", unsafe_allow_html=True)
    
    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Save Progress", type="secondary"):
            st.success("Progress saved!")
    with col2:
        pass
    with col3:
        # Check if required data is complete
        can_continue = (
            st.session_state.project_data.get('project_name') and
            st.session_state.project_data.get('final_domain') != "Choose a domain..." and
            st.session_state.uploaded_documents and
            st.session_state.domain_map
        )
        
        if st.button("Continue to Scanning →", type="primary", disabled=not can_continue):
            if not can_continue:
                missing = []
                if not st.session_state.project_data.get('project_name'):
                    missing.append("Project Name")
                if not st.session_state.project_data.get('final_domain') or st.session_state.project_data.get('final_domain') == "Choose a domain...":
                    missing.append("Domain Selection")
                if not st.session_state.uploaded_documents:
                    missing.append("PDF Upload")
                if not st.session_state.domain_map:
                    missing.append("Domain Map Generation")
                
                st.error(f"Please complete: {', '.join(missing)}")
            else:
                if 1 not in st.session_state.completed_phases:
                    st.session_state.completed_phases.append(1)
                st.session_state.current_phase = 2
                st.rerun()

#added uploaded signal on phase 2 it will connect with phase 1 domain map and generate the strong and week signal.
# Phase 2: Horizon Scanning
def render_phase_2():
    st.header("Phase 2: Horizon Scanning")
    # st.markdown("*Identify signals of change and conduct STEEPV analysis*")
    st.markdown("<p style='font-size: 1.1rem; color: #555; font-style: italic;'>Identify signals of change and conduct STEEPV analysis</p>", unsafe_allow_html=True)

    # Initialize uploaded signals if not exists
    if 'uploaded_signals' not in st.session_state:
        st.session_state.uploaded_signals = {}

    # Upload Signals Section
    st.subheader("📡 Upload Signals")
    st.markdown("<p style='font-size: 1.1rem; color: #555; font-style: italic;'>Upload additional signals, trends, and emerging issues (Optional)</p>", unsafe_allow_html=True)

    st.markdown("<label style='font-size: 1.1rem; font-weight: 500;'>Upload signals, trends, and emerging issues</label>", unsafe_allow_html=True)
    signals_files = st.file_uploader(
        "Upload signals, trends, and emerging issues",
        type=['pdf', 'doc', 'docx', 'xlsx', 'xls', 'csv', 'txt'],
        accept_multiple_files=True,
        key="signals_file_uploader",  # <-- Changed key name
        help="Optional: Upload additional documents containing signals and trends",
        label_visibility="collapsed"
    )

    if signals_files:
        # Initialize as dictionary if not exists
        if 'uploaded_signals' not in st.session_state:
            st.session_state.uploaded_signals = {}
        
        # Clear existing files and add new ones
        st.session_state.uploaded_signals.clear()
        
        for file in signals_files:
            st.session_state.uploaded_signals[file.name] = file
        
        st.success(f"📁 {len(signals_files)} signal files uploaded successfully!")
        
        # Display uploaded files
        st.write("**Uploaded Signal Files:**")
        for filename in st.session_state.uploaded_signals.keys():
            st.write(f"• {filename}")

    # Generate Signals Button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Generate Strong & Weak Signals", type="primary", use_container_width=True):
            if os.getenv('GROQ_API_KEY'):
                try:
                    with st.spinner("Generating signals analysis from all uploaded documents..."):
                        processor = initialize_processor()
                        
                        # Get all uploaded document text (from Phase 1)
                        all_text = ""
                        for file_name, file in st.session_state.uploaded_documents.items():
                            file.seek(0)
                            text = processor.extract_text_from_file(file)
                            all_text += text + "\n\n"
                        
                        # Add signals documents if uploaded
                        # Add signals documents if uploaded
                        if st.session_state.uploaded_signals:
                            for file_name, file in st.session_state.uploaded_signals.items():
                                file.seek(0)
                                # Use the appropriate extraction method based on file type
                                if file_name.endswith('.pdf'):
                                    text = processor.extract_text_from_file(file)
                                else:
                                    # For non-PDF files, read as text
                                    try:
                                        text = file.read().decode('utf-8')
                                    except:
                                        text = f"Could not read {file_name}"
                                
                                all_text += f"\n\n--- SIGNALS DOCUMENT: {file_name} ---\n"
                                all_text += text + "\n\n"

                        # ADD FULL INTERVIEW TEXT (NEW SECTION)
                        if st.session_state.get('full_interview_text'):
                            all_text += f"\n\n--- FULL INTERVIEW DATA ---\n"
                            all_text += st.session_state.full_interview_text + "\n\n"

                        # Generate signals
                        signals_data = processor.generate_signals(
                            st.session_state.project_data.get('final_domain', ''),
                            all_text
                        )
                        
                        if 'error' not in signals_data:
                            st.session_state.signals_data = signals_data
                            st.success("✅ Strong & Weak signals generated successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to generate signals analysis")
                            
                except Exception as e:
                    st.error(f"Failed to generate analysis: {str(e)}")
            else:
                st.error("Please provide your Groq API key to generate signals")

    st.markdown("---")
    
    # Horizon Scanning
    st.subheader("Horizon Scanning")
    
    tab1, tab2, tab3 = st.tabs(["Strong Signals", "Weak Signals", "AI Suggestions"])
    
    with tab1:
        st.markdown("**Strong Signals - Clear, evident trends that are already happening:**")
        
        if st.session_state.signals_data:           
            # Handle different response formats
            if isinstance(st.session_state.signals_data, dict):
                if 'raw_response' in st.session_state.signals_data:
                    # Parse JSON from raw response
                    try:
                        import json
                        import re
                        
                        raw_response = st.session_state.signals_data['raw_response']
                        json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_response, re.DOTALL)
                        
                        if json_match:
                            json_data = json.loads(json_match.group(1))
                            
                            if 'strong_signals' in json_data:
                                for signal in json_data['strong_signals']:
                                    st.markdown(f"""
                                    <div style="
                                        background: #e8f5e8;
                                        border-left: 4px solid #4caf50;
                                        padding: 1rem;
                                        margin: 0.5rem 0;
                                        border-radius: 4px;
                                    ">
                                        <h4 style="color: #2e7d32; margin: 0 0 0.5rem 0;">🟢 {signal.get('title', 'Strong Signal')}</h4>
                                        <p style="margin: 0 0 0.5rem 0;">{signal.get('description', '')}</p>
                                        <small style="font-size: 1rem;"><strong>Source:</strong> {signal.get('source', 'Document Analysis')}</small><br>
                                        <small style="font-size: 1rem;"><strong>Impact:</strong> {signal.get('impact', 'High impact on domain development')}</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.info("No strong signals found in the analysis.")
                        else:
                            st.info("Strong signals data format not recognized.")
                            
                    except Exception as e:
                        st.error(f"Error parsing strong signals: {str(e)}")
                elif 'strong_signals' in st.session_state.signals_data:
                    # Direct access to strong_signals
                    for signal in st.session_state.signals_data['strong_signals']:
                        # Ensure we don't display truncated content
                        description = signal.get('description', '')
                        if len(description) > 500:  # If description is too long, show first part
                            description = description[:500] + "..."
                            
                        st.markdown(f"""
                        <div style="
                            background: #e8f5e8;
                            border-left: 4px solid #4caf50;
                            padding: 1rem;
                            margin: 0.5rem 0;
                            border-radius: 4px;
                        ">
                            <h4 style="color: #2e7d32; margin: 0 0 0.5rem 0;">🟢 {signal.get('title', 'Strong Signal')}</h4>
                            <p style="margin: 0 0 0.5rem 0;">{description}</p>
                            <small style="font-size: 1rem;"><strong>Source:</strong> {signal.get('source', 'Document Analysis')}</small><br>
                            <small style="font-size: 1rem;"><strong>Impact:</strong> {signal.get('impact', 'Significant impact on domain')}</small>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("Strong signals will be generated automatically when you complete Phase 1 and provide your Groq API key.")
        else:
            st.info("Strong signals will be generated automatically when you complete Phase 1 and provide your Groq API key.")
    
    with tab2:
        st.markdown("**Weak Signals - Early indicators of potential future changes:**")
        
        if st.session_state.signals_data:
            if isinstance(st.session_state.signals_data, dict):
                if 'raw_response' in st.session_state.signals_data:
                    try:
                        import json
                        import re
                        
                        raw_response = st.session_state.signals_data['raw_response']
                        json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_response, re.DOTALL)
                        
                        if json_match:
                            json_data = json.loads(json_match.group(1))
                            
                            if 'weak_signals' in json_data:
                                for signal in json_data['weak_signals']:
                                    st.markdown(f"""
                                    <div style="
                                        background: #fff8e1;
                                        border-left: 4px solid #ff9800;
                                        padding: 1rem;
                                        margin: 0.5rem 0;
                                        border-radius: 4px;
                                    ">
                                        <h4 style="color: #f57c00; margin: 0 0 0.5rem 0;">🟡 {signal.get('title', 'Weak Signal')}</h4>
                                        <p style="margin: 0 0 0.5rem 0;">{signal.get('description', '')}</p>
                                        <small style="font-size: 1rem;"><strong>Source:</strong> {signal.get('source', 'Document Analysis')}</small><br>
                                        <small style="font-size: 1rem;"><strong>Potential:</strong> {signal.get('potential', 'Emerging trend to monitor')}</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.info("No weak signals found in the analysis.")
                                
                    except Exception as e:
                        st.error(f"Error parsing weak signals: {str(e)}")
                elif 'weak_signals' in st.session_state.signals_data:
                    for signal in st.session_state.signals_data['weak_signals']:
                        # Ensure we don't display truncated content
                        description = signal.get('description', '')
                        if len(description) > 500:
                            description = description[:500] + "..."
                            
                        st.markdown(f"""
                        <div style="
                            background: #fff8e1;
                            border-left: 4px solid #ff9800;
                            padding: 1rem;
                            margin: 0.5rem 0;
                            border-radius: 4px;
                        ">
                            <h4 style="color: #f57c00; margin: 0 0 0.5rem 0;">🟡 {signal.get('title', 'Weak Signal')}</h4>
                            <p style="margin: 0 0 0.5rem 0;">{description}</p>
                            <small style="font-size: 1rem;"><strong>Source:</strong> {signal.get('source', 'Document Analysis')}</small><br>
                            <small style="font-size: 1rem;"><strong>Potential:</strong> {signal.get('potential', 'Emerging trend with future implications')}</small>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("Weak signals will be generated automatically when you complete Phase 1 and provide your Groq API key.")

    
    with tab3:
        st.markdown("""
        <div class="ai-card">
            <div class="ai-header">
                <div>
                    <h4>AI-Powered Additional Suggestions</h4>
                    <p style="font-size: 0.9rem; color: #666;">AI-generated suggestions for additional signals to monitor</p>
                </div>
                <span class="ai-badge">AI Assistant</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 Generate AI Suggestions", type="primary"):
            if st.session_state.signals_data and os.getenv('GROQ_API_KEY'):
                try:
                    with st.spinner("Generating AI suggestions..."):
                        processor = initialize_processor()
                        suggestions = processor.generate_ai_suggestions(
                            st.session_state.project_data.get('final_domain', ''),
                            st.session_state.signals_data
                        )
                        
                        st.session_state.ai_suggestions = suggestions
                        st.success("AI suggestions generated!")
                        
                except Exception as e:
                    st.error(f"Failed to generate suggestions: {str(e)}")
            else:
                st.error("Please complete signal generation first and ensure API key is provided")
        
        # Display AI suggestions
        if hasattr(st.session_state, 'ai_suggestions') and st.session_state.ai_suggestions:
            # Handle both list and dict formats
            suggestions = st.session_state.ai_suggestions
            
            if isinstance(suggestions, dict) and 'raw_response' in suggestions:
                try:
                    import json
                    import re
                    
                    raw_response = suggestions['raw_response']
                    json_match = re.search(r'```json\s*(\{.*?\}|\[.*?\])\s*```', raw_response, re.DOTALL)
                    
                    if json_match:
                        json_data = json.loads(json_match.group(1))
                        
                        # Handle both array and object formats
                        suggestions_list = json_data if isinstance(json_data, list) else json_data.get('suggestions', [])
                        
                        for suggestion in suggestions_list:
                            if 'error' not in suggestion:
                                category_color = "strong" if suggestion.get('category') == 'Strong' else "weak"
                                bg_color = "#e8f5e8" if suggestion.get('category') == 'Strong' else "#fff8e1"
                                border_color = "#4caf50" if suggestion.get('category') == 'Strong' else "#ff9800"
                                
                                st.markdown(f"""
                                <div style="
                                    background: {bg_color};
                                    border-left: 4px solid {border_color};
                                    padding: 1rem;
                                    margin: 0.5rem 0;
                                    border-radius: 4px;
                                ">
                                    <h4 style="margin: 0 0 0.5rem 0;">💡 {suggestion.get('title', 'AI Suggestion')}</h4>
                                    <p style="margin: 0 0 0.5rem 0;">{suggestion.get('description', '')}</p>
                                    <small style="font-size: 1rem;"><strong>Category:</strong> {suggestion.get('category', 'Weak')} Signal</small><br>
                                    <small style="font-size: 1rem;"><strong>Rationale:</strong> {suggestion.get('rationale', '')}</small>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("AI suggestions data format not recognized.")
                        
                except Exception as e:
                    st.error(f"Error parsing AI suggestions: {str(e)}")
            elif isinstance(suggestions, list):
                for suggestion in suggestions:
                    if 'error' not in suggestion:
                        bg_color = "#e8f5e8" if suggestion.get('category') == 'Strong' else "#fff8e1"
                        border_color = "#4caf50" if suggestion.get('category') == 'Strong' else "#ff9800"
                        text_color = "#2e7d32" if suggestion.get('category') == 'Strong' else "#f57c00"
                        
                        description = suggestion.get('description', '')
                        if len(description) > 400:
                            description = description[:400] + "..."
                            
                        st.markdown(f"""
                        <div style="
                            background: {bg_color};
                            border-left: 4px solid {border_color};
                            padding: 1rem;
                            margin: 0.5rem 0;
                            border-radius: 4px;
                        ">
                            <h4 style="color: {text_color}; margin: 0 0 0.5rem 0;">💡 {suggestion.get('title', 'AI Suggestion')}</h4>
                            <p style="margin: 0 0 0.5rem 0;">{description}</p>
                            <small style="font-size: 1rem;"><strong>Category:</strong> {suggestion.get('category', 'Weak')} Signal</small><br>
                            <small style="font-size: 1rem;"><strong>Rationale:</strong> {suggestion.get('rationale', 'Additional monitoring recommended')}</small>
                        </div>
                        """, unsafe_allow_html=True)

    # Combined download button for both Strong and Weak Signals
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.session_state.signals_data:
            # Prepare combined CSV data
            combined_signals_csv = []
            
            if isinstance(st.session_state.signals_data, dict):
                if 'raw_response' in st.session_state.signals_data:
                    try:
                        import json
                        import re
                        raw_response = st.session_state.signals_data['raw_response']
                        json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_response, re.DOTALL)
                        if json_match:
                            json_data = json.loads(json_match.group(1))
                            
                            # Add strong signals
                            if 'strong_signals' in json_data:
                                for signal in json_data['strong_signals']:
                                    combined_signals_csv.append({
                                        'Signal_Type': 'Strong',
                                        'Title': signal.get('title', 'Strong Signal'),
                                        'Description': signal.get('description', '')
                                    })
                            
                            # Add weak signals
                            if 'weak_signals' in json_data:
                                for signal in json_data['weak_signals']:
                                    combined_signals_csv.append({
                                        'Signal_Type': 'Weak',
                                        'Title': signal.get('title', 'Weak Signal'),
                                        'Description': signal.get('description', '')
                                    })
                    except:
                        pass
                else:
                    # Add strong signals
                    if 'strong_signals' in st.session_state.signals_data:
                        for signal in st.session_state.signals_data['strong_signals']:
                            combined_signals_csv.append({
                                'Signal_Type': 'Strong',
                                'Title': signal.get('title', 'Strong Signal'),
                                'Description': signal.get('description', '')
                            })
                    
                    # Add weak signals
                    if 'weak_signals' in st.session_state.signals_data:
                        for signal in st.session_state.signals_data['weak_signals']:
                            combined_signals_csv.append({
                                'Signal_Type': 'Weak',
                                'Title': signal.get('title', 'Weak Signal'),
                                'Description': signal.get('description', '')
                            })
            
            if combined_signals_csv:
                import pandas as pd
                df_combined = pd.DataFrame(combined_signals_csv)
                csv_combined = df_combined.to_csv(index=False)
                
                st.download_button(
                    label="📥 Download All Signals (CSV)",
                    data=csv_combined,
                    file_name=f"signals_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
        else:
            st.info("Generate signals first to enable download")


    # Replace the STEEPVAnalysis section in render_phase_2() function
    # Find this section: "# Enhanced STEEPV Analysis Display with Debugging"
    # Replace it with the following simplified code:

    # Enhanced STEEPV Analysis Display - Edit Only Mode
    st.subheader("STEEPV Analysis")
    # st.markdown("*Systematic analysis of factors across different dimensions - Edit the generated content*")
    st.markdown("*<span style='font-size: 1.1rem;'>Systematic analysis of factors across different dimensions - Edit the generated content</span>*", unsafe_allow_html=True)

    # Initialize editable STEEPV data if not exists
    if 'editable_steepv' not in st.session_state:
        if st.session_state.get('steepv_analysis'):
            # Copy from generated analysis
            steepv_data = st.session_state.steepv_analysis

            
            # Handle different response formats
            if isinstance( steepv_data, dict) and 'raw_response' in  steepv_data:
                try:
                    import json
                    import re
                    
                    raw_response =  steepv_data['raw_response']
                    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_response, re.DOTALL)
                    
                    if json_match:
                         steepv_data = json.loads(json_match.group(1))
                    else:
                        try:
                             steepv_data = json.loads(raw_response)
                        except:
                            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                            if json_match:
                                 steepv_data = json.loads(json_match.group(0))
                            else:
                                 steepv_data = {}
                except Exception as e:
                     steepv_data = {}
            
            st.session_state.editable_steepv =  steepv_data
        else:
            # Initialize with empty structure
            st.session_state.editable_steepv = {
                        "Social": [],
                        "Technological": [],
                        "Economic": [],
                        "Environmental": [],
                        "Political": [],
                        "Values": []
            }


    if st.session_state.get('editable_steepv'):
        steepv_data = st.session_state.editable_steepv
        
        # Define the standard STEEPV categories in order
        steepv_categories = [
            "Social", "Technological", "Economic", "Environmental", "Political", "Values"
        ]
        
        # Add control buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("🔄 Regenerate Analysis", help="Regenerate STEEPV analysis from AI"):
                if st.session_state.signals_data and os.getenv('GROQ_API_KEY'):
                    try:
                        with st.spinner("Regenerating STEEPV analysis..."):
                            processor = initialize_processor()
                            
                            # Get all uploaded document text (Phase 1)
                            all_text = ""
                            for file_name, file in st.session_state.uploaded_documents.items():
                                file.seek(0)
                                text = processor.extract_text_from_file(file)
                                all_text += text + "\n\n"

                            # ADD UPLOADED SIGNALS DOCUMENTS HERE
                            if st.session_state.uploaded_signals:
                                for file_name, file in st.session_state.uploaded_signals.items():
                                    file.seek(0)
                                    # Use the appropriate extraction method based on file type
                                    if file_name.endswith('.pdf'):
                                        text = processor.extract_text_from_file(file)
                                    else:
                                        # For non-PDF files, read as text
                                        try:
                                            text = file.read().decode('utf-8')
                                        except:
                                            text = f"Could not read {file_name}"
                                    
                                    all_text += f"\n\n--- SIGNALS DOCUMENT: {file_name} ---\n"
                                    all_text += text + "\n\n"
                            
                            # ADD FULL INTERVIEW DATA (REPLACE EXISTING INTERVIEW SECTION)
                            if st.session_state.get('full_interview_text'):
                                all_text += f"\n\n--- FULL INTERVIEW DATA ---\n"
                                all_text += st.session_state.full_interview_text + "\n\n"
                            
                            # Generate new STEEPV analysis
                            steepv = processor.generate_steepv_analysis(
                                st.session_state.project_data.get('final_domain', ''),
                                st.session_state.signals_data,
                                all_text
                            )
                            
                            if 'error' not in steepv:
                                st.session_state.editable_steepv = steepv
                                st.success("STEEPV analysis regenerated!")
                                st.rerun()
                            else:
                                st.error("Failed to regenerate analysis")
                                
                    except Exception as e:
                        st.error(f"Failed to regenerate: {str(e)}")
                else:
                    st.error("Please ensure signals are generated and API key is provided")

        
        with col2:
            pass  # Empty middle column for spacing
        
        with col3:
            if st.button("📥 Export Analysis"):
                import json
                steepv_export = {
                    "project_name": st.session_state.project_data.get('project_name', ''),
                    "domain": st.session_state.project_data.get('final_domain', ''),
                    "steepv_analysis": st.session_state.editable_steepv,
                    "export_timestamp": datetime.now().isoformat()
                }
                
                st.download_button(
                    label="Download STEEPV Analysis",
                    data=json.dumps(steepv_export, indent=2),
                    file_name=f"steepv_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        st.markdown("---")
        
        #this was added for to increse the text size for steepv analysis answer
        # Add CSS for larger text in text areas
        st.markdown(f"""
        <style>
            div[data-testid="stTextArea"] > label > div[data-testid="stTextAreaRootElement"] > div > div > textarea {{
                font-size: 1.1rem !important;
            }}
        </style>
        """, unsafe_allow_html=True)
        
        # Function to display editable category card with inline editing
        def display_editable_category_card(category):
            factors = steepv_data.get(category, [])
            
            # Ensure factors is a list and filter out empty/invalid entries
            if not isinstance(factors, list):
                if isinstance(factors, str):
                    factors = [factors] if factors.strip() else []
                else:
                    factors = []
            
            # Clean up factors
            clean_factors = [str(factor).strip() for factor in factors if factor and str(factor).strip()]
            
            # Add fallback content if empty (generated content)
            if not clean_factors:
                clean_factors = [
                    f"AI analysis for {category.lower()} factors in {st.session_state.project_data.get('final_domain', 'this domain')}",
                    f"Generated insights based on signals and document analysis",
                    f"Key considerations for {category.lower()} dimension"
                ]
                st.session_state.editable_steepv[category] = clean_factors
            
            # Convert factors list to a single text for editing
            factors_text = '\n'.join(f"• {factor}" for factor in clean_factors)
            
            # Create a unique key for the category
            category_key = f"edit_category_{category}"
            
            # Display category with inline editable text area
            st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <h4 style="
                    color: #1976d2; 
                    margin-bottom: 0.5rem;
                    padding: 10px 15px;
                    background: #f0f4ff;
                    border-radius: 8px 8px 0 0;
                    border: 1px solid #e0e0e0;
                    border-bottom: none;
                    margin-top: 0;
                ">{category}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Editable text area inside the card
            updated_text = st.text_area(
                f"{category}",
                value=factors_text,
                key=category_key,
                height=150,
                label_visibility="collapsed",
                placeholder=f"Edit {category.lower()} factors here...",
                help=f"Edit the {category.lower()} factors. Use bullet points (•) or new lines to separate factors."
            )
            
            # Update factors in session state when changed
            if updated_text != factors_text:
                # Parse the updated text back to list
                new_factors = []
                for line in updated_text.split('\n'):
                    line = line.strip()
                    if line:
                        # Remove bullet point if present
                        if line.startswith('• '):
                            line = line[2:]
                        elif line.startswith('- '):
                            line = line[2:]
                        elif line.startswith('* '):
                            line = line[2:]
                        
                        if line.strip():
                            new_factors.append(line.strip())
                
                st.session_state.editable_steepv[category] = new_factors
        
        # Display categories in a 2-column layout
        for row in range(0, len(steepv_categories), 2):
            col1, col2 = st.columns(2)
            
            # First column of the row
            with col1:
                if row < len(steepv_categories):
                    category = steepv_categories[row]
                    display_editable_category_card(category)
            
            # Second column of the row
            with col2:
                if row + 1 < len(steepv_categories):
                    category = steepv_categories[row + 1]
                    display_editable_category_card(category)
        
        # Save Changes Button after all categories
        st.markdown("---")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("💾 Save Changes", type="primary", use_container_width=True):
                st.success("✅ All STEEPV changes saved successfully!")
                # st.balloons()
        
        st.markdown("---")
        
        # Summary section
        st.subheader("📈 STEEPV Summary")
        
        total_factors = sum(len(steepv_data.get(cat, [])) for cat in steepv_categories)
        completed_categories = len([cat for cat in steepv_categories if steepv_data.get(cat)])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Factors", total_factors)
        with col2:
            st.metric("Categories", completed_categories)
        with col3:
            st.metric("Status", "✅ Generated" if total_factors > 0 else "⏳ Pending")

    else:
        st.info("STEEPV analysis will be generated automatically based on your signals.")
        
        # Add manual generation button
        if st.button("🚀 Generate STEEPV Analysis"):
            if st.session_state.signals_data and os.getenv('GROQ_API_KEY'):
                try:
                    with st.spinner("Generating STEEPV analysis..."):
                        processor = initialize_processor()
                        
                        # Get all uploaded document text (Phase 1)
                        all_text = ""
                        for file_name, file in st.session_state.uploaded_documents.items():
                            file.seek(0)
                            text = processor.extract_text_from_file(file)
                            all_text += text + "\n\n"

                        # ADD UPLOADED SIGNALS DOCUMENTS HERE
                        if st.session_state.uploaded_signals:
                            for file_name, file in st.session_state.uploaded_signals.items():
                                file.seek(0)
                                # Use the appropriate extraction method based on file type
                                if file_name.endswith('.pdf'):
                                    text = processor.extract_text_from_file(file)
                                else:
                                    # For non-PDF files, read as text
                                    try:
                                        text = file.read().decode('utf-8')
                                    except:
                                        text = f"Could not read {file_name}"
                                
                                all_text += f"\n\n--- SIGNALS DOCUMENT: {file_name} ---\n"
                                all_text += text + "\n\n"
                        
                        # Generate STEEPV analysis
                        steepv = processor.generate_steepv_analysis(
                            st.session_state.project_data.get('final_domain', ''),
                            st.session_state.signals_data,
                            all_text
                        )
                        
                        if 'error' not in steepv:
                            st.session_state.steepv_analysis = steepv
                            st.session_state.editable_steepv = steepv
                            st.success("STEEPV analysis generated! You can now edit the content.")
                            st.rerun()
                        else:
                            st.error("Failed to generate STEEPV analysis")
                            
                except Exception as e:
                    st.error(f"Failed to generate analysis: {str(e)}")
            else:
                st.error("Please ensure signals are generated and API key is provided")

    # Futures Triangle
    st.subheader("🔺 Futures Triangle")
    st.markdown("*<span style='font-size: 1.1rem;'>Three forces shaping the future of your domain</span>*", unsafe_allow_html=True)
    
    # Initialize editable futures triangle if not exists
    if 'editable_futures_triangle' not in st.session_state:
        if st.session_state.get('futures_triangle'):
            st.session_state.editable_futures_triangle = st.session_state.futures_triangle
        else:
            st.session_state.editable_futures_triangle = {}

    # Generate/Regenerate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔺 Generate Futures Triangle Analysis", type="primary", use_container_width=True):
            if (st.session_state.signals_data and 
                st.session_state.get('editable_steepv') and 
                os.getenv('GROQ_API_KEY')):
                try:
                    with st.spinner("Generating Futures Triangle analysis..."):
                        processor = initialize_processor()
                        
                        # Add this new section to include interview data
                        interview_context = ""
                        if st.session_state.get('full_interview_text'):
                            interview_context = st.session_state.full_interview_text

                        futures_triangle = processor.generate_futures_triangle(
                            st.session_state.project_data.get('final_domain', ''),
                            st.session_state.signals_data,
                            st.session_state.editable_steepv,
                            interview_context  # Pass full interview context
                        )
                        
                        if 'error' not in futures_triangle:
                            # Handle different response formats
                            if 'raw_response' in futures_triangle:
                                try:
                                    import json
                                    import re
                                    
                                    raw_response = futures_triangle['raw_response']
                                    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_response, re.DOTALL)
                                    
                                    if json_match:
                                        futures_triangle = json.loads(json_match.group(1))
                                    else:
                                        futures_triangle = json.loads(raw_response)
                                        
                                except Exception as e:
                                    st.error(f"Error parsing Futures Triangle: {str(e)}")
                                    futures_triangle = {}
                            
                            st.session_state.futures_triangle = futures_triangle
                            st.session_state.editable_futures_triangle = futures_triangle
                            st.success("✅ Futures Triangle generated successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to generate Futures Triangle analysis")
                            
                except Exception as e:
                    st.error(f"Failed to generate analysis: {str(e)}")
            else:
                st.error("Please ensure signals and STEEPV analysis are completed, and API key is provided")

    # Display and Edit Futures Triangle
    if st.session_state.get('editable_futures_triangle'):
        triangle_data = st.session_state.editable_futures_triangle
        
        st.markdown("**Three Forces Shaping the Future:**")
        st.markdown("""
        <style>
            .stTextArea textarea {
                font-size: 1.1rem !important;
                line-height: 1.4 !important;
            }
            div[data-testid="stTextArea"] textarea {
                font-size: 1.1rem !important;
                line-height: 1.4 !important;
            }
            /* Fix column alignment */
            [data-testid="column"] {
                height: 100%;
            }
            /* Ensure equal spacing */
            .element-container {
                width: 100% !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # col_past, col_present, col_future = st.columns(3)
        col_past, col_present, col_future = st.columns([1, 1, 1], gap="medium")
        
        with col_past:
            st.markdown("""
            <div style="border-top: 4px solid #e74c3c; padding: 1rem; background: white; border-radius: 8px; margin-bottom: 1rem; min-height: 120px; display: flex; flex-direction: column; justify-content: center; width: 100%; box-sizing: border-box;">
                <h4 style="margin: 0 0 0.5rem 0; font-size: 1.1rem;">⚓ Weight of the Past</h4>
                <p style="font-size: 1rem; color: #666; margin: 0; line-height: 1.3;">Historical constraints, legacy systems, and valuable traditions</p>
            </div>
            """, unsafe_allow_html=True)

            
            # Obstacles & Challenges
            st.markdown("<strong style='font-size: 1.1rem;'>Obstacles & Challenges:</strong>", unsafe_allow_html=True)
            obstacles_text = '\n'.join(f"• {item}" for item in triangle_data.get('weight_of_past', {}).get('obstacles_challenges', []))
            updated_obstacles = st.text_area(
                "Edit obstacles and challenges:",
                value=obstacles_text,
                height=180,
                key="edit_obstacles",
                label_visibility="collapsed"
            )
            
            # Values to Preserve
            st.markdown("<strong style='font-size: 1.1rem;'>Values to Preserve:</strong>", unsafe_allow_html=True)
            values_text = '\n'.join(f"• {item}" for item in triangle_data.get('weight_of_past', {}).get('values_to_preserve', []))
            updated_values = st.text_area(
                "Edit values to preserve:",
                value=values_text,
                height=180,
                key="edit_values",
                label_visibility="collapsed"
            )
            
            # Update session state
            if 'weight_of_past' not in triangle_data:
                triangle_data['weight_of_past'] = {}
            triangle_data['weight_of_past']['obstacles_challenges'] = [line.strip().lstrip('• ') for line in updated_obstacles.split('\n') if line.strip()]
            triangle_data['weight_of_past']['values_to_preserve'] = [line.strip().lstrip('• ') for line in updated_values.split('\n') if line.strip()]
        
        with col_present:
            st.markdown("""
            <div style="border-top: 4px solid #3498db; padding: 1rem; background: white; border-radius: 8px; margin-bottom: 1rem; min-height: 120px; display: flex; flex-direction: column; justify-content: center; width: 100%; box-sizing: border-box;">
                <h4 style="margin: 0 0 0.5rem 0; font-size: 1.1rem;">➡️ Push of the Present</h4>
                <p style="font-size: 1rem; color: #666; margin: 0; line-height: 1.3;">Current trends, strong signals, and driving forces</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Current Trends
            st.markdown("<strong style='font-size: 1.1rem;'>Current Trends:</strong>", unsafe_allow_html=True)
            trends_text = '\n'.join(f"• {item}" for item in triangle_data.get('push_of_present', {}).get('current_trends', []))
            updated_trends = st.text_area(
                "Edit current trends:",
                value=trends_text,
                height=180,
                key="edit_trends",
                label_visibility="collapsed"
            )
            
            # Strong Drivers
            st.markdown("<strong style='font-size: 1.1rem;'>Strong Drivers:</strong>", unsafe_allow_html=True)
            drivers_text = '\n'.join(f"• {item}" for item in triangle_data.get('push_of_present', {}).get('strong_drivers', []))
            updated_drivers = st.text_area(
                "Edit strong drivers:",
                value=drivers_text,
                height=180,
                key="edit_drivers",
                label_visibility="collapsed"
            )
            
            # Update session state
            if 'push_of_present' not in triangle_data:
                triangle_data['push_of_present'] = {}
            triangle_data['push_of_present']['current_trends'] = [line.strip().lstrip('• ') for line in updated_trends.split('\n') if line.strip()]
            triangle_data['push_of_present']['strong_drivers'] = [line.strip().lstrip('• ') for line in updated_drivers.split('\n') if line.strip()]
        
        with col_future:
            st.markdown("""
            <div style="border-top: 4px solid #2ecc71; padding: 1rem; background: white; border-radius: 8px; margin-bottom: 1rem; min-height: 120px; display: flex; flex-direction: column; justify-content: center; width: 100%; box-sizing: border-box;">
                <h4 style="margin: 0 0 0.5rem 0; font-size: 1.1rem;">🎯 Pull of the Future</h4>
                <p style="font-size: 1rem; color: #666; margin: 0; line-height: 1.3;">Future visions, weak signals, and emerging possibilities</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Future Visions
            st.markdown("<strong style='font-size: 1.1rem;'>Future Visions:</strong>", unsafe_allow_html=True)
            visions_text = '\n'.join(f"• {item}" for item in triangle_data.get('pull_of_future', {}).get('future_visions', []))
            updated_visions = st.text_area(
                "Edit future visions:",
                value=visions_text,
                height=180,
                key="edit_visions",
                label_visibility="collapsed"
            )
            
            # Emerging Possibilities
            st.markdown("<strong style='font-size: 1.1rem;'>Emerging Possibilities:</strong>", unsafe_allow_html=True)
            possibilities_text = '\n'.join(f"• {item}" for item in triangle_data.get('pull_of_future', {}).get('emerging_possibilities', []))
            updated_possibilities = st.text_area(
                "Edit emerging possibilities:",
                value=possibilities_text,
                height=180,
                key="edit_possibilities",
                label_visibility="collapsed"
            )
            
            # Update session state
            if 'pull_of_future' not in triangle_data:
                triangle_data['pull_of_future'] = {}
            triangle_data['pull_of_future']['future_visions'] = [line.strip().lstrip('• ') for line in updated_visions.split('\n') if line.strip()]
            triangle_data['pull_of_future']['emerging_possibilities'] = [line.strip().lstrip('• ') for line in updated_possibilities.split('\n') if line.strip()]
        
        # Save button
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("💾 Save Triangle Changes", type="primary", use_container_width=True):
                st.session_state.editable_futures_triangle = triangle_data
                st.success("✅ Futures Triangle changes saved!")
                # st.balloons()
    
    else:
        st.info("Futures Triangle will be generated based on your signals and STEEPV analysis.")

    st.markdown("---")

    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Back to Framing"):
            st.session_state.current_phase = 1
            st.rerun()
    with col2:
        if st.button("Save Progress", type="secondary"):
            st.success("Scanning phase progress saved!")
    with col3:
        if st.button("Save & Complete Scanning", type="primary"):
            if 2 not in st.session_state.completed_phases:
                st.session_state.completed_phases.append(2)
            st.success("🎉 Phase 2: Environmental Scanning completed successfully!")
            # st.balloons()
            
            # Show completion summary
            st.markdown("""
            ### Phase 2 Complete! 
            
            **What you've accomplished:**
            - ✅ Generated and analyzed strong signals
            - ✅ Identified weak signals for monitoring  
            - ✅ Completed STEEPV analysis
            - ✅ Added custom signals as needed
            
            **Next Steps:**
            - Phase 3: Futuring (Scenario Development) - Coming Soon
            - Phase 4: Visioning (Impact Analysis) - Coming Soon
            
            Your data has been saved and can be exported using the sidebar option.
            """)




# Main content routing
def main():   
    # Phase routing
    if st.session_state.current_phase == 1:
        render_phase_1()
    elif st.session_state.current_phase == 2:
        render_phase_2()
    else:
        st.error("Invalid phase selected")

# Run the main function
if __name__ == "__main__":
    main()







