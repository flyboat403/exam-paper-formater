# 题型排版细则

> 所有题目格式必须遵守本文件。格式错乱 = 废卷。LaTeX 代码片段直接可用。

## 1. 选择题（最重要，AI 最容易出错）

ABCD 选项**禁止**写在同一行，也**禁止与题干同一行**。必须**另起一段**，
用 `multicols{4}` 分四栏（题干一行 → 空一行 → 选项块）：

```latex
\item 题目内容……（\quad）

\begin{multicols}{4}
\begin{enumerate}[label=\Alph*.,leftmargin=*]
\item 选项A内容
\item 选项B内容
\item 选项C内容
\item 选项D内容
\end{enumerate}
\end{multicols}
```

规则：
- **题干与选项必须分段**：例题：`\item 题干（　）A.… B.… C.… D.…` 是错的，
  正确写法是题干一行结束后另起一段放 ABCD 块
- 4 个选项用 `multicols{4}` 均分四栏，每个选项独占一栏
- 选项标签用大写字母 `label=\Alph*.`（A. B. C. D.）
- 选项内容较长（>8 字）**改用 `multicols{2}`** 两栏
- 选项末尾**不加分号、句号**
- 题干末尾留答题空位：`（\quad）` 或 `\underline{\hspace{1cm}}`
- 高中多选（新高考）：题干后注明评分规则
  （全部选对得满分，选对但不全得部分分，有选错得 0 分）

**3 栏主体内的选项分栏**：嵌套 `multicols{4}` 在 3 栏卷中不稳定，
推荐 tabular 方案（`\optab{A}{B}{C}{D}`，定义见 latex-templates.md §1
模板关键点）；2 栏卷嵌套 multicols 一般可用，报错/错位时同样改用 tabular。

## 2. 填空题

```latex
\item 题目内容 \underline{\hspace{3cm}}。
```

- 答案横线 `\underline{\hspace{…}}`，长度按答案调（2–5cm）
- 填空之间 `itemsep=0pt`，保持紧凑
- **只留答案横线，不留大段答题空白**（那是解答题的格式）

## 3. 判断题（小学常用）

```latex
\item 题目内容……（\quad）
```

题末留括号供学生打 √ / ×。

## 4. 解答题 / 计算题

```latex
\item （本题[X]分）题目内容……

\vspace*{4cm}   % 答题空白
```

- 每题标注分值
- `\vspace*{…}`（带星号，空白不被压缩）：小学 2–3cm，初中 4–5cm，高中 5–7cm
- 配图题：图紧跟题干之后、答题空白之前

## 5. 实验题 / 作图题（理科）

- **作图题的答题框在多栏里可能被分栏截断**（multicols 平衡所致）。
  编译后必须视觉核验作图题所在栏；若被截断，把答题框放进
  `\nopagebreak` 包或改用 `\begin{minipage}` 整体保护，仍不行就把该题
  移到栏首（`\clearpage` 局部换栏不现实，只能整体挪题）
- 作图题（物理光路/电路/力学作图）：在题干后留**方格纸或空白区域**供学生作图：

```latex
\item （本题4分）……请在下图虚线框内完成电路图。
\begin{center}
\fbox{\begin{minipage}{0.8\linewidth}\centering
\vspace{2.5cm}\vspace{2.5cm}\end{minipage}}
\end{center}
```

- 实验探究题：装置图/电路图用 TikZ 绘制（见 figures.md），数据表格用
  `\begin{tabular}` + `\small`

## 6. 通用规则（所有题型）

- `itemsep=0pt, topsep=0.8pt`：题目间紧凑
- `leftmargin=*`：题号对齐
- **题号连续贯穿全卷**（不是每个大题从 1 重新编号；用 `start=N` 续接）
- 大题标题格式：`\section*{一、选择题（本大题共X小题，每小题X分，共X分）}`
  （**左对齐/两端对齐，不居中**——模板已设
  `\ctexset{section/format = {\Large\bfseries\raggedright}}`）
- 每大题分值合计写进标题；全部大题合计 = 满分
- 表格：`\small` 起，不得超出栏宽（栏宽见 layout.md）
- 作文题（语文）：预留方格纸区域（见 subject-notes.md）

## 7. 中文排版规范（所有文本）

| 错误 | 正确 | 说明 |
|------|------|------|
| "特征反应" | “特征反应” | 中文引号必须全角，禁用 ASCII `"`（还可能被当数学定界符） |
| -- | —— | 中文破折号 U+2014×2 |
| ... | …… | 中文省略号 |
| `$x = 1。$` | `$x = 1$。` | 中文标点放数学模式**外** |
| `\text{已知}x=1` | — | 数学模式内中文必须 `\text{…}` |
| ① ② ③（带圈数字 U+2460–2469） | (1) (2) (3) | **实测**：ctex 的 CJK 字体范围不含 Enclosed Alphanumerics 区块，① 在 lmroman 西文字体中无字形 → Missing character（答案卷实测） |
| 正文流程箭头 `\rightarrow` | 全角 `→`（文本字符）或 `——` | **实测**：`\rightarrow` 等 math mode 符号命令在 CJK 邻接处会破坏 xeCJK 字体切换，后续中文落入西文字体满屏 Missing character；正文流程一律用全角 `→`（U+2192 作为 CJK 文本字符正常），数学推导公式里的 `\rightarrow` 不受影响 |
| 描述 Excel 公式时的 `$`（绝对引用） | 文字描述"绝对引用/列首行加锁" | **实测**：正文里裸 `$` 破坏 tex 数学模式配对（`Missing $ inserted` 连锁报错）；`\texttt{$}`/`\verb|$|` 在 ctex 下仍被 tex_check 数学扫描计数。**正文不要出现 `$` 字符**，Excel 绝对引用用文字说明（例外：题目原文含 Excel 公式时，用 `\$` 转义忠实保留） |
| SQL/代码内 ASCII 引号（性别='男'） | 保留原样 | 代码忠实优先；checker 的 straight-quote WARNING 可保留（非交付门槛），勿为消警告改题目内容 |
