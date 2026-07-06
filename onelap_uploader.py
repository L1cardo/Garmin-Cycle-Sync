import requests
import os
import json
import argparse
import time
import hashlib

# Onelap配置
LOGIN_URL = "https://www.onelap.cn/api/login"
UPLOAD_URL = "https://otm.onelap.cn/api/otm/ride_record/upload/fit"  # 修改为正确的URL

# 设置变量
FOLDER_PATH = "FIT_OUT"


def upload_to_onelap(account, password):
    # 创建会话
    session = requests.Session()
    
    # 1. 登录获取token
    login_headers = {"Content-Type": "application/json;charset=UTF-8"}
    login_data = {
        "account": account,
        "password": hashlib.md5(password.encode()).hexdigest(),
    }
    
    print(f"正在登录账号: {account}")
    login_response = session.post(
        LOGIN_URL, headers=login_headers, json=login_data
    )
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败，状态码: {login_response.status_code}")
        print(f"响应内容: {login_response.text}")
        return
    
    try:
        login_result = login_response.json()
        print(f"登录响应: {login_result}")
        
        if login_result.get('code') == 200:
            data_list = login_result.get('data', [])
            if data_list and len(data_list) > 0:
                token = data_list[0].get('token')
                if token:
                    print(f"✅ 登录成功，已获取Token")
                    # 重要：不加 Bearer 前缀，直接使用 token
                    session.headers.update({
                        'Authorization': token,  # 直接使用token
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
                        'Origin': 'https://otm.onelap.cn',
                        'Referer': 'https://otm.onelap.cn/calendar',
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'zh-CN,zh;q=0.9',
                    })
                else:
                    print("❌ 未从登录响应中找到Token")
                    return
            else:
                print("❌ 登录响应中没有data数组")
                return
        else:
            print(f"❌ 登录失败: {login_result.get('error', '未知错误')}")
            return
    except json.JSONDecodeError:
        print(f"❌ 登录响应不是JSON格式: {login_response.text}")
        return
    
    # 2. 检查FIT_OUT文件夹
    if not os.path.exists(FOLDER_PATH):
        print(f"❌ 文件夹 {FOLDER_PATH} 不存在，请创建并放入FIT文件")
        return
    
    fit_files = [f for f in os.listdir(FOLDER_PATH) if f.endswith(".fit")]
    if not fit_files:
        print(f"❌ 在 {FOLDER_PATH} 文件夹中未找到任何 .fit 文件")
        return
    
    print(f"找到 {len(fit_files)} 个FIT文件，开始上传...")
    print("=" * 50)
    
    # 统计上传结果
    success_count = 0
    fail_count = 0
    
    # 上传所有文件（移除了测试限制）
    for index, file_name in enumerate(fit_files, 1):
        file_path = os.path.join(FOLDER_PATH, file_name)
        print(f"\n[{index}/{len(fit_files)}] 正在上传: {file_name}")
        
        try:
            with open(file_path, "rb") as file:
                file_data = file.read()
            
            # 使用正确的字段名 'jilu0'
            files = {
                'jilu0': (file_name, file_data, 'application/octet-stream')
            }
            
            # 发送上传请求（session已包含headers）
            upload_response = session.post(
                UPLOAD_URL,
                files=files
            )
            
            # 解析响应
            try:
                result = upload_response.json()
                
                if upload_response.status_code == 200 and result.get('code') == 200:
                    # 成功上传
                    success_info = result.get('data', {})
                    success_files = success_info.get('success_files', [])
                    if success_files:
                        file_key = success_files[0].get('file_key', '未知')
                        file_size = success_files[0].get('size', 0)
                        print(f"✅ 上传成功：{file_name} (文件标识: {file_key}, 大小: {file_size}字节)")
                    else:
                        print(f"✅ 上传成功：{file_name}")
                    success_count += 1
                else:
                    error_msg = result.get('message', '未知错误')
                    print(f"❌ 上传失败：{file_name} - {error_msg}")
                    fail_count += 1
                    
            except json.JSONDecodeError:
                print(f"❌ 上传响应不是JSON格式: {upload_response.text}")
                fail_count += 1
                
        except Exception as e:
            print(f"❌ 上传文件 {file_name} 时发生异常: {e}")
            fail_count += 1
        
        # 添加延时，避免触发频率限制
        if index < len(fit_files):
            time.sleep(1)
    
    # 输出总结
    print("\n" + "=" * 50)
    print(f"📊 上传完成！总计: {len(fit_files)} 个文件")
    print(f"✅ 成功: {success_count} 个")
    print(f"❌ 失败: {fail_count} 个")
    print("=" * 50)


def test_connection(account, password):
    """测试连接和登录功能"""
    print("🔍 测试连接...")
    try:
        session = requests.Session()
        login_data = {
            "account": account,
            "password": hashlib.md5(password.encode()).hexdigest(),
        }
        
        response = session.post(LOGIN_URL, json=login_data, timeout=10)
        result = response.json()
        
        if result.get('code') == 200:
            token = result.get('data', [{}])[0].get('token')
            if token:
                print("✅ 登录测试成功，Token有效")
                return True
        print("❌ 登录测试失败")
        return False
    except Exception as e:
        print(f"❌ 连接测试异常: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='上传FIT文件到顽鹿运动')
    parser.add_argument("account", help="顽鹿账号（手机号或邮箱）")
    parser.add_argument("password", help="顽鹿密码")
    parser.add_argument("--test", action="store_true", help="仅测试连接，不上传文件")
    parser.add_argument("--delay", type=int, default=1, help="上传文件间的延迟秒数（默认1秒）")
    parser.add_argument("--limit", type=int, default=0, help="限制上传文件数量（0表示全部上传）")
    
    args = parser.parse_args()
    
    if args.test:
        test_connection(args.account, args.password)
    else:
        # 更新全局延迟
        if args.delay:
            # 将delay传递给上传函数
            upload_to_onelap(args.account, args.password)
        
        # 如果需要限制上传数量，可以在函数内实现
        # 简单方式：直接调用
        upload_to_onelap(args.account, args.password)
