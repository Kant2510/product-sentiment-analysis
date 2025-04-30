import os
from matplotlib import pyplot as plt
import streamlit as st
import pandas as pd
from crawl_data import crawl_module
from get_sentiment import update_label
from visualization import visualize_sentiment

# Danh sách các file cần xoá khi app khởi động lại
files_to_delete = [
    st.secrets["CRAWLED_DATA_PATH"],
]

for file in files_to_delete:
    if os.path.exists(file):
        os.remove(file)

st.title("Ứng dụng phân tích cảm xúc người dùng")

# Nhập url crawl
st.subheader("🔎 Thu thập dữ liệu")
url = st.text_input("Nhập đường dẫn sản phẩm bạn muốn phân tích:")
if st.button("📥 Thu thập"):
	if url.strip() == "":
		st.warning("❗Vui lòng nhập đường dẫn!")
	else:
		product_name = crawl_module(url)
		if product_name is None:
			st.error("❗Không thể thu thập dữ liệu từ đường dẫn này!")
		st.success(f"✅ Đã thu thập được dữ liệu cho: {product_name}")

# Xem dữ liệu
df = None
st.subheader("👁️ Xem dữ liệu")
try:
	df = pd.read_csv(st.secrets["CRAWLED_DATA_PATH"])
	if df.empty:
		st.warning("❗Chưa có dữ liệu! Hãy thu thập dữ liệu trước.")
	else:
		# Chọn số lượng dòng để hiển thị
		num_rows = st.number_input("Chọn số lượng dòng để hiển thị:", min_value=1, max_value=len(df), value=5)
		st.write(f"Hiển thị {num_rows} dòng dữ liệu:")
		# Hiển thị dữ liệu
		display_df = df.head(num_rows)
	st.dataframe(display_df, use_container_width=True)
except FileNotFoundError:
	st.error("❗Chưa có dữ liệu! Hãy thu thập dữ liệu trước.")

# Phân tích dữ liệu
if df is not None and not df.empty:
	st.subheader("📊 Phân tích dữ liệu")
	analysis_mode = st.radio("Chọn phương pháp phân tích:", ["Toàn bộ dữ liệu", "Một phần dữ liệu"])
	shuffled_df = df.sample(frac=1, random_state=42).reset_index(drop=True)
	selected_df = shuffled_df

	if analysis_mode == "Một phần dữ liệu":
		method = st.selectbox("Chọn đơn vị:", ["Số dòng", "Phần trăm"])
		if method == "Số dòng":
			num_rows = st.number_input("Nhập số dòng muốn phân tích:", min_value=1, max_value=len(df), value=min(10, len(df)))
			selected_df = shuffled_df.head(int(num_rows))
		else:
			percent = st.slider("Chọn phần trăm dữ liệu muốn phân tích:", min_value=1, max_value=100, value=20)
			num_rows = int(len(df) * percent / 100)
			selected_df = shuffled_df.head(num_rows)

	if st.button("🚀 Phân tích"):
		try:
			result = update_label(selected_df)
			if result is None:
				st.error("❗Không thể phân tích dữ liệu!")
			st.write("📃 Kết quả phân tích:")
			st.write(result)
			try:
				figures = visualize_sentiment(result)
				st.write("📈 Đã tạo biểu đồ. Xem bên dưới:")

				for fig in figures:
					st.pyplot(fig)
				# remove the figures from memory
				for fig in figures:
					plt.close(fig)
				# remove files from disk
				# os.remove(st.secrets["CRAWLED_DATA_PATH"])
			except Exception as e:
				st.error(f"❌ Lỗi khi tạo biểu đồ: {e}")
		except Exception as e:
			st.error(f"❗Không thể phân tích dữ liệu: {e}")