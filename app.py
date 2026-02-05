"""TulipScout Dashboard - Lead Review and Analytics (Standalone Version)."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="TulipScout Dashboard",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== AUTHENTICATION ====================
def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["passwords"]["dashboard_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    # First run, show input for password
    if "password_correct" not in st.session_state:
        st.title("🍷 TulipScout Dashboard")
        st.markdown("### Secure Access Required")
        st.text_input(
            "Enter Password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.caption("🔒 This dashboard is password-protected for your security.")
        return False
    
    # Password not correct, show input + error
    elif not st.session_state["password_correct"]:
        st.title("🍷 TulipScout Dashboard")
        st.markdown("### Secure Access Required")
        st.text_input(
            "Enter Password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.error("😕 Password incorrect. Please try again.")
        return False
    
    # Password correct
    else:
        return True

# Stop execution if password is incorrect
if not check_password():
    st.stop()

# ==================== DATA LOADING ====================
@st.cache_data
def load_leads_data():
    """Load leads from JSON file."""
    json_path = Path(__file__).parent / "day1_results.json"
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        
        # Add derived columns
        if 'search_date' in df.columns:
            df['search_date'] = pd.to_datetime(df['search_date'])
        
        return df
    except FileNotFoundError:
        st.error(f"❌ Data file not found: {json_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame()

# ==================== COUNTRY FLAGS ====================
COUNTRY_FLAGS = {
    "Argentina": "🇦🇷",
    "Australia": "🇦🇺",
    "Austria": "🇦🇹",
    "Belgium": "🇧🇪",
    "Brazil": "🇧🇷",
    "Canada": "🇨🇦",
    "Czech Republic": "🇨🇿",
    "Japan": "🇯🇵",
    "Poland": "🇵🇱",
    "Romania": "🇷🇴",
    "South Korea": "🇰🇷",
}

def get_flag(country):
    """Get flag emoji for country."""
    return COUNTRY_FLAGS.get(country, "🌍")

# ==================== MAIN APP ====================
# Load data
df = load_leads_data()

# Header
st.title("🍷 TulipScout - Lead Generation Dashboard")
st.markdown("*B2B Wine Importer Lead Intelligence System*")

# Sidebar
with st.sidebar:
    st.header("🧭 Navigation")
    page = st.radio("Go to", ["📊 Overview", "🎯 Leads Explorer", "🌍 Geographic Analysis"])
    
    st.divider()
    st.markdown("### 📈 Quick Stats")
    
    if not df.empty:
        st.metric("Total Leads", len(df))
        st.metric("Countries", df['country'].nunique())
        st.metric("Companies Identified", df['company_name'].nunique())
        
        # Status breakdown
        if 'israel_trade_status' in df.columns:
            st.markdown("#### Trade Status")
            status_counts = df['israel_trade_status'].value_counts()
            for status, count in status_counts.items():
                st.caption(f"• {status}: {count}")
    
    st.divider()
    st.caption("🔒 Secure Dashboard")
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ==================== OVERVIEW PAGE ====================
if page == "📊 Overview":
    st.header("📊 Dashboard Overview")
    
    if df.empty:
        st.warning("⚠️ No data available. Please check your data files.")
        st.stop()
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Leads",
            value=len(df),
            delta=f"+{len(df)} this session"
        )
    
    with col2:
        st.metric(
            label="Countries Covered",
            value=df['country'].nunique(),
            delta="Global reach"
        )
    
    with col3:
        companies_with_names = len(df[df['company_name'] != 'Unknown'])
        st.metric(
            label="Companies Identified",
            value=companies_with_names,
            delta=f"{(companies_with_names/len(df)*100):.0f}% identified"
        )
    
    with col4:
        contacts_found = len(df[df['decision_maker'].notna()])
        st.metric(
            label="Decision Makers",
            value=contacts_found,
            delta=f"{(contacts_found/len(df)*100):.0f}% contacted"
        )
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌍 Leads by Country")
        country_counts = df['country'].value_counts().reset_index()
        country_counts.columns = ['Country', 'Count']
        country_counts['Flag'] = country_counts['Country'].apply(get_flag)
        
        fig = px.bar(
            country_counts,
            x='Country',
            y='Count',
            text='Count',
            color='Count',
            color_continuous_scale='Reds',
        )
        fig.update_layout(
            showlegend=False,
            xaxis_title="",
            yaxis_title="Number of Leads",
            height=400
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🤝 Trade Status Distribution")
        if 'israel_trade_status' in df.columns:
            trade_status = df['israel_trade_status'].value_counts().reset_index()
            trade_status.columns = ['Status', 'Count']
            
            fig = px.pie(
                trade_status,
                values='Count',
                names='Status',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Trade status data not available")
    
    st.divider()
    
    # Recent leads table
    st.subheader("📋 Recent Leads")
    
    display_df = df.copy()
    if 'country' in display_df.columns:
        display_df['Country'] = display_df['country'].apply(lambda x: f"{get_flag(x)} {x}")
    
    display_columns = ['Country', 'company_name', 'decision_maker', 'decision_maker_title', 'israel_trade_status']
    display_columns = [col for col in display_columns if col in display_df.columns or col == 'Country']
    
    st.dataframe(
        display_df[display_columns].head(10),
        use_container_width=True,
        hide_index=True,
    )

# ==================== LEADS EXPLORER PAGE ====================
elif page == "🎯 Leads Explorer":
    st.header("🎯 Lead Explorer")
    
    if df.empty:
        st.warning("⚠️ No data available.")
        st.stop()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        countries = ["All"] + sorted(df['country'].unique().tolist())
        selected_country = st.selectbox("🌍 Filter by Country", countries)
    
    with col2:
        if 'israel_trade_status' in df.columns:
            statuses = ["All"] + sorted(df['israel_trade_status'].dropna().unique().tolist())
            selected_status = st.selectbox("🤝 Filter by Trade Status", statuses)
        else:
            selected_status = "All"
    
    with col3:
        search_query = st.text_input("🔍 Search Company Name", "")
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_country != "All":
        filtered_df = filtered_df[filtered_df['country'] == selected_country]
    
    if selected_status != "All" and 'israel_trade_status' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['israel_trade_status'] == selected_status]
    
    if search_query:
        filtered_df = filtered_df[
            filtered_df['company_name'].str.contains(search_query, case=False, na=False)
        ]
    
    st.markdown(f"**Showing {len(filtered_df)} lead(s)**")
    
    # Display leads
    for idx, lead in filtered_df.iterrows():
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                company_name = lead.get('company_name', 'Unknown')
                country = lead.get('country', 'Unknown')
                flag = get_flag(country)
                
                st.markdown(f"### {flag} {company_name}")
                
                # Details
                details = []
                if pd.notna(lead.get('decision_maker')):
                    details.append(f"👤 **Contact:** {lead['decision_maker']}")
                    if pd.notna(lead.get('decision_maker_title')):
                        details[-1] += f" ({lead['decision_maker_title']})"
                
                if pd.notna(lead.get('website')):
                    details.append(f"🌐 **Website:** {lead['website']}")
                
                if pd.notna(lead.get('email')):
                    details.append(f"📧 **Email:** {lead['email']}")
                
                if pd.notna(lead.get('phone')):
                    details.append(f"📞 **Phone:** {lead['phone']}")
                
                for detail in details:
                    st.markdown(detail)
            
            with col2:
                if pd.notna(lead.get('israel_trade_status')):
                    st.info(f"**Trade Status**\n\n{lead['israel_trade_status']}")
            
            # Relevance score
            if pd.notna(lead.get('relevance_score')):
                st.success(f"✨ **Why this lead:** {lead['relevance_score']}")
            
            # Additional data
            with st.expander("📄 View All Data"):
                lead_dict = lead.dropna().to_dict()
                st.json(lead_dict)
            
            st.divider()
    
    # Export button
    st.download_button(
        label="📥 Download Filtered Leads (CSV)",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name=f"tulipscout_leads_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

# ==================== GEOGRAPHIC ANALYSIS PAGE ====================
elif page == "🌍 Geographic Analysis":
    st.header("🌍 Geographic Analysis")
    
    if df.empty:
        st.warning("⚠️ No data available.")
        st.stop()
    
    # World map
    st.subheader("🗺️ Lead Distribution Map")
    
    country_summary = df.groupby('country').size().reset_index(name='lead_count')
    
    # Create choropleth map
    fig = px.choropleth(
        country_summary,
        locations='country',
        locationmode='country names',
        color='lead_count',
        hover_name='country',
        hover_data={'lead_count': True, 'country': False},
        color_continuous_scale='Reds',
        labels={'lead_count': 'Number of Leads'}
    )
    
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth'
        ),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Country breakdown
    st.subheader("📊 Country Breakdown")
    
    for country in sorted(df['country'].unique()):
        country_df = df[df['country'] == country]
        
        with st.expander(f"{get_flag(country)} {country} ({len(country_df)} leads)"):
            # Stats
            col1, col2, col3 = st.columns(3)
            
            with col1:
                identified = len(country_df[country_df['company_name'] != 'Unknown'])
                st.metric("Companies Identified", identified)
            
            with col2:
                contacts = len(country_df[country_df['decision_maker'].notna()])
                st.metric("Decision Makers Found", contacts)
            
            with col3:
                if 'website' in country_df.columns:
                    websites = len(country_df[country_df['website'].notna() & (country_df['website'] != '')])
                    st.metric("With Websites", websites)
            
            # Company list
            st.markdown("**Companies:**")
            companies = country_df[country_df['company_name'] != 'Unknown']['company_name'].unique()
            if len(companies) > 0:
                for company in companies:
                    st.markdown(f"• {company}")
            else:
                st.caption("No companies identified yet")

# ==================== FOOTER ====================
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🍷 TulipScout v1.0")
with col2:
    st.caption("Made for Tulip Winery")
with col3:
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
