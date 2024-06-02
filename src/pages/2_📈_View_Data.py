import duckdb
import streamlit as st

st.set_page_config(page_title="Explore Data", page_icon="📈")
st.title("Explore data ingested with `dlt`")

con = duckdb.connect("dlt_ingests.duckdb")
table_info = con.execute("show all tables;").df()
schemas = sorted(list(table_info["schema"].unique()))
left, right = st.columns([0.3, 0.7])
with left:
    schema = st.selectbox("Choose a schema", schemas)
    tables = sorted(table_info.loc[table_info.schema == schema]["name"].to_list())
with right:
    selected_tables = st.multiselect("Choose tables", tables)
if selected_tables:
    for table in selected_tables:
        table_df = con.execute(f"from {schema}.{table};").df()
        with st.expander(f"{schema}.{table}"):
            st.dataframe(table_df)
    query = st.text_area(f"Write a SQL query against the '{schema}' schema")
    if st.button("Run query"):
        try:
            con.execute(f"use {schema};")
            st.dataframe(con.query(query).df())
        except Exception as e:
            st.error(f"Please fix your query and try again.\n{e}")
