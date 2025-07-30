# TagFinder

一个用于从各种镜像仓库中查找最新镜像标签的命令行工具。

## 安装

```bash
pip install -e .
```

## 使用方法

### 基本用法

```bash
# 使用默认参数（harbor.milvus.io, milvus/milvus, master-latest, amd64）
tagfinder get-tag

# 指定标签和架构
tagfinder get-tag --tag master-latest --arch amd64

# 简写形式
tagfinder get-tag -t master-latest -a amd64
```

### 使用不同的镜像仓库

```bash
# 使用Harbor仓库
tagfinder get-tag --registry harbor.milvus.io --repository milvus/milvus

# 使用Docker Hub
tagfinder get-tag --registry registry.hub.docker.com --repository username/repository
```

### 使用仓库配置

您可以为常用的镜像仓库和路径组合设置配置，以便更方便地使用：

```bash
# 添加仓库配置
tagfinder registry add docker-hub --registry registry.hub.docker.com --repository username/repository

# 使用仓库配置
tagfinder get-tag --profile docker-hub -t latest -a amd64
# 或使用简写形式
tagfinder get-tag -f docker-hub -t latest -a amd64

# 列出所有仓库配置
tagfinder registry list

# 删除仓库配置
tagfinder registry remove docker-hub
```

## 参数说明

### get-tag 命令

- `--tag`, `-t`: 短标签名称，默认为 "master-latest"
- `--arch`, `-a`: 架构（如 amd64, arm64 等），默认为 "amd64"
- `--registry`, `-r`: 镜像仓库地址，默认为 "harbor.milvus.io"
- `--repository`, `-p`: 仓库路径（格式为 project/repo），默认为 "milvus/milvus"
- `--profile`, `-f`: 使用预定义的仓库配置

### registry 命令

- `add`: 添加仓库配置
  - `NAME`: 配置名称
  - `--registry`, `-r`: 镜像仓库地址
  - `--repository`, `-p`: 仓库路径
- `remove`: 删除仓库配置
  - `NAME`: 要删除的配置名称
- `list`: 列出所有仓库配置
