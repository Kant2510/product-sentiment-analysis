import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
from tqdm import tqdm

load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url="http://localhost:11434/v1"
)

def get_response(prompt):
    fewshot_content = 'Comment: Lấy máy về 2 ngày bị lỗi vân tay. Nhận diện khuôn mặt cũng chậm. Không đáng giá tiền tí nào. Chán😟 => Label: negative\nComment: Máy quá đẹp..hơn hẳn mong đợi..chỉ là giờ chưa có ốp lưng hay cường lực.. mong bên siêu thị nhập về sớm là ok => Label: positive\nComment: Mới nhận lúc sáng, sạc có vẻ lâu hơn vs oppo f11pro sạc cùng lúc và cùng lượng pin...nhưng khi oppo f11 đc 50% thì đt mik mới đc 33% thôi => Label: negative\nComment: Mới làm quả, từ 6 thường lên 7 plus thấy khác. Nhanh, mạnh, pin ổn. Nhu cầu một ngày thoải mái => Label: positive\nComment: pin trâu, xạc nhanh, chiến game ngon, nhưng bắt sóng quá tệ. đang xài bị rớt xuống mạng E, tắt nguồn khởi động lại vẫn vậy => Label: negative\nComment: Máy dùng được thời gian bị đơ máy phải khởi động lại mới được, loa nghe được 1 bên không biết là bị lỗi hay chỉ có 1 bên loa => Label: negative\nComment: Không nên mua đt này. Pin sau 1 đêm tụt quá nhanh. Bgqafy đầu tụt 7% họ sau nữa tụt 13% nhiều lúc bật khoong sáng, dùng cảm ứng vân tay, phím nguồn đều khoong sáng. Pin 5000 những khoong cảm thấy pin trâu. => Label: negative\nComment: Chưa ưng hẳn vì con chip 660 nhưng xung nhịp thấp nhất 1.8gh cũng ok, vẫn cho 5*\nThiết kế rất ok, nâng con chip lên sd 8x thì hoàn hảo luôn! => Label: positive\nComment: Máy bắt wf kém quá...không chi rieng sam sung a70 noi riêng mà hau như dòng sam sung bắt wf quá kem thất vọng... Cùng một mang wf nhung oppo bắt wf tốt hơn nhiều. => Label: negative\nComment: Pin khá trâu đó ngoài sự mong đợi . Nên mua đó bà con giá hợp lý  . Chơi game cũng mượt .... => Label: positive\nComment: Riêng hãng oppo k bao giờ mua. Chơi game k ra gì lag giật như gì. => Label: negative\nComment: Về phần thiết kế thì đẹp và nhìn sang trọng. Chip xử lí tốt. Đáng mua trong tầm giá => Label: positive'
    messages = [
        {"role": "system", "content": "Bạn là trợ lý AI giúp phân tích cảm xúc của khách hàng."},
        {"role": "user", "content": f"Bạn hãy dự đoán cảm xúc của khách hàng theo 2 lớp: positive và negative. Nếu cảm xúc là tích cực thì trả về Label: positive, nếu cảm xúc là tiêu cực thì trả về Label: negative. Chỉ trả về nội label (positive hoặc negative), không thêm gì khác"},
        {"role": "user", "content": f"Đây là ví dụ:\n{fewshot_content}"},
        {"role": "user", "content": f"Đây là câu hỏi:\n{prompt}"}
    ]
    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=messages
    )
    return response.choices[0].message.content

# print(get_response("Điện thoại dùng không tốt"))

def update_label(df=None):
    def filter(txt):
        if "positive" in txt:
            return 'positive'
        if "negative" in txt:
            return 'negative'
        return 'other'
    df = df.copy()
    df.loc[:, 'Label'] = None
    progress_bar = st.progress(0)
    status_text = st.empty()
    for i in tqdm(df.index):
        df.at[i, 'Label'] = filter(get_response(df.at[i, 'comment_text']))
        progress = int((i + 1) / len(df) * 100)
        progress_bar.progress(progress)
        status_text.text(f"Đang xử lý dòng {i+1}/{len(df)}")
    progress_bar.progress(100)
    status_text.success("✅ Hoàn thành!")
    return df
