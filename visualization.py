import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

def visualize_sentiment(df):
	"""
	Hàm này dùng để trực quan hóa dữ liệu phân tích cảm xúc của người dùng.
	Nó sẽ tạo ra các biểu đồ phân bố sentiment, rating star, mối quan hệ giữa rating star và sentiment label,
	và xu hướng sentiment theo thời gian.
	"""
	# Tiền xử lý thời gian
	df['comment_time'] = pd.to_datetime(df['comment_time'], errors='coerce')
	df.dropna(subset=['comment_time'], inplace=True)
	df['month'] = df['comment_time'].dt.to_period("M")

	figs = []

	# 1. Biểu đồ phân bố sentiment
	fg1, ax1 = plt.subplots(figsize=(6, 4))
	sns.countplot(data=df, x='Label', hue='Label', palette='Set2', legend=False)
	# plt.title("Số lượng comment theo sentiment label")
	# plt.xlabel("Sentiment Label")
	# plt.ylabel("Số lượng")
	# plt.tight_layout()
	# plt.savefig("label_distribution.png")
	# plt.show()
	ax1.set_title("Số lượng comment theo sentiment label")
	ax1.set_xlabel("Sentiment Label")
	ax1.set_ylabel("Số lượng")
	ax1.figure.savefig("label_distribution.png")
	figs.append(fg1)


	# 2. Biểu đồ phân bố rating star
	fg2, ax2 = plt.subplots(figsize=(6, 4))
	sns.countplot(data=df, x='rating', hue='rating', palette='Set3', legend=False)
	# plt.title("Phân bố số sao đánh giá")
	# plt.xlabel("Số sao")
	# plt.ylabel("Số lượng")
	# plt.tight_layout()
	# plt.savefig("rating_distribution.png")
	# plt.show()
	ax2.set_title("Phân bố số sao đánh giá")
	ax2.set_xlabel("Số sao")
	ax2.set_ylabel("Số lượng")
	ax2.figure.savefig("rating_distribution.png")
	figs.append(fg2)

	# 3. Mối quan hệ giữa rating star và sentiment label
	fg3, ax3 = plt.subplots(figsize=(8, 6))
	sns.countplot(data=df, x='rating', hue='Label', palette='pastel')
	# plt.title("Số sao và sentiment label")
	# plt.xlabel("Số sao")
	# plt.ylabel("Số lượng")
	# plt.legend(title="Sentiment")
	# plt.tight_layout()
	# plt.savefig("rating_vs_sentiment.png")
	# plt.show()
	ax3.set_title("Số sao và sentiment label")
	ax3.set_xlabel("Số sao")
	ax3.set_ylabel("Số lượng")
	ax3.legend(title="Sentiment")
	ax3.figure.savefig("rating_vs_sentiment.png")
	figs.append(fg3)

	# 4. Biểu đồ xu hướng sentiment theo thời gian
	trend_df = df.groupby(['month', 'Label']).size().unstack().fillna(0)
	trend_df.index = trend_df.index.astype(str)  # convert Period to string
	fg4, ax4 = plt.subplots(figsize=(10, 6))
	trend_df.plot(kind='line', marker='o', ax=ax4)
	# plt.title("Xu hướng sentiment theo thời gian")
	# plt.xlabel("Thời gian (tháng)")
	# plt.ylabel("Số lượng comment")
	# plt.grid(True)
	# plt.tight_layout()
	# plt.savefig("sentiment_trend.png")
	# plt.show()
	ax4.set_title("Xu hướng sentiment theo thời gian")
	ax4.set_xlabel("Thời gian (tháng)")
	ax4.set_ylabel("Số lượng comment")
	ax4.grid(True)
	ax4.figure.savefig("sentiment_trend.png")
	figs.append(fg4)

	return figs

	# # 5. Wordcloud cho từng sentiment
	# for sentiment in df['label'].unique():
	#     text = " ".join(df[df['label'] == sentiment]['comment_text'].dropna())
	#     wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

	#     plt.figure(figsize=(10, 5))
	#     plt.imshow(wordcloud, interpolation='bilinear')
	#     plt.axis('off')
	#     plt.title(f"Wordcloud cho sentiment: {sentiment}")
	#     plt.tight_layout()
	#     plt.savefig(f"wordcloud_{sentiment}.png")
	#     plt.show()