# Streamlit app to teach users how the megaproject bill works. 

# Created by: Christopher Poulos, Public Finance Analyst, Chicago Teachers Union
# Contact: christopherpoulos@ctulocal1.org

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import io

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data.csv')
        df = df[df['Level']=="District"]
        df = df[["RCDTS","District","County","$ Total School Tax Rate per $100",]]
        df.columns = df.columns.str.strip()
        df = df.dropna()
        return df
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}. Please ensure the CSV files are in the correct location.")
        return None

# Streamlit app title
def main():    

    # Set page configuration

    st.set_page_config(
        page_title="IL Megaproject Taxbreak Calculator", 
        layout="centered",
        page_icon="💰",
        initial_sidebar_state="expanded"
    )

    
    # Load data

    df = load_data()
    if df is None:
        return

#  This is referred to as <b><font style="background-color:yellow;">tax expenditure</font></b> which refers is a <font style="background-color:yellow;">the loss of government revenue due to subsidies.</font>
    # Title

    st.markdown("""<h1>Illinois Megaproject Tax Break Calculator</h1>""",unsafe_allow_html=True)

    st.markdown("""<p>A new megaproject bill (HB0910) is being talked about in Illinois' legislature right now. If it passes, very big building projects — costing $100 million or more — could get a big tax break for many years, sometimes up to 40 years.

This tool helps explain how the tax break works and shows how much money your school district could lose.

Follow the steps below to learn how it works.
</p>""",unsafe_allow_html=True)

    if 'stage' not in st.session_state:
        st.session_state.stage = 0
        
    def set_state(i):
        st.session_state.stage = i

    if st.session_state.stage == 0:
        st.button('Click here to begin', on_click=set_state, args=[1])

    if st.session_state.stage >= 1:
        st.markdown(f"""<h2>Step 1. Pick a megaproject.</h2>""",unsafe_allow_html=True)
        st.markdown(f"""<p>Megaprojects can include things like a new corporate headquarters, a new stadium, or a new warehouse. Anything costing $100 million or more qualifies for a tax break. 
        
Pick an example megaproject below or type in your own amount to get started.

</p>""",unsafe_allow_html=True)
        project = st.selectbox("Pick a megaproject or enter a custom amount", ["Select one...","Google headquarters","Amazon warehouse","McCaskeys’ Stadium for the Bears and Entertainment Center","Enter Custom Amount"],index=0,key="project",on_change=set_state,args=[2])
        
        if project == "Enter Custom Amount":
            project_name_for_text = "a custom project"
            project_amount = st.number_input(
                "",
                min_value=100_000_000,
                value=280_000_000,
                step=10_000_000,
                format="%d",
                help="Enter whole dollars only. They must be at least $100 million."
            )
            st.caption(f"Custom amount selected: ${int(project_amount):,}")

    inflation = 1.03

    # Defaults — overridden once user picks a district/project
    county = st.session_state.get("county", "COOK")
    tax_rate = st.session_state.get("tax_rate", 0)
    project = st.session_state.get("project", "Select one...")

    # Defaults — overridden once user picks a project
    project_name = ""
    project_cost = 0
    project_cost_text = "$0"
    base_eav = 0
    tax_revenue_year1 = 0
    added_eav = 0
    added_eav_revenue_y1 = 0
    tax_break_term = 0
    special_payment_percentage = 0
    special_payment_min = 0

    # Set added equalized assesseed value (assuming added EAV equals the full proposed project cost amount) - (Value * Assessed Value (for commerical) * equalization factor).
    # Most recent equalization factor is for 2025 (https://tax.illinois.gov/research/news/2024-cook-county-final-multiplier.html)

    # Cook County Assessment Level and Equalization Factor 

    if county ==  "COOK":
        assessment_level = .25
        equalization_factor = 3.0355
    else:
        assessment_level = .3333
        equalization_factor = 1

    
    if project == "Google headquarters":

        # Initial project variables

        project_cost = 280000000
        project_cost_text = "about $280 million"
        base_eav =  26249106  # Based on 2025 Assessor certified value of parcels found using maps.cookcountyil.gov. PINs: 17-09-434-024-0000, 17-09-434-021-0000, 17-09-434-022-0000, and 17-09-434-023-00000
        tax_revenue_year1 = base_eav*tax_rate
        added_eav = project_cost*assessment_level*equalization_factor
        added_eav_revenue_y1 = added_eav*tax_rate 
        project_name = "a Google headquarters"
        project_name_2 = project_name
            
    if project == "Amazon warehouse":

        # Initial project variables

        project_cost = 500000001
        project_cost_text = "just over $500 million"
        base_eav =  project_cost*assessment_level*equalization_factor*.1 # Assigning 10% of project cost to acquistion amount
        tax_revenue_year1 = base_eav*tax_rate
        added_eav = project_cost*assessment_level*equalization_factor
        added_eav_revenue_y1 = added_eav*tax_rate
        project_name = "an Amazon warehouse"
        project_name_2 = project_name

    elif project == "McCaskeys’ Stadium for the Bears and Entertainment Center":

        # Initial project variables

        project_cost = 2000000001
        project_cost_text = "just over $2 billion"
        base_eav = 13042965 # Based on 2025 Assessor certified value of parcels found using maps.cookcountyil.gov. PINs: 02-24-303-009-0000, 02-23-403-002-0000, 02-26-201-010-0000, 02-25-100-005, and 02-25-202-011
        tax_revenue_year1 = base_eav*tax_rate
        added_eav = project_cost*assessment_level*equalization_factor
        added_eav_revenue_y1 = added_eav*tax_rate
        project_name = "the McCaskeys’ Stadium for the Bears and Entertainment Center"
        project_name_2 = project_name

    elif project == "Enter Custom Amount":

        # Initial project variables

        project_cost = project_amount
        project_cost_text = f"${project_cost:,.0f}"
        base_eav = project_cost*assessment_level*equalization_factor*.1 # Assigning 10% of project cost to acquistion amount
        tax_revenue_year1 = base_eav*tax_rate
        added_eav = project_cost*assessment_level*equalization_factor
        added_eav_revenue_y1 = added_eav*tax_rate
        project_name = "a custom megaproject"
        project_name_2 = "custom megaproject"

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

    


    if st.session_state.stage >= 2:
        st.markdown(f"""<p>You picked {project_name}. This project costs {project_cost_text} to build.

Normally that would add about \${added_eav:,.0f} in new taxable property.

But the megaproject bill says very big projects like this do not have to pay property taxes on new buildings for many years.

That means <b><font style="background-color:#FFC107;">this ${added_eav:,.0f} would not be taxed in the first year alone.</font></b>

Now let’s find a tax rate to see how big the tax break would be.

</p>""",unsafe_allow_html=True)
        # Find Chicago Public Schools in index of df["District"].unique()
        cps = [i for i, s in enumerate(df["District"].unique()) if "Chicago Public Schools" in s][0]

        st.markdown("""<h2>Step 2. Pick a school district to find the tax rate.</h2>""", unsafe_allow_html=True)

        district = st.selectbox("", df["District"].unique(), index=cps, key="district")
        df_district = df[df["District"] == district]
        tax_rate = df_district["$ Total School Tax Rate per $100"].values[0] / 100
        county = str(df_district["County"].values[0]).upper()
        st.session_state.tax_rate = tax_rate
        st.session_state.county = county

        st.markdown(f"""<p>You selected {district} which has a tax rate of {tax_rate*100:.2f}%.</p>""",unsafe_allow_html=True)

        col1,col2,col3 = st.columns([1,2,1])

        st.button("Click here to calculate the tax break!",on_click=set_state,args=[3])

        st.button('Go Back', on_click=set_state, args=[1])



    if st.session_state.stage >= 3:

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

        with st.container(horizontal_alignment="center",border=True):

            st.markdown(f"""<h4 style="text-align: center;">Calculation...</h4>
<h3 style="text-align: center;">Your district will lose <font style="color:#D81B60;">${df_project["Tax Expenditure (Cumulative)"].values[-1]:,.0f}</font> over the {tax_break_term} year tax break.

</h3>""",unsafe_allow_html=True)

            if st.button("Click here to take a closer look at the math.",key="closer_look"):

                st.markdown(f"""<h3>A closer look at the math...</h3>""",unsafe_allow_html=True)


                if project_cost > 2_000_000_000:
                    st.markdown(f"""
<p>
{project} costs {project_cost_text}. Projects over $2 billion qualify it for a {tax_break_term} year tax break.

We can estimate how much money schools and other local services could miss out on by using your tax rate and the part of the project that would normally be taxed.

In the first year, your school district could lose about ${df_project["Potential Tax Revenue Year 1"].values[0]:,.0f}.

By the end of the {tax_break_term}-year tax break, your school district could lose about ${df_project["Potential Tax Revenue (Cumulative)"].values[-1]:,.0f} in total.

For projects under \$2 billion, owners have to pay some money back to schools, parks, and other local services. But because your project costs more than \$2 billion, the owners do not have to make those payments.

</p>
""",unsafe_allow_html=True)

                if project_cost > 1_000_000_000 and project_cost <= 2_000_000_000:
                    st.markdown(f"""
<p>
The {project_name_2} costs ${project_cost_text}. Projects over $1 billion qualify it for a {tax_break_term} year tax break.

We can estimate how much money schools and other local services could miss out on by using your tax rate and the part of the project that would normally be taxed.

In the first year, your school district could lose about ${df_project["Potential Tax Revenue Year 1"].values[0]:,.0f}.

Projects under \$2 billion have to pay some money back to schools, parks, and other local services. The bill calls this a "special payment."

In the first year, your school district would get about ${df_project["Special Payment Year 1"].values[0]:,.0f} from this special payment.

Even after this payment, by the end of the {tax_break_term}-year tax break, your school district could still lose about ${df_project["Tax Expenditure (Cumulative)"].values[-1]:,.0f} in total.

</p>
""",unsafe_allow_html=True)

                if project_cost >= 100_000_000 and project_cost < 1_000_000_000:
                    st.markdown(f"""
<p>
The {project_name_2} costs ${project_cost_text}. Projects over $1 billion qualify it for a {tax_break_term} year tax break.

We can estimate how much money schools and other local services could miss out on by using your tax rate and the part of the project that would normally be taxed.

In the first year, your school district could lose about ${df_project["Potential Tax Revenue Year 1"].values[0]:,.0f}.

Projects under \$2 billion have to pay some money back to schools, parks, and other local services. The bill calls this a "special payment."

In the first year, your school district would get about ${df_project["Special Payment Year 1"].values[0]:,.0f} from this special payment.

Even after this payment, by the end of the {tax_break_term}-year tax break, your school district could still lose about ${df_project["Tax Expenditure (Cumulative)"].values[-1]:,.0f} in total.

</p>
""",unsafe_allow_html=True)

                st.markdown(f"""<h3>Take a look at how the tax break grows over time...</h3>""", unsafe_allow_html=True)
                st.markdown(f"""<p>The chart shows the growth of the total revenue lost and the special payment (if one is required).</p>""", unsafe_allow_html=True)
            
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

        st.button('Start Over', on_click=set_state, args=[0])

        st.markdown(f"""
<sub>
This calculator was built by the Illinois Federation of Teachers based on our best reading of the megaproject bill (HB0910) as-written. The calculator is intended to help municipalities, school districts, and the general public better understand the sweeping changes and impacts of the bill being rushed forward.  If you have any questions, comments, or concerns regarding the calculations, asssumptions, or data, please contact us as team@ift-aft.org.  


<b>Last updated</b>: 2026-05-07
</sub>
""",unsafe_allow_html=True)

if __name__ == "__main__":
    main()
