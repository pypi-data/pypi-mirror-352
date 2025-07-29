import sqlite3
import pandas as pd
import panel as pn
import matplotlib.pyplot as plt

# Enable Panel's Matplotlib support


# Connect to the SQLite database
conn = sqlite3.connect(r'D:\Users\ritvik\projects\GEOGLAM\Output\ml\db\presentation_v2.db')

# Find every table except config*
all_tables = pd.read_sql_query(
    "SELECT name FROM sqlite_master WHERE type='table';",
    conn
)['name'].tolist()
data_tables = [t for t in all_tables if not t.lower().startswith('config')]

# Columns we need in each table
required = {
    'Country',
    'Crop',
    'Harvest Year',
    'Observed Yield (tn per ha)',
    'Predicted Yield (tn per ha)'
}

frames = []
for tbl in data_tables:
    cols = pd.read_sql_query(f"PRAGMA table_info('{tbl}');", conn)['name'].tolist()
    if required.issubset(cols):
        df = pd.read_sql_query(f"""
            SELECT
                Country,
                Crop,
                [Harvest Year]    AS year,
                [Observed Yield (tn per ha)]   AS observed,
                [Predicted Yield (tn per ha)]  AS predicted
            FROM "{tbl}"
        """, conn)
        frames.append(df)

if not frames:
    raise ValueError("No tables found with the required schema!")

df_all = pd.concat(frames, ignore_index=True)
print(df_all)
conn.close()

# 3. Build Panel widgets
country_select = pn.widgets.Select(
    name='Country',
    options=sorted(df_all['Country'].unique())
)
crop_select = pn.widgets.Select(name='Crop', options=[])
year_select = pn.widgets.Select(
    name='Year',
    options=sorted(df_all['year'].astype(str).unique())
)

# When Country changes, update Crop list
@pn.depends(country_select.param.value, watch=True)
def update_crops(country):
    crops = sorted(df_all[df_all['Country'] == country]['Crop'].unique())
    crop_select.options = crops
    if crops:
        crop_select.value = crops[0]

update_crops(country_select.value)

# 4. Scatter plot: Observed vs Predicted
@pn.depends(
    country_select.param.value,
    crop_select.param.value,
    year_select.param.value
)
def scatter_plot(country, crop, year):
    year = int(year)
    # Change year column to dtype int
    df_all['year'] = df_all['year'].astype(int)
    df = df_all[(df_all['Country'] == country) & (df_all['Crop']    == crop)&(df_all['year']    == year)]
    fig, ax = plt.subplots()
    ax.scatter(df['observed'], df['predicted'])
    ax.set_xlabel('Observed Yield (tn per ha)')
    ax.set_ylabel('Predicted Yield (tn per ha)')
    ax.set_title(f'{crop} in {country}, {year}')
    return fig

# 5. Assemble & serve
dashboard = pn.Column(
    pn.Row(country_select, crop_select, year_select),
    scatter_plot
)

dashboard.servable()
