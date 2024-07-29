# Garmin Cycle Sync

这是一个将 Garmin(中国) 的骑行记录上传到其他骑行平台的项目

## 功能

- 从 Garmin Connect(中国) 下载 FIT 文件
- 上传 FIT 文件到 国内其他 平台

## 支持平台

- 捷安特

- 顽鹿-迈金

未来会支持更多平台

## 本地使用方法

### 准备工作

1. 确保您的系统已安装Python 3.10或更高版本。
2. 克隆此仓库到本地：
   ```bash
   git clone https://github.com/L1cardo/Garmin-Cycle-Sync.git
   cd Garmin-Cycle-Sync
   ```
3. 安装所需的依赖：
   ```bash
   pip install -r requirements.txt
   ```

### 使用步骤

1. 从 Garmin Connect(中国) 下载 FIT 文件：
   ```bash
   python garmin_download.py ${GARMIN_EMAIL} ${GARMIN_PASSWORD}
   ```

2. 上传 FIT 文件到 捷安特：
   ```bash
   python giant_upload.py ${GIANT_USERNAME} ${GIANT_PASSWORD}
   ```

3. 上传 FIT 文件到 顽鹿-迈金：
   ```bash
   python onelap_upload.py ${ONELAP_ACCOUNT ${ONELAP_PASSWORD}
   ```

## GitHub Actions 使用方法

本项目已配置 GitHub Actions 来自动运行同步过程。以下是设置和使用方法：

1. Fork 这个仓库到您的 GitHub 账户。

2. 在您的仓库设置中，添加以下 Secrets：
   - `GARMIN_EMAIL`: Garmin Connect(中国) 账户邮箱
   - `GARMIN_PASSWORD`: Garmin Connect(中国) 账户密码
   - `GIANT_USERNAME`: 捷安特 用户名
   - `GIANT_PASSWORD`: 捷安特 密码
   - `ONELAP_ACCOUNT`: 顽鹿-迈金 账户
   - `ONELAP_PASSWORD`: 顽鹿-迈金 密码

3. GitHub Actions 工作流程已经配置好，它会：
   - 每 8 小时运行一次，在每天的 07:31, 15:31, 23:31 (北京时间)
   - 当您推送代码到 main 分支时运行
   - 允许手动触发

4. 您可以通过更改变量 `platform` 来控制上传到哪些平台。

### 自定义工作流程

如果您想要修改工作流程：

1. 编辑 `.github/workflows/sync.yml` 文件。
2. 您可以调整运行时间、触发条件或添加更多步骤。
3. 如果您只想上传到特定平台，可以修改
   ```yaml
   matrix:
        platform: [giant, onelap]
   ```

例如，只上传到 捷安特：
```yaml
matrix:
   platform: [giant]
```

或者，上传到 捷安特 和 顽鹿-迈金：
```yaml
matrix:
   platform: [giant, onelap]
```

## 注意事项

- 请确保您的账户密码安全，不要在公开场合分享。
- 如果您频繁运行这些脚本，可能会受到相关平台的访问限制。请适度使用。
- 本项目仅供学习和个人使用，请遵守各平台的使用条款。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 许可证

[GPL-3.0](LICENSE)
