p1 = 0:.01:1;
t1 = p1;
w1 = [1;1];
b1 = [0; -0.5];
w2 = [2 -4];
b2 = 0;
w1p = w1*w2;
b1p = w1*b2 + b1;

a1 = poslin(w1*p1+b1*ones(1,length(p1)));
a = w2*poslin(w1p*a1+b1p*ones(1,length(p1)))+b2;

a2 = w2*a1 + b2;

figure;plot(p1,a2)

net6 = feedforwardnet(2);
net6.input.processFcns={};
net6.output.processFcns={};
net6=configure(net6,p1,t1);
net6.IW{1}=w1;
net6.LW{2,1}=w2;
net6.b{1}=b1;
net6.b{2}=b2;
net6.layers{1}.transferFcn = 'poslin';
y1=net6(p1);
y2=net6(y1);
y3=net6(y2);
figure;plot(p1,y1,p1,y2,p1,y3)
figure;plot(p1,a)

net8 = feedforwardnet([2 2]);
net8.input.processFcns={};
net8.output.processFcns={};
net8 = configure(net8,p1,t1);
net8.IW{1}=w1;
net8.LW{2,1}=w1p;
net8.LW{3,2}=w2;
net8.b{1}=b1;
net8.b{2}=b1p;
net8.b{3}=b2;
net8.layers{1}.transferFcn = 'poslin';
net8.layers{2}.transferFcn = 'poslin';
y5 = net8(p1);
y5t = net6(y1);
figure;plot(p1,y1,p1,y5,p1,y5t)



net7 = feedforwardnet([2 2 2]);
net7.input.processFcns={};
net7.output.processFcns={};
net7 = configure(net7,p1,t1);
net7.IW{1}=w1;
net7.LW{2,1}=w1p;
net7.LW{3,2}=w1p;
net7.LW{4,3}=w2;
net7.b{1}=b1;
net7.b{2}=b1p;
net7.b{3}=b1p;
net7.b{4}=b2;
net7.layers{1}.transferFcn = 'poslin';
net7.layers{2}.transferFcn = 'poslin';
net7.layers{3}.transferFcn = 'poslin';
y4 = net7(p1);
figure;plot(p1,y1,p1,y4)

net10 = feedforwardnet([2 2 2 2]);
net10.input.processFcns={};
net10.output.processFcns={};
net10 = configure(net10,p1,t1);
net10.IW{1}=w1;
net10.LW{2,1}=w1p;
net10.LW{3,2}=w1p;
net10.LW{4,3}=w1p;
net10.LW{5,4}=w2;
net10.b{1}=b1;
net10.b{2}=b1p;
net10.b{3}=b1p;
net10.b{4}=b1p;
net10.b{5}=b2;
net10.layers{1}.transferFcn = 'poslin';
net10.layers{2}.transferFcn = 'poslin';
net10.layers{3}.transferFcn = 'poslin';
net10.layers{4}.transferFcn = 'poslin';
y4 = net10(p1);
figure;plot(p1,y1,p1,y4)

