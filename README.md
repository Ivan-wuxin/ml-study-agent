# 学习资料检索与问题分流 Agent

作者：李一帆 028123109 计算机科学与技术（个人项目）

## 运行

Python 3.10及以上；仅使用标准库，无需安装依赖或API密钥。

```sh
python agent.py --query "过拟合怎么办"
python evaluate.py
python agent.py --serve
```

浏览器打开 http://127.0.0.1:8765 ，输入问题后点击检索。停止服务使用Ctrl+C。

## 文件与复现

- agent.py：字符一元/二元特征、多项式朴素贝叶斯、TF-IDF检索、输入校验及本地HTTP服务。
- data.json：6个主题，30条分类训练问句、18条测试问句和6篇人工概括的知识摘要，包含官方来源链接。
- evaluate.py：增加6条域外测试；比较纯检索、分类路由加拒答、关闭拒答三种模式。输出逐条结果、数据哈希、环境与指标。
- results.json：实际运行记录；耗时受机器影响，其余指标确定性复现。
- demo_run.json：完整单次运行输入对应的处理轨迹与输出。

训练仅使用train字段；test字段仅用于评估。知识摘要是检索库，在推理前可用。数据由AI辅助编写，非真实学生日志；同源构造有措辞偏差，样本量不足以支持泛化结论。网页不上传数据，但也不持久化保存用户问题。

## 演示步骤

1. 展示“过拟合怎么办”的分类、检索摘要及来源。
2. 输入“帮我订火车票”，检查拒答；如果错误回答，解释字面匹配造成的错误。
3. 输入空字符串查看校验。
4. 打开results.json对比三种模式和失败样例。

## 组件及贡献

模型与检索算法为本项目Python实现，未使用外部Agent框架；测试流程复用了Anthropic webapp-testing skill。Python标准库（PSF许可证）提供JSON、HTTP、文件访问和数学运算。官方scikit-learn文档用于方法学习与资料摘要，并未调用其包或复制实现。详见报告附录的复用与核验说明。AI辅助选题、实现、构造测试和撰稿，学生须复跑并核对后提交，不应声称未经核验的个人原创。

## 提交

将此目录上传至本人GitHub仓库或云盘，把可访问链接补入报告；仓库地址为https://github.com/Ivan-wuxin/ml-study-agent。正式提交前按课程要求核对全部材料，并录制或截图网页完整运行过程。


## 异常处理与验证

运行 `python -m unittest discover -s . -p "test_*.py" -v` 执行七组测试。知识库缺失、损坏或字段不完整时返回error；检索工具异常时停止回答。医疗、金融、法律及隐私权限关键词触发review。关键词规则可能漏检或误拦，不能视为完整安全识别模型。修复知识库后需重启服务。

所有评估模式共享高影响规则；no_reject仅关闭相似度拒答。新版指标由results.json重新生成，不能沿用旧版的17/24。当前该模式为18/24，其余两种模式为23/24。

Windows可双击启动演示.bat（需要已安装Python且可从命令行调用），服务启动后浏览器访问页面。若端口被占用，请关闭此前启动的同一服务后重试。


## 扩展评估与改进版本

`python expanded_evaluate.py` 保留原集之外的12条验证、30条固定扩展测试、12条边界任务全部结果。改进同时采用英文术语映射、全局候选和验证集所选阈值0.08。原版14/30，纯检索15/30，联合改进26/30；12条边界中11条符合预期，混合主题任务仍失败。不能将联合改进收益分别归因于单个组件。

`python agent.py --serve --mode improved` 启动改进版本；默认仍为原版，便于复现原始截图及实验。`evidence/` 提供真实浏览器整页截图，包含问题、回答和执行轨迹。报告附录包含这些图片。所有新增样例仍是AI辅助人工构造，不能声称是真实用户测试。


## 实际复用的开源 skill

来源：https://github.com/anthropics/skills/tree/main/skills/webapp-testing 。Apache 2.0，main分支2026-11-19下载快照，逐文件SHA256见vendor/webapp-testing/UPSTREAM.json（提交号API限流，未记录不可核验提交号）。原始文件及许可证保持不变。

执行 `python verify_skill.py`，实际调用上游with_server.py，启动8766端口的真实Agent处理器，运行三项HTTP断言并退出。适配代码为skill_server.py、skill_smoke.py、verify_skill.py。skill作用是测试与复现，不是问答模型；Playwright部分未执行，截图由真实CUA浏览器操作获取。执行脚本会启动本地进程，勿将不可信内容作为服务命令。

为适应GitHub网页上传，vendor与截图另提供vendor.zip、evidence.zip；源码包中也保留完整目录。若从仓库直接运行verify_skill.py，它会解开随附vendor.zip。解压evidence.zip可查看演示图片。报告为report.pdf。正式提交PDF按本地提供的“学号_姓名_项目名称”版本命名。
