import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import folium
from streamlit_folium import folium_static

# Load your data
all_data = pd.read_csv('dashboard/all_data.csv')
geolocation_df = pd.read_csv('dashboard/geolocation_dataset.csv')  # Update the path to your geolocation data

# Streamlit app
st.title('Dashboard')

# Sidebar
st.sidebar.title('Sidebar')
st.sidebar.image('dashboard/toko.jpg', use_column_width=True)

# Year range filter
min_year = int(all_data['order_purchase_timestamp'].min()[:4])
max_year = int(all_data['order_purchase_timestamp'].max()[:4])
year_range = st.sidebar.slider('Select Year Range', min_year, max_year, (min_year, max_year))

# Filter data based on the selected year range
all_data['order_year'] = pd.to_datetime(all_data['order_purchase_timestamp']).dt.year
filtered_data = all_data[(all_data['order_year'] >= year_range[0]) & (all_data['order_year'] <= year_range[1])]

# Payment Type Plot
st.subheader('Payment Type')
fig1 = plt.figure(figsize=(15, 7))
fig1.suptitle('Payment Type', fontsize=20)
plt.xlabel('customer_id', fontsize=20)
plt.ylabel('payment_type', fontsize=20)

payment_type = filtered_data.groupby('payment_type')['customer_id'].count().reset_index()
payment_type.sort_values('customer_id', ascending=True, inplace=True)
x = payment_type['payment_type']
y = payment_type['customer_id']

plt.barh(x, y, color='lightblue')
st.pyplot(fig1)

# Order Status Plot
st.subheader('Order Status')
fig2 = plt.figure(figsize=(15, 7))
fig2.suptitle('Order Status', fontsize=20)
plt.xlabel('order_id', fontsize=20)
plt.ylabel('order_status', fontsize=20)

stat_order = filtered_data.groupby('order_status')['order_id'].count().reset_index()
stat_order.sort_values('order_id', ascending=True, inplace=True)
x = stat_order['order_status']
y = stat_order['order_id']

plt.barh(x, y, color='lightblue')
st.pyplot(fig2)

# Review Scores Plot
st.subheader('Review Scores')
review_scores = filtered_data['review_score'].value_counts().sort_values(ascending=False)
most_common_score = review_scores.idxmax()

sns.set(style="darkgrid")
fig3 = plt.figure(figsize=(10, 5))
sns.barplot(x=review_scores.index,
            y=review_scores.values,
            order=review_scores.index,
            palette=["#068DA9" if score == most_common_score else "#D3D3D3" for score in review_scores.index]
            )

plt.title("Rating by customers for service", fontsize=15)
plt.xlabel("Rating")
plt.ylabel("Count")
plt.xticks(fontsize=12)
st.pyplot(fig3)

# Map Visualization
st.subheader('Geolocation Map')

# Kelompokkan data berdasarkan kode pos dan hitung jumlah titik per kode pos
zip_count = geolocation_df["geolocation_state"].value_counts().reset_index()
zip_count.columns = ["geolocation_state", "count"]

# Titik tengah untuk peta
center_lat = geolocation_df["geolocation_lat"].mean()
center_lng = geolocation_df["geolocation_lng"].mean()

# Buat peta dasar
m = folium.Map(location=[center_lat, center_lng], zoom_start=12)

# Tambahkan layer Choropleth
geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
folium.Choropleth(
    geo_data=geojson_url,  # Data batas wilayah (GeoJSON)
    name="choropleth",
    data=zip_count,
    columns=["geolocation_state", "count"],
    key_on="feature.properties.sigla",  # Sesuaikan dengan properti di GeoJSON
    fill_color="YlGn",  # Skema warna: 'YlOrRd', 'BuPu', 'Greens', dll.
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Jumlah Titik per Kode Pos"
).add_to(m)

folium.LayerControl().add_to(m)

# Tampilkan peta
folium_static(m)