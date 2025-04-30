import requests
import json
import pandas as pd
import time
from datetime import datetime
import os
import random
import string

class ShopeeMobileAPICrawler:
    def __init__(self):
        # Headers giả lập ứng dụng di động Shopee
        self.headers = {
            'User-Agent': 'Shopee Android App',
            'X-API-SOURCE': 'rn',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Requested-With': 'com.shopee.vn',
            'X-Shopee-Language': 'vi',
            # Device ID ngẫu nhiên
            'X-Device-ID': ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        }
        
        # URL cơ sở API
        self.base_url = "https://shopee.vn/api/v4/item/get_ratings"

        self.product_name = None  # Tên sản phẩm mặc định là None, sẽ được lấy từ API nếu không có tên trong URL
        
    def extract_ids_from_url(self, product_url):
        """
        Trích xuất shopid và itemid từ URL sản phẩm
        """
        try:
            # Pattern 1: URL ends with i.shopid.itemid
            if 'i.' in product_url:
                parts = product_url.split('i.')
                if len(parts) > 1:
                    ids = parts[1].split('.')
                    if len(ids) > 1:
                        shopid = ids[0]
                        itemid = ids[1].split('?')[0]  # Remove any query params
                        return shopid, itemid
            
            # Pattern 2: URL contains -i.shopid.itemid
            if '-i.' in product_url:
                parts = product_url.split('-i.')
                if len(parts) > 1:
                    ids = parts[1].split('.')
                    if len(ids) > 1:
                        shopid = ids[0]
                        itemid = ids[1].split('?')[0]  # Remove any query params
                        return shopid, itemid
            
            # print("Không thể trích xuất shop ID và item ID từ URL")
            return None, None
            
        except Exception as e:
            # print(f"Lỗi trích xuất ID: {e}")
            return None, None

    def get_product_name(self, shopid, itemid):
        """
        Lấy tên sản phẩm từ API
        """
        try:
            url = f"https://shopee.vn/api/v4/item/get?itemid={itemid}&shopid={shopid}"
            
            headers = self.headers.copy()
            headers['X-Device-ID'] = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
            
            # Fake trình duyệt web
            headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            headers['Accept-Language'] = 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7'
            headers['Referer'] = f'https://shopee.vn/-i.{shopid}.{itemid}'
            
            # Tạo session với cookies
            session = requests.Session()
            session.cookies.set("SPC_F", ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)))
            session.cookies.set("SPC_CLIENTID", ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)))
            
            response = session.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Debug cấu trúc phản hồi API
                # print("Cấu trúc phản hồi API product name:")
                # if 'data' in data:
                    # print(f"Các khóa trong data: {list(data['data'].keys())}")
                
                # Thử nhiều đường dẫn khác nhau để tìm tên sản phẩm
                if 'data' in data:
                    if 'name' in data['data']:
                        return data['data']['name']
                    elif 'item' in data['data'] and 'name' in data['data']['item']:
                        return data['data']['item']['name']
                    elif 'title' in data['data']:
                        return data['data']['title']
                elif 'item' in data and 'name' in data['item']:
                    return data['item']['name']
                
                # Lưu phản hồi từ API để phân tích
                with open(f"product_info_{shopid}_{itemid}.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # Nếu không tìm thấy tên, sử dụng mặc định từ URL sản phẩm
                return f"Sản phẩm Shopee {itemid}"
            
            return f"Sản phẩm Shopee {itemid}"
        except Exception as e:
            # print(f"Lỗi khi lấy tên sản phẩm: {e}")
            return f"Sản phẩm Shopee {itemid}"
    
    def get_comments(self, shopid, itemid, limit=50, offset=0, max_comments=100, filter_type=0):
        """
        Lấy bình luận từ API mobile của Shopee
        
        Parameters:
        - shopid: ID của shop
        - itemid: ID của sản phẩm
        - limit: Số lượng bình luận mỗi request (mặc định 50 để lấy nhiều hơn mỗi lần)
        - offset: Vị trí bắt đầu
        - max_comments: Số lượng bình luận tối đa cần lấy
        - filter_type: Loại bình luận (0=tất cả, 1=có hình ảnh...)
        
        Returns:
        - Danh sách bình luận
        """
        all_comments = []
        current_offset = offset
        
        # Thử với nhiều phiên bản API khác nhau
        api_versions = [4, 2]
        
        for api_version in api_versions:
            if len(all_comments) >= max_comments:
                break
                
            # print(f"\nThử với API v{api_version}...")
            url = f"https://shopee.vn/api/v{api_version}/item/get_ratings"
            
            # Tạo session để duy trì cookies
            session = requests.Session()
            
            # Thêm một số cookie giả để trông giống người dùng thực
            session.cookies.set("SPC_F", ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)))
            session.cookies.set("SPC_CLIENTID", ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)))
            
            # Thêm giá trị ngẫu nhiên cho một số header
            headers = self.headers.copy()
            headers['X-Device-ID'] = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
            headers['X-Request-ID'] = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
            
            # Thử với các query param khác nhau
            param_sets = [
                {
                    'exclude_filter': 0,
                    'filter': filter_type,
                    'flag': 1,
                    'itemid': itemid,
                    'limit': limit,
                    'offset': current_offset,
                    'shopid': shopid,
                    'type': 0
                },
                {
                    'exclude_filter': 1,
                    'filter': filter_type,
                    'flag': 1,
                    'itemid': itemid,
                    'limit': limit,
                    'offset': current_offset,
                    'shopid': shopid,
                    'type': 0,
                    'variation_filters': ''
                },
                {
                    'itemid': itemid,
                    'shopid': shopid,
                    'limit': limit,
                    'offset': current_offset,
                    'filter': filter_type
                }
            ]
            
            success = False
            
            for param_index, params in enumerate(param_sets):
                if success or len(all_comments) >= max_comments:
                    break
                    
                # print(f"Thử với bộ tham số #{param_index+1}...")
                
                while len(all_comments) < max_comments:
                    # Cập nhật offset
                    params['offset'] = current_offset
                    
                    try:
                        # print(f"Đang tải bình luận từ offset {current_offset}...")
                        response = session.get(url, headers=headers, params=params)
                        
                        # Xem xét response
                        if response.status_code != 200:
                            # print(f"HTTP Error: {response.status_code}")
                            # print(f"Response: {response.text[:200]}...")
                            break
                        
                        try:
                            data = response.json()
                        except Exception as e:
                            # print(f"Lỗi khi parse JSON: {e}")
                            # print(f"Response: {response.text[:200]}...")
                            break
                        
                        # Kiểm tra lỗi API
                        if 'error' in data and data['error'] != 0:
                            # print(f"API Error: {data.get('error')}, Message: {data.get('error_msg', 'Không có thông báo lỗi')}")
                            break
                        
                        # Debug cấu trúc dữ liệu
                        # print(f"Cấu trúc phản hồi API: {list(data.keys())}")
                        
                        # Tìm dữ liệu bình luận theo nhiều cấu trúc có thể có
                        comments = None
                        
                        if 'data' in data:
                            if 'ratings' in data['data']:
                                comments = data['data']['ratings']
                                # print("Sử dụng cấu trúc data.ratings")
                            elif 'list' in data['data']:
                                comments = data['data']['list']
                                # print("Sử dụng cấu trúc data.list")
                            elif 'item' in data['data'] and 'ratings' in data['data']['item']:
                                comments = data['data']['item']['ratings']
                                # print("Sử dụng cấu trúc data.item.ratings")
                        elif 'items' in data:
                            comments = data['items']
                            # print("Sử dụng cấu trúc items")
                        
                        # In ra cấu trúc data chi tiết hơn để debug
                        # if 'data' in data:
                            # print(f"Các khóa trong data: {list(data['data'].keys())}")
                            
                            # Check thêm vị trí khác
                            # for key in data['data'].keys():
                            #     if isinstance(data['data'][key], dict):
                                    # print(f"  Các khóa trong data.{key}: {list(data['data'][key].keys())}")
                        
                        if not comments:
                            # print("Không tìm thấy dữ liệu bình luận trong các cấu trúc đã biết")
                            
                            # Thử tìm kiếm các mảng có thể chứa bình luận
                            found_array = False
                            for key in data:
                                if isinstance(data[key], list) and len(data[key]) > 0:
                                    # print(f"Thử với mảng tại {key} có {len(data[key])} phần tử")
                                    sample = data[key][0]
                                    if isinstance(sample, dict):
                                        # print(f"  Sample keys: {list(sample.keys())}")
                                        # Kiểm tra xem có phải bình luận không
                                        comment_indicators = ['comment', 'rating', 'user', 'content', 'text']
                                        if any(ind in sample for ind in comment_indicators):
                                            # print(f"  Tìm thấy các chỉ báo bình luận trong {key}")
                                            comments = data[key]
                                            found_array = True
                                            break
                            
                            if not found_array and 'data' in data:
                                for data_key in data['data']:
                                    if isinstance(data['data'][data_key], list) and len(data['data'][data_key]) > 0:
                                        # print(f"Thử với mảng tại data.{data_key} có {len(data['data'][data_key])} phần tử")
                                        sample = data['data'][data_key][0]
                                        if isinstance(sample, dict):
                                            # print(f"  Sample keys: {list(sample.keys())}")
                                            # Kiểm tra xem có phải bình luận không
                                            comment_indicators = ['comment', 'rating', 'user', 'content', 'text']
                                            if any(ind in sample for ind in comment_indicators):
                                                # print(f"  Tìm thấy các chỉ báo bình luận trong data.{data_key}")
                                                comments = data['data'][data_key]
                                                found_array = True
                                                break
                            
                            if not found_array:
                                # print("Không tìm thấy cấu trúc dữ liệu phù hợp")
                                break
                        
                        if len(comments) == 0:
                            # print("Không còn bình luận nào")
                            break
                        
                        # print(f"Đã tìm thấy {len(comments)} bình luận")
                        success = True
                        
                        # Thêm bình luận vào danh sách
                        all_comments.extend(comments)
                        # print(f"Tổng số bình luận đã thu thập: {len(all_comments)}")
                        
                        # Cập nhật offset cho request tiếp theo
                        current_offset += len(comments)
                        
                        # Giới hạn số lượng bình luận
                        if len(all_comments) >= max_comments:
                            all_comments = all_comments[:max_comments]
                            break
                        
                        # Delay để tránh rate limit
                        time.sleep(random.uniform(1.5, 3.0))
                        
                    except Exception as e:
                        # print(f"Lỗi khi tải bình luận: {e}")
                        break
                
                if success and len(all_comments) > 0:
                    # print(f"Tìm thấy bộ tham số phù hợp: API v{api_version}, bộ tham số #{param_index+1}")
                    break
            
            if success and len(all_comments) > 0:
                break
        
        return all_comments
    
    def parse_comments_simplified(self, comments, default_product_name):
        """
        Phân tích dữ liệu bình luận thô thành định dạng đơn giản với 4 cột:
        - product: Tên sản phẩm (từ product_items.name nếu có)
        - rating: Số sao đánh giá
        - comment_time: Thời gian bình luận
        - comment_text: Nội dung bình luận
        """
        parsed_data = []
        
        for comment in comments:
            try:
                # Kiểm tra nếu comment là string thì thử parse JSON
                if isinstance(comment, str):
                    try:
                        comment = json.loads(comment)
                    except:
                        # print(f"Không thể parse bình luận dạng string: {comment[:50]}...")
                        continue
                # print(comment)
                # # save to json file
                # with open("comment.json", "w", encoding="utf-8") as f:
                #     json.dump(comment, f, ensure_ascii=False, indent=2)
                # break
                # Khởi tạo bản ghi với tên sản phẩm mặc định
                parsed_comment = {
                    'product': default_product_name
                }
                
                # Tìm tên sản phẩm từ product_items
                if 'product_items' in comment and comment['product_items']:
                    if isinstance(comment['product_items'], list) and len(comment['product_items']) > 0:
                        product_item = comment['product_items'][0]
                        if isinstance(product_item, dict):
                            if 'name' in product_item:
                                parsed_comment['product'] = product_item['name']
                            elif 'model_name' in product_item:
                                parsed_comment['product'] = product_item['model_name']
                
                # Thử các vị trí khác có thể chứa tên sản phẩm
                if parsed_comment['product'] == default_product_name:
                    if 'product' in comment and isinstance(comment['product'], dict):
                        if 'name' in comment['product']:
                            parsed_comment['product'] = comment['product']['name']
                        elif 'model_name' in comment['product']:
                            parsed_comment['product'] = comment['product']['model_name']
                    elif 'product_name' in comment:
                        parsed_comment['product'] = comment['product_name']
                    elif 'item_name' in comment:
                        parsed_comment['product'] = comment['item_name']
                self.product_name = parsed_comment['product']
                # Rating
                if 'rating_star' in comment:
                    parsed_comment['rating'] = comment['rating_star']
                elif 'rating' in comment:
                    parsed_comment['rating'] = comment['rating']
                elif 'rate' in comment:
                    parsed_comment['rating'] = comment['rate']
                elif 'star' in comment:
                    parsed_comment['rating'] = comment['star']
                else:
                    parsed_comment['rating'] = 0
                
                # Comment text
                if 'comment' in comment:
                    parsed_comment['comment_text'] = comment['comment']
                elif 'content' in comment:
                    parsed_comment['comment_text'] = comment['content']
                elif 'text' in comment:
                    parsed_comment['comment_text'] = comment['text']
                elif 'review' in comment:
                    parsed_comment['comment_text'] = comment['review']
                else:
                    parsed_comment['comment_text'] = ''
                
                # Comment time
                if 'ctime' in comment:
                    parsed_comment['comment_time'] = datetime.fromtimestamp(
                        int(comment['ctime']) if isinstance(comment['ctime'], (int, float, str)) else 0
                    ).strftime('%Y-%m-%d %H:%M:%S')
                elif 'mtime' in comment:
                    parsed_comment['comment_time'] = datetime.fromtimestamp(
                        int(comment['mtime']) if isinstance(comment['mtime'], (int, float, str)) else 0
                    ).strftime('%Y-%m-%d %H:%M:%S')
                elif 'create_time' in comment:
                    parsed_comment['comment_time'] = datetime.fromtimestamp(
                        int(comment['create_time']) if isinstance(comment['create_time'], (int, float, str)) else 0
                    ).strftime('%Y-%m-%d %H:%M:%S')
                elif 'post_time' in comment:
                    parsed_comment['comment_time'] = datetime.fromtimestamp(
                        int(comment['post_time']) if isinstance(comment['post_time'], (int, float, str)) else 0
                    ).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    parsed_comment['comment_time'] = ''
                
                parsed_data.append(parsed_comment)
                
            except Exception as e:
                # print(f"Lỗi khi phân tích bình luận đơn giản: {e}")
                # Debug thêm thông tin
                # if isinstance(comment, dict):
                    # In ra các khóa chính
                    # print(f"Các khóa trong comment: {list(comment.keys())}")
                    # Kiểm tra product_items chi tiết
                    # if 'product_items' in comment:
                        # print(f"product_items: {comment['product_items']}")
                continue
        
        return pd.DataFrame(parsed_data)
    
    def save_comments_simplified(self, df, filename='shopee_comments_simplified.csv'):
        """
        Lưu bình luận đơn giản vào file CSV
        """
        # Tạo thư mục lưu trữ nếu chưa tồn tại
        if not os.path.exists('data'):
            os.makedirs('data')
        
        # Đường dẫn đến file CSV
        csv_file_path = os.path.join('data', 'result.csv')
        
        if df is not None and not df.empty:
            # Chỉ giữ lại và sắp xếp các cột chúng ta cần
            cols = ['product', 'rating', 'comment_time', 'comment_text']
            df = df[cols]
            
            df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
            # print(f"Bình luận đã được lưu vào {filename}")
            
            return True
        else:
            # print("Không có dữ liệu bình luận để lưu")
            return False
    
    def crawl_product_comments_simplified(self, product_url=None, shopid=None, itemid=None, max_comments=100, filter_type=0):
        """
        Phương thức chính để crawl bình luận đơn giản của sản phẩm
        """
        # Trích xuất shopid và itemid từ URL nếu được cung cấp
        if product_url:
            shopid, itemid = self.extract_ids_from_url(product_url)
        
        # Kiểm tra xem có cả hai id không
        if not shopid or not itemid:
            # print("Cần có cả Shop ID và Item ID")
            return None
        
        # print(f"Crawl bình luận cho sản phẩm - Shop ID: {shopid}, Item ID: {itemid}")
        
        # Lấy tên sản phẩm
        product_name = self.get_product_name(shopid, itemid)
        self.product_name = product_name
        # print(f"Tên sản phẩm: {product_name}")
        
        # Thử lấy tên sản phẩm từ URL của người dùng nếu có
        if product_url and "Unknown Product" in product_name:
            try:
                # Lấy phần trước i. trong URL (thường là tên sản phẩm)
                product_parts = product_url.split('i.')
                if len(product_parts) > 1:
                    url_product_name = product_parts[0].split('/')[-1]
                    # Chuyển dấu - thành khoảng trắng và decode URL
                    url_product_name = url_product_name.replace('-', ' ')
                    import urllib.parse
                    url_product_name = urllib.parse.unquote(url_product_name)
                    if len(url_product_name) > 5:  # Nếu tên hợp lệ
                        product_name = url_product_name
                        self.product_name = product_name
                        print(f"Đã trích xuất tên sản phẩm từ URL: {product_name}")
            except:
                print("Không thể trích xuất tên sản phẩm từ URL")
        
        # Lấy bình luận
        comments = self.get_comments(shopid, itemid, max_comments=max_comments, filter_type=filter_type)
        
        if not comments:
            print("Không tìm thấy bình luận nào")
            return None
        
        # Phân tích bình luận theo định dạng đơn giản
        df_comments = self.parse_comments_simplified(comments, product_name)
        
        # Lưu bình luận
        output_filename = f"shopee_comments_{shopid}_{itemid}_simplified.csv"
        self.save_comments_simplified(df_comments, output_filename)
        
        # print(f"\nĐã lưu bình luận vào file: {output_filename}")
        # print("Định dạng CSV có 4 cột: product, rating, comment_time, comment_text")
        
        return df_comments

# Hàm lọc các bình luận có nội dung
def filter_comments_with_content(df):
    """
    Lọc chỉ lấy các bình luận có nội dung text
    """
    if df is None or df.empty:
        return df
    
    # Lọc những bình luận có nội dung text
    df_with_content = df[df['comment_text'].notna() & (df['comment_text'] != '')]
    # print(f"Từ {len(df)} bình luận, giữ lại {len(df_with_content)} bình luận có nội dung text")
    
    return df_with_content

# Hàm chính để crawl dữ liệu từ Shopee
def crawl_module(product_url):
    """
    Hàm chính để crawl dữ liệu từ Shopee
    """
    # Khởi tạo crawler
    crawler = ShopeeMobileAPICrawler()
    
    # Trích xuất shop ID và item ID từ URL
    shopid, itemid = crawler.extract_ids_from_url(product_url)
    
    if shopid and itemid:
        # print(f"Đã trích xuất được Shop ID: {shopid}, Item ID: {itemid}")
        
        # Tự động sử dụng các giá trị mặc định
        # 1. Dùng tên sản phẩm lấy tự động từ API
        product_name = None  # Sẽ được lấy tự động trong quá trình crawl
        # print("Sử dụng tên sản phẩm mặc định từ API")
        
        # 2. Mặc định crawl 1000 bình luận
        max_comments = 1000
        # print(f"Crawl tối đa {max_comments} bình luận")
        
        # 3. Lấy tất cả đánh giá (thay vì filter_type = 2)
        filter_type = 0  # Tất cả bình luận
        # print("Crawl tất cả bình luận, sau đó sẽ lọc lại những bình luận có nội dung")
        
        # 4. Tên file mặc định
        output_filename = "result.csv"
        # print(f"File kết quả: {output_filename}")
        
        # Thực hiện crawl
        # print("\n--- Bắt đầu crawl bình luận qua Mobile API (Tự động) ---")
        
        # Sử dụng method chuẩn để lấy tất cả bình luận trước
        all_comments_df = crawler.crawl_product_comments_simplified(
            product_url=product_url,
            shopid=shopid, 
            itemid=itemid, 
            max_comments=max_comments,
            filter_type=filter_type  # Lấy tất cả bình luận
        )
        
        # Lọc để chỉ giữ lại những bình luận có nội dung
        if all_comments_df is not None and not all_comments_df.empty:
            # Lưu tất cả bình luận
            all_filename = "all_" + output_filename
            crawler.save_comments_simplified(all_comments_df, all_filename)
            # print(f"\nĐã crawl được tổng cộng {len(all_comments_df)} bình luận")
            
            # Lọc chỉ lấy bình luận có nội dung
            comments_with_content_df = filter_comments_with_content(all_comments_df)
            
            # Lưu bình luận có nội dung
            if not comments_with_content_df.empty:
                crawler.save_comments_simplified(comments_with_content_df, output_filename)
                print("\nMẫu 3 bình luận có nội dung đầu tiên:")
                print(comments_with_content_df.head(3))
                print(f"\nBình luận có nội dung đã được lưu vào file: {output_filename}")
                print(f"Tất cả bình luận (bao gồm cả không có nội dung) được lưu vào: {all_filename}")
                return crawler.product_name
            else:
                print("\nKhông có bình luận nào có nội dung text.")
        else:
            print("\nKhông crawl được bình luận nào.")
            print("Có thể sản phẩm này không có bình luận hoặc Shopee đã thay đổi cấu trúc API.")
            print("Bạn có thể thử các giải pháp sau:")
            print("1. Thử sản phẩm khác có nhiều bình luận")
            print("2. Kiểm tra trên giao diện web xem sản phẩm có bình luận không")
    else:
        print("Không thể trích xuất Shop ID và Item ID từ URL. Vui lòng kiểm tra lại URL sản phẩm.")