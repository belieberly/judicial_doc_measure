#读取指定文书
if __name__=='__main__':
    test_prefix = 'G:/judicial_data/民事一审案件.tar/民事一审案件'
    file = open(test_prefix+'msys_all/100024.xml','r',encoding = 'utf-8')
    for line in file.readlines():
        print(line)