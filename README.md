# Garmin Cycle Sync

这是一个将 Garmin(中国) 的骑行记录上传到其他骑行平台的项目

## 支持平台

- **[捷安特](#捷安特)**

- **[顽鹿-迈金](#顽鹿-迈金)**

未来会支持更多平台

## 使用说明

### 本地运行

1. 安装 Python 库

    ```bash
    pip install -r requirements.txt
    ```

2. 从 Garmin(中国) 下载 FIT 文件, 文件会下载到 `FIT_OUT` 文件夹
    ```bash
    python garmin_downloader.py ${email} ${password}
    ```
    其中：
    - `${email}` 是你的 Garmin(中国) 邮箱
    - `${password}` 是你的 Garmin(中国) 密码

3. 将 FIT 文件上传到其他平台

    - ### 捷安特
        ```bash
        python giant_uploader.py ${username} ${password}
        ```
        其中：
        - `${username}` 是你的 捷安特 用户名
        - `${password}` 是你的 捷安特 密码
    
    - ### 顽鹿-迈金
        ```bash
        python onelap_uploader.py ${account} ${password}
        ```
        其中：
        - `${username}` 是你的 顽鹿（迈金） 用户名
        - `${password}` 是你的 顽鹿（迈金） 密码

### GitHub Action
1. Fork 本项目
2. 在 GitHub Action Repository secrets中配置相关账号信息
    - #### Garmin(中国)
        - `GARMIN_EMAIL`: Garmin(中国) 邮箱
        - `GARMIN_PASSWORD`: Garmin(中国) 密码
    - #### 捷安特
        - `GIANT_USERNAME`: 捷安特 用户名
        - `GIANT_PASSWORD`: 捷安特 密码
3. 等待 GitHub Action 自动运行

    
    


## 版权声明

本软件遵循 Apache-2.0 license 协议。
