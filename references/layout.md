# 版式参数映射（纸张 × 方向 × 栏数）

> 本文件定义试卷排版的全部版式参数如何由用户选择映射到 LaTeX（或 HTML 回退）的具体取值。
> 生成任何试卷前，必须先完成 SKILL.md 中的版式参数询问，再按本文件取值。

## 1. 纸张 × 方向 → paperwidth / paperheight

| 纸张 | 纵向 portrait | 横向 landscape |
|------|--------------|----------------|
| A4   | 210 × 297 mm | 297 × 210 mm |
| A3   | 297 × 420 mm | 420 × 297 mm（中国学校标准考试大纸） |
| B5   | 182 × 257 mm | 257 × 182 mm |
| A5   | 148 × 210 mm | 210 × 148 mm |
| **正度8开** | **260 × 370 mm** | **370 × 260 mm** |
| 自定义 | 用户给的 W × H（mm） | 交换 W/H |

LaTeX 中写死具体数值（`tex_check.py` 会校验）：

```latex
\usepackage[paperwidth=420mm,paperheight=297mm,top=1.6cm,bottom=2.0cm,left=3.2cm,right=1.2cm]{geometry}
```

**方向最容易错**：横向 = paperwidth 取长边。生成后必须对照用户选择检查，
`tex_check.py --paper WxH` 会自动校验。

## 2. 边距

| 项目 | 有密封线 | 无密封线 |
|------|---------|---------|
| 左边距 | **3.2cm**（密封线占 2.2cm） | 1.8cm |
| 上边距 | **1.6cm** | **1.6cm** |
| 下边距 | **2.0cm** | **2.0cm** |
| 右边距 | 1.2cm | 1.2cm |

- **下边距 ≥ 1.4cm**：为 `fancyhdr` 页脚页码留足竖直空间，避免
  《页码只显示一部分》被裁切。栏宽只依赖左/右/栏距，不受下边距影响

字号：正文 11pt（小学低年级 12pt）；`\parindent=0pt`、`\parskip=0.9pt`（**题目间段间距收紧，排列更紧密**）、
`\emergencystretch=3em`（防中文长句右溢）。

## 3. 栏数（1 / 2 / 3）

| 栏数 | 实现 | columnsep |
|------|------|-----------|
| 1 | 整卷**不使用** multicols（全幅单栏） | — |
| 2 | `\begin{multicols}{2}` 包住全部题目 | 10mm |
| 3 | `\begin{multicols}{3}` 包住全部题目 | 8mm |

- multicols 只包**题目主体**；试卷头（标题/满分/时间）、得分表、卷尾结束标记在栏外。
- `\columnseprule=0pt`（栏间不画线）。
- 注意：选择题选项内部会用嵌套的 `multicols{4}`（见 question-format.md），
  与主体栏数无关，tex_check 只校验**第一个**（正文级）multicols。

### 栏宽计算

```
栏宽 = (纸宽 − 左边距 − 右边距 − (n−1)×columnsep) / n
```

常见组合速查（有密封线/无密封线）：

| 配置 | 栏宽 |
|------|------|
| A3 横 3 栏（密封线） | ≈120 mm（标准学校试卷） |
| A3 横 2 栏（密封线） | ≈183 mm |
| **A3 纵 2 栏（密封线，默认配置）** | **≈121 mm** |
| A3 纵 3 栏（密封线） | ≈79 mm |
| A4 纵 2 栏（无密封线） | ≈85 mm |
| A4 纵 3 栏（无密封线） | ≈55 mm（窄！图需 ≤0.4 scale） |
| A4 横 3 栏（无密封线） | ≈84 mm |
| B5 纵 2 栏（无密封线） | ≈71 mm |
| B5 纵 1 栏（无密封线） | 152 mm |
| A5 纵 1 栏（无密封线） | 118 mm |
| 8开 横 2 栏（密封线） | ≈139 mm（370 宽向，短边卷，卷尾禁用 `\vspace*{\fill}`，见 SKILL.md 红线 11） |

**图形适配规则**（详见 figures.md）：图宽 ≤ 90% 栏宽；
栏宽 < 60 mm 时，图形 scale ≤ 0.4 或建议用户减栏。

## 4. 密封线（可选，默认有）

每页左侧：

- 虚线竖线：`densely dashed`、`line width=0.8pt`，距左边缘 **2.2cm**，通高
- 小圆圈：半径 2mm，沿虚线在 7%、12%、…、93% 纸高位置均匀分布
- 竖排文字「密封线内不得答题」位于 1.65cm 处（英文卷：*Do not write inside the seal line*）
- **第 1 页**：竖排 学校 / 班级 / 姓名 / 学号（英文卷 School / Class / Name / ID）
- **第 2 页起**：只保留虚线 + 圆圈 + 竖排文字，**不含个人信息**

实现见 latex-templates.md 的 `shipout/background` hook 代码块
（on/off 由参数控制，整块复制或删除）。

## 5. 试卷头与得分表

试卷头（**第 1 页最前面**，自上而下；1 栏=整页宽，**2/3 栏时位于左栏内、
与试题同栏分栏，不整页通栏**）：
（① 学校名称、② 试卷用途/名称、③ 满分/时间 —— ①②按第 2 步采集）

```
{\large \textbf{[学校名称]}}
\vspace{2pt}
{\LARGE \textbf{[试卷用途/名称：XX年度X年级X学科期末考试卷]}}
\vspace{2pt}
{\small 满分：[分数]分 \quad 考试时间：[时间]分钟}
```

得分表（紧随试卷头，**位于同一栏**；列数 = 1（题号）+ 每个大题一列 +
1（总分）），**必须覆盖全部题型**（解答题/实验题/作图题最容易漏）。
**列宽必须用 \linewidth 比例（禁止固定 cm）**：固定宽表在多栏卷会超栏，
溢出被画到栏沟与邻栏、与邻栏题干文字交错（实测 11 列固定宽表超栏 89mm，
见 SKILL.md 红线 13）。比例列宽下大题数多少都放得下（实测 183mm 栏宽
11 列无压力）；仅题号放不下的极多列情形（如 3 栏卷 10+ 大题）才合并
题号区间（两大题共一列）。
- **列数约定：每个大题 1 列（不要给每个大题开 2 个子列），否则
  列数多、易触发 `! Extra alignment tab`**。题号范围可放在题号行下方
  的第二行（`\hline` 分隔），并非独立列。
- 结构（两行表头 + 一行得分）；单元格内容**水平+垂直居中**
  （`m{}` 列 + `>{\centering\arraybackslash}`，加 `\renewcommand{\arraystretch}{1.5}` 增高）；
  `\tabcolsep=0` + `\fill` 胶水自动均分剩余间隙（比例列宽见左）：

```latex
% 题号/总分列 = 0.12\linewidth；大题列 = 0.70\linewidth/n − 2pt（n = 大题数，改分母即可）
\begin{center}
\small
\renewcommand{\arraystretch}{1.5}
\setlength{\tabcolsep}{0pt}
\begin{tabular*}{\linewidth}{@{\extracolsep{\fill}}|>{\centering\arraybackslash}m{0.12\linewidth}|>{\centering\arraybackslash}m{\dimexpr0.70\linewidth/3-2pt\relax}|>{\centering\arraybackslash}m{\dimexpr0.70\linewidth/3-2pt\relax}|>{\centering\arraybackslash}m{\dimexpr0.70\linewidth/3-2pt\relax}|>{\centering\arraybackslash}m{0.12\linewidth}|}
\hline
题号 & 一（选择） & 二（填空） & 三（解答） & 总分 \\
\hline
1–12 & 13–18 & 19–25 & & \\
\hline
得分 & & & & \\
\hline
\end{tabular*}
\end{center}
```

- 需要「题号范围」时放在题号行的下一行（`\hline` 分隔），不再加子列
- **逐题分值加总必须 = 满分**（交付前手工验证）

## 6. 答题卡（第 3 个输出产物，固定 A4 纵向）

- **答题卡 = 学生作答卡**（区别于 答案卷 = 参考答案）：只放
  **题号 + 选项框（A/B/C/D、判断 A/B）+ 填空空白**，不含参考答案
- **固定 A4 纵向** 210×297mm，与试卷纸张无关（A3/A4 横卷答题卡也恒为
  A4 纵向）；单栏、无密封线，顶部放 学校/班级/姓名/学号 填字段
- 产出第 3 个 PDF：`答题卡.tex` + `答题卡.pdf`（默认生成；用户说
  "不要答题卡"才省略）
- 客观题用紧凑网格：`\item[1.] A $\square$ B $\square$ C $\square$ D $\square$`
  （选项用 `amssymb` 的 `\square`，多题并排、隔 5 题分节）

## 7. 页脚与卷尾

- 页脚居中页码：`\fancyfoot[C]{\small \thepage}`
- 卷尾（栏外，右下角）：

```latex
\vspace*{\fill}   % 8开横向等短边卷禁用 \fill（撑爆剩余空间，红线 11），改固定 \vspace*{2cm}
\hfill {\small \textbf{—— 试卷到此结束，请认真检查 ——}}
```

英文卷：`—— End of Paper. Please check your answers. ——`

## 8. 默认配置

用户说"随便 / 默认 / 你定"时使用：

**A3 / 纵向 / 2 栏 / 密封线：有 / 答案卷：生成 / 字号 11pt**

（≈121mm 栏宽，兼顾密度与图形空间；学校印刷标准是 A3 横 3 栏，
若用户提到"学校印刷 / 中考 / 高考"，主动建议 A3 横 3 栏。）
