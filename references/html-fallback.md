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
  /* 密封线不在这里画：见 §2.1。Chromium 无法把 CSS 元素限定到第 1 页；
     这里只靠 @page 的 left margin（有密封线 32mm）预留位置。 */
  /* 卷头/得分表必须写在 .cols 内（多栏卷 = 左栏顶部，见 layout.md §5） */
  h1 { font-size: 18pt; line-height: 1.25; text-align: center; margin: 0 0 4pt; }
  .sub { text-align: center; font-size: 10pt; }
  /* 得分表宽度 = 100% 栏宽（禁止固定 cm：A3 纵 2 栏只有 121mm，137mm 会超栏） */
  .score { width: 100%; max-width: 100%; table-layout: fixed;
           border-collapse: collapse; margin: 6pt auto; font-size: 9pt;
           break-inside: avoid; }
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
  <!-- 密封线不在这里画：打印后用 scripts/draw_seal.py 叠加（§2.1）。
       @page 的 left margin（32mm）已经预留密封线占位。 -->

  <!-- 卷头 + 得分表必须在 .cols 内：多栏卷时它们落在左栏顶部，
       与试题同栏（对齐 latex-templates.md §1 / layout.md §5）。
       写在 .cols 外面会整幅通栏居中、跨过栏沟。 -->
  <div class="cols">
    <h1>{TITLE}</h1>
    <p class="sub">满分：{FULLMARKS}分 &nbsp; 考试时间：{TIME}分钟</p>
    <hr>

    <!-- 得分表：列数 = 1 + 大题数 + 1（与 LaTeX 版规则相同） -->
    <table class="score">
      <tr><th>题号</th><th>一</th><th>二</th><th>三</th><th>总分</th></tr>
      <tr><td>得分</td><td></td><td></td><td></td><td></td></tr>
    </table>

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

### 1.1 卷头与得分表必须在 `.cols` 内

多栏卷（2/3 栏）的 `<h1>`、`.sub`、`<hr>`、`<table class="score">` **必须**写在
`<div class="cols">` 里面，位于第一道题之前：

- 写在 `.cols` 外面 = 整幅通栏居中，标题中心落在**两栏缝**上，与
  `latex-templates.md` §1（卷头在 `\begin{multicols}` 之后）和 `layout.md` §5
  （"2/3 栏时位于左栏内、与试题同栏分栏，不整页通栏"）都不一致
- 移进 `.cols` 后它自然排在**左栏顶部**，与 LaTeX 版同栏分栏效果一致
- 1 栏卷 `.cols` 不带 `column-count`，写法不变，卷头仍是整页宽
- 得分表用 `width:100%; max-width:100%; table-layout:fixed`，**禁止写死 cm**
  （如 137mm）：A3 纵 2 栏（默认配置）只有 121mm、A3 横 3 栏 120mm、A4 纵 3 栏
  55mm，固定宽必然超栏；100% 栏宽与 LaTeX 的 `\linewidth` 比例列宽等效（红线 13）
- `h1` 18pt 与 LaTeX `\LARGE`（11pt 档 17.28pt）基本等价。窄栏里长标题**会折行**，
  LaTeX 同样折行（121mm 栏宽约 19 个汉字/行，158mm 约 24 个汉字/行）——折行不是
  缺陷，超栏/"落在栏缝上"才是；确实要压行数可降到 15–16pt，但那是审美取舍，
  不是必修项

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

### 2.1 密封线：打印后叠加（唯一可靠做法）

**不要在 HTML/CSS 里画密封线个人信息。** 两个已实测的失败模式：

1. 把四项写成**一个** `writing-mode: vertical-rl` 的 `.seal-info` div，四项会挤成
   一条竖线；且 `top: 20%` 相对**整篇文档**而非单页，长卷会落到第 2 页。
2. “第 2 页起删除 `.seal-info`”无法自动执行：Chromium 没有能选中文档元素的
   `@page :first`；`position: fixed` 会每页重复，同样不能只限第 1 页。逐页手删
   不是可重复管线。

改为：HTML 只保留 32mm 左边距，打印后由 `scripts/draw_seal.py` 在 PDF 上叠加：

```bash
python "$SKILL_ROOT/scripts/draw_seal.py" output/试卷.pdf \
  -o output/试卷_密封.pdf --paper 420x297 --lang zh
```

- 虚线 x=22mm 通高；圆点 r=2mm 沿虚线 7%–92%（步长 5%）；提示语
  x=16.5mm、50% 纸高；个人信息 x=7.5mm、65/50/35/20% 纸高，`rotate=90`，
  每项后接 **26mm 连续竖线**（不是一串 `＿` 字符）。坐标取
  `latex-templates.md` 的 TikZ 标称值（x 为 PDF 文本基线锚点）。
- **默认整条密封线只画第 1 页**：P1 左侧 2 个文本块（提示语 + 个人信息），
  P2/P3 为 0。这正是避免“每页都印密封线”的关键；不要用 CSS 去补救。
- 若确实需要 LaTeX 模板的“每页虚线 + 圆点 + 提示语”，加 `--repeat`：
  此时 P2+ 仍有 1 个提示语块，但个人信息始终只在 P1。
- `--paper` 必须与试卷方向一致（A3 横 = `420x297`），脚本会校验；
  `--lang en` 输出 School/Class/Name/ID 与英文提示语。
- 依赖 PyMuPDF：`pip install pymupdf`；`check_env.py` 的 `pdf_overlay` 字段
  会报告是否可用。密封线选“无”时跳过本步骤，左边距按 18mm。

核验（P1 有个人信息，P2+ 无）：

```bash
python - <<'PY'
import fitz
d = fitz.open("output/试卷_密封.pdf")
labels = ("学校", "班级", "姓名", "学号")
for i, p in enumerate(d, 1):
    left = [b for b in p.get_text("blocks") if b[2] < 22 * 72 / 25.4]
    info = [b for b in left if any(k in b[4] for k in labels)]
    print(i, "left_blocks=", len(left), "info_blocks=", len(info))
PY
```

期望（默认）：P1 `left_blocks=2, info_blocks=1`（提示语 + 个人信息），
P2/P3 `left_blocks=0, info_blocks=0`（无密封线）。
加 `--repeat` 时 P2/P3 变为 `left_blocks=1, info_blocks=0`（仅提示语）。

## 3. 质量检查（回退模式等效项）

tex_check.py 只查 .tex；HTML 模式由 agent 逐项自查：

- [ ] `@page size` 与用户选择的纸张/方向一致
- [ ] 栏数与选择一致（1 栏无 column-count）
- [ ] 卷头（`h1` / `.sub` / `<hr>`）与得分表在 `.cols` **内**（多栏卷 = 左栏顶部，
      不整幅通栏、不压栏沟，见 §1.1）；得分表 `width:100%`，没有固定 cm 宽度
- [ ] 密封线由 `draw_seal.py` 叠加（不是 CSS）：默认仅 P1 有整条密封线，
      P2+ 无；加 `--repeat` 时 P2+ 只有虚线/圆点/提示语，个人信息仍限 P1
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
