from great_tables import GT, md, system_fonts
import pandas as pd

# Your data as a pandas DataFrame
data = [
    [2, "10<sup>th</sup>",          "<=14; >14",                     89.2, "2010 - 2021"],
    [2, "25<sup>th</sup>",          "<=18.7; >18.7",                 82.2, "2010 - 2021"],
    [2, "50<sup>th</sup>",          "<=24.6; >24.6",                 83.7, "2010 - 2021"],
    [2, "75<sup>th</sup>",          "<=31; >31",                     88.3, "2010 - 2021"],
    [2, "90<sup>th</sup>",          "<=38.9; >38.9",                 96.9, "2010 - 2021"],
    [3, "33<sup>rd</sup>, 67<sup>th</sup>",  "<=20.3; 20.3 - 29.6; >29.6",     60.5, "2010 - 2021"],
    [4, "25<sup>th</sup>, 50<sup>th</sup>, 75<sup>th</sup>",
         "<=18.7; 18.7-24.6; 24.6-31; >31",                           64.4, "2010 - 2021"]
]
cols = ["Number of classes", "Percentile(s)", "Yield categories", "Accuracy (%)", "Years"]

df = pd.DataFrame(data, columns=cols)

# Create a Great Tables object
gt_tbl = GT(data=df)

# Example formatting, coloring, and styling
gt_tbl = (gt_tbl
    # Format the "Accuracy (%)" column to show one decimal place
    .fmt_number(
        columns=["Accuracy (%)"],
        decimals=1
    )
    # Color-scale the "Accuracy (%)" column (optional)
    #.data_color(
    #    columns=["Accuracy (%)"],
    #    palette=["tomato", "gold", "palegreen"],
    #    domain=[50, 100]  # Range from the lowest to highest accuracy
    #)
    # Set column widths
    .cols_width({
        "Number classes":    "60px",
        "Percentile(s)":     "140px",
        "Yield categories":  "220px",
        "Accuracy (%)":      "100px",
        "Years":             "90px"
    })
    # Add a table header/title
    .tab_header(
        title=md("**Accuracy of Model for Different Yield Categories**")
    )
    # Add a source note (optional)
    # .tab_source_note(
    #     md(
    #         "**Source**: Internal records<br>"
    #         "**Note**: Data from 2010-2021"
    #     )
    # )
    # Customize general table options
    .tab_options(
        heading_background_color='antiquewhite',
        column_labels_background_color='antiquewhite',
        source_notes_background_color='antiquewhite',
        table_background_color='snow',
        table_font_names=system_fonts("humanist"),
        data_row_padding='2px'
    )
    # Align all columns center except "Yield categories", which might be longer text
    .cols_align(align="center")
    .cols_align(align="left", columns=["Yield categories"])
)

# Display the table
GT.save(gt_tbl, file="aa.png")
