import pickle
import sys
class Perprocess:
    def __init__(self,sentence_length):
        self.sentence_length=sentence_length

    def load_pkl(self,name):
        file=open('../resource/'+name,'rb')
        f=pickle.load(file)
        file.close()
        return f

    def evaluate(self,trainset):
        min_length=sys.maxsize
        max_length=0
        avg_length=0
        num=0
        for i,row in enumerate(trainset):
            l=len(row)
            if(l>=200):
                num+=1
                #print(''.join(row))
            min_length=min(l,min_length)
            max_length=max(l,max_length)
            avg_length+=l
        print('sentence number is ',len(trainset))
        print('length lager than 200 number is ',num)
        print("sentence max length is ",max_length)
        print("sentence min length is ",min_length)
        print("sentence avg length is ",avg_length/len(trainset))

    def sentence_level(self,train_doc_x,train_doc_y):
        doc_sentence_matrix=[]
        train_sentence_x=[]
        train_sentence_y=[]
        for i,row in enumerate(train_doc_x):
            last_pos=0
            for j,word in enumerate(row):
                if(word=='。'):
                        train_sentence_x.append(row[last_pos:j])
                        train_sentence_y.append(train_doc_y[i][last_pos:j])
                        last_pos=j+1
                        doc_sentence_matrix.append(i)


        #拆分长句子的，合并短句子
        for i in range(len(train_sentence_x)):
            row=train_sentence_x[i]
            row_y=train_sentence_y[i]
            if(len(row)>200):
                last_pos=0
                for j in range(len(row)):
                    word=row[j]
                    if(j-last_pos>=50 and (word==',' or word==';'or word==' 'or word=='、')):
                        del train_sentence_x[i]
                        del train_sentence_y[i]
                        train_sentence_x.insert(i,row[last_pos:j])
                        train_sentence_y.insert(i,row_y[last_pos:j])

                        train_sentence_x.insert(i+1,row[j+1:])
                        train_sentence_y.insert(i+1,row_y[j+1:])
                        doc_sentence_matrix.insert(i,doc_sentence_matrix[i])
                        break
        Perprocess.evaluate(self,train_sentence_x)
        return train_sentence_x,train_sentence_y
    def save_file(self,train_x,name_x):
        f=open('../resource/'+name_x,'wb')
        pickle.dump(train_x,f)
        f.close()

if __name__ == '__main__':
    myper=Perprocess(sentence_length=150)
    train_doc_x=myper.load_pkl('train_doc_x.pkl')
    train_doc_y=myper.load_pkl('train_doc_y.pkl')
    train_sentence_x,train_sentence_y=myper.sentence_level(train_doc_x,train_doc_y)#按句号第一次划分句子 拆分长句
    print('a')
