# 理科图形绘制（数学 / 物理 / 化学 / 生物 / 地理）

> 目标：每张图印刷级清晰、数学关系精确、宽度适配栏宽（见 layout.md 栏宽表）。
> 三条路径按复杂度选择：**TikZ（矢量，首选）→ matplotlib 工具（复杂图）→ 外部图片**。

## 0. 配图清单（动手前必做）

写任何一道题**之前**，先列出本卷所有需要配图的题号：

```
【配图清单】
第X题 — 几何图形（三角形/圆/函数图像/立体图形）→ TikZ
第Y题 — 统计图（条形/折线/扇形）→ diagram_tools.py
第Z题 — 电路图 / 光路图 / 受力图 → TikZ
…
```

每写完一道题立即对照清单核图：题干出现「如图 / 见右图 / 如图所示 / 函数图像 /
统计图 / 装置图 / 电路图 / 光路图」（英文卷 as shown in the figure 等）
**则该题必须有图，无图禁止输出**（tex_check.py 会逐题检查）。
反向检查：每段 TikZ 代码必须被某道题引用，孤立图要删掉或补题干。

## 1. TikZ（矢量，印刷级，首选）

模板已 `\usetikzlibrary{calc,positioning,angles,quotes,intersections,through,
arrows.meta,patterns}`。

### ctex 环境下的已知陷阱（实测）

- **不要写 `every node/.style={\scriptsize}`**：与 ctex 组合会触发
  `TeX capacity exceeded [input stack size]`。需要小字标签时逐个
  `\node[\scriptsize]` 或 `\tikzset{font=\scriptsize}`（局部 scope）
- **`\bullet` 等符号在 ctex 下必须数学模式**：写 `{$\bullet$}`，
  直接 `\node{\bullet}` 会报 Missing $
- 中文标签：`\node{\small 学校}` 可以直接写中文（ctex 已处理字体）

### 数学图 —— 每张图必须逐条通过 12 项自检

**核心原则：数学驱动画图，每条线段/角度都从数学关系计算坐标。**

1. 角度弧线方向：必须 `start_angle < end_angle`（TikZ arc 逆时针，从小区间画到大区间；
   `arc[start angle=180, end angle=150]` 这种 start>end 立即改）
2. 角度标签：极坐标定位 `($(顶点)+(弧中点角度:半径+0.2)$)`，禁止手写 x/y 偏移
3. 直角标记：向量加法 `($(r1)+(r2)-(顶点)$)`，禁止手写 `++(0.2,0)` 固定偏移
4. 弦垂直直径：圆中垂径定理图，弦的 x 坐标恒定（竖直弦）
5. 切线垂直半径：`($(O)!0.5!-90:(C)$)` 语法
6. 垂足/投影点：`($(A)!(D)!(C)$)` 自动计算，禁止手写估计坐标
7. 仰角图视线：从仪器眼睛高度点（Aeye/Beye）画出，不能从地面画
8. 标签不重叠：每个 node 用 above/below/left/right 明确指定
9. 函数定义域：双曲线避开 x=0 奇点，抛物线覆盖所有关键点
10. 点坐标有数学依据：凭感觉写的坐标必须重写，注释中标注计算过程
11. 三视图/选项图：`scale ≥ 0.4`，印刷后至少 1.5cm 宽
12. 栏宽内可读：图宽 ≤ 90% 栏宽；栏宽 ≥100mm 时 scale 0.4–0.7，
    标签 `\scriptsize`（栏宽 <60mm 时 scale ≤ 0.4 或建议减栏）

示例：

```latex
% 直角三角形（A 处直角）
\begin{tikzpicture}[scale=0.6]
  \coordinate (A) at (0,0);
  \coordinate (B) at (4,0);
  \coordinate (C) at (4,3);
  \draw (A) -- (B) -- (C) -- cycle;
  % 直角标记：沿两边各取 0.2 单位小偏移点，向量加法 (r1)+(r2)-(顶点)
  \coordinate (r1) at ($(A)!0.25!(B)$);
  \coordinate (r2) at ($(A)!0.25!(C)$);
  \draw (r1) -- ($(r1)+(r2)-(A)$) -- (r2);
  \node[below left] at (A) {A};
  \node[below right] at (B) {B};
  \node[above right] at (C) {C};
\end{tikzpicture}
```

```latex
% 带箭头的函数关系 / 树形图
\begin{tikzpicture}
  \node {Root}
    child {node {Left}}
    child {node {Right}};
\end{tikzpicture}
```

### 物理图

- **电路图**：直线 + 节点；元件符号标准（电池长线为正极、电阻用矩形/锯齿、
  开关断开/闭合明确）；`arrows.meta` 标电流方向
- **光路图**：实线 = 光线（带箭头），虚线 = 法线，角度弧线标注入射/折射/反射角
- **力学图**：箭头表示力，标注力的大小和方向，作用点精确（重心/接触点）
- **实验装置图**：简化绘制，关键部件标注清楚（烧杯/温度计/弹簧秤等可组合圆+矩形+直线）

### 化学图

- 实验装置图：简化仪器外形（试管/集气瓶/导管），节点标注，连接关系正确
- 工业流程图：矩形框 + 箭头，标注物质名称与操作条件（过滤/蒸发/通电…）
- 分子/晶胞示意：`pattern` 库可画点阵

### 生物 / 地理

- 生物结构图：示意框图 + 箭头指引线 + 文字标注
- 遗传图解：矩形框 + 连接线表示亲代/子代（P → F1 → F2）
- 地理简图：简化轮廓 + 标注，不要求精确经纬度；等值线数值合理

## 2. matplotlib 工具（复杂图：坐标/函数/统计/概率/流程）

`scripts/diagram_tools.py` 提供 12 个现成函数，输出 PNG（150 DPI，已含
Windows 中文字体适配）：

| 函数 | 用途 | 关键参数 |
|------|------|---------|
| `coordinate_system` | 平面直角坐标系 + 点 + 线段 | points, segments, labels |
| `function_plot` | 函数图像 | func, x_range, title（支持 `$y=x^2$`） |
| `number_line` | 数轴 + 标记点 | points, labels |
| `force_diagram` | 受力分析图 | forces=[{x,y,label,color}] |
| `geometry_triangle` | 三角形（按三边长） | a, b, c |
| `bar_chart` | 条形图 | categories, values |
| `line_chart` | 折线图 | x, y |
| `scatter_plot` | 散点图 | x, y |
| `box_plot` | 箱线图 | data, labels |
| `probability_tree` | 概率树（两层） | branches=[{label,prob,children}] |
| `venn_diagram` | 两集合韦恩图 | labels={A,B,A_only,B_only,intersection} |
| `flowchart` | 流程图（标准符号） | nodes={名:{pos,type}}, edges=[(a,b,标注)] |

flowchart 节点 type：`start/end`（圆角）、`process`（矩形）、
`decision`（菱形）、`io`（平行四边形）。

用法（从生成脚本调用，输出到 `output/` 目录）：

```python
import sys
sys.path.insert(0, r"{SKILL_ROOT}\scripts")   # SKILL_ROOT = 技能根目录（SKILL.md 所在），见 SKILL.md「路径约定」
from diagram_tools import coordinate_system, function_plot, force_diagram

coordinate_system(points=[(1, 2), (-2, -1)], segments=[((0, 0), (1, 2))],
                  labels={0: "P", 1: "Q"}, output_path="output/fig_q5.png")
function_plot(lambda x: x ** 2, (-3, 3), output_path="output/fig_q6.png",
              title=r"$y = x^2$")
force_diagram([{"x": 2, "y": 1, "label": "F$_1$", "color": "red"}],
              output_path="output/fig_q9.png")
```

然后嵌入 .tex（**宽度适配栏宽**）：

```latex
\begin{center}
\includegraphics[width=\linewidth]{output/fig_q5.png}   % 栏宽 120mm 时可写 width=110mm
\end{center}
```

`width=\linewidth` 在多栏里自动等于当前栏宽，是最安全的写法；
图本身很宽时用 `width=0.9\linewidth` 留白。

## 3. 外部图片

- 用户提供的图：`\includegraphics[width=…]{path}`，保持原始比例
- 分辨率 ≥ 150 DPI（打印）；过小的图放大后发糊，宁可 TikZ 重画
- 路径用相对 .tex 文件的路径（tex_check 会校验文件存在）

## 4. 图形质量自检（编译前，逐张逐条过）

- [ ] 配图清单上每题都有图？（题干「如图」→ 有 tikzpicture/includegraphics）
- [ ] 每张 TikZ 图过了 12 项自检（数学）/ 物理/化学/生物/地理对应项？
- [ ] 图宽 ≤ 90% 栏宽，不超出栏？
- [ ] 标签无重叠、无被裁切（`Overfull \hbox` 警告 = 超宽，修）
- [ ] 外部 PNG 文件存在且 ≥150 DPI？
- [ ] 每段图都有题干引用（无孤立图）？

**任何一条不通过 = 回去重画/修正，不允许带病编译输出。**
