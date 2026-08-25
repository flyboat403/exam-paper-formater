# LaTeX 模板（中文卷 / 英文卷 / 答案卷 / 答题卡）

> 占位符：`{PAPERWIDTH}` `{PAPERHEIGHT}`（mm，见 layout.md 映射表）、
> `{LEFT}`（3.2cm 有密封线 / 1.8cm 无）、`{COLUMNSEP}`（8mm 3栏 / 10mm 2栏）、
> `{COLUMNS}`（2 或 3；**1 栏时删除整个 multicols 环境**）、
> `{TITLE}` `{FULLMARKS}` `{TIME}`、得分表按实际题型调整。
>
> 生成后必须跑 `scripts/tex_check.py` 校验参数一致性，再编译。

## 1. 中文试卷（ctexart）

```latex
\documentclass[11pt]{ctexart}
\usepackage[paperwidth={PAPERWIDTH}mm,paperheight={PAPERHEIGHT}mm,top=1.6cm,bottom=2.0cm,left={LEFT}cm,right=1.2cm]{geometry}
% bottom≥1.4cm：给页脚页码留足空间，避免页码显示不全（当前取值 2.0cm）
\usepackage{amsmath,amssymb}
\usepackage{enumitem}
\usepackage{multicol}
\usepackage{array}      % 得分表 m{} 列：单元格内容水平+垂直居中
\usepackage{tikz}
\usepackage{fancyhdr}
\usetikzlibrary{calc,positioning,angles,quotes,intersections,through,arrows.meta,patterns}

\setlength{\headheight}{15pt}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.9pt}   % 段间距收紧（题目间更紧密；如需更疏再调回 2pt）
\setlength{\columnsep}{COLUMNSEP}
\setlength{\columnseprule}{0pt}
\setlength{\emergencystretch}{3em}
\widowpenalty=10000
\clubpenalty=10000
\brokenpenalty=10000

% 大题标题（\section*）：左对齐/两端对齐，不居中
\ctexset{section/format = {\Large\bfseries\raggedright}}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot[C]{\small \thepage}
\renewcommand{\headrulewidth}{0pt}

% ==== 密封线（无密封线时删除整块） ====
\AddToHook{shipout/background}{%
  \put(0,-\paperheight){%
    \begin{tikzpicture}[remember picture, overlay]
      \draw[densely dashed, line width=0.8pt]
        (2.2cm, 0) -- (2.2cm, \paperheight);
      \node[rotate=90] at (1.65cm, 0.5\paperheight)
        {\small\sffamily 密封线内不得答题};
      \foreach \y in {0.07,0.12,...,0.93} {
        \draw[line width=0.5pt] (2.2cm, \y\paperheight) circle (2mm);
      }
      \ifnum\value{page}=1
        \node[rotate=90] at (0.75cm, 0.65\paperheight)
          {\small 学校\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_};
        \node[rotate=90] at (0.75cm, 0.50\paperheight)
          {\small 班级\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_};
        \node[rotate=90] at (0.75cm, 0.35\paperheight)
          {\small 姓名\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_};
        \node[rotate=90] at (0.75cm, 0.20\paperheight)
          {\small 学号\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_};
      \fi
    \end{tikzpicture}%
  }%
}
% ==== 密封线结束 ====

\begin{document}

% === 题目主体（1 栏时无 multicols） ===
\begin{multicols}{COLUMNS}

% === 试卷信息（第 1 页最前面；多栏时位于左栏内、与试题同栏分栏，不整页通栏） ===
\begin{center}
{\large \textbf{{SCHOOL}}}            % 学校名称（第 1 页最前面）
\vspace{2pt}

{\LARGE \textbf{{TITLE}}}           % 试卷名称
\vspace{2pt}

{\normalsize \textbf{{PURPOSE}}}    % 试卷用途：单元测验 / 期中检测 / 期末考试 / 模拟考试 …
\vspace{2pt}

{\small 满分：{FULLMARKS}分 \quad 考试时间：{TIME}分钟}
\end{center}
\vspace{-2pt}
\hrule
\vspace{4pt}

% === 得分表（与试卷信息同栏；列数 = 1 + 大题数 + 1总分） ===
% **列宽必须用 \linewidth 比例，禁止固定 cm**（实测：固定宽表在多栏卷超栏，
% 溢出被画到栏沟与邻栏、与邻栏题干文字交错，红线 13）：
%   题号列/总分列 = 0.12\linewidth；每个大题列 = 0.70\linewidth/n − 2pt
%   （n = 大题数，按实际改分母，\dimexpr 自动算）；
% \tabcolsep=0 + \extracolsep{\fill} 自动均分剩余间隙，总宽恒不超栏；
% m{} 列 + \centering 使单元格内容【水平+垂直居中】，\arraystretch 加高行。
% 题号区间放第二行（\hline 分隔）；比例列宽下大题数多少都放得下
% （实测 183mm 栏宽 11 列 OK），仅题号放不下的极多列情形才合并两大题共一列
\begin{center}
\small
\renewcommand{\arraystretch}{1.5}
\setlength{\tabcolsep}{0pt}
\begin{tabular*}{\linewidth}{@{\extracolsep{\fill}}|>{\centering\arraybackslash}m{0.12\linewidth}|>{\centering\arraybackslash}m{\dimexpr0.70\linewidth/3-2pt\relax}|>{\centering\arraybackslash}m{\dimexpr0.70\linewidth/3-2pt\relax}|>{\centering\arraybackslash}m{\dimexpr0.70\linewidth/3-2pt\relax}|>{\centering\arraybackslash}m{0.12\linewidth}|}
\hline
题号 & 一 & 二 & 三 & 总分 \\
\hline
1–12 & 13–18 & 19–25 & & \\
\hline
得分 & & & & \\
\hline
\end{tabular*}
\end{center}
\vspace{4pt}

% === 两级结构（可选：有「第一部分/第二部分」的卷，职教高考/会考常见） ===
% 部分行用 \section*（导言区把 section/format 提为 \LARGE\bfseries\raggedright，
% 并加 \ctexset{subsection/format = {\large\bfseries\raggedright}}），
% 大题改用 \subsection*：层级 标题 \LARGE > 部分 \LARGE > 大题 \large。
%   \section*{第一部分　专业知识（应知）}
%   \subsection*{一、单项选择题（…）}
% checker 得分表覆盖检查同时认 \section* / \subsection* 大题；
% 部分行以「第」开头，不会被误计为大题。

\section*{一、选择题（本大题共X小题，每小题X分，共X分）}
\begin{enumerate}[leftmargin=*,label=\arabic*.,itemsep=0pt,topsep=1pt]

\item 题目内容……（\quad）
% 选项必须另起一段（与题干分段，禁止题干与选项同一行）：
\begin{multicols}{4}
\begin{enumerate}[label=\Alph*.,leftmargin=*]
\item 选项A
\item 选项B
\item 选项C
\item 选项D
\end{enumerate}
\end{multicols}

% ……更多选择题
\end{enumerate}

\section*{二、填空题（本大题共X小题，每小题X分，共X分）}
\begin{enumerate}[leftmargin=*,label=\arabic*.,start=11,itemsep=0pt,topsep=1pt]
\item 题目内容 \underline{\hspace{3cm}}。
% ……更多填空题
\end{enumerate}

\section*{三、解答题（本大题共X小题，共X分）}
\begin{enumerate}[leftmargin=*,label=\arabic*.,start=17,itemsep=0pt,topsep=1pt]
\item （本题6分）题目内容……
% 配图题：紧跟 \begin{tikzpicture}…\end{tikzpicture}
% 或 \includegraphics[width=\linewidth]{output/fig_xx.png}

\vspace*{4cm}

% ……更多解答题
\end{enumerate}

\end{multicols}

% 卷尾结束标记：A3/A4 等常规纸用 \vspace*{\fill} 推到底部；
% **8 开横向（370×260mm）等短边卷改用固定 \vspace*{2cm}**——
% \fill 会在短边方向撑爆剩余空间报 Overfull \vbox（实测 44pt，红线 11）
\vspace*{\fill}
\hfill {\small \textbf{—— 试卷到此结束，请认真检查 ——}}

\end{document}
```

**模板关键点（最容易错）：**
1. 选择题每个 `\item` 之后**紧跟**选项分栏，绝不能把 ABCD 写成一行；
   选项长（>8 字）改用两栏。**3 栏主体内嵌套 multicols 不稳定**
   （跨栏跨页时可能报错/错位），3 栏卷推荐用 tabular 方案：

   ```latex
   % 导言区定义一次（array 宏包）：
   \usepackage{array}
   \newcolumntype{C}{>{\centering\arraybackslash}p{0.24\linewidth}}
   \newcommand{\optab}[4]{%
     \par\noindent%
     \setlength{\tabcolsep}{0pt}%
     \begin{tabular*}{\linewidth}{@{\extracolsep{\fill}}C C C C@{}}
       A.~#1 & B.~#2 & C.~#3 & D.~#4 \\
     \end{tabular*}}

   % 题目内使用（选项内容长时拆成两行 tabular 各放两个选项）：
   \item 题目内容……（\quad）
   \optab{选项A}{选项B}{选项C}{选项D}
   ```

   2 栏卷嵌套 `multicols{4}` 一般可用；若编译出现 multicols 相关
   错误/错位，一律改用上面的 tabular 方案。
   **`\optab` 的两个关键点（均为实测）**：
   (a) **`\par\noindent` 必须保留**——选项表是宽 = \linewidth 的不可断行盒，
   若与题干文本同段（源码里只空一行 ≠ 分段），TeX 断行器宁可让
   「题干+选项」同一行 Overfull（超宽 = 题干宽度），也不换行产生
   badness 10000 的欠行；多栏卷时该行溢出画进栏沟/邻栏（红线 13）。
   `\par` 让选项真正另起一段：选项段独占一行、恰好满栏宽、零超宽。
   题干行短会报 Underfull (badness 10000)，属正常现象，不必处理
   （交付门槛只查 Overfull / Missing character）。
   (b) **`\tabcolsep=0` + `\fill` 胶水必须保留**：默认 \tabcolsep 下
   表宽 = 0.96\linewidth + 3×12pt，超 2/3 栏栏宽 5–8mm（实测）。
   含公式的选项必须 `$…$` 包裹（\optab 参数槽是文本模式，
   裸 `30^\circ` 会报 Missing $ inserted）。
2. 题干末尾留 `（\quad）` 答题空位；选项末尾**不加**标点
3. 填空题 `\underline{\hspace{…}}`（2–5cm），`itemsep=0pt`
4. 解答题每题标分值 + `\vspace*{…}`（小学 2–3cm / 初中 4–5cm / 高中 5–7cm）
5. 题号**全卷连续**（用 `start=N` 续接）
6. 配图紧跟题目，题干出现「如图」必须有图（tex_check 会查）

## 2. 英文试卷（article）

与中文卷同构，差异如下（其余结构、密封线逻辑、得分表完全一致）：

```latex
\documentclass[11pt]{article}
\usepackage{mathptmx}   % Times 系（Windows 自带）；缺失时删除本行退回默认字体
\usepackage[T1]{fontenc}
% \usepackage[paperwidth=…mm,paperheight=…mm,top=1.6cm,bottom=2.0cm,left=3.2cm,right=1.2cm]{geometry}
% 其余宏包、密封线 hook、fancyhdr、penalty 设置与中文卷完全相同
```

- 密封线竖排文字改英文：`\node[rotate=90] … {\small\sffamily Do not write inside the seal line};`
  个人信息行：School / Class / Name / ID
- 试卷头（第 1 页最前面）：`{\large \textbf{{SCHOOL}}}`（学校名称）+
  `{\LARGE \textbf{{TITLE}}}` + `{\normalsize {{PURPOSE}}}`（用途）+
  `{\small Full marks: {FULLMARKS} \quad Time allowed: {TIME} minutes}`
- 题型标题示例：`I. Multiple Choice (…points)` / `II. Fill in the Blanks` /
  `III. Free Response (…points)`
- 卷尾：`{\small \textbf{--- End of Paper. Please check your answers. ---}}`
  （英文卷 Times 字体没有 U+2014 破折号字形，直接用 `——` 会
  Missing character；`---` 会被 LaTeX 转成 Times 的 em dash）
- 填空横线：`\underline{\hspace{3cm}}` 相同

## 3. 答案卷（中文 / 英文同构）

独立 .tex 文件，**默认 A4 竖向（210×297mm）**、单栏；仅当用户明确要求
"跟随试卷纸张"时才与试卷同纸张同方向：

```latex
\documentclass[11pt]{ctexart}   % 英文卷用 article + mathptmx
\usepackage[paperwidth=210mm,paperheight=297mm,top=1.8cm,bottom=1.8cm,left=2.5cm,right=2.5cm]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{enumitem}
\usepackage{tikz}
\usetikzlibrary{calc,positioning,angles,quotes}
\setlength{\parindent}{0pt}
\setlength{\parskip}{4pt}

% 大题标题（\section*）：左对齐/两端对齐，不居中
\ctexset{section/format = {\Large\bfseries\raggedright}}

\begin{document}

\begin{center}
{\LARGE \textbf{{TITLE} 参考答案}}
\end{center}
\vspace{-6pt}
\hrule
\vspace{8pt}

\section*{一、选择题}
% 答案速查表（一行）+ 逐题解析
\begin{center}
\small 1–5：\textbf{A B C D A} \quad 6–10：\textbf{C D B A C}
\end{center}

\section*{二、填空题}
% 逐题：答案 + 关键步骤

\section*{三、解答题}
% 完整解题过程 + 一题多解 + 易错点

\hrule
\vspace{6pt}
\begin{center}
{\small \textbf{—— 答案完 ——}}
\end{center}

\end{document}
```

## 4. 答题卡（固定 A4 纵向）

**第三个输出产物：答题卡（学生用），固定 A4 纵向** 210×297mm，无论试卷
是 A3 横 / A4 横 / B5 等一律 A4 纵向。单栏，不需密封线（顶部放
学校/班级/姓名/学号填字段），供学生在客观题上涂/填答案。

```latex
% 答题卡.tex —— 固定 A4 纵向
\documentclass[11pt]{ctexart}
\usepackage[paperwidth=210mm,paperheight=297mm,top=1.8cm,bottom=1.5cm,
            left=2.2cm,right=2.2cm]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{enumitem}
\usepackage{multicol}
\setlength{\parindent}{0pt}
\setlength{\parskip}{3pt}

% 大题标题（\section*）：左对齐/两端对齐，不居中
\ctexset{section/format = {\Large\bfseries\raggedright}}

\pagestyle{plain}
\begin{document}
\begin{center}
{\LARGE \textbf{{TITLE} —— 答题卡}}

\vspace{6pt}
{\small 姓名：\underline{\hspace{3cm}} \quad
        班级：\underline{\hspace{3cm}} \quad 学号：\underline{\hspace{2.5cm}}}
\end{center}
\hrule
\vspace{6pt}

% 一、单项选择（1–34）：每题 A B C D 用方块/圆圈数字排版
\section*{一、单项选择题（1–34）}
% 用 compact 网格：每题  1.  A □  B □  C □  D □（□ 即 amssymb 的 \square）
\begin{itemize}[leftmargin=*,itemsep=2pt,topsep=0pt]
\item[1.]  A $\square$  B $\square$  C $\square$  D $\square$\quad
% …
\end{itemize}

\section*{二、多项选择题（35–42）}
\begin{itemize}[leftmargin=*]
\item[35.] A $\square$  B $\square$  C $\square$  D $\square$
% …
\end{itemize}

\section*{三、判断题（43–75）}
\begin{itemize}[leftmargin=*]
\item[43.] A $\square$  B $\square$
% …
\end{itemize}

\vspace*{\fill}
\hfill {\small \textbf{—— 答题卡完 ——}}
\end{document}
```

- 选择题：`A $\square$ B $\square$ C $\square$ D $\square$`（`amssymb` 的
  `\square` 在数学模式内使用；也可 TikZ 小方块）；可多横行多列紧凑排版
- 答题卡只含**题号 + 选项 + 填空空白**，**不含参考答案**（参考答案在 答案卷）
- 答题卡 A4 纵向固定 → geometry 直接写死 210×297mm，不引用试卷边距

> 注：若单科试卷体量小、用户无需独立答题卡（如用户说"不要答题卡"），
> 第 2 步输出开关「答题卡：生成 / 不生成（默认 生成）」

## 5. 编译命令

```bash
xelatex -interaction=nonstopmode 试卷.tex      # 跑两遍（交叉引用/栏平衡）
xelatex -interaction=nonstopmode 答案.tex
```

- 必须**零错误零警告**（`\missing character`、`Overfull \hbox` 超过栏宽、
  `Undefined control sequence` 都要修）
- 编译通过后清理 `.aux .log .out .toc` 临时文件
- MiKTeX 首次编译会按需下载宏包（已设 auto_install），耐心等待即可
