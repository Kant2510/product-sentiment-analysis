from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
from tqdm import tqdm

load_dotenv()

client = OpenAI(
    api_key=st.secrets["API_KEY"],
    base_url=st.secrets["HOST"],
)


def get_response(prompt):
    fewshot_content = 'Nội dung comment về sản phẩm điện thoại:\nComment: Lấy máy về 2 ngày bị lỗi vân tay. Nhận diện khuôn mặt cũng chậm. Không đáng giá tiền tí nào. Chán😟 => Label: negative\nComment: Máy quá đẹp..hơn hẳn mong đợi..chỉ là giờ chưa có ốp lưng hay cường lực.. mong bên siêu thị nhập về sớm là ok => Label: positive\nComment: Mới nhận lúc sáng, sạc có vẻ lâu hơn vs oppo f11pro sạc cùng lúc và cùng lượng pin...nhưng khi oppo f11 đc 50% thì đt mik mới đc 33% thôi => Label: negative\nComment: Mới làm quả, từ 6 thường lên 7 plus thấy khác. Nhanh, mạnh, pin ổn. Nhu cầu một ngày thoải mái => Label: positive\nComment: pin trâu, xạc nhanh, chiến game ngon, nhưng bắt sóng quá tệ. đang xài bị rớt xuống mạng E, tắt nguồn khởi động lại vẫn vậy => Label: negative\nComment: Máy dùng được thời gian bị đơ máy phải khởi động lại mới được, loa nghe được 1 bên không biết là bị lỗi hay chỉ có 1 bên loa => Label: negative\nComment: Không nên mua đt này. Pin sau 1 đêm tụt quá nhanh. Ngày đầu tụt 7% họ sau nữa tụt 13% nhiều lúc bật không sáng, dùng cảm ứng vân tay, phím nguồn đều khoong sáng. Pin 5000 những khoong cảm thấy pin trâu. => Label: negative\nComment: Chưa ưng hẳn vì con chip 660 nhưng xung nhịp thấp nhất 1.8gh cũng ok, vẫn cho 5*\nThiết kế rất ok, nâng con chip lên sd 8x thì hoàn hảo luôn! => Label: positive\nComment: Máy bắt wf kém quá...không chi rieng sam sung a70 noi riêng mà hau như dòng sam sung bắt wf quá kem thất vọng... Cùng một mang wf nhung oppo bắt wf tốt hơn nhiều. => Label: negative\nComment: Pin khá trâu đó ngoài sự mong đợi . Nên mua đó bà con giá hợp lý  . Chơi game cũng mượt .... => Label: positive\nComment: Riêng hãng oppo k bao giờ mua. Chơi game k ra gì lag giật như gì. => Label: negative\nComment: Về phần thiết kế thì đẹp và nhìn sang trọng. Chip xử lí tốt. Đáng mua trong tầm giá => Label: positive\nComment: ✨ ĐƠN VỊ BẢO TRỢ TMUS GOT TALENT 2025: TRANG PHỤC BIỂU DIỄN PHÚC DƯƠNG ✨💫 Mang niềm tin tới mọi sân khấu lớn với phương châm “Tận tâm Chu đáo Trách nhiệm”, Trang phục biểu diễn Phúc Dương luôn nỗ lực mang đến những sản phẩm và dịch vụ tốt nhất cho khách hàng. Với những bộ cánh áo sặc sỡ, chất lượng cao, Phúc Dương đã góp phần không ít tạo nên thành công tại nhiều sự kiện lớn nhỏ trên khắp địa bàn Hà Nội cũng như toàn quốc. => Label: other\nComment: Hàng mall ko cho đồng kiểm tới khi kiểm tra lỗi ép khách hàng nhận. Lừa đảo không Ps: điện thoại mua ko khui ra nhìn cái hộp để biết lỗi à? Lỗi sp viết ko liền nét ko phải lỗi chứ cái gì mới là lỗi? Bút ko viết dc chữ thì còn là bút à? Trung tâm bảo hành thì xa, mua ol kiểu v sao ko kêu khách tự ra cửa hàng mà mua? Bán ol có tiền ship ko? Tôi đi bảo hành các a trả tiền di chuyển cho tôi à? => Labe: negative\nComment: ‼️Các kèo 2-3 củ khoai áp 15% đáng săn nhất đêm nay👇Sai thì sửa, chán thì đổi cách yêu, cãi vã để thấu hiểu rồi làm hoà, chứ đừng buông bỏ nhau.🤍 => Label: other\nComment: Njkhjjibjbhjbbbbjknnoonnniijhinbbknihblvyvvyvvyvyvvyyggv => Label: other'
    messages = [
        {"role": "system", "content": "Bạn là trợ lý AI giúp phân tích cảm xúc của khách hàng."},
        {"role": "user",
            "content": f"Bạn hãy dự đoán cảm xúc của khách hàng theo 3 lớp: positive, negative và other. Nếu cảm xúc là tích cực thì trả về Label: positive, nếu cảm xúc là tiêu cực thì trả về Label: negative, nếu nội dung của bình luận không liên quan đến nội dung sản phẩm hay trải nghiệm sử dụng thì trả về Label: other. Chỉ trả về nội dung label (positive hoặc negative hoặc other), không thêm gì khác"},
        {"role": "user", "content": f"Đây là ví dụ:\n{fewshot_content}"},
        {"role": "user", "content": f"Đây là câu hỏi:\n{prompt}"}
    ]
    response = client.chat.completions.create(
        model=st.secrets["MODEL_NAME"],
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
        # remove rows with other label
        if df.at[i, 'Label'] == 'other':
            df.drop(i, inplace=True)
            continue
        progress = int((i + 1) / len(df) * 100)
        progress_bar.progress(progress)
        status_text.text(f"Đang xử lý dòng {i+1}/{len(df)}")
    progress_bar.progress(100)
    status_text.success("✅ Hoàn thành! Đã loại bỏ các dòng không liên quan.")
    df.reset_index(drop=True, inplace=True)
    return df

def review_chart(images):
    images_prompt = []
    for i in images:
        images_prompt.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{i}",
                "detail": "auto"
            }
        })
    messages = [
        {"role": "system", "content": "Bạn là trợ lý AI có nhiệm vụ phân tích biểu đồ về sự đánh giá của người dùng đối với một sản phẩm. Bạn được cung cấp các hình ảnh về biểu đồ."},
        {"role": "user", "content": f"Tôi sẽ đưa cho bạn các hình ảnh biểu đồ. Các biểu đồ lần lượt là: biểu đồ phân bổ sentiment, biểu đồ phân bổ rating, biểu đồ quan hệ giữa rating star và sentiment label, biểu đồ xu hướng sentiment theo thời gian. Bạn hãy phân tích biểu đồ này và đưa ra nhận xét về sự đánh giá của người dùng đối với sản phẩm này. Bạn hãy trả lời theo khuôn khổ sau: 1. **Phân bổ sentiment**: <nội dung đánh giá>\n2. **Phân bổ sao đánh giá**: <nội dung đánh giá>\n3. **Mối quan hệ giữa sao và sentiment**: <nội dung đánh giá>\n4. **Xu hướng sentiment theo thời gian**: <nội dung đánh giá>.\nTóm lại, sản phẩm nhận được sự đánh giá <như thế nào>. Bạn hãy trả lời bằng tiếng Việt và không được thêm bất kỳ thông tin nào khác ngoài nội dung phân tích."},
        {
            "role": "user",
            "content": images_prompt,
        },
    ]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    # print(response)
    return response.choices[0].message.content