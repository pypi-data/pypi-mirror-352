function test_train_marq3D()

% Plot the 3d composite function
p21 = -2:0.1:2;
[X,Y] = meshgrid(p21);
p = [X(:) Y(:)]';
temp = sqrt(sum(p.^2));
t2 = cos(pi*temp/2);
true = cos(pi*sqrt(X.^2 + Y.^2)/2);
figure; mesh(p21,p21,true)
ax = axis;
title('cos(pi*||p||/2)')
t = true(:)';

% Make validation and testing the same as training for this demo
VV.P=p;
VV.T=t;
VV.stop=false;        % We don't stop for validation
TT.P=p;
TT.T=t;

trainParam = train_marq_three_lay('pdefaults');
trainParam.show = 1000;
trainParam.max_epoch = 5000;

% Change the next three lines to try different network architectures
trainParam.S1 = 3;
trainParam.S2 = 2;
trainParam.num_lay = 3;


% Train the network
[net,tr] = train_marq_three_lay(trainParam,p,t,VV,TT); 

% Plot performance and gradient
figure; loglog(tr.perf); title('Perf')
figure; loglog(tr.grad); title('Grad')

% Compute trained network response
net.trainParam = trainParam;
a3 = net3lay(p, net);

% Put response in grid and make 3d plot
numa = length(p21);
ta3 = a3(1,1:numa);
for i=1:(numa-1),
	ta3 = [ta3 ; a3(1,(1:numa)+(numa*i))];
end
figure;mesh(p21,p21,ta3);
axis(ax)
title('Network Approximation of cos(pi*||p||/2)')

% Plot the error
figure;mesh(p21,p21,ta3-true);
title('Approximation Error')

% Print the number of parameters
[r,q] = size(p);
[s,q] = size(t);
if trainParam.num_lay == 2,
    numParam = trainParam.S1*(r+1) + s*(trainParam.S1+1);
else
    numParam = trainParam.S1*(r+1) + trainParam.S2*(trainParam.S1+1) + s*(trainParam.S2+1);
end
    
disp(['Number of parameters = ' num2str(numParam)])

end


function [a] = net3lay(p,net)
  % Two or three layer network response
  a1 = net.trainParam.tf1(net.W1*p+net.B1*ones(1,size(p,2)));
  if net.trainParam.num_lay==3,
      a2 = net.trainParam.tf2(net.W2*a1+net.B2*ones(1,size(p,2)));
      a = net.W3*a2 + net.B3*ones(1,size(p,2));
  else
      a = net.W2*a1 + net.B2*ones(1,size(p,2));
  end
end

