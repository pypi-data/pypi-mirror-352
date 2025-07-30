function radialFunctionExample()
%
% Demo to show how to make a three layer network to implement the function
%
%  g(p) = cos(pi*||p||/2
%
% with three layers, with 4 and 2 neurons in the hidden layers. This is a
% radial function, which is difficult to approximate as closely with only
% one hidden layer, unless the number of neurons is much larger.
% The three layer network first approximates the square function p.^2 using
% a two layer network. This is then is duplicated to square both elements 
% of a vector p. The output of the duplicated network is then summed
% together to create ||p||^2. Next, another two layer network is created to
% approximate the function cos(pi*sqrt(p)/2). When these networks are
% cascaded together, they create the total function above. Some linear
% layers can be combined together, so the result is just three layers.

p = -2:.01:2;
t = p.^2;

% Weights for making the squared function p.^2
w1 = [ -0.2; -0.2];
b1 = [ 2; -2];
w2 = [-320  320];
b2 = 243.7;

% Weights for making cos(pi*sqrt(p)/2)
w1c = [-0.2489; -0.3541];
b1c = [1.2931; -2.6491];
w2c =  [-6.6898   69.3431];
b2c = 1.6693;

% Show the squared function
net2 = fitnet(2);
net2.layers{1}.transferFcn = 'logsig';
net2.input.processFcns = {};
net2.output.processFcns = {};
net2 = configure(net2,p,t);
net2.IW{1,1} = w1;
net2.b{1} = b1;
net2.LW{2,1} = w2;
net2.b{2} = b2;
y1 = net2(p);
ynew = net2(p);
figure;plot(p,t,p,ynew)
xlabel('The squared function and the network approximation.')
legend('True','Approximation')


% Show the cos(pi*sqrt(p)/2) function
p1 = 0:.01:8;
t1 = cos(pi*sqrt(p1)/2);

net3 = fitnet(2);
net3.layers{1}.transferFcn = 'logsig';
net3.input.processFcns = {};
net3.output.processFcns = {};
net3 = configure(net3,p1,t1);
net3.IW{1,1} = w1c;
net3.b{1} = b1c;
net3.LW{2,1} = w2c;
net3.b{2} = b2c;
ynew1 = net3(p1);
figure;plot(p1,t1,p1,ynew1)
xlabel('The cos(pi*sqrt(p)) function and the network approximation.')
legend('True','Approximation')


% Compute the weights for the composite function
w1p = [w1 zeros(size(w1)); zeros(size(w1)) w1];
b1p = [b1;b1];
w2p = [w2 zeros(size(w2)); zeros(size(w2)) w2];
b2p = [b2; b2];
w3p = [1 1];
b3p = 0;

% Plot the 3d composite function
p21 = -2:0.1:2;
[X,Y] = meshgrid(p21);
p2 = [X(:) Y(:)]';
temp = sqrt(sum(p2.^2));
t2 = cos(pi*temp/2);
true = cos(pi*sqrt(X.^2 + Y.^2)/2);
figure; mesh(p21,p21,true)
ax = axis;
title('cos(pi*||p||/2)')


% Implement the composite function in the NNT
% net4 = fitnet([4,2]);
% net4.layers{1}.transferFcn = 'logsig';
% net4.layers{2}.transferFcn = 'logsig';
% net4.input.processFcns = {};
% net4.output.processFcns = {};
% net4 = configure(net4,p2,t2);
% net4.IW{1,1} = w1p;
% net4.b{1} = b1p;
% net4.LW{2,1} = w1c*w3p*w2p;
% net4.b{2} = w1c*w3p*b2p + w1c*b3p + b1c;
% net4.LW{3,2} = w2c;
% net4.b{3} = b2c;
% a = net4(p2);
% figure
% numa = length(p21);
% ta = a(1,1:numa);
% for i=1:(numa-1),
% 	ta = [ta ; a(1,(1:numa)+(numa*i))];
% end
% mesh(p21,p21,ta);

% Implement the composite function without the NNT
w1 = w1p;
b1 = b1p;
w2 = w1c*w3p*w2p;
b2 = w1c*w3p*b2p + w1c*b3p + b1c;
w3 = w2c;
b3 =b2c;
a3 = net3lay(w1,b1,w2,b2,w3,b3,p2);

numa = length(p21);
ta3 = a3(1,1:numa);
for i=1:(numa-1),
	ta3 = [ta3 ; a3(1,(1:numa)+(numa*i))];
end
figure;mesh(p21,p21,ta3);
axis(ax)
title('Network Approximation of cos(pi*||p||/2)')

% Plot the error
%figure;mesh(p21,p21,ta3-true);



function [a3] = net3lay(w1,b1,w2,b2,w3,b3,p)
% Three layer network with logsig hidden layers
a1 = logsig(w1*p+b1*ones(1,size(p,2)));
a2 = logsig(w2*a1+b2*ones(1,size(p,2)));
a3 = w3*a2 + b3;

