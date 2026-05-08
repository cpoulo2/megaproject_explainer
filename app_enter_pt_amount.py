# Streamlit app to calcuate the tax break 
# 
# for a megaproject in Illinois. 
# The app will allow users to select a district and a megaproject example, 
# and then it will calculate how much the school district would lose in 
# property tax revenue as a result of the megaproject incentive bill.

# Created by: Christopher Poulos, Public Finance Analyst, Chicago Teachers Union
# Contact: christopherpoulos@ctulocal1.org

# Consulation on propety taxes provided by Joe Pilewski.

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
    
    tax_rate_pct = st.slider("",min_value=1.00,max_value=20.00,value=9.48,step=0.01,format="%0.2f%%",help="You can find your total local tax rate on your property tax bill, which can be found online on the Cook County Treasurer's website: https://www.cookcountytreasurer.com/setsearchparameters.aspx.")
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

    # Set special payment percentage

    special_payment_percentage = .1

    # Inflation - 103% (liberal estimate. According to the Congressional Budget Office's An Update to the Budget and Economic Outlook: 2024 to 2034 (https://www.cbo.gov/publication/60419) the 10 year inflation average is 2%)
    
    inflation = 1.03

    # Set added equalized assesseed value (assuming added EAV equals the full proposed project cost amount) - (Value * Assessed Value (for commerical) * equalization factor).
    # Most recent equalization factor is for 2025 (https://tax.illinois.gov/research/news/2024-cook-county-final-multiplier.html)

    if county ==  "COOK":
        google_hq = (280000000*.25*3.0355)
        bears = (2000000000*.25*3.0355)
        if project == "Enter Custom Amount":
            custom = (project_amount*.25*3.0355)
    else:
        google_hq = (280000000*.3333*1)
        bears = (2000000000*.33333*1)
        if project == "Enter Custom Amount":
            custom = (project_amount*.3333*1)

    if project == "Google HQ":

        # Initial project variables

        project_cost = 280000000
        base_eav =  26249106  # Based on 2025 Assessor certified value of parcels found using maps.cookcountyil.gov. PINs: 17-09-434-024-0000, 17-09-434-021-0000, 17-09-434-022-0000, and 17-09-434-023-00000
        tax_break_term = 25
        special_payment_min = special_payment_percentage * (base_eav*tax_rate) # Assume 100% special payment
        value_added_y1 = google_hq
        project_name = "Google HQ"

        # Tax break calculations

        if county ==  "COOK":
            df_project = pd.DataFrame({
                "Year": list(range(1,26)),
                "Base EAV":[base_eav*1.108**((year - 1) // 3) for year in range(1, 26)],
                "Tax Revenue":[(base_eav*tax_rate)*inflation ** (year-1) for year in range(1,26)],
                "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,26)],
                "Tax Break Nominal": [value_added_y1 for year in range(1,26)],
                "Tax Break EAV Adjusment": [value_added_y1 * 1.108 ** ((year - 1) // 3) for year in range(1, 26)]
            })
            df_project['Tax Break (Cumulative)'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
            df_project['Special Payment (Cumulative)'] = df_project['Special Payment'].cumsum()
            df_project["Tax Break After Special Payment"] = df_project["Tax Break (Cumulative)"] - df_project["Special Payment (Cumulative)"]
            
        else:
            df_project = pd.DataFrame({
                "Year": list(range(1,26)),
                "Base EAV":[base_eav*1.108**((year - 1) // 3) for year in range(1, 26)],
                "Tax Revenue":[(base_eav*tax_rate)*inflation ** (year-1) for year in range(1,26)],
                "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,26)],
                "Tax Break Nominal": [value_added_y1 for year in range(1,26)],
                "Tax Break EAV Adjusment": [value_added_y1 * 1.108 ** ((year - 1) // 4) for year in range(1, 26)]
            })
            df_project['Tax Break (Cumulative)'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
            df_project['Special Payment (Cumulative)'] = df_project['Special Payment'].cumsum()
            df_project["Tax Break After Special Payment"] = df_project["Tax Break (Cumulative)"] - df_project["Special Payment (Cumulative)"]
            
    if project == "Large Online Retail Warehouse ($500 million project)":

        # Initial project variables

        project_cost = 500000001
        base_eav =  project_cost*.1
        tax_break_term = 30
        special_payment_min = special_payment_percentage * (base_eav*tax_rate) # Assume 100% special payment
        value_added_y1 = google_hq
        project_name = "Large Online Retail Warehouse"

        # Tax break calculations

        if county ==  "COOK":
            df_project = pd.DataFrame({
                "Year": list(range(1,31)),
                "Base EAV":[base_eav*1.108**((year - 1) // 3) for year in range(1, 31)],
                "Tax Revenue":[(base_eav*tax_rate)*inflation ** (year-1) for year in range(1,31)],
                "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,31)],
                "Tax Break Nominal": [value_added_y1 for year in range(1,31)],
                "Tax Break EAV Adjusment": [value_added_y1 * 1.108 ** ((year - 1) // 3) for year in range(1, 31)]
            })
            df_project['Tax Break (Cumulative)'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
            df_project['Special Payment (Cumulative)'] = df_project['Special Payment'].cumsum()
            df_project["Tax Break After Special Payment"] = df_project["Tax Break (Cumulative)"] - df_project["Special Payment (Cumulative)"]
            
        else:
            df_project = pd.DataFrame({
                "Year": list(range(1,31)),
                "Base EAV":[base_eav*1.108**((year - 1) // 3) for year in range(1, 31)],
                "Tax Revenue":[(base_eav*tax_rate)*inflation ** (year-1) for year in range(1,31)],
                "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,31)],
                "Tax Break Nominal": [value_added_y1 for year in range(1,31)],
                "Tax Break EAV Adjusment": [value_added_y1 * 1.108 ** ((year - 1) // 4) for year in range(1, 31)]
            })
            df_project['Tax Break (Cumulative)'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
            df_project['Special Payment (Cumulative)'] = df_project['Special Payment'].cumsum()
            df_project["Tax Break After Special Payment"] = df_project["Tax Break (Cumulative)"] - df_project["Special Payment (Cumulative)"]
            


    elif project == "McCaskeys’ Stadium for the Bears and Entertainment Center":

        # Initial project variables

        project_cost = 2000000001
        base_eav = 13042965
        tax_break_term = 40
        special_payment_percentage = 0 # SPECIAL PAYMENT NOT REQUIRED 35 ILCS 200/10-1025(a) (line 22-23) https://ilga.gov/documents/legislation/104/HB/PDF/10400HB0910lv.pdf
        special_payment_min = special_payment_percentage*(base_eav*tax_rate) # Assume 100% special payment
        value_added_y1 = bears
        project_name = "McCaskeys’ Stadium for the Bears and Entertainment Center"
        
        # Tax break calculations

        if county ==  "COOK":
            df_project = pd.DataFrame({
                "Year": list(range(1,41)),
                "Base EAV":[base_eav*1.108**((year - 1) // 3) for year in range(1, 41)],
                "Tax Revenue":[(base_eav*tax_rate)*inflation ** (year-1) for year in range(1,41)],
                "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,41)],
                "Tax Break Nominal": [value_added_y1 for year in range(1,41)],
                "Tax Break EAV Adjusment": [value_added_y1 * 1.108 ** ((year - 1) // 3) for year in range(1, 41)]
            })
            df_project['Tax Break (Cumulative)'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
            df_project['Special Payment (Cumulative)'] = df_project['Special Payment'].cumsum()
            df_project["Tax Break After Special Payment"] = df_project["Tax Break (Cumulative)"] - df_project["Special Payment (Cumulative)"]
            
        else:
            df_project = pd.DataFrame({
                "Year": list(range(1,41)),
                "Base EAV":[base_eav*1.108**((year - 1) // 3) for year in range(1, 41)],
                "Tax Revenue":[(base_eav*tax_rate)*inflation ** (year-1) for year in range(1,41)],
                "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,41)],
                "Tax Break Nominal": [value_added_y1 for year in range(1,41)],
                "Tax Break EAV Adjusment": [value_added_y1 * 1.108 ** ((year - 1) // 4) for year in range(1, 41)]
            })
            df_project['Tax Break (Cumulative)'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
            df_project['Special Payment (Cumulative)'] = df_project['Special Payment'].cumsum()
            df_project["Tax Break After Special Payment"] = df_project["Tax Break (Cumulative)"] - df_project["Special Payment (Cumulative)"]

    elif project == "Enter Custom Amount":

        # Initial project variables
        value_added_y1 = custom
        project_name = "Your custom megaproject"
        project_cost = project_amount

        if project_amount >= 100_000_000 and project_amount <= 500_000_000:
            base_eav = project_amount*.1 # Assigning 10% of project cost to acquistion amount
            tax_break_term = 25
            special_payment_min = special_payment_percentage * (base_eav*tax_rate) # Assume 100% special payment
        # Tax break calculations

            if county ==  "COOK":
                df_project = pd.DataFrame({
                    "Year": list(range(1,26)),
                    "Base EAV":[base_eav*1.108**((year - 1) // 3) for year in range(1, 26)],
                    "Tax Revenue":[(base_eav*tax_rate)*inflation ** (year-1) for year in range(1,26)],
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,26)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,26)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.108 ** ((year - 1) // 3) for year in range(1, 26)]
                })
                df_project['Tax Break (Cumulative)'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment (Cumulative)'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break (Cumulative)"] - df_project["Special Payment (Cumulative)"]
                

            else:
                df_project = pd.DataFrame({
                    "Year": list(range(1,26)),
                    "Base EAV":[base_eav*1.108**((year - 1) // 3) for year in range(1, 26)],
                    "Tax Revenue":[(base_eav*tax_rate)*inflation ** (year-1) for year in range(1,26)],
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,26)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,26)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.108 ** ((year - 1) // 4) for year in range(1, 26)]
                })
                df_project['Tax Break (Cumulative)'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment (Cumulative)'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break (Cumulative)"] - df_project["Special Payment (Cumulative)"]
                

        if project_amount > 500_000_000 and project_amount <= 1_000_000_000:
            base_eav = project_amount*.1 # Assigning 10% of project cost to acquistion amount
            tax_break_term = 30
            special_payment_min = special_payment_percentage * (base_eav*tax_rate) # Assume 100% special payment
            
            # Tax break calculations

            if county ==  "COOK":
                df_project = pd.DataFrame({
                    "Year": list(range(1,31)),
                    "Base EAV":[base_eav*1.108**((year - 1) // 3) for year in range(1, 31)],
                    "Tax Revenue":[(base_eav*tax_rate)*inflation ** (year-1) for year in range(1,31)],
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,31)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,31)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.108 ** ((year - 1) // 3) for year in range(1, 31)]
                })
                df_project['Tax Break (Cumulative)'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment (Cumulative)'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break (Cumulative)"] - df_project["Special Payment (Cumulative)"]
                

            else:
                df_project = pd.DataFrame({
                    "Year": list(range(1,31)),
                    "Base EAV":[base_eav*1.108**((year - 1) // 3) for year in range(1, 31)],
                    "Tax Revenue":[(base_eav*tax_rate)*inflation ** (year-1) for year in range(1,31)],
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,31)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,31)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.108 ** ((year - 1) // 4) for year in range(1, 31)]
                })
                df_project['Tax Break (Cumulative)'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment (Cumulative)'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break (Cumulative)"] - df_project["Special Payment (Cumulative)"]
                


        if project_amount > 1_000_000_000 and project_amount <= 2_000_000_000:
            base_eav = project_amount*.1 # Assigning 10% of project cost to acquistion amount
            tax_break_term = 40
            special_payment_min = special_payment_percentage * (base_eav*tax_rate) # Assume 100% special payment
            
            # Tax break calculations

            if county ==  "COOK":
                df_project = pd.DataFrame({
                    "Year": list(range(1,41)),
                    "Base EAV":[base_eav*1.108**((year - 1) // 3) for year in range(1, 41)],
                    "Tax Revenue":[(base_eav*tax_rate)*inflation ** (year-1) for year in range(1,41)],
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,41)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,41)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.108 ** ((year - 1) // 3) for year in range(1, 41)]
                })
                df_project['Tax Break (Cumulative)'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment (Cumulative)'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break (Cumulative)"] - df_project["Special Payment (Cumulative)"]
                

            else:
                df_project = pd.DataFrame({
                    "Year": list(range(1,41)),
                    "Base EAV":[base_eav*1.108**((year - 1) // 3) for year in range(1, 41)],
                    "Tax Revenue":[(base_eav*tax_rate)*inflation ** (year-1) for year in range(1,41)],
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,41)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,41)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.108 ** ((year - 1) // 4) for year in range(1, 41)]
                })
                df_project['Tax Break (Cumulative)'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment (Cumulative)'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break (Cumulative)"] - df_project["Special Payment (Cumulative)"]
                

        if project_amount > 2_000_000_000:
            base_eav = project_amount*.1 # Assigning 10% of project cost to acquistion amount
            tax_break_term = 40
            special_payment_percentage = 0
            special_payment_min = special_payment_percentage * (base_eav*tax_rate) # Assume 100% special payment
            # Tax break calculations

            if county ==  "COOK":
                df_project = pd.DataFrame({
                    "Year": list(range(1,41)),
                    "Base EAV":[base_eav*1.108**((year - 1) // 3) for year in range(1, 41)],
                    "Tax Revenue":[(base_eav*tax_rate)*inflation ** (year-1) for year in range(1,41)],
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,41)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,41)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.108 ** ((year - 1) // 3) for year in range(1, 41)]
                })
                df_project['Tax Break (Cumulative)'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment (Cumulative)'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break (Cumulative)"] - df_project["Special Payment (Cumulative)"]
                
            else:
                df_project = pd.DataFrame({
                    "Year": list(range(1,41)),
                    "Base EAV":[base_eav*1.108**((year - 1) // 3) for year in range(1, 41)],
                    "Tax Revenue":[(base_eav*tax_rate)*inflation ** (year-1) for year in range(1,41)],
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,41)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,41)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.108 ** ((year - 1) // 4) for year in range(1, 41)]
                })
                df_project['Tax Break (Cumulative)'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment (Cumulative)'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break (Cumulative)"] - df_project["Special Payment (Cumulative)"]
                
    # Overview

    #st.dataframe(df_project)

    # Variables for table

    # mega project without bill

    without = (df_project["Tax Break (Cumulative)"].values[-1] + df_project["Tax Revenue"].values[-1])
    without_schools = without/2

    withbreak = without-(df_project["Tax Break After Special Payment"].values[-1]+ df_project["Tax Revenue"].values[-1])
    with_schools = withbreak/2
    
    with_total = without-withbreak
    with_total_schools = with_total/2

    st.markdown(f"""<h3>Revenue With and Without the Mega Project Bill Over the {tax_break_term} Year Tax Break</h3>""", unsafe_allow_html=True)

    df_table = pd.DataFrame({
        "": ["Town or City", "Schools"],
        "Without Mega Project Bill": [f"${without:,.0f}", f"${without_schools:,.0f}"],
        "With Mega Project Bill": [f"${withbreak:,.0f}", f"${with_schools:,.0f}"],
        "Total Loss": [f"${with_total:,.0f}", f"${with_total_schools:,.0f}"]
    })

    styled_df_table = df_table.style.set_properties(
        subset=["Without Mega Project Bill"],
        **{"color": "green", "font-weight": "bold"}
    ).set_properties(
        subset=["Total Loss"],
        **{"color": "red", "font-weight": "bold"}
    )

    st.dataframe(styled_df_table, hide_index=True, use_container_width=True)
    st.markdown(f"""<sub><b>NOTE</b>: Property tax revenue represents the legally possible yearly levy increase. For more information see the field dictionary in the data_and_calculations.xlsx.</sub>""", unsafe_allow_html=True)

    st.markdown(f"""<h3>Cumulative tax break over time</h3>""", unsafe_allow_html=True)
    
# Animated chart

    base = df_project[["Year", "Tax Break (Cumulative)", "Special Payment (Cumulative)"]].copy()
    chart_data = base.melt(
        id_vars="Year",
        value_vars=["Tax Break (Cumulative)", "Special Payment (Cumulative)"],
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
#     st.markdown(f"""<h3>Without the Mega Project bill's tax gifts to developers, your city or town would receive an additional <b><font size="6"; color="green">${tax_break_year1:,.0f}</b></font> in the first year of the project, and schools would receive <b><font size="6"; color="green">${tax_break_year1_schools:,.0f}.</b></font></h3>

# <h3>But the Mega Project bill removes those funds from local revenue. Over the {tax_break_term} year tax break, <b><font size="6"; color="red">${tax_break_total_after_special_payment:,.0f}</b></font> would stay in developers’ pockets instead of funding your city or town’s needs. Schools would lose <b><font size="6"; color="red">${tax_break_total:,.0f}</b></font> in funds from the project.</h3>
# """,unsafe_allow_html=True,help="The funds removed from localities (the large, bolded red numbers) take into account the so-called 'special payment', which is a payment made on behalf of the owners to the locality in lieu of not paying property taxes. This payment is equal to 10% of the property tax revenue generated by the project's property prior to the year of the mega project subsidy. However, this does not apply to projects over $2 billion.")
#   st.markdown(f"""<p style="text-align: center;">Download our data and calculations to enter your own assumptions</p>""",unsafe_allow_html=True)

    buffer = io.BytesIO()

#     st.dataframe(df_project, hide_index=True, use_container_width=True)

#     df_project = df_project[["Base EAV",]]

#     st.write(df_project.columns)

# #    df_field_dictionary = pd.DataFrame({
        

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_project.to_excel(writer, index=False, sheet_name="Tax Break Data")
        
    buffer.seek(0)

    _, download_col, _ = st.columns([1, 2, 1])
    with download_col:
        st.download_button(
            label="Download Data and Calculations",
            data=buffer,
            file_name="data_and_calculations.xlsx",
            mime="application/vnd.ms-excel",
            icon=":material/download:"
        )

    st.markdown(f"""<sub>
This calculator was built by the Illinois Federation of Teachers based on our best reading of the HB0910 Mega Project bill as-written to help municipalities, school districts, and the general public better understand the sweeping changes and impacts of the bill being rushed forward.  If you have any questions, comments, or concerns regarding the calculations, asssumptions, or data, please contact us as christopherpoulos@ctulocal1.org.  
</sub>
""",unsafe_allow_html=True)

if __name__ == "__main__":
    main()
