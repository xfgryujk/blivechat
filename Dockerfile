#
# 构建前端
#

FROM node:18.17.0-bullseye AS builder
ARG BASE_PATH='/root/blivechat'
WORKDIR "${BASE_PATH}/frontend"

# 前端依赖
COPY frontend/package.json ./
RUN npm i

# 编译前端
COPY frontend ./
RUN npm run build

#
# 准备后端
#

FROM python:3.8.12-bullseye
ARG BASE_PATH='/root/blivechat'
ARG EXT_DATA_PATH='/mnt/data'
WORKDIR "${BASE_PATH}"

# 后端依赖
COPY blivedm/requirements.txt blivedm/
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt

# 数据目录
COPY . ./
RUN mkdir -p "${EXT_DATA_PATH}/frontend/dist" \
    && mv data "${EXT_DATA_PATH}/data" \
    && ln -s "${EXT_DATA_PATH}/data" data \
    && mv log "${EXT_DATA_PATH}/log" \
    && ln -s "${EXT_DATA_PATH}/log" log \
    && ln -s "${EXT_DATA_PATH}/frontend/dist" frontend/dist

# 编译好的前端
COPY --from=builder "${BASE_PATH}/frontend/dist" "${EXT_DATA_PATH}/frontend/dist/"

# 运行
VOLUME "${EXT_DATA_PATH}"
EXPOSE 12450
ENTRYPOINT ["python3", "main.py"]
CMD ["--host", "0.0.0.0", "--port", "12450"]
