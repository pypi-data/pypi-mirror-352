# kanbanz
看板管理工具的底层能力

## 常规操作

### 导出环境
```
uv export --format requirements-txt > requirements.txt
```
### 更新文档
```
mkdocs serve # 预览
mkdocs gh-deploy -d ../.temp # 同步到github网站
```
### 发布
```
uv build
uv publish
```
### 运行测试并同步到测试服务
```
bash run_test.sh
```



