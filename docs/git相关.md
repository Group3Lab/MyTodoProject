# 概述

本文档说明 MyTodoProject 的 Git 使用规范与 PR 协作流程。

仓库地址：<https://github.com/Group3Lab/MyTodoProject>（组织：Group3Lab）

# 基本git操作与命令

## 0. 一次性配置（每台电脑只做一次，这个用ide自行处理就好）

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

`user.name` 会显示在提交记录里，请填真名或组内通用的 GitHub ID，方便组长辨认是谁提交的。

## 1. 拿到仓库

```bash
git clone https://github.com/Group3Lab/MyTodoProject.git
cd MyTodoProject
```

已经 clone 过就跳过这一步。

## 2. 查看状态与历史（用ide的工具就好）

```bash
git status              # 看当前在哪个分支、哪些文件改了
git branch              # 看本地分支，带 * 的是当前分支
git log --oneline -10   # 看最近 10 条提交
git diff                # 看还没暂存的改动内容
git diff --staged       # 看已经暂存、准备提交的改动内容
```

## 3. 提交改动（用ide的工具就好）

```bash
git add 文件名          # 暂存某一个文件（推荐，一次只提交一个文件的改动）
git add .               # 暂存当前目录所有改动
git commit -m "docs(git): 补全git使用文档"   # 提交
```

也可以暂存后不写 `-m`，此时会打开编辑器让你写较长的提交说明。

## 4. 撤销与回退（改错了用）（用ide的工具就好）

```bash
git restore 文件名              # 丢弃工作区里还没暂存的改动（危险，改了就回不来）
git restore --staged 文件名     # 只把它从暂存区拿出来，改动内容保留
git log --oneline               # 找到要回退到的提交号
git revert 提交号               # 生成一条"反向提交"来抵消某次提交（已推送过用这个，安全）
```

已经推送到远程的提交，不要用 `git reset --hard` 去改历史，用 `git revert`。

## 5. 与远程同步

```bash
git fetch origin                 # 只把远程最新情况拉下来，不动本地文件
git pull origin main             # 拉取并合并 main 的最新内容
git push -u origin 分支名        # 第一次推送自己的分支
git push                         # 之后推送当前分支
```

# pr协作流程
## 基本流程
1. 自己认领工单
2. 切回主分支
3. 开自己的分支
4. 在github上提交pr请求
5. 等待合并通过
   1. 遇到冲突时的处理
6. 等待组长确认完成情况关闭工单

## 具体命令

### 第 1 步：认领工单

在 GitHub 的 Issues 页面找到自己要做的工单，把自己设成 Assignee（负责人），工单标题就是这条任务的范围。不要两个人认领同一个工单。

### 第 2 步：切回主分支并更新

```bash
git switch main          # 切回主分支（旧版 git 用 git checkout main）
git pull origin main     # 保证自己是从最新的 main 开分支
```

**分支一定要从最新的 main 开**，否则后面几乎必然冲突。

### 第 3 步：开自己的分支

dts部分是你的称呼

```bash
git switch -c dts/简要说明
```

分支命名按组里的约定来，例如 `dts/补全git文档`。「dts」是组内统一前缀，「/」后面写这次要做什么，用中文或英文都可以。

### 第 4 步：写代码并提交（就是正常提交流程）

```bash
git status
git add 改动的文件
git commit -m "feat(task): 添加任务类与优先级校验"
git push -u origin dts/简要说明
```

写完一个文件就提交一次，提交信息格式见下面「git提交风格」。中途想同步 main 的新内容：

```bash
git fetch origin # 从远程下载最新代码
git merge origin/main # 从main合并到当前分支，自行解决合并冲突
```

### 第 5 步：在 GitHub 上发 PR

推送后 GitHub 会提示 Compare & pull request，点它，然后：

1. base 选 `main`，compare 选自己的分支
2. 标题写清楚做了什么，用自然语言风格即可
3. 描述里写：关联的工单（`Closes #工单号`）、改了什么，解决了什么问题
4. 创建 PR

之后按审查意见继续 `git add` / `git commit` / `git push`，PR 会自动更新，不需要重新开一个 PR。

## 遇到冲突时的处理
此时在github界面上会显示不给合并
参考第4步自行从main合并到当前分支

## 合并与收尾

- 仓库规定：合并必须经一人审查，审查通过后由审查人（管理员）点 Merge。
- 组里写权限足够自己点合并，所以**请自觉不要自己审查自己、自己点合并**。
- 组长确认工单内容真的完成后，关闭对应工单；不使用pr关联工单功能

## 常用排错

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `git push` 报 rejected / non-fast-forward | 远程有你没有的提交 | 先 `git pull`（或 `git fetch` + `git merge`），解决冲突后再 push |
| 提示 `Please tell me who you are` | 没配 user.name / user.email | 做第 0 步的全局配置 |
| PR 里混进了不该提交的文件 | `git add .` 加多了 | `git restore --staged 文件`，删掉后重新提交 |
| 推错分支 | 分支选错 | 在正确分支上重新 push，用错的分支直接删掉 |
| 不确定自己在哪 | 分支、状态混乱 | `git status` + `git branch`，先看清楚再动手 |

# git提交风格

格式固定为：

```
类型(模块): 描述
```

类型只用下面五种，不要自己造：

| 类型 | 含义 | 例子 |
| --- | --- | --- |
| `feat` | 新功能 | `feat(task): 完成任务类与清单管理` |
| `fix` | 修 bug | `fix(search): 修正完成率算成 0 的问题` |
| `docs` | 文档 | `docs(git): 补全git使用文档` |
| `test` | 自测 | `test(task): 补充添加任务的边界自测` |
| `chore` | 杂事 | `chore(repo): 添加.gitignore` |

示例：

- `feat(task): 完成任务类与清单管理`
- `fix(search): 修正完成率算成 0 的问题`

要求：

- 写完一个文件就提交一次，不要写「更新」「修改一下」这类没有信息量的描述。
- 是英文冒号，后面跟着空格
- 不要提交大文件 （会在git忽略项拦住但是还是注意下）
- 提交不能集中在最后一天。
- 描述用中文写清楚「做了什么」，一句话讲明白，不要在结尾加句号。
