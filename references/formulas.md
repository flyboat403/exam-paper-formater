# 公式、化学式与符号排版规则

> 适用学科：数学 / 物理 / 化学等理科（英文卷同样适用）。
> 目标：XeLaTeX 编译零 `Missing character` / `Undefined control sequence` 警告。

## 1. 基本原则

- 一切公式、希腊字母、运算符、上下标一律用 **LaTeX 数学模式**
  （`$…$` 行内，`$$…$$` 独立显示）
- 常用命令：`\alpha \beta \gamma \theta \sigma \mu \pi \sum \int \prod
  \frac \sqrt \lim \infty \pm \times \div \leq \geq \neq \approx \vec`
- 数学模式内出现中文：`\text{…}`（英文卷无此问题）
- 中文标点（，。；：）放在 `$…$` **外面**
- 表格单元格里的公式必须**完整包裹** `$…$`，每个单元格各自闭合
- 禁止相邻数学模式（`$x$$y$`、`Cu$^2$$^+$`）→ 合并成一个

## 2. 化学式 / 化学方程式（高频错点）

**上下标必须合并写在一个 `$…$` 内：**

| 错误 | 正确 |
|------|------|
| `Cu$^2$$^+$` | `Cu$^{2+}$` |
| `CO$_3$^{2-}$` | `CO$_3^{2-}$` |
| H₂O（Unicode 下标） | `H$_2$O` |
| x²、m/s² | `$x^2$`、`m/s$^2$` |

常用示例：

```latex
H$_2$SO$_4$      Na$_2$CO$_3$      KMnO$_4$
离子：Cu$^{2+}$、SO$_4^{2-}$、NH$_4^+$
条件：$-\xrightarrow{\text{点燃}}$、$\xrightarrow{\Delta}$
2H$_2$ + O$_2$ $\xrightarrow{\text{点燃}}$ 2H$_2$O
气态/沉淀：CO$_2\uparrow$、BaSO$_4\downarrow$
```

- 反应条件放箭头上方：`$-\xrightarrow{\text{点燃}}$`；加热用 `\Delta`
- 生成气体/沉淀：`\uparrow` / `\downarrow`
- 元素符号、化学式在正文中也应 `$…$` 包裹（如 把 `Fe` 写成 `$\text{Fe}$` 或 `Fe` 均可，
  但**下标必须数学模式**：`Fe$_2$O$_3$`）

## 3. 物理

- 单位：`m/s$^2$`、`kg·m/s$^2$`、`J`、`W`、`Ω`（`\Omega`）
- 矢量：`\vec{v}`、`\vec{F}`
- 常量：`g = 9.8\,\text{N/kg}`（`\,` 细空格）
- 数量级：`×10$^n$`

## 4. 数学

```latex
$$\mathbf{A} = \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix}$$

$$f(x) = \begin{cases} x, & x \geq 0 \\ 0, & x < 0 \end{cases}$$

$x^2 + 2x - 3 = 0$      $f(x) = \sin x$      $\{a_n\}$      $S_{10}$
```

## 5. Unicode 残留（tex_check 会扫描告警）

源文档里的 Unicode 上下标（² ³ ₐ–ₜ）、逻辑符号（∧ ∨ ¬ ↔ ∀ ∃）、
比较符（≤ ≥ ≠ ≈）一律转 LaTeX：上下标进 `$^n$` / `$_n$`，逻辑/比较符用
`\land \lor \neg \leftrightarrow \forall \exists \leq \geq \neq \approx`。
完整映射表见 `scripts/tex_check.py` 的 `UNICODE_LOGIC` / `SUBSUP_RE`，
以脚本扫描结果为准——tex_check 报 WARNING 即逐条转换。

**箭头特殊**：`\rightarrow`（U+2192）**仅限数学公式内部**使用；正文流程箭头
（"步骤 A → 步骤 B"）必须用全角 `→` 文本字符——实测 math mode 的
`\rightarrow` 在 CJK 邻接处破坏 xeCJK 字体切换，后续中文满屏
Missing character（见 question-format.md §7）。

## 6. Python 生成 .tex 的转义陷阱

用 Python 字符串拼装 .tex 内容时：

- **必须用 raw string**（`r"…"` / `r"""…"""`）。普通字符串里
  `\f \r \t \n \a \b \v` 会被解释成控制字符，破坏
  `\forall \rightarrow \theta \text \alpha \beta \frac \varepsilon` 等命令
  （表现为编译时 `Missing $ inserted`、图形乱码）
- raw string 里的字面 `\n` 是「反斜杠+n」两个字符，不是换行；
  若内容里确实写了字面 `\n` 需要变换行，先保护再替换：

```python
content = content.replace('\\newpage', '__NEWPAGE__')
content = content.replace('\\neq', '__NEQ__')
content = content.replace('\\neg', '__NEG__')
content = content.replace('\\n', '\n')
content = content.replace('__NEWPAGE__', '\\newpage')
content = content.replace('__NEQ__', '\\neq')
content = content.replace('__NEG__', '\\neg')
```

（凡是以 `\n` 开头的 LaTeX 命令都要这样保护。）
- 若不用 raw string，则每个反斜杠写两遍：`\\forall`
- tex_check.py 会检测控制字符（ERROR 级）

## 7. 常见错误速查

| 现象 | 原因 | 修复 |
|------|------|------|
| 化学式显示方块 | Unicode 下标未转换 | 转 `$_n$` / `$^n$` |
| `Cu$^2$$^+$` 分裂显示 | 相邻数学模式 | 合并 `Cu$^{2+}$` |
| `Missing character in font` | 数学模式内有中文 | `\text{…}` |
| `Missing $ inserted` | 普通字符串 `\f` 破坏 `\forall` | raw string |
| 表格公式错位 | 单元格公式未闭合 | 每个单元格 `$…$` 完整 |
| 中文引号渲染怪异 | 用了 ASCII `"` | 改 `“”` |
| 孤行/顶行 | 未设 penalty | 模板已含 `\widowpenalty=10000` 等 |
| 右端溢出 | 中文长句 | `\emergencystretch=3em`（模板已含） |
| 答案卷正文满屏 Missing character（中文落 lmroman） | ① 带圈数字 / `\rightarrow` CJK 邻接 / 裸 `$` 破坏数学配对 | 见 question-format.md §7 表格三行（均为实测） |
