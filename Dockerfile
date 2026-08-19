# syntax=docker/dockerfile:1

#
# 构建前端
#

FROM node:18.17.0-bullseye AS builder
ARG BASE_PATH='/root/blivechat'
WORKDIR "${BASE_PATH}/frontend"

# 前端依赖
COPY frontend/package.json ./
RUN npm i --registry=https://registry.npmmirror.com

# 编译前端
COPY frontend ./
RUN npm run build

#
# 准备后端
#

FROM ghcr.io/astral-sh/uv:python3.12-trixie
ARG BASE_PATH='/root/blivechat'
ARG EXT_DATA_PATH='/mnt/data'
ENV UV_NO_DEV=1
ENV UV_NO_CACHE=1
WORKDIR "${BASE_PATH}"

# 代码、数据目录
COPY --exclude=frontend/ . ./
RUN uv sync --locked \
    && sed 's/^host =.*$/host = 0.0.0.0/; s/^loader_url =.*$/loader_url =/' data/config.example.ini >> data/config.ini \
    && mkdir -p "${EXT_DATA_PATH}" \
    && mv data "${EXT_DATA_PATH}/data" \
    && ln -s "${EXT_DATA_PATH}/data" data \
    && mv log "${EXT_DATA_PATH}/log" \
    && ln -s "${EXT_DATA_PATH}/log" log

# 编译好的前端
COPY --from=builder "${BASE_PATH}/frontend/dist" frontend/dist

# 运行
VOLUME "${EXT_DATA_PATH}"
EXPOSE 12450
ENTRYPOINT ["uv", "run", "main.py"]
