import garth
import zipfile
import os
import argparse
import time

# Garmin配置
GARMIN_DOMAIN = "garmin.cn"
ACTIVITY_TYPE = "cycling"
ACTIVITY_LIMIT = 5
ACTIVITY_START = 0
EXCLUDE_CHILDREN = False

# 文件夹路径
FIT_OUT = "FIT_OUT"


def download_from_garmin(username, password):
    fit_files = []

    if not os.path.exists(FIT_OUT):
        os.makedirs(FIT_OUT)

    garth.configure(domain=GARMIN_DOMAIN)
    garth.login(username, password)
    activities = garth.connectapi(
        f"/activitylist-service/activities/search/activities",
        params={
            "activityType": ACTIVITY_TYPE,
            "limit": ACTIVITY_LIMIT,
            "start": ACTIVITY_START,
            "excludeChildren": EXCLUDE_CHILDREN,
        },
    )

    for activity in activities:

        activity_id = str(activity["activityId"])
        res = garth.download(f"/download-service/files/activity/{activity_id}")

        zip_file_path = os.path.join(FIT_OUT, f"{activity_id}.zip")
        with open(zip_file_path, "wb") as f:
            f.write(res)

        # 解压zip文件到FIT_OUT文件夹
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(FIT_OUT)

        fit_file_path = os.path.join(FIT_OUT, f"{activity_id}_ACTIVITY.fit")
        fit_files.append(fit_file_path)

        os.remove(zip_file_path)

        time.sleep(1)  # 每次请求之间等待 1 秒

    print(f"FIT file downloaded and extracted to: {fit_files}")
    return fit_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("email", nargs="?", help="input garmin email")
    parser.add_argument("password", nargs="?", help="input giant password")
    options = parser.parse_args()

    email = options.email
    password = options.password

    download_from_garmin(email, password)
