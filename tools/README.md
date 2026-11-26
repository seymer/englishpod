# 页面增强工具

所有脚本可重复执行；完整重建按下面顺序：

```bash
git checkout -- html/ index.html
python3 tools/inject_karaoke.py       # 台词逐词高亮
python3 tools/inject_zh.py            # 台词中文翻译
python3 tools/inject_zh_toggle.py     # 中/英切换按钮
python3 tools/inject_zh_vocab.py      # 词汇中文名 + 中文释义
python3 tools/inject_index_titles.py  # 首页列表中文标题（hover 显示）
python3 tools/inject_print.py         # 打印分页：正文 / 词汇两页
python3 tools/inject_layout.py        # 行高与打印排版微调
```

数据源来自 `~/Developer/englishpod_all` 的 `webapp/data.js`、`align.jsonl`、`zh.js`、`zh_words_full.js`。

运行时依赖只有两个共享脚本：

- `js/karaoke.js`：逐词高亮
- `js/zh-toggle.js`：右上角 A4 边框内的「中/英」三态按钮

打印时只隐藏音频；右上角「中/英」按钮会一起打印出来，作为这份材料当前中文状态的标记（「英」态下中文留空，可用于翻译练习）。
