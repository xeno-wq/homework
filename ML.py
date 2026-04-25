from random import randint,choice
class Player:
    def __init__(self,id,name,money,hp,mood):
        self.id=id
        self.name=name
        self.money=money
        self.hp=max(hp,0)
        self.mood=mood
    def __str__(self):
        return f"Player(id:{self.id},name:{self.name},money:{self.money},hp:{self.hp},mood:{self.mood})"
p=Player(1,'Nurzhan',100,100,100)
move=0
for _ in range(10):
    move+=1
    if p.hp<=0:
        break
    p.hp=min(100,p.hp)
    p.mood=min(100,p.mood)
    e=choice(['work','ill','earn', 'rest'])
    print(f"ход:{move},событие:{e}")
    if e=="work":
        print("Go to work or not to go?")
        decision=input("Go/Not")
        if decision=="Go":
            p.money+=randint(5,20)
            p.mood-=randint(5,20)
            p.hp-=randint(5,20)
    elif e=="ill":
        p.hp-=randint(5,20)
        print("You got sick")
        print("Will you get treatment?")
        decision=input("Yes/No")
        if decision=="Yes":
            p.hp+=randint(5,20)
            p.money-=randint(5,20)
        else:
            p.hp-=randint(5,20)
    elif e=="earn":
        print("Есть шанс быстро заработать / найти деньги")
        decision=input("Рискнуть,Пропустить 1/0")
        if decision=="1":
            accident=choice([1,0])    #1:+,0:-
            if accident==1:
                money=randint(5,20)
                p.money+=money
                print(f"earned:{money}")
            else:
                p.money -= randint(5, 20)
        else:
            print("ничего не происходит")
    elif e=="rest":
        print("Rest or not")
        decision=input("yes/no")
        if decision=='yes':
            p.hp+=randint(5,20)
            p.mood+=randint(5,20)
        else:
            p.mood -= randint(5, 20)

    if p.mood<0:
        p.mood=0
    if p.money>=500:
        print("WIN")
        break
    if  p.hp<=0:
        print("GAME OVER")
        break
    print(p)






