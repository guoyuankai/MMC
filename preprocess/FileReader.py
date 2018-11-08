import os
import pickle
class FileReader:
    def __init__(self, train_file,test_file,entity):
        self.train_file=train_file
        self.test_file=test_file
        self.entity_dict=self.init_entity_dict(entity)


    def init_entity_dict(self,entity):
        label=['B-','I-','E-','U-']
        entity_dict={}
        entity_dict['O']=0
        index=1
        for i in entity:
            for j in label:
                entity_dict[j+i]=index
                index+=1
        return entity_dict


    def read_train(self):
        filelist=[]
        raw_train_x=[]
        raw_train_y=[]
        for root, dirs, files in os.walk(self.train_file):
            filelist=files #当前路径下所有非目录子文
        for i in filelist:
            file=open(self.train_file+'/'+i,'r',encoding='utf-8')
            suffix=i.split('.')[1]
            if(suffix=='ann'):
                doc_ans=[]
                for i in file:
                    token=i.split('\t')
                    number=token[0]
                    entity_type=token[1]
                    entity=token[2].replace('\n','')
                    doc_ans.append([number,entity_type,entity])
                raw_train_y.append(doc_ans)
            else:
                train_doc=''
                for i in file:
                    train_doc+=i
                train_doc=train_doc.replace('\n','@')
                raw_train_x.append(train_doc)
        return raw_train_x,raw_train_y


    def creat_label_seq(self,length):
        label=[]
        for i in range(length):
            label.append('O')
        return label

    def fill_lable_helper(self,start,end,label_doc,entity_type):
        if(end-start==1):
            label_doc[start]='U-'+entity_type
        else:
            label_doc[start]='B-'+entity_type

            i=start+1
            while(i<end-1):
                label_doc[i]='I-'+entity_type
                i+=1
            label_doc[end-1]='E-'+entity_type
        return label_doc


    def fill_lable(self,label_doc,entity_info):
        entity_name=entity_info[2]
        if(entity_info[1].find(";")==-1):
            temp=entity_info[1].split(' ')
            entity_type,start_pos,end_pos=temp

            label_doc=FileReader.fill_lable_helper(self,start=int(start_pos),end=int(end_pos),
                                         label_doc=label_doc,entity_type=entity_type)
            return label_doc
        else:
            temp=entity_info[1].split(";")
            token_0=temp[0].split(' ')
            token_1=temp[1].split(' ')
            entity_type,start_pos_1,end_pos_1=token_0
            start_pos_2,end_pos_2=token_1
            label_doc=FileReader.fill_lable_helper(self,start=int(start_pos_1),end=int(end_pos_1),
                                         label_doc=label_doc,entity_type=entity_type)
            label_doc=FileReader.fill_lable_helper(self,start=int(start_pos_2),end=int(end_pos_2),
                                         label_doc=label_doc,entity_type=entity_type)
            return label_doc

    def produce_y(self,raw_train_x,raw_train_y):#生成对应标记
        train_y=[]
        train_x=[]
        for i,row in enumerate(raw_train_x):
            list1 = list(row)
            train_x.append(list1)
            label_doc=FileReader.creat_label_seq(self,len(list1))
            for j,infor in enumerate(raw_train_y[i]):
                label_doc=FileReader.fill_lable(self,label_doc,infor)
            train_y.append(label_doc)

        return train_x,train_y


    def wirte_file(self,filename,target):#全部实体集合
        file=open(filename,'w',encoding='utf-8')
        for i in range(len(target)):
            for j in range(len(target[i])):
                file.writelines(target[i][j][0]+'\t'+target[i][j][1]+'\t'+target[i][j][2])
                file.writelines('\n')
            file.writelines('\n')
        file.close()

    def wirte_all(self,train_x,train_y): #一次一行写入文件
        file=open('../resource/row_label.txt','w',encoding='utf-8')
        for i in range(len(train_x)):
            for j in range(len(train_x[i])):
                file.writelines(train_x[i][j]+'\t'+train_y[i][j]+'\n')
            file.writelines('\n')
            file.writelines('------------- document '+str(i)+'--------------')
            file.writelines('\n')
        file.close()


    def fix_entity(self,raw_train_y,train_x,train_y): #合并因为换行分割开的实体 以及删除原有的换行
        for i in range(len(raw_train_y)):
            delte_count=0 #删除换行的个数 偏移量
            for j in range(len(raw_train_y[i])):
                entity_info=raw_train_y[i][j]
                if(entity_info[1].find(";")!=-1):
                    temp=entity_info[1].split(";")
                    token_0=temp[0].split(' ')
                    token_1=temp[1].split(' ')
                    entity_type,start_pos_1,end_pos_1=token_0
                    start_pos_2,end_pos_2=token_1
                    true_strat=int(start_pos_1)-delte_count
                    true_end=int(end_pos_2)-delte_count
                    enter_pos=int(end_pos_1)-delte_count
                    del (train_x[i][int(enter_pos)])
                    del (train_y[i][int(enter_pos)])#删除换行
                    true_end=true_end-1
                    delte_count+=1
                    train_y[i]=FileReader.fill_lable_helper(self,true_strat,true_end,train_y[i],entity_type)

        return train_x,train_y

    def delete_char(self,train_x,train_y):
        for index_i,row in enumerate(train_x):
            for index_j,word in enumerate(row):
                if(word=='@'):
                    del train_x[index_i][index_j]
                    del train_y[index_i][index_j]
        return train_x,train_y

    def save_file(self,train_x,name_x):
        f=open('../resource/'+name_x,'wb')
        pickle.dump(train_x,f)
        f.close()

if __name__ == '__main__':
    entity=['Disease','Test','Test_Value','Symptom','Drug','Anatomy','Method','Frequency','Duration','SideEff','Operation','Reason']
    myreader=FileReader(train_file='../resource/ruijin_round1_train2_20181022',
                        test_file='../resource/ruijin_round1_test_a_20181022',
                        entity=entity)
    raw_train_x,raw_train_y=myreader.read_train()#原始的训练文档集合，对应的文档实体信息集合
    myreader.wirte_file('all_label_set.txt',target=raw_train_y)
    train_x,train_y=myreader.produce_y(raw_train_x,raw_train_y)#文本按字分割的集合，对应文档的标注集合

    train_x,train_y=myreader.fix_entity(raw_train_y,train_x,train_y)

    train_x,train_y=myreader.delete_char(train_x,train_y)
    myreader.wirte_all(train_x,train_y)
    myreader.save_file(train_x,'train_doc_x.pkl')
    myreader.save_file(train_y,'train_doc_y.pkl')#未分句的数据



