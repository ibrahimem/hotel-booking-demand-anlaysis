import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Hotel Booking Analysis Dashboard",
    layout="wide",
    page_icon="🏨"
)

# -------------------------
# Load Data
# -------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_hotel_bookings.csv")
    return df


df = load_data()

# -------------------------
# Sidebar Filters
# -------------------------


st.sidebar.title("Navigation & Filters")

page = st.sidebar.radio(
    "Go to",
    ["Main Dashboard", "Analysis", "Final Insights"]
)

st.sidebar.divider()
st.sidebar.subheader("Filter Data")

hotel_filter = st.sidebar.multiselect(
    "Hotel Type",
    options=df["hotel"].unique(),
    default=df["hotel"].unique()
)

market_segment_filter = st.sidebar.multiselect(
    "Market Segment",
    options=df["market_segment"].unique(),
    default=df["market_segment"].unique()
)

customer_type_filter = st.sidebar.multiselect(
    "Customer Type",
    options=df["customer_type"].unique(),
    default=df["customer_type"].unique()
)

meal_filter = st.sidebar.multiselect(
    "Meal Type",
    options=df["meal"].unique(),
    default=df["meal"].unique()
)

deposit_type_filter = st.sidebar.multiselect(
    "Deposit Type",
    options=df["deposit_type"].unique(),
    default=df["deposit_type"].unique()
)

status_filter = st.sidebar.multiselect(
    "Reservation Status",
    options=df["reservation_status"].unique(),
    default=df["reservation_status"].unique()
)

arrival_month_filter = st.sidebar.multiselect(
    "Arrival Month",
    options=df["arrival_date_month"].unique(),
    default=df["arrival_date_month"].unique()
)
 
lead_time_filter = st.sidebar.slider(
    "Lead Time (Days)",
    int(df["lead_time"].min()),
    int(df["lead_time"].max()),
    (int(df["lead_time"].min()), int(df["lead_time"].max()))
)

st.sidebar.divider()
with st.sidebar.expander("Filter Summary"):
    st.write(f"**Hotels:** {len(hotel_filter)} selected")
    st.write(f"**Market segments:** {len(market_segment_filter)} selected")
    st.write(f"**Customer types:** {len(customer_type_filter)} selected")
    st.write(f"**Deposit types:** {len(deposit_type_filter)} selected")
    st.write(f"**Reservation statuses:** {len(status_filter)} selected")
    st.write(f"**Arrival months:** {len(arrival_month_filter)} selected")

# -------------------------
# Apply Filters
# -------------------------

filtered_df = df[
    (df["hotel"].isin(hotel_filter)) &
    (df["market_segment"].isin(market_segment_filter)) &
    (df["customer_type"].isin(customer_type_filter)) &
    (df["meal"].isin(meal_filter)) &
    (df["deposit_type"].isin(deposit_type_filter)) &
    (df["reservation_status"].isin(status_filter)) &
    (df["arrival_date_month"].isin(arrival_month_filter)) &
    (df["lead_time"].between(lead_time_filter[0], lead_time_filter[1]))
]

# =================================================
# MAIN PAGE
# =================================================

if page == "Main Dashboard":
    st.title("🏨 Hotel Booking Analysis Dashboard")
    st.markdown("Explore trends and cancellations in hotel bookings.")

    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)

    total_bookings = filtered_df.shape[0]
    cancellation_rate = filtered_df["is_canceled"].mean()
    avg_adr = filtered_df["adr"].mean()
    special_reqs = filtered_df["total_of_special_requests"].sum()

    col1.metric("Total Bookings", f"{total_bookings:,}")
    col2.metric("Cancellation Rate", f"{cancellation_rate:.2%}")
    col3.metric("Avg Daily Rate (ADR)", f"${avg_adr:,.2f}")
    col4.metric("Special Requests", f"{special_reqs:,}")

    st.divider()
    st.subheader("Filtered Data Preview")
    st.dataframe(filtered_df.head(10), use_container_width=True)

# =================================================
# ANALYSIS PAGE
# =================================================

elif page == "Analysis":
    st.title(" Exploratory Data Analysis")

    tab1, tab2, tab3 = st.tabs([
        "Univariate Analysis",
        "Bivariate Analysis",
        "Multivariate Analysis"
    ])

    with tab1:
        st.subheader("Distribution of Lead Time")
        fig1 = px.histogram(
            filtered_df,
            x="lead_time",
            nbins=50,
            title="Lead Time Distribution",
            color_discrete_sequence=['yellowgreen']
        )
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("Hotel Type Proportion")
        hotel_counts = filtered_df['hotel'].value_counts().reset_index()
        hotel_counts.columns = ['hotel', 'count']
        fig2 = px.pie(
            hotel_counts,
            values='count',
            names='hotel',
            title="Hotel Type Distribution",
            hole=0.3   #Creates a donut chart
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Booking Target Distribution")
        target_counts = filtered_df["is_canceled"].value_counts().reset_index()
        target_counts.columns = ["is_canceled", "bookings"]
        target_counts["status"] = target_counts["is_canceled"].map({0: "Not Canceled", 1: "Canceled"})
        fig_target = px.bar(
            target_counts.sort_values("is_canceled"),
            x="status",
            y="bookings",
            title="Booking Target Distribution",
            text_auto=True,
            labels={"status": "Booking Outcome", "bookings": "Number of Bookings"}
        )
        st.plotly_chart(fig_target, use_container_width=True)


    with tab2:
        st.subheader("Lead Time vs Cancellation")
        sample_df = filtered_df.sample(min(2000, len(filtered_df)))
        fig3 = px.box(
            sample_df,
            x="is_canceled",
            y="lead_time",
            title="Lead Time by Cancellation Status",
            labels={"is_canceled": "Canceled", "lead_time": "Lead Time (Days)"}
        )
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("ADR (Average Daily Rate) by Booking Target")
        fig3b = px.box(
            sample_df,
            x="is_canceled",
            y="adr",
            title="ADR by Booking Target",
            labels={"is_canceled": "Canceled", "adr": "Average Daily Rate"}
        )
        st.plotly_chart(fig3b, use_container_width=True)

        st.subheader("ADR by Market Segment")
        adr_by_segment = (
            filtered_df
            .groupby("market_segment")["adr"]
            .mean()
            .reset_index()
            .sort_values(by="adr", ascending=False)
        )
        fig4 = px.bar(
            adr_by_segment,
            x="market_segment",
            y="adr",
            title="Average ADR per Market Segment",
            text_auto='.2f'
        )
        st.plotly_chart(fig4, use_container_width=True)

    with tab3:
        st.subheader("Cancellation and Booking Patterns")
        col_a, col_b = st.columns(2)

        with col_a:
            monthly_counts = (
                filtered_df
                .groupby("arrival_date_month")["hotel"]
                .count()
                .reset_index()
                .rename(columns={"hotel": "bookings"})
            )
            monthly_counts["arrival_date_month"] = pd.Categorical(
                monthly_counts["arrival_date_month"],
                categories=[
                    'January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December'
                ],
                ordered=True
            )
            monthly_counts = monthly_counts.sort_values("arrival_date_month")
            fig5 = px.bar(
                monthly_counts,
                x="arrival_date_month",
                y="bookings",
                title="Bookings by Arrival Month",
                text_auto=True
            )
            fig5.update_layout(xaxis_title="Month", yaxis_title="Bookings")
            st.plotly_chart(fig5, use_container_width=True)

        with col_b:
            cancel_segment = (
                filtered_df
                .groupby("market_segment")["is_canceled"]
                .mean()
                .reset_index()
                .sort_values(by="is_canceled", ascending=False)
            )
            fig6 = px.bar(
                cancel_segment,
                x="market_segment",
                y="is_canceled",
                title="Cancellation Rate by Market Segment",
                text_auto='.0%'
            )
            fig6.update_layout(yaxis_tickformat='%')
            st.plotly_chart(fig6, use_container_width=True)

    with st.expander("Meal and Cancellation Summary"):
        meal_summary = (
            filtered_df
            .groupby("meal")
            .agg(
                bookings=("hotel", "count"),
                canceled=("is_canceled", "sum"),
                avg_lead_time=("lead_time", "mean"),
                total_special_requests=("total_of_special_requests", "sum")
            )
            .reset_index()
        )
        meal_summary["cancel_rate"] = meal_summary["canceled"] / meal_summary["bookings"]
      

# =================================================
# FINAL INSIGHTS PAGE
# =================================================

elif page == "Final Insights":
    st.title("🧠 Project Findings")

    st.markdown(
        """
        ### 1. Data Cleaning Documentation
        - **Missing Values:** Handled nulls in 'country', 'agent', and 'company' during pre-processing.
        - **Data Types:** Converted date strings to datetime objects.
        - **Duplicates:** Removed redundant rows to ensure analysis accuracy.

        ### 2. Main Discoveries
        - **Cancellations:** Higher lead times are strongly correlated with a higher probability of cancellation.
        - **Revenue:** Market segments like 'Online TA' tend to have higher Average Daily Rates (ADR) but also higher cancellation rates.
        - **Seasonality:** Booking volumes peak during summer months (arrival_date_month).

        ### 3. Business Recommendations
        - **Deposit Policies:** Implement non-refundable deposits for bookings with lead times greater than 100 days.
        - **Overbooking Strategy:** Use the cancellation rate insights to optimize room occupancy.
        - **Marketing:** Target segments with low cancellation rates (like 'Groups') for long-term stability.
        """
    )
