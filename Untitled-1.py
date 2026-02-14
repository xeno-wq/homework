def analyze(data):
    res={}
    m=0
    b=0
    for x,y in data.items():
        mean=0
        c=0
        for i in y:
            mean+=i
            m+=i
            b+=1
            c+=1
        res[x]=mean/c
        
    max_q=0
    best={}
    min_q=res['Ali']
    worst={}
    for x,y in res.items():
        if y>max_q:
            max_q=y
        if y<min_q:
            min_q=y
    
    
    
    for x in res.items():
        if x[1]==max_q:
            best[x[0]]=x[1]    
        if x[1]==min_q:
            worst[x[0]]=x[1] 
      
    return res,best,worst,m/b

data={
 "Ali": [80, 90, 75],
 "Dana": [100, 95, 92],
 "Oleg": [60, 70, 65]
}
mean,best,worst,mean=analyze(data)
print(mean)
print(best)
print(worst)
print(mean)
