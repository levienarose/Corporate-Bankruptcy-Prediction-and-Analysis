import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    layout="wide",
    
)
"""
# :material/query_stats: Corporate Bankruptcy Prediction and Analysis

"""

"" #add some space

@st.cache_data
def load_data(file):
    data = pd.read_csv(file)
    return data

df = pd.read_csv("simple_corporate_data.csv")
raw_df = df.copy()


    # ===================================================================================
    # SCATTER PLOT
    # ===================================================================================

# Default settings
numeric_columns = df.select_dtypes(
    include=["number"]
).columns.tolist()

all_columns = df.columns.tolist()

if len(numeric_columns) < 2:
    st.error("Your CSV needs at least 2 numeric columns.")
    st.stop()
    
# Session state defaults
if "x_axis" not in st.session_state:
    st.session_state.x_axis = numeric_columns[0]

if "y_axis" not in st.session_state:
    st.session_state.y_axis = numeric_columns[1]

if "color_by" not in st.session_state:
    st.session_state.color_by = None

#Create Figure
fig = px.scatter(
    df,
    x=st.session_state.x_axis,
    y=st.session_state.y_axis,
    color="Company Status",
    color_discrete_map={
        "Bankrupt": "#F87171",
        "Stable":"#4ADE80",    
    },
    template="plotly_white",
    title="Comparison Chart",
    hover_data=df.columns
)

# FIGURE LAYOUT
fig.update_layout(
    height=650,
    clickmode="event+select",
    title={
        "text": (
            f"<b>{st.session_state.x_axis} vs {st.session_state.y_axis} by Company Status</b><br>"
            f"<sup> Access the Chart Settings in the Sidebar </sup>"
        ),
        "x": 0.5,
        "xanchor": "center"
    },
    legend_title_text= "Company Status"
)

fig.update_traces(
marker=dict(
    size=10,
    opacity=0.75,
    line=dict(width=1, color="white")
    )
)

    # ===================================================================================
    # BOXPLOT
    # ===================================================================================
    
# Ensure the status column contains labels
#st.write("Current columns:", df.columns.tolist())
df["Company Status"] = df["Company Status"].map({
    0: "Stable",
    1: "Bankrupt"
}).fillna(df["Company Status"])

# Create a 2x2 Subplot Grid
boxplot_fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        "Profit Rate by Status",
        "Debt Percentage by Status",
        "Cash Percentage by Status",
        "Sales Efficiency by Status"
    ),
    vertical_spacing=0.18,
    horizontal_spacing=0.12
)

metrics = [
    ('Profit Rate', 1, 1),
    ('Debt Percentage', 1, 2),
    ('Cash Percentage', 2, 1),
    ('Sales Efficiency', 2, 2)
]

# 4. Populate Box Plots into the grid
for metric, row, col in metrics:
    for status in ['Bankrupt', 'Stable']:
        metric_data = df[df['Company Status'] == status][metric]
        
        boxplot_fig.add_trace(
            go.Box(
                y=metric_data,
                x=df[df['Company Status'] == status]['Company Status'],
                name=status,
                # Box filling and outline
                #fillcolor="rgba(92, 115, 242, 0.25)", # Semi-transparent vibrant blue
                line=dict( width=2),
                
                # Outlier configurations matching the dot style
                boxpoints='outliers',
                marker=dict(
                    size=5,
                    opacity=0.75
                ),
                showlegend=False
            ),
            row=row, col=col
        )

# 5. Global Layout & Theme Configuration
boxplot_fig.update_layout(
    height=850,
    width=1200,
    margin=dict(t=140, b=80, l=80, r=40),
    
    # Custom main titles matching the "Comparing Columns" header layout
    title=dict(
        text= f"<b>Company Financial Metrics Comparison</b><br> <sup>X-Axis: Company Status | All Metrics: 0 to 1</sup>",
        x=0.5,
        y=0.95,
        xanchor='center',
        yanchor='top',
        #font=dict(size=22,)
    )
)

# Apply axes styles (faint horizontal lines, no vertical lines)
for i in range(1, 5):
    r = (i-1)//2 + 1
    c = (i-1)%2 + 1
    
    boxplot_fig.update_yaxes(
        showgrid=True,
        zeroline=False,
        showline=False,
        ticks='',
        #tickfont=dict(size=11),
        tickvals=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        range=[-0.05, 1.05],
        row=r, col=c
    )
    
    boxplot_fig.update_xaxes(
        title_text="Company Status" if r == 2 else "", # X-axis title on bottom charts
        #title_font=dict(size=12),
        showgrid=False,
        showline=True,
        #tickfont=dict(size=12),
        row=r, col=c
    )

# Explicitly add individual Y-axis labels
boxplot_fig.update_yaxes(title_text="Profit Rate", row=1, col=1)
boxplot_fig.update_yaxes(title_text="Debt Percentage", row=1, col=2)
boxplot_fig.update_yaxes(title_text="Cash Percentage", row=2, col=1)
boxplot_fig.update_yaxes(title_text="Sales Efficiency", row=2, col=2)

# Adjust Subplot Header Fonts
#for annotation in fig['layout']['annotations']:
#    annotation['font'] = dict(size=15)

    # ===================================================================================
    # HEATMAP
    # ===================================================================================

desired_metrics = [
    "Profit Rate", "Gross Margin", "Liquidity Ratio", 
    "Cash Percentage", "Debt Percentage", "Loan Dependency", "Sales Efficiency"
]

if 'df' in locals() or 'df' in globals():
    # Force all dataset column names to be lowercase and stripped of hidden spaces
    df.columns = df.columns.str.strip().str.lower()
    
    # Create a mapping of lowercase names to your desired display names
    mapping = {name.lower(): name for name in desired_metrics}
    
    # Find which columns in your dataset match our metrics (ignoring case/spaces)
    matched_cols = [col for col in df.columns if col in mapping]

    # If we found all 7 metrics, proceed dynamically
    if len(matched_cols) == len(desired_metrics):
        # Filter dataframe to just those columns and calculate correlation
        corr_matrix = df[matched_cols].corr()
        
        # Rename the correlation matrix index and columns to look pretty (Title Case)
        corr_matrix.index = [mapping[col] for col in corr_matrix.index]
        corr_matrix.columns = [mapping[col] for col in corr_matrix.columns]

        # --- Plotly Heatmap Code ---
        custom_coolwarm = [
            [0.0, "#3f51b5"],  # Dark Blue
            [0.5, "#e0e0e0"],  # Light Gray
            [1.0, "#b71c1c"]   # Dark Red
        ]

        heatmap_fig = px.imshow(
            corr_matrix,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale=custom_coolwarm,
            zmin=-1.0, 
            zmax=1.0
        )

        heatmap_fig.update_layout(
            title=dict(
                text="<b>Correlation Heatmap of Financial Metrics</b>",
                x=0.5,
                y=0.95,
                xanchor='center',
                yanchor='top',
                    ),
            margin=dict(t=140, b=80, l=80, r=40),
            height=850
        )

        heatmap_fig.update_traces(
            xgap=2, 
            ygap=2  
        )


    else:
        # If it still fails, this debug info will tell us EXACTLY what Python is seeing
        st.error("Still missing some metrics. Let's look at the exact match breakdown below:")
        
        st.write("1. What the app is looking for (lowercase):", list(mapping.keys()))
        st.write("2. What actually exists in your file (lowercase):", list(df.columns))
        
        missing = [m for m in mapping.keys() if m not in df.columns]
        st.warning(f"Specifically, Python cannot find these columns: {missing}")
        

    # ===================================================================================
    # DASHBOARD LAYOUT
    # ===================================================================================

#KPi CARDS
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1.container(border=True):
    st.metric("Total Records", len(df))

with kpi2.container(border=True):
    st.metric("Bankrupt", len(df[df["company status"] == "Bankrupt"]))

with kpi3.container(border=True):
    st.metric("Stable", len(df[df["company status"] == "Stable"]))

with kpi4.container(border=True):
    st.metric("Features", len(df.columns))


#FIRST ROW
cols = st.columns([1, 3])

# SCATTER PLOT CARD
right_cell = cols[1].container(
    border=True, height="stretch", vertical_alignment="center"
)

event = None

with right_cell:
    event = st.plotly_chart(
        fig,
        use_container_width=True,
        on_select="rerun"
    )
        
# SETTINGS CARD
top_left_corner = cols[0].container(
border=True, height="content", vertical_alignment="center"
)

with top_left_corner:
    
    #st.subheader("Chart Settings")
    st.markdown("### :material/settings: Chart Settings")
    
    st.session_state.x_axis = st.selectbox(
        "Select X-Axis",
        numeric_columns,
        index=numeric_columns.index(
            st.session_state.x_axis
        )
    )

    st.session_state.y_axis = st.selectbox(
        "Select Y-Axis",
        numeric_columns,
        index=numeric_columns.index(
            st.session_state.y_axis
        )
    )
    
        
# SELECTION CARD
bottom_left_cell = cols[0].container(
    border=True, height="stretch", vertical_alignment="center"
)

with bottom_left_cell:

    st.markdown("### :material/ads_click: Selection Data")

    with st.expander("Raw Selection Event", expanded=False):

        if event:
            st.json(event, expanded=False)
        else:
            st.info("No points selected.")

    #st.divider()

    st.markdown("### Selected Rows")

    if (
        event
        and "selection" in event
        and event["selection"]["point_indices"]
    ):

        selected_indices = event["selection"]["point_indices"]
        st.success(
            f"Showing {len(selected_indices)} selected rows"
        )
        st.dataframe(
            df.iloc[selected_indices],
            use_container_width=True,
            height=250
        )

    else:
        st.info(
            "Use the lasso or box-select tool on the graph."
        )
                

#SECOND ROW
left, right = st.columns(2)

#BOXPLOT CARD
with left:
    box_card = st.container(border=True)

    with box_card:
        st.plotly_chart(
            boxplot_fig,
            use_container_width=True
        )

#HEATMAP CARD
with right:
    heatmap_card = st.container(border=True)

    with heatmap_card:
        st.plotly_chart(
            heatmap_fig,
            use_container_width=True
        )


sns.set_style("whitegrid")

