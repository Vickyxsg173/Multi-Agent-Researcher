import streamlit as st
import time
from pipeline import run_research_pipeline
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor

def clean_txt(text):
    # Safe replacement of unicode chars for reportlab
    replacements = {
        '\u201c': '"', '\u201d': '"',
        '\u2018': "'", '\u2019': "'",
        '\u2014': '-', '\u2013': '-',
        '\u2022': '&bull;',
        '\u2192': '-&gt;',
        '\u00e9': 'e',
        '\u0301': '',
    }
    for orig, rep in replacements.items():
        text = text.replace(orig, rep)
    return text

def convert_markdown_to_pdf(markdown_text):
    buffer = BytesIO()
    
    # Establish doc layout
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Elegant typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=HexColor('#111111'),
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'H1Style',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=HexColor('#222222'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=HexColor('#444444'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=HexColor('#333333'),
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    story = []
    
    cleaned_md = clean_txt(markdown_text)
    
    for line in cleaned_md.split('\n'):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 4))
            continue
            
        # Parse headings
        if line.startswith('# '):
            cleaned = line[2:].replace('**', '').replace('*', '')
            story.append(Paragraph(cleaned, title_style))
        elif line.startswith('## '):
            cleaned = line[3:].replace('**', '').replace('*', '')
            story.append(Paragraph(cleaned, h1_style))
        elif line.startswith('### '):
            cleaned = line[4:].replace('**', '').replace('*', '')
            story.append(Paragraph(cleaned, h2_style))
        # Bullet points
        elif line.startswith('- ') or line.startswith('* '):
            cleaned = line[2:].replace('**', '').replace('*', '')
            story.append(Paragraph(f"&bull; {cleaned}", bullet_style))
        else:
            cleaned = line.replace('**', '').replace('*', '')
            story.append(Paragraph(cleaned, body_style))
            
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

st.set_page_config(
    page_title="Research Suite",
    page_icon="📓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Intuitive, warm dark theme with high typography focus
st.markdown("""
<style>
    /* Hide Streamlit header, menu button, deploy button, and footer */
    header, [data-testid="stHeader"] {
        visibility: hidden;
        height: 0% !important;
    }
    #MainMenu, footer {
        visibility: hidden;
    }
    .stAppDeployButton, div[data-testid="stAppDeployButton"] {
        display: none !important;
    }
    
    /* Sleek, organic dark theme */
    .stApp {
        background-color: #16161a;
        color: #e6e6e9;
        padding-top: 0rem;
    }
    h1 {
        font-family: 'Georgia', serif;
        font-weight: 500;
        color: #f2f2f7;
        text-align: center;
        margin-bottom: 5px;
    }
    .subtitle {
        text-align: center;
        color: #9a9a8b;
        font-family: 'Georgia', serif;
        font-style: italic;
        font-size: 15px;
        margin-bottom: 30px;
    }
    /* Minimal loader text alignment */
    .step-item {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        font-size: 16px;
        color: #c9c9d4;
        margin: 10px 0;
        display: flex;
        align-items: center;
    }
    .metric-value {
        font-family: 'Georgia', serif;
        font-size: 54px;
        color: #f2f2f7;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 14px;
        color: #9a9a8b;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

st.title("Research Suite")
st.markdown("<p class='subtitle'>An organic multi-agent pipeline generating structured reports with constructive critiques.</p>", unsafe_allow_html=True)

# Main container for clean layout
st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
topic = st.text_input("Enter topic to investigate...", placeholder="What would you like to explore?")

if st.button("Begin Synthesis", type="primary", use_container_width=True):
    if not topic.strip():
        st.warning("Please enter a valid topic.")
    else:
        status_placeholder = st.empty()
        
        steps = {
            "Searching the web...": "Search Agent",
            "Scraping relevant content...": "Reader Agent",
            "Drafting research report...": "Writer Agent",
            "Critiquing the report...": "Critic Agent"
        }
        
        state = {}
        
        # Run pipeline and display loading states
        for status, current_state in run_research_pipeline(topic):
            state = current_state
            
            with status_placeholder.container():
                st.write("### Working...")
                for key, name in steps.items():
                    if key == status:
                        st.markdown(f"<div class='step-item'>⏳ <b>{name}</b> — <i>{key}</i></div>", unsafe_allow_html=True)
                    elif (key == "Searching the web..." and "search_result" in state) or \
                         (key == "Scraping relevant content..." and "scraped_content" in state) or \
                         (key == "Drafting research report..." and "report" in state) or \
                         (key == "Critiquing the report..." and "feedback" in state) or \
                         status == "Complete" or "Revising" in status or "Re-evaluating" in status:
                        st.markdown(f"<div class='step-item'>✓ <b>{name}</b> — Done</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='step-item' style='opacity: 0.3;'><b>{name}</b> — Waiting...</div>", unsafe_allow_html=True)
                
                # Show active critique correction loops
                if "Revising" in status or "Re-evaluating" in status:
                    st.markdown(f"<div class='step-item' style='color: #cca43b;'>🔄 <b>Feedback Loop</b> — <i>{status}</i></div>", unsafe_allow_html=True)
            
            time.sleep(0.1)
            
        # Clean progress steps away entirely upon completion
        status_placeholder.empty()
        
        # Tabs for final result representation
        tab1, tab2 = st.tabs(["📝 Research Report", "⭐ Critique"])
        
        with tab1:
            report_content = state.get("report", "No report drafted.")
            st.markdown(report_content)
            
            # Format filename properly
            safe_filename = "".join([c if c.isalnum() else "_" for c in topic]).strip("_")[:40]
            
            # PDF Generation option
            try:
                pdf_bytes = convert_markdown_to_pdf(report_content)
                st.download_button(
                    label="Download Report as PDF",
                    data=pdf_bytes,
                    file_name=f"{safe_filename}_report.pdf",
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(f"Could not prepare PDF download: {e}")
            
        with tab2:
            feedback = state.get("feedback", "No feedback available.")
            score = "N/A"
            for line in feedback.split("\n"):
                if "score:" in line.lower():
                    score = line.split(":")[-1].strip()
                    break
            
            col1, col2 = st.columns([1, 2.5])
            with col1:
                st.markdown(f"""
                <div style='border: 1px solid #2a2a30; border-radius: 8px; padding: 20px; text-align: center; background: #1a1a20;'>
                    <div class='metric-label'>Critic Score</div>
                    <div class='metric-value'>{score}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(feedback)
