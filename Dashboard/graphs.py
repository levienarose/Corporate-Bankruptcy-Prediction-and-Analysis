import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Sales Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    
)
st.title("Sales Streamlit Dashboard")
st.markdown("_Prototype v0.4.1_")

@st.cache_data
def load_data(file):
    data = pd.read_csv(file)
    return data

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])


if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    


        # ===================================================================================
        # PLOTLY
        # ===================================================================================
    #Default settings
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

    fig = px.scatter(
        df,
        x=st.session_state.x_axis,
        y=st.session_state.y_axis,
        color="Company Status",
        color_discrete_map={
            "Bankrupt": "#F87171",
            "Stable":"#4ADE80"    
        },
        template="plotly_white",
        title="Comparison Chart",
        hover_data=df.columns
    )

    # FIGURE LAYOUT
    fig.update_layout(
        height=650,
        clickmode="event+select",
        #barmode={'Stable': '#2ecc71', 'Bankrupt': '#e74c3c'},
        title={
            "text": (
                f"<b>Comparing Columns</b><br>"
                f"<sup>X-Axis: {st.session_state.x_axis} | "
                f"Y-Axis: {st.session_state.y_axis}</sup>"
            ),
            "x": 0.5,
            "xanchor": "center"
        },
        legend_title_text=(
            f"Legend ({st.session_state.color_by})"
            if st.session_state.color_by
            else "Variables"
        )
    )    

    fig.update_traces(
    marker=dict(
        size=10,
        opacity=0.75,
        line=dict(width=1, color="white")
        )
    )
    
    # DISPLAY CHART FIRST
    event = None
    # SETTINGS BELOW GRAPH
    st.markdown("---")

    with st.expander("⚙️ Chart Settings", expanded=True):

        col1, col2, col3 = st.columns(3)

        with col1:
            st.session_state.x_axis = st.selectbox(
                "Select X-Axis",
                numeric_columns,
                index=numeric_columns.index(
                    st.session_state.x_axis
                )
            )

        with col2:
            st.session_state.y_axis = st.selectbox(
                "Select Y-Axis",
                numeric_columns,
                index=numeric_columns.index(
                    st.session_state.y_axis
                )
            )

        with col3:
            color_options = [None] + all_columns

            current_index = (
                color_options.index(st.session_state.color_by)
                if st.session_state.color_by in color_options
                else 0
            )

            st.session_state.color_by = st.selectbox(
                "Color By",
                color_options,
                index=current_index
            )

   #Selection Data
    st.markdown("---")

    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.subheader("📌 Raw Selection Data")
        st.json(event)

    with right_col:
        st.subheader("📄 Selected Rows")

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
                use_container_width=True
            )

        else:
            st.info(
                "💡 Use the lasso or box-select tool "
                "on the graph to select data points."
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
    
    # Dark mode styling constants extracted from your target image
    BG_COLOR = "#0D1117"          # Deep dark background
    ACCENT_BLUE = "#5C73F2"       # Vibrant purple-blue fill
    GRID_COLOR = "#21262D"        # Faint gridline color
    TEXT_COLOR = "#FFFFFF"        # White text for readability
    
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
                    fillcolor="rgba(92, 115, 242, 0.25)", # Semi-transparent vibrant blue
                    line=dict(color=ACCENT_BLUE, width=2),
                    
                    # Outlier configurations matching the dot style
                    boxpoints='outliers',
                    marker=dict(
                        color=ACCENT_BLUE,
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
        plot_bgcolor=BG_COLOR,
        paper_bgcolor=BG_COLOR,
        margin=dict(t=140, b=80, l=80, r=40),
        
        # Custom main titles matching the "Comparing Columns" header layout
        title=dict(
            text="<b>Company Financial Metrics Comparison</b><br><span style='font-size:13px;color:#C9D1D9;'>X-Axis: Company Status | All Metrics: 0 to 1</span>",
            x=0.5,
            y=0.95,
            xanchor='center',
            yanchor='top',
            font=dict(size=22, color=TEXT_COLOR)
        )
    )
    
    # Apply axes styles (faint horizontal lines, no vertical lines)
    for i in range(1, 5):
        r = (i-1)//2 + 1
        c = (i-1)%2 + 1
        
        boxplot_fig.update_yaxes(
            showgrid=True,
            gridcolor=GRID_COLOR,
            zeroline=False,
            showline=False,
            ticks='',
            tickfont=dict(color="#8B949E", size=11),
            tickvals=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            range=[-0.05, 1.05],
            row=r, col=c
        )
        
        boxplot_fig.update_xaxes(
            title_text="Company Status" if r == 2 else "", # X-axis title on bottom charts
            title_font=dict(color="#8B949E", size=12),
            showgrid=False,
            showline=True,
            linecolor=GRID_COLOR,
            tickfont=dict(color=TEXT_COLOR, size=12),
            row=r, col=c
        )
    
    # Explicitly add individual Y-axis labels
    boxplot_fig.update_yaxes(title_text="Profit Rate", title_font=dict(color="#8B949E"), row=1, col=1)
    boxplot_fig.update_yaxes(title_text="Debt Percentage", title_font=dict(color="#8B949E"), row=1, col=2)
    boxplot_fig.update_yaxes(title_text="Cash Percentage", title_font=dict(color="#8B949E"), row=2, col=1)
    boxplot_fig.update_yaxes(title_text="Sales Efficiency", title_font=dict(color="#8B949E"), row=2, col=2)
    
    # Adjust Subplot Header Fonts
    for annotation in fig['layout']['annotations']:
        annotation['font'] = dict(size=15, color=TEXT_COLOR)
    
    # 6. Render chart inside Streamlit
    #st.plotly_chart(fig, use_container_width=True)
    
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
            st.markdown(
            "<h2 style='text-align: center; color: white;'>Correlation Heatmap of Financial Metrics</h2>",
            unsafe_allow_html=True
            )    
        
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
                plot_bgcolor="#0e1117",  
                paper_bgcolor="#0e1117", 
                font=dict(color="white", family="Arial"),
                xaxis=dict(tickmode='linear', side='bottom', gridcolor="#262730"),
                yaxis=dict(tickmode='linear', gridcolor="#262730"),
                hoverlabel=dict(bgcolor="#1f2c3f", font_size=14),
                margin=dict(l=150, r=20, t=20, b=100), 
                height=650
            )
    
            heatmap_fig.update_traces(
                textfont=dict(size=12, color="white"),
                xgap=2, 
                ygap=2  
            )
    
            #st.plotly_chart(fig, use_container_width=True)
    
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


        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        with kpi1:
            st.metric("Total Records", len(df))
        
        with kpi2:
            st.metric(
                "Bankrupt",
                len(df[df["Company Status"] == "Bankrupt"])
            )
        
        with kpi3:
            st.metric(
                "Stable",
                len(df[df["Company Status"] == "Stable"])
            )
        
        with kpi4:
            st.metric(
                "Features",
                len(df.columns)
            )
        
        st.plotly_chart(
            scatter_fig,
            use_container_width=True
        )
        
        left, right = st.columns(2)
        
        with left:
            st.plotly_chart(
                boxplot_fig,
                use_container_width=True
            )
        
        with right:
            st.plotly_chart(
                heatmap_fig,
                use_container_width=True
            )
            

else:
    st.info("Please upload a CSV file to begin.")
    

sns.set_style("whitegrid")

