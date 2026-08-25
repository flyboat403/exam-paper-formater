# 学科版式特殊需求

> 只收录**排版相关**的学科差异。知识范围、题型分值、超纲红线属于命题范畴，
> 不在本 skill 内（由用户提供题目时一并提供）。

## 常见图类型速查（决定用 TikZ 还是 matplotlib）

| 学科 | 常见图 | 推荐路径 |
|------|--------|---------|
| 数学 | 几何图形、函数图像、三视图、统计图 | 几何/函数 → TikZ；条形/折线/扇形/箱线 → `diagram_tools.py` |
| 物理 | 电路图、光路图、受力分析、实验装置图、运动图 | 电路/光路/受力 → TikZ；复杂装置 → matplotlib 或外部图 |
| 化学 | 实验装置图、工业流程图 | TikZ（节点+箭头） |
| 生物 | 细胞结构、遗传图解、生态系统图、代谢途径 | TikZ 框图 |
| 地理 | 等高线/等值线、气候图、简图 | matplotlib（等值线）/ TikZ（简图） |
| 语文 | 无 | — |
| 英语 | 无（听力说明除外） | — |

## 特殊排版需求

- **作文（语文）**：预留方格纸区域。小学 300–500 字、初中 600 字、高中 800 字以上。
  LaTeX 实现：`\vspace*{…}` 或方格表格（每行 20 格 × 行数 = 字数）：

  ```latex
  \begin{center}\small
  % 20 列 × 10 行 = 200 字；按字数调整行数
  \newcolumntype{G}{>{\centering\arraybackslash}p{0.6cm}}
  \setlength{\tabcolsep}{0pt}
  \renewcommand{\arraystretch}{1.3}
  \begin{tabular}{|*{20}{G}|}
  \hline
  \multirow{10}{*}{\parbox{0.6cm}{\centering 作\\文\\区}} & \multicolumn{19}{c|}{\vspace{0.6cm}}\\
  \cline{2-20} \multicolumn{20}{|c|}{\vspace{0.6cm}}\\
  \cline{2-20} \multicolumn{20}{|c|}{\vspace{0.6cm}}\\
  \cline{2-20} \multicolumn{20}{|c|}{\vspace{0.6cm}}\\
  \cline{2-20} \multicolumn{20}{|c|}{\vspace{0.6cm}}\\
  \hline
  \end{tabular}
  \end{center}
  ```

  （行数按字数 ÷ 20 取整补齐；`array`、`multirow`、`tabularx` 宏包需加入导言区）

- **小学低年级看拼音写词语**：田字格区域（同上方法，12pt 字号 + 更大方格）
- **英语听力**：试卷中只标注「听力部分（另附录音）」/ "Listening section
  (audio provided separately)"，**不排版听力文本**
- **小学低年级卷**：字号 12pt，减少题目密度，答题空白加大
- **理科实验题**（物/化/生）：装置图必须绘制（TikZ/matplotlib），
  无法绘制的标注「见答题卡」—— 不允许只有文字没有图
- **高中多选**：题干后注明评分规则（见 question-format.md）

## 学段与版式

| 学段 | 建议字号 | 建议栏数 | 答题空白（解答题） |
|------|---------|---------|------------------|
| 小学低段（1–2） | 12pt | 1–2 | 2–3cm |
| 小学高段（3–6） | 11pt | 2 | 2–3cm |
| 初中 | 11pt | 2–3 | 4–5cm |
| 高中 | 11pt | 2–3 | 5–7cm |

（栏数以**用户选择**为准，本表仅作建议参考。）
