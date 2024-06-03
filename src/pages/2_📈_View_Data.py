import duckdb
import streamlit as st

DLT_TABLES = {"_dlt_loads", "_dlt_pipeline_state", "_dlt_version"}
st.set_page_config(page_title="Explore Data", page_icon="📈")
st.title("Explore data ingested with `dlt`")

con = duckdb.connect("dlt_ingests.duckdb")
table_info = con.execute("show all tables;").df()
schemas = sorted(list(table_info["schema"].unique()))
schema = st.selectbox("Choose a schema", schemas)
tables = set(sorted(table_info["name"].to_list())) - DLT_TABLES
st.markdown(f"### Tables in `{schema}`")
for table in tables:
    table_df = con.execute(f"from {schema}.{table};").df()
    with st.expander(table):
        st.dataframe(table_df)
query = st.text_area(f"Write a SQL query against the `{schema}` schema")
if st.button("Run query"):
    try:
        con.execute(f"use {schema};")
        st.dataframe(con.query(query).df())
    except Exception as e:
        st.error(f"Please fix your query and try again.\n\n{e}")
