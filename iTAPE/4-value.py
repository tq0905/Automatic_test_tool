# coding:utf8
from rouge import Rouge
#获得预测的title列表a1
f=open(r'testout/iTAPE_step_25000_minlen8.txt','r',encoding='utf-8')
a=list(f)
a1=[]
for per in a:
    per=per.strip('\n')#去掉读取txt文件获得的换行符
    a1.append(per)
f.close()

#获得真实的title列表b1
f=open(r'data/title.train.txt','r',encoding='utf-8')
b=list(f)
b1=[]
for per in b:
    per=per.strip('\n')#去掉读取txt文件获得的换行符
    b1.append(per)
f.close()

#获得测试集的平均Rouge-1, Rouge-2, Rouge-L的F1评分
rouge = Rouge()
rouge_score = rouge.get_scores(a1, b1)
average_1=0
average_2=0
average_l=0
for item in rouge_score:#rouge_score的结构为：[{xxx},{xxx},...{'rouge-1':{'r':...,'p':...,'f':...}]
    average_1+=item["rouge-1"]['f']
    average_2 += item["rouge-2"]['f']
    average_l += item["rouge-l"]['f']
average_1=average_1/len(rouge_score)
average_2=average_2/len(rouge_score)
average_l=average_l/len(rouge_score)
print(average_1)
print(average_2)
print(average_l)
