FROM python:3.11.2

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到容器的 /app 目录
COPY app /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 设置环境变量，告诉 uvicorn 使用哪个文件
ENV UVICORN_CMD="uvicorn main:app --host 0.0.0.0 --port 8000"

# 暴露端口 80
EXPOSE 8000

# 运行 FastAPI 应用
CMD ["sh", "-c", "$UVICORN_CMD"]