import dropbox
import os
dbx = dropbox.Dropbox('ci5XgAwUieAAAAAAAAAB2zbtk_ued0ayJ6hqkJn5Fahh6hBWDjKuwKkOZXGUYxTq')


# with open('/Users/guanli/Dropbox/records/RLRtree/insert/H_uniform_160000_1_2_DQN_null_10000.txt',"rb") as f:
#     dbx.files_upload(f.read() ,"test.txt")

def upload(source_name, target_path):

    with open(source_name, "rb") as f:
        dbx.files_upload(f.read(), target_path)


if __name__ == '__main__':
    path = "/Users/guanli/Dropbox/records/RLRtree"  # 文件夹目录
    files = os.listdir(path)  # 得到文件夹下的所有文件名称
    s = []
    for file in files:  # 遍历文件夹
        print(file)
        # if not os.path.isdir(file):  # 判断是否是文件夹，不是文件夹才打开
        #
        #     f = open(path + "/" + file);  # 打开文件
        #     iter_f = iter(f);  # 创建迭代器
        #     str = ""
        #     for line in iter_f:  # 遍历文件，一行行遍历，读取文本
        #         str = str + line
        #     s.append(str)  # 每个文件的文本存到list中
    print(s)
