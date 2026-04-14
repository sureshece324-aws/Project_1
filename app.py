import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CONFIGURATION & CUSTOM THEME ---
st.set_page_config(page_title="PhonePe Pulse Analysis 2026", layout="wide")

# Custom CSS for Background and Typography
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #2d1653;
    background-image: url("https://www.phonepe.com/pulse/static/74929829875f6d656041189311027170/pulse-logo.png");
    background-size: 400px;
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-position: bottom right;
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

[data-testid="stToolbar"] {
    right: 2rem;
}

/* Optional: Styling the sidebar to match */
[data-testid="stSidebar"] {
    background-color: #1a0b33;
}

/* Making text and headers white for better visibility */
h1, h2, h3, p, span {
    color: white !important;
}
</style>
            

""", unsafe_allow_html=True)

# --- 2. DATABASE CONNECTION ---
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password="Beast@9202", database="phonepe_pulse"
    )

try:
    conn = get_connection()
except Exception as e:
    st.error(f"Database Connection Failed: {e}")
    st.stop()

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title("Pulse Navigation")
selection = st.sidebar.selectbox(
    "Choose an Analysis",
    ["Home", "Transaction Dynamics", "Device Dominance", "Insurance Penetration", 
     "User Engagement Strategy", "Market Expansion"]
)

if selection == "Home":
    st.markdown("""
<div style='text-align: left;'>
    <img src="https://download.logo.wine/logo/PhonePe/PhonePe-Logo.wine.png" width="200">
</div>
""", unsafe_allow_html=True)
    st.title("PhonePe Pulse: The Beat of Progress")
    st.subheader("State-wise Data Distribution")
    
    map_metric = st.selectbox("Select Metric", ["Total Transactions", "Total Users", "App Opens"])
    
    query_map = {
        "Total Transactions": "SELECT State, SUM(Transaction_count) as val FROM top_transactions GROUP BY State",
        "Total Users": "SELECT State, SUM(Registered_Users) as val FROM aggregated_user GROUP BY State",
        "App Opens": "SELECT State, SUM(App_Opens) as val FROM aggregated_user GROUP BY State"
    }
    
    map_df = pd.read_sql(query_map[map_metric], conn)
    map_df['State'] = map_df['State'].str.replace('-', ' ').str.title()

    fig = px.choropleth(
        map_df,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations='State',
        color='val',
        color_continuous_scale=["#48b040", "#ab573b", "#164A53"],
        template="plotly_dark"
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', geo_bgcolor='rgba(0,0,0,0)', height=600)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.title(f"{selection}")
    
    # 1. DEFINE COLOR MAPPING FOR EACH CASE STUDY
    # You can choose from: 'plotly_dark', 'viridis', 'plasma', 'magma', 'inferno', 'blues', 'purples', etc.
    case_study_colors = {
        "Transaction Dynamics": "purples",
        "Device Dominance": "viridis",
        "Insurance Penetration": "emrld",
        "User Engagement Strategy": "plasma",
        "Market Expansion": "magenta"
    }

    # Get the color scale for the current selection (default to 'burg' if not found)
    current_color_scale = case_study_colors.get(selection, "burg")

    # Configuration with Aligned SQL
    analysis_config = {
        "Transaction Dynamics": {
            "State-wise Market Share (Value)": ("SELECT State, SUM(Transaction_amount) as Value FROM top_transactions GROUP BY State ORDER BY Value DESC", "bar", "State", "Value"),
            "Quarterly Volume Trends": ("SELECT CONCAT('Q', Quarter, '-', Year) as Period, SUM(Transaction_count) as Volume FROM top_transactions GROUP BY Year, Quarter ORDER BY Year, Quarter", "line", "Period", "Volume"),
            "Transaction Type Distribution": ("SELECT Transaction_type, SUM(Transaction_count) as Count FROM aggregated_transactions GROUP BY Transaction_type", "pie", "Transaction_type", "Count"),
            "Top 10 Districts by Count": ("SELECT Name, SUM(Transaction_count) as Count FROM top_transactions WHERE Level = 'District' GROUP BY Name ORDER BY Count DESC LIMIT 10", "bar", "Name", "Count"),
            "Avg. Ticket Size by State": ("SELECT State, (SUM(Transaction_amount)/SUM(Transaction_count)) as Avg_Size FROM top_transactions GROUP BY State ORDER BY Avg_Size DESC", "bar", "State", "Avg_Size")
        },
        "Device Dominance": {
            "Brand Market Share": ("SELECT Brand, SUM(User_count) as Users FROM aggregated_user GROUP BY Brand ORDER BY Users DESC", "bar", "Brand", "Users"),
            "Karnataka vs Maharashtra Brands": (
                "SELECT Brand, SUM(CASE WHEN State = 'karnataka' THEN User_count ELSE 0 END) AS Karnataka, SUM(CASE WHEN State = 'maharashtra' THEN User_count ELSE 0 END) AS Maharashtra FROM aggregated_user WHERE State IN ('karnataka', 'maharashtra') GROUP BY Brand", 
                "group_bar", "Brand", ["Karnataka", "Maharashtra"]
            ),
            "Xiaomi vs Apple Yearly Growth": ("SELECT Year, Brand, SUM(User_count) as Count FROM aggregated_user WHERE Brand IN ('Xiaomi', 'Apple') GROUP BY Year, Brand", "line_multi", "Year", "Count"),
            "User Engagement Score": ("SELECT Brand, AVG(Percentage)*100 as Engagement FROM aggregated_user GROUP BY Brand", "bar", "Engagement", "Brand"),
            "Brands with Low App Opens": ("SELECT Brand, AVG(Percentage) as Rate FROM aggregated_user GROUP BY Brand HAVING Rate < 0.05", "bar", "Brand", "Rate"),
        },
        "Insurance Penetration": {
            "Top Insurance States": ("SELECT State, SUM(Insurance_count) as Count FROM aggregated_insurance GROUP BY State ORDER BY Count DESC", "bar", "State", "Count"),
            "Insurance Registered Users": ("SELECT State, SUM(Registered_Users) as Users FROM map_user GROUP BY State", "bar", "State", "Users"),
            "Insurance vs Total Spend": ("SELECT a.State, SUM(a.Insurance_amount) AS Insurance_Amount, SUM(t.Transaction_amount) AS Total_Spend FROM aggregated_insurance a JOIN top_transactions t ON a.State = t.State AND a.Year = t.Year AND a.Quarter = t.Quarter GROUP BY a.State ORDER BY Total_Spend DESC LIMIT 10", "group_bar", "State", ["Insurance_Amount", "Total_Spend"]),
            "District Insurance Leaders": ("SELECT Name, SUM(Insurance_count) as Count FROM top_insurance WHERE Level = 'District' GROUP BY Name ORDER BY Count DESC LIMIT 10", "pie", "Name", "Count"),
            "Quarterly Policy Growth": ("SELECT Quarter, SUM(Insurance_count) as Policies FROM aggregated_insurance GROUP BY Quarter", "line", "Quarter", "Policies"),
        },
        "User Engagement Strategy": {
            "Annual User Growth": ("SELECT Year, SUM(Registered_Users) as Total FROM aggregated_user GROUP BY Year ORDER BY Year", "line", "Year", "Total"),
            "App Open Density": ("SELECT State, SUM(App_Opens) as Opens FROM aggregated_user GROUP BY State ORDER BY Opens DESC", "bar", "State", "Opens"),
            "User-to-Open Ratio": ("SELECT State, (SUM(App_Opens)/SUM(Registered_Users)) as Ratio FROM aggregated_user GROUP BY State ORDER BY Ratio ASC", "bar", "State", "Ratio"),
            "Top Growing Districts": ("SELECT Name, SUM(Registered_Users) as New_Users FROM top_users WHERE Level = 'District' GROUP BY Name ORDER BY New_Users DESC LIMIT 10", "pie", "Name", "New_Users"),
            "High-Density Pincodes": ("SELECT Name, SUM(Registered_Users) as Users FROM top_users WHERE Level = 'Pincode' GROUP BY Name ORDER BY Users DESC LIMIT 10", "line", "Name", "Users")

        },
        "Market Expansion": {
            "High Value States (>1B)": ("SELECT State, SUM(Transaction_amount) as Total FROM top_transactions GROUP BY State HAVING Total > 1000000000 ORDER BY Total DESC", "bar", "State", "Total"),
            "District Vol vs Val": ("SELECT District, SUM(Transaction_count) as Vol, SUM(Transaction_amount) / 1000000000000 as Val_in_Trillions FROM map_transaction GROUP BY District ORDER BY Vol DESC LIMIT 10", "group_bar", "District", ["Vol", "Val_in_Trillions"]),
            "Best Performing Quarters": ("SELECT Quarter, AVG(Transaction_count) as Avg_Vol FROM top_transactions GROUP BY Quarter", "pie", "Quarter", "Avg_Vol"),
            "Top Transaction Districts": ("SELECT Name, SUM(Transaction_count) as Count FROM top_transactions WHERE Level = 'District' GROUP BY Name ORDER BY Count DESC LIMIT 10", "pie", "Name", "Count"),
            "App Adoption Efficiency": ("SELECT State, (SUM(App_Opens)/SUM(Registered_Users)) as Efficiency FROM aggregated_user GROUP BY State", "bar", "State", "Efficiency")
        }
    }

    current_topic = analysis_config[selection]
    
    for title, (query, plot_type, x_col, y_col) in current_topic.items():
        st.subheader(title)
        try:
            df = pd.read_sql(query, conn)
            plot_df = df.copy()
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.dataframe(df, use_container_width=True)
                
            with col2:
                # Initialize fig as None to ensure it's defined
                fig = None

                # 1. GROUPED BAR & DUAL-AXIS LOGIC
                if plot_type == "group_bar":
                    # Check for Market Expansion (Vol) OR Insurance Penetration (Insurance_Amount)
                    is_market_dual = isinstance(y_col, list) and "Vol" in y_col
                    is_insurance_dual = isinstance(y_col, list) and "Insurance_Amount" in y_col
                    
                    if is_market_dual or is_insurance_dual:
                        fig = go.Figure()
                        
                        # Set column names and labels dynamically
                        col_left = "Vol" if is_market_dual else "Insurance_Amount"
                        col_right = "Val_in_Trillions" if is_market_dual else "Total_Spend"
                        label_left = "Volume (Count)" if is_market_dual else "Insurance Amount (₹)"
                        label_right = "Value (Trillions ₹)" if is_market_dual else "Total Spend (₹)"
                        color_left = "#277e32" if is_market_dual else "#00ced1"

                        # Primary Axis: Bar (Left)
                        fig.add_trace(go.Bar(
                            x=plot_df[x_col], y=plot_df[col_left],
                            name=label_left, marker_color=color_left, yaxis="y1"
                        ))

                        # Secondary Axis: Line (Right)
                        fig.add_trace(go.Scatter(
                            x=plot_df[x_col], y=plot_df[col_right],
                            name=label_right, line=dict(color="#ffc107", width=3),
                            marker=dict(size=8), yaxis="y2", mode="lines+markers"
                        ))

                        fig.update_layout(
                            template="plotly_dark",
                            yaxis=dict(title=label_left, title_font_color=color_left, tickfont_color=color_left),
                            yaxis2=dict(
                                title=label_right, title_font_color="#ffc107", tickfont_color="#ffc107",
                                anchor="x", overlaying="y", side="right", showgrid=False
                            ),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                            hovermode="x unified",
                            margin=dict(l=0, r=0, t=30, b=0)
                        )
                    else:
                        # Standard Grouped Bar (e.g., Device Brands)
                        colors = ["#277e32", "#ffc107"] if selection == "Device Dominance" else ["#346b27", "#70b35f"]
                        fig = px.bar(plot_df, x=x_col, y=y_col, barmode='group', 
                                     template="plotly_dark", color_discrete_sequence=colors)

                # 2. STANDARD BAR CHART
                elif plot_type == "bar":
                    fig = px.bar(plot_df, x=x_col, y=y_col, color=y_col, 
                                 template="plotly_dark", color_continuous_scale=current_color_scale)
                    fig.update_layout(coloraxis_showscale=False)

                # 3. LINE CHARTS
                elif plot_type == "line":
                    fig = px.line(plot_df, x=x_col, y=y_col, markers=True, template="plotly_dark")
                    fig.update_traces(line_color="#ffc107")

                elif plot_type == "line_multi":
                    fig = px.line(plot_df, x=x_col, y=y_col, color="Brand", markers=True, template="plotly_dark")

                # 4. PIE CHART
                elif plot_type == "pie":
                    fig = px.pie(plot_df, values=y_col, names=x_col, hole=0.4, template="plotly_dark")

                # 5. SCATTER PLOT
                elif plot_type == "scatter":
                    fig = px.scatter(plot_df, x=x_col, y=y_col, size=y_col, color=x_col, 
                                     template="plotly_dark", color_continuous_scale=current_color_scale)

                # FINAL RENDER: This is the ONLY st.plotly_chart call inside the loop
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Visual Error on '{title}': {e}")
        st.divider()