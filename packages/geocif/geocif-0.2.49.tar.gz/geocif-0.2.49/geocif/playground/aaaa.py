import geopandas as gpd
import holoviews as hv
import hvplot.pandas                                # registers .hvplot accessor
import panel as pn
hv.extension("bokeh"); pn.extension()

# ------------------------------------------------------------------
# 1. Paths
# ------------------------------------------------------------------
SHAPE_PATH      = r"C:\Users\ritvik\Downloads\output.shp"
RISK_PATH       = r"C:\Users\ritvik\Downloads\output_risk.shp"
LOGO_IMAGE      = r"C:\Users\ritvik\Downloads\combined_logo.png"

# ------------------------------------------------------------------
# 2. Load & prep  varRatio  layer
# ------------------------------------------------------------------
gdf = gpd.read_file(SHAPE_PATH)
if "varRatio" not in gdf.columns:
    raise KeyError("'varRatio' column missing in output.shp")

uid_col   = "UID" if "UID" in gdf.columns else "index"
gdf[uid_col]     = gdf.get(uid_col, gdf.index)
gdf["varRatio"]  = gdf["varRatio"].round(2)            # 2-decimals

# ------------------------------------------------------------------
# 3. Load & prep  risk  layer
# ------------------------------------------------------------------
risk_gdf = gpd.read_file(RISK_PATH)
risk_cols = ["risk", "yvrRsk", "clim_risk", "climCh_ris"]
missing   = [c for c in risk_cols if c not in risk_gdf.columns]
if missing:
    raise KeyError(f"Columns {missing} missing in output_risk.shp")

uid2 = "UID" if "UID" in risk_gdf.columns else "index"
risk_gdf[uid2] = risk_gdf.get(uid2, risk_gdf.index)
for c in risk_cols:
    risk_gdf[c] = risk_gdf[c].round(2)

# ------------------------------------------------------------------
# 4. Widgets
# ------------------------------------------------------------------
country_opts = sorted(gdf["Cntry_Code"].dropna().unique())
default_val  = "US" if "US" in country_opts else "All"

country_select = pn.widgets.Select(name="Country",
                                   options=["All"] + country_opts,
                                   value=default_val)

crop_select    = pn.widgets.Select(name="Crop",
                                   options=["Maize"],
                                   value="Maize")

# ------------------------------------------------------------------
# 5. varRatio   map
# ------------------------------------------------------------------
def make_varratio_map(country, crop):
    data = gdf if country == "All" else gdf[gdf["Cntry_Code"] == country]
    if data.empty:
        return pn.pane.Markdown(f"**No data for {country}**")

    vmin, vmax = data["varRatio"].min(), data["varRatio"].max()
    if vmin == vmax: vmin -= 1e-6; vmax += 1e-6

    return data.hvplot.polygons(
        c="varRatio", tiles="CartoLight", cmap="Viridis",
        clim=(vmin, vmax),
        line_width=0.1,
        hover_tooltips=[
            #(uid_col, f"@{uid_col}"),
            ("varRatio", "@varRatio{0.00}")
        ],
        colorbar=True,
        toolbar='above', 
        line_color='white',
        height=650, width=950,
        title=f"varRatio – {country if country!='All' else 'All Countries'}",
    ).opts(
        hv.opts.Polygons(tools=['hover'], show_grid=False, show_frame=False, toolbar='below', 
        line_color='white'))

varratio_panel = pn.bind(make_varratio_map, country_select, crop_select)

# ------------------------------------------------------------------
# 6. Helpers to build 4-map risk grid
# ------------------------------------------------------------------
def _risk_layer(df, col, title):
    vmin, vmax = df[col].min(), df[col].max()

    # …then force a symmetric range around 0 so the colourbar is centred
    abs_max = max(abs(vmin), abs(vmax))
    vmin, vmax = -abs_max, abs_max       # 0 now sits in the middle

    return df.hvplot.polygons(
        c=col, 
        cmap="PiYG_r", 
        clim=(vmin, vmax),
        tiles="CartoLight",
        line_width=0.1,
        hover_tooltips=[
            #(uid2, f"@{uid2}"),
            (col,  f"@{col}{{0.00}}")
        ],
        colorbar=True,
        height=325, 
        width=450,
        title=title
    ).opts(
        hv.opts.Polygons(tools=['hover'], show_grid=False, show_frame=False, toolbar='below', 
        line_color='white'))

pn.extension(
    raw_css=[
        """
        /* tighten row/column/grid gaps */
        .tight {
          gap: 4px !important;      /* space between children   */
        }
        """
    ]
)

def make_risk_panel(country, crop):
    data = risk_gdf if country == "All" else risk_gdf[risk_gdf["Cntry_Code"] == country]
    if data.empty:
        return pn.pane.Markdown(f"**No risk data for {country}**")

    maps = [
        _risk_layer(data, "risk",        "Composite Risk Indicator"),
        _risk_layer(data, "yvrRsk",      "Historical Yield Variance Risk Indicator"),
        _risk_layer(data, "clim_risk",   "Growing Season Climate Risk Indicator"),
        _risk_layer(data, "climCh_ris", "Climate Change Risk Indicator"),
    ]

    return pn.GridBox(
        *maps,
        ncols=2,
        sizing_mode="stretch_both",
        css_classes=["tight"],   # ← activates the new 4-px gap rule
        margin=0                 # (optional) remove outer margin
    )


risk_panel = pn.bind(make_risk_panel, country_select, crop_select)

# ------------------------------------------------------------------
# 7. Template
# ------------------------------------------------------------------
template = pn.template.FastListTemplate(
    title="Climate Risk Dashboard",
    sidebar=[
        country_select, crop_select, pn.Spacer(height=20),
        pn.pane.Image(LOGO_IMAGE, width=240, height=360, align="center")
    ],
    main=[
        pn.Tabs(
            ("varRatio",      varratio_panel),
            ("Risk Indicator", risk_panel)
        )
    ],
    header_background="lightblue",
    accent_base_color="#1f77b4",
    main_max_width="100%"
)

template.servable()