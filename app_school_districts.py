# Streamlit app to calcuate the tax break 
# 
# for a megaproject in Illinois. 
# The app will allow users to select a district and a megaproject example, 
# and then it will calculate how much the school district would lose in 
# property tax revenue as a result of the megaproject incentive bill.

# Created by: Christopher Poulos, Public Finance Analyst, Chicago Teachers Union
# Contact: christopherpoulos@ctulocal1.org

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import io

# TODO: add county into df so I can create assessment rate and equalization factor for cook. (confirm these only apply to cook).abs


# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data.csv')
        df = df[df['Level']=="District"]
        df = df[["RCDTS","District","County","$ Total School Tax Rate per $100"]]
        df.columns = df.columns.str.strip()
        df = df.dropna()
        return df
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}. Please ensure the CSV files are in the correct location.")
#        return None
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

    # Title

    st.markdown("""<h1>Illinois Megaproject Taxbreak Calculator</h1>""",unsafe_allow_html=True)

    st.markdown("""<h2>Select a school district and megaproject amount or example to see how HB0910 will cost your students.</h2>""",unsafe_allow_html=True)

    # Find Chicago Public Schools in index of df["District"].unique()

    cps = [i for i, s in enumerate(df["District"].unique()) if "Chicago Public Schools" in s][0]

    # Select district
    district = st.selectbox("Select a school district",df["District"].unique(),index=cps)

    df_district = df[df["District"] == district]

    # Create a variable for selected district's property tax rate and eav

    tax_rate = (df_district["$ Total School Tax Rate per $100"].values[0] / 100) # NOTE: This is a conservativer assumption since commercial tax rates are higher than residential. 

#    st.markdown("""<h3>Select a megaproject example</h3>""",unsafe_allow_html=True)

    # Select megaproject
    project = st.radio("Select a megaproject example or enter a custom amount", ["Google HQ","Bears Stadium and Entertainment Center","Enter Custom Amount"],index=2)
    if project == "Enter Custom Amount":
        project_amount = st.number_input(
            "Or enter a custom megaproject amount ($)",
            min_value=100_000_000,
            value=280_000_000,
            step=10_000_000,
            format="%d",
            help="Enter whole dollars only."
        )
        st.caption(f"Custom amount selected: ${int(project_amount):,}")

    # Set special payment percentage

    special_payment_percentage = .1

    # Inflation - 103% (liberal estimate. According to the Congressional Budget Office's An Update to the Budget and Economic Outlook: 2024 to 2034 (https://www.cbo.gov/publication/60419) the 10 year inflation average is 2%)
    
    inflation = 1.03

    # Set added equalized assesseed value (assuming added EAV equals the full proposed project cost amount) - (Value * Assessed Value (for commerical) * equalization factor).
    # Most recent equalization factor is for 2025 (https://tax.illinois.gov/research/news/2024-cook-county-final-multiplier.html)

    if df_district['County'].values[0] ==  "Cook":
        google_hq = (280000000*.25*3.0355)
        b = (500000000*.25*3.0355)
        c = (1000000000*.25*3.0355)
        bears = (2000000000*.25*3.0355)
        if project == "Enter Custom Amount":
            custom = (project_amount*.25*3.0355)
    else:
        google_hq = (280000000*.25*3.0355)
        b = (500000000*.25*3.0355)
        c = (1000000000*.25*3.0355)
        bears = (2000000000*.25*3.0355)
        if project == "Enter Custom Amount":
            custom = (project_amount*.25*3.0355)

    if project == "Google HQ":

        # Initial project variables

        project_cost = 280000000
        base_eav =  26249106  # Based on 2025 Assessor certified value of parcels found using maps.cookcountyil.gov. PINs: 17-09-434-024-0000, 17-09-434-021-0000, 17-09-434-022-0000, and 17-09-434-023-00000
        tax_break_term = 25
        special_payment_min = special_payment_percentage * (base_eav*tax_rate) # Assume 100% special payment
        value_added_y1 = google_hq
        project_name = "Google HQ"

        # Tax break calculations

        if df_district['County'].values[0] ==  "Cook":
            df_project = pd.DataFrame({
                "Year": list(range(1,26)),
                "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,26)],
                "Tax Break Nominal": [value_added_y1 for year in range(1,26)],
                "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 3) for year in range(1, 26)]
            })
            df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
            df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
            df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
        else:
            df_project = pd.DataFrame({
                "Year": list(range(1,26)),
                "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,26)],
                "Tax Break Nominal": [value_added_y1 for year in range(1,26)],
                "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 4) for year in range(1, 26)]
            })
            df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
            df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
            df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]


    elif project == "Bears Stadium and Entertainment Center":

        # Initial project variables

        project_cost = 2000000000
        base_eav = 13042965
        tax_break_term = 40
        special_payment_percentage = 0 # SPECIAL PAYMENT NOT REQUIRED 35 ILCS 200/10-1025(a) (line 22-23) https://ilga.gov/documents/legislation/104/HB/PDF/10400HB0910lv.pdf
        special_payment_min = special_payment_percentage*(base_eav*tax_rate) # Assume 100% special payment
        value_added_y1 = bears
        project_name = "Bears Stadium and Entertainment Center"
        
        # Tax break calculations

        if df_district['County'].values[0] ==  "Cook":
            df_project = pd.DataFrame({
                "Year": list(range(1,41)),
                "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,41)],
                "Tax Break Nominal": [value_added_y1 for year in range(1,41)],
                "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 3) for year in range(1, 41)]
            })
            df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
            df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
            df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
        else:
            df_project = pd.DataFrame({
                "Year": list(range(1,41)),
                "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,41)],
                "Tax Break Nominal": [value_added_y1 for year in range(1,41)],
                "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 4) for year in range(1, 41)]
            })
            df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
            df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
            df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]

    elif project == "Enter Custom Amount":

        # Initial project variables
        value_added_y1 = custom
        project_name = "Your custom megaproject"
        project_cost = project_amount

        if project_amount >= 100_000_000 and project_amount <= 500_000_000:
            base_eav = project_amount*.2 # Assigning 20% of project cost to acquistion amount
            tax_break_term = 25
            special_payment_min = special_payment_percentage * (base_eav*tax_rate) # Assume 100% special payment
        # Tax break calculations

            if df_district['County'].values[0] ==  "Cook":
                df_project = pd.DataFrame({
                    "Year": list(range(1,26)),
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,26)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,26)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 3) for year in range(1, 26)]
                })
                df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
            else:
                df_project = pd.DataFrame({
                    "Year": list(range(1,26)),
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,26)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,26)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 4) for year in range(1, 26)]
                })
                df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
        if project_amount > 500_000_000 and project_amount <= 1_000_000_000:
            base_eav = project_amount*.2 # Assigning 20% of project cost to acquistion amount
            tax_break_term = 30
            special_payment_min = special_payment_percentage * (base_eav*tax_rate) # Assume 100% special payment
            
            # Tax break calculations

            if df_district['County'].values[0] ==  "Cook":
                df_project = pd.DataFrame({
                    "Year": list(range(1,31)),
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,31)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,31)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 3) for year in range(1, 31)]
                })
                df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
            else:
                df_project = pd.DataFrame({
                    "Year": list(range(1,31)),
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,31)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,31)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 4) for year in range(1, 31)]
                })
                df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
        if project_amount > 1_000_000_000 and project_amount <= 2_000_000_000:
            base_eav = project_amount*.2 # Assigning 20% of project cost to acquistion amount
            tax_break_term = 40
            special_payment_min = special_payment_percentage * (base_eav*tax_rate) # Assume 100% special payment
            
            # Tax break calculations

            if df_district['County'].values[0] ==  "Cook":
                df_project = pd.DataFrame({
                    "Year": list(range(1,41)),
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,41)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,41)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 3) for year in range(1, 41)]
                })
                df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
            else:
                df_project = pd.DataFrame({
                    "Year": list(range(1,41)),
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,41)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,41)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 4) for year in range(1, 41)]
                })
                df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
        if project_amount > 2_000_000_000:
            base_eav = project_amount*.2 # Assigning 20% of project cost to acquistion amount
            tax_break_term = 40
            special_payment_percentage = 0
            special_payment_min = special_payment_percentage * (base_eav*tax_rate) # Assume 100% special payment
            # Tax break calculations

            if df_district['County'].values[0] ==  "Cook":
                df_project = pd.DataFrame({
                    "Year": list(range(1,41)),
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,41)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,41)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 3) for year in range(1, 41)]
                })
                df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
            else:
                df_project = pd.DataFrame({
                    "Year": list(range(1,41)),
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,41)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,41)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 4) for year in range(1, 41)]
                })
                df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]

    # Overview

    special_payment_total = df_project["Special Payment Cumulative"].values[-1]
    tax_break_total = df_project["Tax Break Cumulative"].values[-1]
    special_payment_ratio = (special_payment_total / tax_break_total) if tax_break_total else 0

    if project == "Enter Custom Amount":
        st.markdown(f"""<h2>How much would a project like this cost your school district?</h2>
<p>
<ul>
<li>{project_name} makes it <b>eligible for a {tax_break_term} year tax break.</b></li>
<li>This would cost {district} <b>${df_project["Tax Break After Special Payment"].values[-1]:,.0f}</b> over the {tax_break_term} year period.<sup>1</sup></li>
<li>This cost includes the "special payment" required by HB0910 that must be made by the owner to the district. This amounts to a cumulative of <b>${special_payment_total:,.0f}</b> over the {tax_break_term} year period. This equals <b>{special_payment_ratio:.2%}</b> of the cumulative gross tax break.</li>
<li>Half the the "special payment" is required to be deposited in a "property tax relief fund" meaning that only <b>${special_payment_total / 2:,.0f}</b> directly impacts the district's finances, or <b>{special_payment_ratio / 2:.2%}</b> of the cumulative gross tax break.</li>
</ul>
</p>
""",unsafe_allow_html=True,help="Special payment is a payment in lieu of the owner avoiding taxes. It applies to projects under $2 billion and is equal to 10% of the property tax revenue generated by the project area the 'base year', which is the year prior to the calednar year in which the megaproject is awarded a tax expenditure.")
    else:
        st.markdown(f"""<h2>How much would a project like this cost your school district?</h2>
<p>
<ul>
<li>The {project_name} is a ${project_cost:,.0f} megaproject, which makes it <b>eligible for a {tax_break_term} year tax break.</b></li>
<li>This would cost {district} <b>${df_project["Tax Break After Special Payment"].values[-1]:,.0f}</b> over the {tax_break_term} year period.<sup>1</sup></li>
<li>This cost includes the "special payment" required by HB0910 that must be made by the owner to the district. This amounts to a cumulative of <b>${special_payment_total:,.0f}</b> over the {tax_break_term} year period. This equals <b>{special_payment_ratio:.2%}</b> of the cumulative gross tax break.</li>
<li>Half the the "special payment" is required to be deposited in a "property tax relief fund" meaning that only <b>${special_payment_total / 2:,.0f}</b> directly impacts the district's finances, or <b>{special_payment_ratio / 2:.2%}</b> of the cumulative gross tax break.</li>
</ul>
</p>
</h3>
""",unsafe_allow_html=True)
    st.subheader(f"Cumulative tax break over time")

    # Download button

    # @st.cache_data
    # def convert_for_download(df_project):
    #     return df_project.to_excel()

    # xlsx = convert_for_download(df_project)

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_project.to_excel(writer, index=False, sheet_name="Tax Break Data")
        
    buffer.seek(0)

    st.download_button(
        label="Download Tax Break Data",
        data=buffer,
        file_name="data.xlsx",
        mime="application/vnd.ms-excel",
        icon=":material/download:",
        help="The excel file contains the underlying data used to perform the calculations and steps to replicating our math."
    )
    



# Animated chart

    base = df_project[["Year", "Tax Break Cumulative", "Special Payment Cumulative"]].copy()
    chart_data = base.melt(
        id_vars="Year",
        value_vars=["Tax Break Cumulative", "Special Payment Cumulative"],
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
        labels={"Amount Displayed": "Cumulative Amount", "Year": "Year", "Category": "", "Frame": "Year"}
    )

    fig.update_layout(transition={"duration": 400}, xaxis={"dtick": 1}, legend=dict(y=1.1,orientation='h'))
    fig.update_yaxes(autorange=True, tickprefix="$", separatethousands=True)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""<sub><b>Notes:</b></sub>

<sub>1. The current legislation requires a so-called "special payment" (this is a payment in lieu of the owner paying full taxes) equal to 10% of the base year property tax revenue adjusted for inflation.</sub>

<sub><b>Sources:</b></sub>
<ul>
<sub><li>School district equalized assessed value and tax rate data - Illinois Report Card SY2025, Illinois School Board of Education.</li></sub>
<sub><li>Megaproject legislation on termination dates and special assessments - <a href="https://ilga.gov/documents/legislation/104/HB/PDF/10400HB0910lv.pdf">HB0910</a>.</li></sub>
</ul>
""",unsafe_allow_html=True)

#    df_project_year = df_project[df_project["Year"] == year_value]    

#    st.markdown(f"The tax break for year {year_value} is \${df_project.loc[df_project['Year'] == year_value, "Tax Break After Special Payment"].values[0]:,.0f}.")

if __name__ == "__main__":
    main()
