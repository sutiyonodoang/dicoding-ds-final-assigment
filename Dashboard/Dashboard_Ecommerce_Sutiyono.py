import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
# from babel.numbers import format_currency

sns.set(style='dark')

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe
def create_monthly_orders_df(df):
    monthly_orders = df.resample('M', on='order_purchase_timestamp').agg({
        "order_id": "nunique"})
    monthly_orders = monthly_orders.reset_index()
    monthly_orders.rename(columns={
        "order_id": "order_count"
    }, inplace=True)
    return monthly_orders

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").order_id.nunique().sort_values(ascending=False).head(10)
    bystate_df.index.name = 'state'

    return bystate_df

def create_peakorder_df(df):
    # extrak jam dan hari dari kolom order_purchase_timestamp kedalam kolom order_hour dan order_dayofweek
    df['order_hour'] = df['order_purchase_timestamp'].dt.hour
    df['order_dayofweek'] = df['order_purchase_timestamp'].dt.dayofweek
    peakorder_df = df.pivot_table(index='order_hour', columns='order_dayofweek', values='order_id', aggfunc='count')
    
    # Mengurutkan hari berdasarkan urutan dalam minggu
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    peakorder_df = peakorder_df.reindex(columns=day_order)
    return peakorder_df

# Load data
orders_df = pd.read_csv('orders_dataset.csv')
orders_df = orders_df[orders_df['order_status'] == 'delivered']
customers_df = pd.read_csv('customers_dataset.csv')

# data cleaning
orders_df = orders_df.dropna(subset=['order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date'])
print(orders_df.isna().sum())

datetime_columns = ["order_purchase_timestamp",
                    "order_approved_at",
                    "order_delivered_carrier_date",
                    "order_delivered_customer_date",
                    "order_estimated_delivery_date"]

for column in datetime_columns:
    orders_df[column] = pd.to_datetime(orders_df[column])

orders_customers_df = pd.merge(
    left=orders_df,
    right=customers_df,
    how="left",
    left_on="customer_id",
    right_on="customer_id"
)

all_df = pd.DataFrame(orders_customers_df)

datetime_columns = ["order_purchase_timestamp"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Filter data
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("logo.png")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) &
                 (all_df["order_purchase_timestamp"] <= str(end_date))]

# Menyiapkan berbagai dataframe
monthly_orders_df = create_monthly_orders_df(main_df)
bystate_df = create_bystate_df(main_df)
peakorder_df = create_peakorder_df(main_df)

# Title
st.header('E-Commerce Public Dataset :sparkles:')

# Membuat visualisasi tren order dari waktu ke waktu, dalam satuan bulanan
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_orders_df["order_purchase_timestamp"],
    monthly_orders_df["order_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)

# Menambahkan nilai pada kolom
for i, txt in enumerate(monthly_orders_df["order_count"]):
    ax.text(monthly_orders_df["order_purchase_timestamp"].iloc[i], txt,
            f'{txt}', ha='left', va='bottom', fontsize=12)
    
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.set_xlabel('Periode', fontsize=23)
ax.set_ylabel('Jumlah Order', fontsize=18)
ax.set_title('Tren Jumlah Order dari Waktu ke Waktu (bulan)', fontsize=25)
ax.grid()
st.pyplot(fig)

# konklusi tren order
with st.expander("Konklusi Pertanyaan 1"):
    st.write("Berdasarkan grafik garis yang disajikan, dapat diambil beberapa kesimpulan sebagai berikut:")
    st.markdown("- Pada tahun 2016, terdapat hanya 3 bulan data yang mencakup, dan terdapat kecenderungan penurunan jumlah pesanan, meskipun tidak signifikan.")
    st.markdown("- Tahun 2017 menunjukkan tren kenaikan yang sangat signifikan dari bulan ke bulan. Meskipun terdapat bulan tertentu (bulan 5, 7, dan 10) dengan penurunan pesanan, namun penurunan tersebut tidak signifikan jika dibandingkan dengan kenaikan pesanan pada bulan-bulan lain.'")
    st.markdown("- Tahun 2018 diawali dengan penurunan jumlah order kurang lebih setengahnya dari jumlah kenaikan bulan sebelumnya. 10 bulan bejalan mengalami kenaikan jumlah order, tapi tidak se ekxtrim pada tahun 2017")
    st.markdown("- kenaikan paling tinggi selama periode data adalah pada periode desember 2017, sementara penurunan jumlah order berada pada bulan berikutnya, yaitu januari 2018")


# Membuat visualisasi 10 state dengan jumlah order terbanyak
# Mengatur ukuran 
fig, ax = plt.subplots(figsize=(12, 8))

# Membuat grafik bar
ax.bar(bystate_df.index, bystate_df, color='skyblue')

# Menambahkan nilai pada kolom
for i, v in enumerate(bystate_df):
    ax.text(i, v + 0.2, str(v), ha='center', va='bottom', fontsize=10)

# Menambahkan label dan judul
ax.set_xlabel('State')
ax.set_ylabel('Jumlah Order Unik')
ax.set_title('Top 10 States dengan Jumlah Order Terbanyak', fontsize=25)
ax.grid(axis='y', linestyle='--', alpha=0.7)
ax.set_xticklabels(bystate_df.index, rotation=45, ha='right')  # Rotasi label agar lebih mudah dibaca

# Menampilkan grafik
st.pyplot(fig)

# konklusi top 10 state by most order
with st.expander("Konklusi Pertanyaan 2"):
    st.write("Berdasarkan grafik kolom yang disajikan, dapat diambil beberapa kesimpulan sebagai berikut:")
    st.markdown("- Dari grafik terlihat bahwa terdapat satu state yang mendominasi jumlah order, yaitu SP. Jumlah order di SP sangat signifikan dibandingkan state lainnya. Ini menunjukkan adanya sentralisasi aktivitas bisnis atau populasi di area tersebut.")
    st.markdown("- 9 State yang lainya memiliki perbedaan jumlah order yang tidak signifikan.")
    st.markdown("- Grafik top 10 state ini mungkin memiliki pangsa pasar yang signifikan dalam konteks bisnis. Oleh karena itu, fokus pada pemasaran dan layanan pelanggan di state-state ini dapat menjadi strategi yang efektif untuk meningkatkan penjualan.")
    st.markdown("- Pemahaman mengapa beberapa state memiliki jumlah order yang lebih tinggi dibandingkan dengan yang lain dapat membantu perusahaan untuk memperbaiki atau mengoptimalkan strategi kedepan.")
    st.markdown("- Analisis lebih lanjut sangat dibutuhkan terhadap data 10 state dengan order paling banyak ini untuk bisa berstrategi lebih spesifik.")


# Membuat heatmap
fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(peakorder_df, cmap='viridis', annot=True, fmt='g', ax=ax)
ax.set_title('Peak Ordering Time - Heatmap')
ax.set_xlabel('Hour of Day')
ax.set_ylabel('Day of Week')
st.pyplot(fig)



# konklusi peak order
with st.expander("Konklusi Pertanyaan 3"):
    st.write("Berdasarkan pada grafik heatmap, maka dapat diambil beberapa kesimpulan pola peak order yang terjadi sebagai berikut:")
    st.markdown("- Jumlah order mengalami peningkatan mulai dari pukul 8, dan mulai menurun pukul 22, sementara harinya mulai dari senin hingga jumat") 
    st.markdown("- Jumlah order pada hari sabtu dan minggu cenderung stabil, berada di 60%-70% dari total order di jam dan hari paling ramai, dan mulai bertambah hinggai kisaran 80% pada minggu malam.")
    st.markdown("- Pada pukul 10 hingga pukul 16, hari senin hingga rabu merupakan peak order paling tinggi.")
    st.markdown("- Dengan pola order yang digambarkan pada heatmap ini kita bisa mengetahui beban layanan yang harus dipersiapkan perusahaan")
# caption
st.caption('Copyright © Sutiyono 2023')
