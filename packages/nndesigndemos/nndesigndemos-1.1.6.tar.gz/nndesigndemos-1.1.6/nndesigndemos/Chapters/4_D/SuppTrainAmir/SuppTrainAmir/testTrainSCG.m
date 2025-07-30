function [P,T,net1,tr] = testTrainSCG()
% Get the default network parameters and adjust what you want
params = newmultilay('pdefaults');
% number of neurons in each layer
params.S = {300,2};
% dropout (keep) ratio
params.do = {.95, 1};

% Create the network
net = newmultilay(params);

% Set stdv of noise to be added to training inputs. 0.3 seems good
stdv = 0.3;

 P = [0.2  0.2  0     0     -.35 -.35    -0.5 0    0.25 0   -0.25 0     0.25 -.15 -.15  0.1 0.1; ...
      -0.75 0.75 0.65  -0.65 -.45 0.45    0   -0.5  0.5  0.25 0    -0.25 -0.5 .2   -.2   0.3 -0.3];
 T = [ 0    0    0    0      0    0       0    0     1    1    1    1    1     1    1    1    1; ...
       1    1    1    1      1    1       1    1     0    0    0    0    0     0    0    0    0];

 P = [P P+stdv*(rand(size(P))-0.5) P+stdv*(rand(size(P))-0.5) ...
       P+stdv*(rand(size(P))-0.5) P+stdv*(rand(size(P))-0.5) ...
       P+stdv*(rand(size(P))-0.5) P+stdv*(rand(size(P))-0.5)];
 T = [T T T T T T T];        

     
% Get default training parameters and adjust what you want
params = trainscg0('pdefaults');
% params.show = 1;
params.epochs = 300;
net.trainParam = params;

% Train the network
[net1,tr] = trainscg0(net,P,T,[],[]);
% TV.Pd = P;
% TV.Tl = T;
% [net1,tr] = trainscg0(net,P,T,[],TV);

% Run the trained network
[a] = simnet(net1,P);


% mx = max(P,[],2);
% mn = min(P,[],2);

% range for plotting decision boundary and inputs
mx = [1 1];
mn = [-1 -1];

xlim = [mn(1) mx(1)]; dx = (mx(1)-mn(1))/100;
ylim = [mn(2) mx(2)]; dy = (mx(2)-mn(2))/100;
xpts = xlim(1):dx:xlim(2);
ypts = ylim(1):dy:ylim(2);
[X,Y] = meshgrid(xpts,ypts);

testInput = [X(:) Y(:)]';
net1.doflag = 0;
testOutputs = simnet(net1,testInput);
testOutputs = testOutputs{2}(1,:)-testOutputs{2}(2,:);
[m,n] = size(X);
F = reshape(testOutputs,m,n);

% plot decision boundary with class 1 inputs circled x, class 2 inputs just x
figure; contourf(xpts,ypts,F,[0.0, 0.0]);
hold on
ind = find(T(1,:));
plot(P(1,:),P(2,:),'x')
plot(P(1,ind),P(2,ind),'or')
plot([-1 1],[0 0],'k')
plot([0 0],[-1 1],'k')
axis('square')

%figure;mesh(xpts,ypts,F)
