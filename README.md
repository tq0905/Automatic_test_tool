# Automatic_test_tool
本项目是对于论文**"Stay professional and efficient: automatically generate titles for your bug reports"**中提出工具的具体理解。

### 1.项目结构：

- "iTAPE工具报告.pdf" ：阐述了对于工具的理解，包括它的难点、算法、模块实现、数据流通等

- "自动化 presentation.pptx"

- iTAPE文件夹：工具的代码
  - 0-0-preprocess.py：数据预处理
  - 0-1-refine_and_deal_human_named_token.py：运用3个启发式规则过滤样本并在低频令牌前后加上tag
  - 0-2-export_txt_data.py：生成适用于模型训练的6个TXT文件，即分别用于训练、验证、测试的body、title文件
  - 1-build.sh：预处理，构建一个scr-tgt对齐的数据集合一个词表
  - 2-train.sh：训练模型（有使用复制机制）
  - 3-test.sh：用训练完成的模型对于测试集body生成title的TXT文件

### 2.运行要求

1. 环境要求

   ```
   opennmt-py >= 1.0.0（建议使用1.2.0，最好不要太高）
   pytorch >= 1.3.0
   nltk >= 3.4.5
   ```

   opennmt-py参考链接：https://pypi.org/project/OpenNMT-py/1.2.0/

2. 运行顺序：按照代码文件序号依次运行（即0-0 ---> 0-1 ---> 0-2 --->1 --->2 --->3）

3. 如果使用cpu计算，pytorch要选cpu模型，shell脚本里关于gpu的设置都需要删除；如果使用gpu计算，则所有的设置都需为gpu
