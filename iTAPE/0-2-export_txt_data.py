import json, nltk, random, re

def main():
    #导出数据到txt文件中
    with open("data/good_issues.json") as f:
        valid_issues_train, valid_issues_val, valid_issues_test = json.load(f)
    with open("data/body.train.txt", "w",encoding='utf-8') as fbody, open("data/title.train.txt", "w",encoding='utf-8') as ftitle:
        bodies = [x['body'] + "\n" for x in valid_issues_train]
        titles = [x['title'] + "\n" for x in valid_issues_train]
        fbody.writelines(bodies)
        ftitle.writelines(titles)
    with open("data/body.valid.txt", "w",encoding='utf-8') as fbody, open("data/title.valid.txt", "w",encoding='utf-8') as ftitle:
        bodies = [x['body'] + "\n" for x in valid_issues_val]
        titles = [x['title'] + "\n" for x in valid_issues_val]
        fbody.writelines(bodies)
        ftitle.writelines(titles)
    with open("data/body.test.txt", "w",encoding='utf-8') as fbody, open("data/title.test.txt", "w",encoding='utf-8') as ftitle:
        bodies = [x['body'] + "\n" for x in valid_issues_test]
        titles = [x['title'] + "\n" for x in valid_issues_test]
        fbody.writelines(bodies)
        ftitle.writelines(titles)

if __name__ == "__main__":
    main()