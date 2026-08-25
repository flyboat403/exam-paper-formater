# HTML/CSS 回退管线（无 xelatex 环境）

> **何时使用**：`check_env.py` 报告 `pipeline: html-fallback`（无 xelatex 且无法安装）。
> 质量说明：KaTeX 公式渲染良好，CSS 多栏分页控制弱于 LaTeX multicols
> （栏间断题不如 LaTeX 精确），建议回退模式下优先 1–2 栏的简单版式。
> 有 xelatex 时**永远优先 LaTeX 主管线**。

## 1. 页面骨架（占位符与 LaTeX 模板同名）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{TITLE}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body,{delimiters:[
    {left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}]});"></script>
<style>
  @page {
    size: {PAPERWIDTH}mm {PAPERHEIGHT}mm;   /* 方向=交换两个值 */
    margin: 16mm {12mm} 13mm {LEFT}mm;      /* 上 右 下 左；左 32mm 有密封线 / 18mm 无。上/下≈试卷正文边距 ×4/3 */
  }
  * { box-sizing: border-box; }
  body { font-family: "SimSun","Noto Serif CJK SC",serif; font-size: 11pt;
         margin: 0; color: #000; }
  .paper { position: relative; }
  .cols  { column-count: {COLUMNS}; column-gap: {COLUMNSEP}; }
  /* 1 栏：.cols 不加 column-count */
  .seal { position: absolute; left: 22mm; top: 0; bottom: 0; width: 0;
          border-left: 1px dashed #000; }
  .seal-text { position: absolute; left: 12mm; top: 50%;
               transform: translateY(-50%) ; writing-mode: vertical-rl;
               font-size: 9pt; letter-spacing: 4pt; }
  .seal-info { position: absolute; left: 6mm; top: 20%;
               writing-mode: vertical-rl; font-size: 9pt; letter-spacing: 2pt; }
  .seal-circle { position: absolute; left: calc(22mm - 2mm); width: 4mm; height: 4mm;
                 border: 0.5pt solid #000; border-radius: 50%; }
  h1 { font-size: 18pt; text-align: center; margin: 0 0 4pt; }
  .sub { text-align: center; font-size: 10pt; }
  .score { border-collapse: collapse; margin: 6pt auto; font-size: 9pt; }
  .score td, .score th { border: 0.5pt solid #000; padding: 2pt 6pt; text-align: center; }
  .q { break-inside: avoid; margin: 0 0 2pt; }        /* 单题尽量不跨栏断；题间距收紧 */
  .opts { column-count: 4; column-gap: 4mm; }          /* 选择题四栏 */
  .opts li { list-style: none; margin: 0; }
  .blank { display: inline-block; border-bottom: 0.5pt solid #000; height: 1em; }
  .answer-space { height: 40mm; }                      /* 解答题答题空白 */
  .pagenum { text-align: center; font-size: 9pt; }
  img.fig { width: 100%; max-width: 100%; }            /* 图宽 = 栏宽 */
</style>
</head>
<body>
<div class="paper">
  <!-- 密封线（seal=on 时保留；第 2 页起删除 .seal-info） -->
  <div class="seal"></div>
  <div class="seal-text">密封线内不得答题</div>
  <div class="seal-info">学校______ 班级______ 姓名______ 学号______</div>

  <h1>{TITLE}</h1>
  <p class="sub">满分：{FULLMARKS}分 &nbsp; 考试时间：{TIME}分钟</p>
  <hr>

  <!-- 得分表：列数 = 1 + 大题数 + 1（与 LaTeX 版规则相同） -->
  <table class="score">
    <tr><th>题号</th><th>一</th><th>二</th><th>三</th><th>总分</th></tr>
    <tr><td>得分</td><td></td><td></td><td></td><td></td></tr>
  </table>

  <div class="cols">
    <section class="q">
      <h3>一、选择题（共 X 题，每题 X 分）</h3>
      <p>1. 题目内容……（&nbsp;&nbsp;）</p>
      <ul class="opts">
        <li>A. 选项A</li><li>B. 选项B</li>
        <li>C. 选项C</li><li>D. 选项D</li>
      </ul>
      <!-- 填空题：题目 <span class="blank" style="width:3cm"></span>。 -->
      <!-- 解答题：<div class="answer-space"></div> -->
      <!-- 配图：<img class="fig" src="output/fig_q5.png">（diagram_tools.py 生成，同主管线） -->
    </section>
  </div>

  <p style="text-align:right">—— 试卷到此结束，请认真检查 ——</p>
  <p class="pagenum">第 <span class="pageNumber"></span> 页</p>
</div>
<script>
  // 页码注入（Edge/Chromium 打印支持 CSS counter，这里用 JS 双保险）
  document.querySelectorAll('.pageNumber').forEach(el => {
    const total = Math.max(1, Math.ceil(document.body.scrollHeight / 900));
    el.textContent = '…'; // 简单卷（≤2页）可省略动态页码
  });
</script>
</body>
</html>
```

## 2. 打印为 PDF

Windows（Edge 自带，无需安装）：

```bash
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" ^
  --headless --disable-gpu --no-pdf-header-footer ^
  --print-to-pdf="output\试卷.pdf" "file:///C:/path/to/试卷.html"
```

（PowerShell 里用 `& "…msedge.exe" --headless --no-pdf-header-footer --print-to-pdf=… file:///…`；
Linux 用 `chromium --headless --print-to-pdf`。）

- `--no-pdf-header-footer`：去掉浏览器默认页眉页脚（日期/URL）
- 若 Edge 不在默认路径，用 `check_env.py` 报告的路径
- 打印前**必须**等 KaTeX 渲染完成：headless 模式下 `--virtual-time-budget=8000`
  （给 CDN 脚本 + 公式渲染留 8 秒虚拟时间）：

```bash
msedge --headless --no-pdf-header-footer --virtual-time-budget=8000 ^
       --print-to-pdf=out.pdf file:///…
```

- **离线环境**：KaTeX CDN 不可达时，把 katex.min.css / katex.min.js /
  auto-render.min.js 下载到本地并改相对路径引用

## 3. 质量检查（回退模式等效项）

tex_check.py 只查 .tex；HTML 模式由 agent 逐项自查：

- [ ] `@page size` 与用户选择的纸张/方向一致
- [ ] 栏数与选择一致（1 栏无 column-count）
- [ ] 密封线 on/off 与选择一致（第 1 页有个人信息、其余页无）
- [ ] 题干「如图」→ 有对应 `<img>`，且图片文件存在
- [ ] 公式全部 `$…$` / `$$…$$` 包裹（KaTeX 语法与 LaTeX 兼容，
      化学式规则同 formulas.md：`H$_2$O`、`Cu$^{2+}$`）
- [ ] 得分表覆盖全部题型，分值加总 = 满分
- [ ] 打开生成的 PDF 目检：公式已渲染（不是原始 `$` 符号）、图未超栏、
      无浏览器页眉页脚

## 4. 答案卷

同样结构：默认 A4 竖向、单栏（无 `.cols`）、边距 25mm；
用户要求"跟随试卷纸张"时用试卷的 `@page size`。
标题「{TITLE} 参考答案」，内容规则同 LaTeX 答案模板。
