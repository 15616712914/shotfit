# Shotfit

iPhone 截图 → App Store 可上传尺寸（1320×2868）的在线工具。

- 纯前端：单个 `index.html`，无依赖、无后端、无统计
- 图片不上传，全部在浏览器 canvas 内完成
- 支持批量、6.9"/6.7"/6.5" 三种输出、自动去 alpha

## 本地预览

```bash
python3 -m http.server 8080
# http://127.0.0.1:8080
```

## 部署

把整个文件夹拖到 https://app.netlify.com/drop 即可；也可以在 Netlify/Vercel/Cloudflare Pages 里绑定这个目录。

自定义域名：在 DNS 加一条 CNAME 指向托管平台给的地址即可（例如 `shotfit.example.com`）。
