hh = [-4 2;1 2];
t = [-1;1];
x = -1:0.025:1;
y = x;
xtick = [-1 0 1];
ytick = xtick;
x0 = [1;1];
cont=[0.2 0.5 1 2 4 8 16 32];
len = 0.04;
fact = 0.5;
lr = 0.05;
width = 3;
steepdescent(hh,t,x0,x,y,xtick,ytick,cont,len,fact,lr,width)