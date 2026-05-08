# Streamlit app to calcuate the tax break under the proposed HB0910 Mega Project bill.

# The end user is aimed at journalists and others with a knowledge of the bill. 
# 
# Created by: Christopher Poulos, Public Finance Analyst, Chicago Teachers Union
# Contact: christopherpoulos@ctulocal1.org

# I am currently working on an explainer version for those with less familiarity with the bill.

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import io

# Streamlit app title
def main():    

    # Set page configuration

    st.set_page_config(
        page_title="IL Megaproject Taxbreak Calculator", 
        layout="centered",
        page_icon="💰",
        initial_sidebar_state="expanded"
    )

    # Title

    st.markdown("""<h1>Illinois Megaproject - Mega Loss Calculator</h1>""",unsafe_allow_html=True)

    st.markdown("""<p>As-written, the Mega Project bill rewrites the tax code for the State of Illinois and signifies the largest transfer of responsibility for revenue for local revenue, schools, and services from private developers to individual property owners in the state’s history.

To understand the impact of the proposed mega project bill, use the calculator below.
</p>""",unsafe_allow_html=True)

    st.markdown("""<h2>Step 1. Adjust to reflect your local tax rate.</h2>""",unsafe_allow_html=True)
    
    tax_rate_pct = st.slider("",min_value=1.00,max_value=20.00,value=9.48,step=0.01,format="%0.2f%%",help="You can find your total local tax rate on your property tax bill.")
    tax_rate = tax_rate_pct / 100

    st.markdown("""<h2>Step 2. Select your county.</h2>""",unsafe_allow_html=True)

    counties = [ "ADAMS", "ALEXANDER", "BOND", "BOONE", "BROWN", "BUREAU", "CALHOUN", "CARROLL", "CASS", "CHAMPAIGN", "CHRISTIAN", "CLARK", "CLAY", "CLINTON", "COLES", "COOK", "CRAWFORD", "CUMBERLAND", "DEKALB", "DEWITT", "DOUGLAS", "DUPAGE", "EDGAR", "EDWARDS", "EFFINGHAM", "FAYETTE", "FORD", "FRANKLIN", "FULTON", "GALLATIN", "GREENE", "GRUNDY", "HAMILTON", "HANCOCK", "HARDIN", "HENDERSON", "HENRY", "IROQUOIS", "JACKSON", "JASPER", "JEFFERSON", "JERSEY", "JO DAVIESS", "JOHNSON", "KANE", "KANKAKEE", "KENDALL", "KNOX", "LAKE", "LASALLE", "LAWRENCE", "LEE", "LIVINGSTON", "LOGAN", "MACON", "MACOUPIN", "MADISON", "MARION", "MARSHALL", "MASON", "MASSAC", "MCDONOUGH", "MCHENRY", "MCLEAN", "MENARD", "MERCER", "MONROE", "MONTGOMERY", "MORGAN", "MOULTRIE", "OGLE", "PEORIA", "PERRY", "PIATT", "PIKE", "POPE", "PULASKI", "PUTNAM", "RANDOLPH", "RICHLAND", "ROCK ISLAND", "SALINE", "SANGAMON", "SCHUYLER", "SCOTT", "SHELBY", "ST CLAIR", "STARK", "STEPHENSON", "TAZEWELL", "UNION", "VERMILION", "WABASH", "WARREN", "WASHINGTON", "WAYNE", "WHITE", "WHITESIDE", "WILL", "WILLIAMSON", "WINNEBAGO", "WOODFORD" ]

    county = st.selectbox("", counties, index=15)

    st.markdown("""<h2>Step 3. Select a sample megaproject or enter a custom amount.</h2>""",unsafe_allow_html=True)

    # Select megaproject
    project = st.radio("", ["Google HQ","Large Online Retail Warehouse ($500 million project)","McCaskeys’ Stadium for the Bears and Entertainment Center","Enter Custom Amount"],index=3)
    if project == "Enter Custom Amount":
        project_amount = st.number_input(
            "",
            min_value=100_000_000,
            value=280_000_000,
            step=10_000_000,
            format="%d",
            help="Enter whole dollars only. They must be at least $100 million."
        )
        st.caption(f"Custom amount selected: ${int(project_amount):,}")

    # Inflation - 103% (liberal estimate. According to the Congressional Budget Office's An Update to the Budget and Economic Outlook: 2024 to 2034 (https://www.cbo.gov/publication/60419) the 10 year inflation average is 2%)
    
    inflation = 1.03

    # Set added equalized assesseed value (assuming added EAV equals the full proposed project cost amount) - (Value * Assessed Value (for commerical) * equalization factor).
    # Most recent equalization factor is for 2025 (https://tax.illinois.gov/research/news/2024-cook-county-final-multiplier.html)

    # Cook County Assessment Level and Equalization Factor 

    if county ==  "COOK":
        assessment_level = .25
        equalization_factor = 3.0355
    else:
        assessment_level = .3333
        equalization_factor = 1

    
    if project == "Google HQ":

        # Initial project variables

        project_cost = 280000000
        base_eav =  26249106  # Based on 2025 Assessor certified value of parcels found using maps.cookcountyil.gov. PINs: 17-09-434-024-0000, 17-09-434-021-0000, 17-09-434-022-0000, and 17-09-434-023-00000
        tax_revenue_year1 = base_eav*tax_rate
        added_eav = project_cost*assessment_level*equalization_factor
        added_eav_revenue_y1 = added_eav*tax_rate 
        project_name = "Google HQ"
            
    if project == "Large Online Retail Warehouse ($500 million project)":

        # Initial project variables

        project_cost = 500000001
        base_eav =  project_cost*assessment_level*equalization_factor*.1 # Assigning 10% of project cost to acquistion amount
        tax_revenue_year1 = base_eav*tax_rate
        added_eav = project_cost*assessment_level*equalization_factor
        added_eav_revenue_y1 = added_eav*tax_rate
        project_name = "Large Online Retail Warehouse"

    elif project == "McCaskeys’ Stadium for the Bears and Entertainment Center":

        # Initial project variables

        project_cost = 2000000001
        base_eav = 13042965 # Based on 2025 Assessor certified value of parcels found using maps.cookcountyil.gov. PINs: 02-24-303-009-0000, 02-23-403-002-0000, 02-26-201-010-0000, 02-25-100-005, and 02-25-202-011
        tax_revenue_year1 = base_eav*tax_rate
        added_eav = project_cost*assessment_level*equalization_factor
        added_eav_revenue_y1 = added_eav*tax_rate
        project_name = "McCaskeys’ Stadium for the Bears and Entertainment Center"

    elif project == "Enter Custom Amount":

        # Initial project variables

        project_cost = project_amount
        base_eav = project_cost*assessment_level*equalization_factor*.1 # Assigning 10% of project cost to acquistion amount
        tax_revenue_year1 = base_eav*tax_rate
        added_eav = project_cost*assessment_level*equalization_factor
        added_eav_revenue_y1 = added_eav*tax_rate
        project_name = "Your custom megaproject"

    # Set tax break year qualificaiton

    if project_cost >= 100_000_000 and project_cost <= 500_000_000:
        tax_break_term = 25
    elif project_cost > 500_000_000 and project_cost <= 1_000_000_000:
        tax_break_term = 30
    elif project_cost > 1_000_000_000:
        tax_break_term = 40

    # Set special payment percentage # If the project cost is greater than $2 billion then the special payment is not required 35 ILCS 200/10-1025(a) (line 22-23) https://ilga.gov/documents/legislation/104/HB/PDF/10400HB0910lv.pdf

    if project_cost > 2_000_000_000:
        special_payment_percentage = 0
        special_payment_min = (special_payment_percentage * (tax_revenue_year1))/2 
    else:
        special_payment_percentage = .1
        special_payment_min = (special_payment_percentage * (tax_revenue_year1))/2

    if county == "COOK":
        assessment_cycle = 3
    else:
        assessment_cycle = 4

    df_project = pd.DataFrame({
        "Year": list(range(1,(tax_break_term+1))),
        "Tax Revenue Inflator (3% Assumption)": [inflation ** (year-1) for year in range(1,(tax_break_term+1))],
        "Potential Tax Revenue Year 1": [added_eav_revenue_y1 for year in range(1,(tax_break_term+1))],
        "Potential Tax Revenue (Inflated)": [added_eav_revenue_y1*inflation ** (year-1) for year in range(1,(tax_break_term+1))],
        "Special Payment Year 1": [special_payment_min for year in range(1,(tax_break_term+1))],
        "Special Payment (Inflated)":[(special_payment_min)*inflation ** (year-1) for year in range(1,(tax_break_term+1))]
    })

    df_project["Potential Tax Revenue (Cumulative)"] = df_project["Potential Tax Revenue (Inflated)"].cumsum()
    df_project["Special Payment (Cumulative)"] = df_project["Special Payment (Inflated)"].cumsum()
    df_project["Tax Expenditure (Cumulative)"] = df_project["Potential Tax Revenue (Cumulative)"] - df_project["Special Payment (Cumulative)"]

    # Variables for table

    # Without Mega Project Bill
    potential_tax_revenue = df_project["Potential Tax Revenue (Cumulative)"].values[-1]
    potential_tax_revenue_schools = potential_tax_revenue/2

    # With Mega Project Bill

    actual_tax_revenue = df_project["Special Payment (Cumulative)"].values[-1]
    actual_tax_revenue_schools = actual_tax_revenue/2
    
    total_without_bill = potential_tax_revenue-actual_tax_revenue
    total_without_bill_schools = potential_tax_revenue_schools-actual_tax_revenue_schools 

    st.markdown(f"""<h3>Revenue With and Without the Mega Project Bill Over the {tax_break_term} Year Tax Break</h3>""", unsafe_allow_html=True)

    df_table = pd.DataFrame({
        "": ["Town or City", "Schools"],
        "Without Mega Project Bill": [f"${total_without_bill:,.0f}", f"${total_without_bill_schools:,.0f}"],
        "With Mega Project Bill": [f"${actual_tax_revenue:,.0f}", f"${actual_tax_revenue_schools:,.0f}"],
        "Total Loss": [f"${total_without_bill:,.0f}", f"${total_without_bill_schools:,.0f}"]
    })

    styled_df_table = df_table.style.set_properties(
        subset=["Without Mega Project Bill"],
        **{"color": "green", "font-weight": "bold"}
    ).set_properties(
        subset=["Total Loss"],
        **{"color": "red", "font-weight": "bold"}
    )

    st.dataframe(styled_df_table, hide_index=True, use_container_width=True)
    
    st.markdown(f"""<sub>
<b>Notes</b>:

1. Potential property tax revenue represents the amount legally allowable under the Property Tax Extension Law Limit (PTELL). For more information see the field dictionary in the downloadable Excel workbook below.

2. If the project cost is greater than $2 billion then the special payment is not required in the current version of the legislation.</sub>
""", unsafe_allow_html=True)

    st.markdown(f"""<h3>Cumulative tax break over time</h3>""", unsafe_allow_html=True)
    
# Animated chart

    base = df_project[["Year", "Potential Tax Revenue (Cumulative)", "Special Payment (Cumulative)"]].copy()
    base.columns = ["Year", "Potential Tax Revenue", "Special Payment"]
    chart_data = base.melt(
        id_vars="Year",
        value_vars=["Potential Tax Revenue", "Special Payment"],
        var_name="Category",
        value_name="Amount"
    )

    frames = []
    for t in base["Year"]:
        temp = chart_data.copy()
        temp["Frame"] = t
        temp["Amount Displayed"] = temp.apply(
            lambda r: r["Amount"] if r["Year"] <= t else 0,
            axis=1
        )
        frames.append(temp)

    anim_chart_data = pd.concat(frames, ignore_index=True)

    fig = px.bar(
        anim_chart_data,
        x="Year",
        y="Amount Displayed",
        color="Category",
        animation_frame="Frame",
        barmode="group",
        labels={"Amount Displayed": "Revenue"}
    )

    y_max = anim_chart_data["Amount Displayed"].max()
    fig.update_layout(transition={"duration": 400}, xaxis={"dtick": 1}, legend=dict(y=1.1,orientation='h'))
    fig.update_yaxes(range=[0, y_max * 1.05], tickprefix="$", separatethousands=True)

    st.plotly_chart(fig, use_container_width=True)

    # Create field dicitionary

    df_field_dictionary = pd.DataFrame({
        "Field": [
            "Year", 
            "Tax Revenue Inflator (3% Assumption)", 
            "Potential Tax Revenue Year 1", 
            "Potential Tax Revenue (Inflated)",
            "Potential Tax Revenue (Cumulative)",
            "Special Payment Year 1", 
            "Special Payment (Inflated)",
            "Special Payment (Cumulative)",
            "Tax Expenditure (Cumulative)"],
        "Description": [
            "Year of the tax break term (1 to 25, 30, or 40 years depending on project cost)",
            "Assumed annual inflation rate of 3% for potential tax revenue and special payment. Our inflator is meant to simulate the Consumer Price Index for All Urban Consumers (CPI-U). Illinois' Property Tax Extension Law Limit (PTELL) limits levy increases by the lessor of 5% or inflation as measured by CPI-U.",
            "The potential tax revenue in year 1 is the selected tax rate multiplied by the added EAV from the megaproject. The added EAV is equal to the project cost multiplied by the assessment rate (.25 if its in Cook County and .3333 if elsewhere) and the equalization factor (3.0355 if its in Cook County and 1 if elsewhere)). We, therefore, assume that the fair market value of the project's parcels are equal to the value of the means of production and labor power used to create the project.",
            "The potential tax revenue tax revenue multiplied by our inflator. It is potential because the bill would prohibit the ability to tax the added EAV and therefore the taxing jurisdicitons would lose out on the ability to increase the levy by the added revenue multiplied by the PTELL limit.",
            "The cumulative sum of the potential tax revenue for each year of the tax break term.",
            "The special payment amount in year 1, which is a minimum required payment from the owner to the taxing jurisdiction in lieu of not having to pay taxes on the added equalized assessed value. The special payment is 10% of the tax revenue in the \"base year\", which is the year to the project adjusted for inflation as measured by the CPI-U. We then divide by 2 because the legislation requires 50% of the special payment to be placed in a property tax relief fund. The special payment is not required by projects greater than $2 billion.",
            "The special payment for each year of the tax break term inflated by the assumed inflation rate.",
            "The cumulative sum of the special payment for each year of the tax break term.",
            "The difference between the cumulative potential tax revenue and the cumulative special payment, which represents the cumulative tax expenditure for the town or city and schools over the tax break term."
        ]
    })

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_project.to_excel(writer, index=False, sheet_name="Tax Break Data")
        df_field_dictionary.to_excel(writer, index=False, sheet_name="Field Dictionary & Methodology")
        
    buffer.seek(0)

    _, download_col, _ = st.columns([1, 2, 1])
    with download_col:
        st.download_button(
            label="Download Data and Methodology",
            data=buffer,
            file_name=f"data_and_methodology_{pd.Timestamp.now().strftime('%Y-%m-%d')}.xlsx",
            mime="application/vnd.ms-excel",
            icon=":material/download:"
        )

    st.markdown(f"""<sub>
This calculator was built by the Illinois Federation of Teachers based on our best reading of the HB0910 Mega Project bill as-written. The calculator is intended to help municipalities, school districts, and the general public better understand the sweeping changes and impacts of the bill being rushed forward.  If you have any questions, comments, or concerns regarding the calculations, asssumptions, or data, please contact us as team@ift-aft.org.  

<b>Last updated</b>: 2026-05-07
</sub>
""",unsafe_allow_html=True)

if __name__ == "__main__":
    main()
