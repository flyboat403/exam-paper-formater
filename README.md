# exam-paper-formater — 试卷排版 Skill

把用户提供的题目内容（docx / html / txt / md / 粘贴文本）排版为
**可直接印刷的 PDF 试卷**（含独立答案卷与答题卡）。只排版，不出题。

> **来源声明**：本技能派生自两个 MIT 许可的上游项目——
> [elangan1997-cmyk/exam-prompt-skill](https://github.com/elangan1997-cmyk/exam-prompt-skill/)
> 与 [haitanghuaweimianTom/exam-paper-skill](https://github.com/haitanghuaweimianTom/exam-paper-skill/)，
> 在其基础上按"试卷排版"范围提取、整合并做了大量自定义扩展（正度8开纸张预设、
> 答题卡输出、12 条质量红线、双通道视觉核验、ctex 实测陷阱等，详见下文
> 「上游与许可」一节）。完整版权与许可说明见该节。

## 核心能力

- **版式三选**：纸张大小（A4 / A3 / B5 / A5 / **正度8开 260×370mm** / 自定义 mm）、
  方向（纵向 / 横向）、每页栏数（**1 / 2 / 3 三选一**）——生成前必问，未答全必追问
- **密封线**：虚线 + 圆圈 + 竖排「密封线内不得答题」，第 1 页学校/班级/姓名/学号
  （可关）
- **得分表**：按题型自适应列数，分值加总校验
- **理科公式/化学式**：数学公式、物理量、化学式/化学方程式（`H$_2$O`、
  `Cu$^{2+}$`、`\xrightarrow{点燃}`）的规范 LaTeX 写法 + 自动质检
- **理科图形**：TikZ 矢量图（几何/函数/电路/光路/受力/实验装置，含 12 项自检清单）
  + matplotlib 工具（统计图/概率树/韦恩图/流程图等 12 函数）+ 外部图片
- **三份输出**：试卷 + 独立答案卷（默认 A4 竖向）+ 答题卡（固定 A4 纵向）
- **中英文双模式**：中文卷 ctexart；纯英文卷 article（Times 字体，无 CJK 依赖）
- **双管线**：LaTeX（xelatex，印刷级）主管线；无 LaTeX 环境自动降级
  HTML/CSS + KaTeX + Edge 无头打印
- **双通道视觉核验**：有图像能力的模型渲染 PNG 目检；纯文本模型用
  pypdfium2 逐页文本提取核对（卷头/题号/得分表/缺字占位符），交付说明注明通道
- **输入白名单**：只收 `.docx` / `.html` / `.txt` / `.md` / 对话粘贴文本，
  其他格式（pdf/doc/图片）一律拒绝并给转换提示，禁止降级解析

## 目录结构

```
.（本仓库根目录 = 技能根目录）
├── SKILL.md              # 核心原则 + 十步流程 + 12 条质量红线
├── README.md
├── evals/
│   ├── evals.json        # 5 个测试 prompt + 断言
│   └── inputs/           # 5 份 .md 测试卷（数学期中/物理期末/化学单元/
│                         #   英文物理/计算机模拟）
├── scripts/
│   ├── check_env.py      # 环境检测 → 管线建议
│   ├── tex_check.py      # .tex 质量检查（纸张/栏数/密封线/配图/公式）
│   └── diagram_tools.py  # matplotlib 绘图工具（12 函数）
└── references/
    ├── intake.md         # 10 项采集清单（首部 4 项+版式 6 项）、识别→确认→提问三级处理
    ├── layout.md         # 纸张×方向×栏数映射、边距、栏宽、密封线、得分表
    ├── latex-templates.md# 中/英文试卷 + 答案卷 + 答题卡四套模板
    ├── question-format.md# 题型排版细则
    ├── formulas.md       # 公式/化学式规则
    ├── figures.md        # 绘图三路径 + 12 项自检
    ├── subject-notes.md  # 学科版式特殊需求
    └── html-fallback.md  # 无 LaTeX 回退管线
```

## 使用

在支持 skill 的 agent 环境中直接描述需求即可：

```
帮我把这份卷子排成 PDF：A4 纵向 2 栏，无密封线，带答案卷
（附上题目 markdown / docx）
```

或先说需求再补题目：

```
出一份九年级物理期末卷的排版版式：A3 横向 3 栏、密封线、
满分 100 分 100 分钟
```

agent 会先确认版式三选参数（纸张/方向/栏数），再排版、质检、编译、
视觉核验后交付 PDF。

## 依赖

| 依赖 | 用途 | 缺失时 |
|------|------|--------|
| XeLaTeX（MiKTeX/TeX Live，需 ctex/tikz/multicol 等宏包） | 主管线 | 自动降级 HTML 回退 |
| CJK 字体（Windows 宋体/黑体自动；Linux 需 Noto CJK） | 中文排版 | HTML 回退需 Noto CJK |
| Python 3.8+ + matplotlib | 绘图工具 | TikZ/外部图仍可用 |
| pypdfium2 或 poppler | PDF 视觉核验 | 跳过视觉核验（不建议） |
| Edge / Chromium | HTML 回退打印 | 仅主管线可用 |

Windows 无管理员权限安装 MiKTeX（本仓库验证过的方案）：

```bash
# 1. 下载 setup utility（miktex.org/download → Command-line installer）
#    或 CTAN: systems/win32/miktex/setup/windows-x64/
# 2. 下载包仓库 + 静默安装
miktexsetup_standalone --local-package-repository=E:\tools\miktex-pkgs --package-set=basic download
miktexsetup_standalone --quiet --local-package-repository=E:\tools\miktex-pkgs ^
    --portable=E:\tools\miktex --package-set=basic --use-registry=no install
# 3. 把 E:\tools\miktex\texmfs\install\miktex\bin\x64 加入用户 PATH
```

## 测试

`evals/evals.json` 含 5 个测试用例（A4 2 栏数学 / A3 3 栏物理密封线 /
B5 1 栏化学 / A4 2 栏英文物理 / A3 2 栏计算机模拟卷含答题卡），
输入卷均为 `.md`（位于 `evals/inputs/`）。

## 上游与许可（版权说明）

**本技能不是原创项目，而是以下两个 MIT 许可上游技能的派生作品**，
已按"试卷排版"范围从中提取、整合，并加入了大量自定义内容。
为遵守版权规范，在此逐项注明来源：

### 上游 1：[elangan1997-cmyk/exam-prompt-skill](https://github.com/elangan1997-cmyk/exam-prompt-skill/)

取自该项目的部分：

- A3 学校印刷版式规范（横向 3 栏 ≈120mm 栏宽、密封线占 2.2cm 左边距）
- 密封线视觉规范（虚线 + 小圆圈 + 竖排「密封线内不得答题」+ 第 1 页个人信息）
- 得分表结构约定（列数 = 1 + 大题数 + 1 总分、逐题分值加总 = 满分）
- 题型排版格式规范（选择题选项分栏、填空横线、解答题分值标注与答题空白）
- TikZ 理科绘图 12 项自检清单（角度弧线方向、直角标记、标签不重叠等）
- 出卷/排版自检工作流的思路

### 上游 2：[haitanghuaweimianTom/exam-paper-skill](https://github.com/haitanghuaweimianTom/exam-paper-skill/)

取自该项目的部分：

- 公式/化学式排版规范（`H$_2$O`、`Cu$^{2+}$`、`\xrightarrow{点燃}` 等写法与转义陷阱）
- matplotlib 绘图工具：`scripts/diagram_tools.py` **改编自其
  `tools/diagram_tools.py`**（本仓库扩展了 Windows CJK 字体列表）
- 质量检查思路：`scripts/tex_check.py` **改编自其 `tools/quality_check.py`**
  （由 markdown 检查扩展为 .tex 参数化检查：纸张/栏数/密封线/配图完整性/
  环境配平/公式闭合/控制字符/得分表覆盖）

### 本项目的自定义内容（原创部分）

在上述基础上，以下内容为本项目原创整合与扩展：

- 十步流程编排与「核心原则」三个 trade-off 框架、质量红线 12 条（每条附 why）
- 正度8开（260×370mm）纸张预设、短边卷 `\vspace*{\fill}` 陷阱（实测 44pt Overfull）
- 答题卡作为第 3 个输出产物（固定 A4 纵向）
- 输入白名单机制（docx/html/txt/md，非白名单拒绝 + 转换提示，禁止降级解析）
- 双通道视觉核验（图像目检 / 纯文本模型 pypdfium2 文本提取）
- `references/intake.md` 采集三级处理（识别→确认→提问）
- ctex/xeCJK 实测陷阱三条（带圈数字无字形、正文 `\rightarrow` 破坏字体切换、
  正文裸 `$` 破坏数学配对）
- 5 个 `.md` 测试卷（`evals/inputs/`）与断言

### 许可

两个上游项目均为 **MIT License**，本派生作品同样以 **MIT** 发布。
按 MIT 条款，保留上述来源与版权说明即为合规使用；
上游作者的版权主张不受本派生作品影响。
