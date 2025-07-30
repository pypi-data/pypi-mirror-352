function netHistograms()

% set the number of examples
q = 1000;

% set the number of neurons
s = 4;

% set the distribution of the inputs
%distr = 'uniform';
distr = 'normal';

% set the weight initialization algorithm
%initial = 'xav'; % Xavier initialization
%initial = 'nw'; % Nguyen-Widrow initialization
%initial = 'kai'; % Kaiming initialization
initial = 'smr'; % small random initialization

% set the activation function
net.tf1 = @tansig1;
%net.tf1 = @poslin1;

% should batchnorm be executed
%bnorm = true;
bnorm = false;


% number of elements of the input vector
r = 2;

% mean and variance of the input
pmean = [0;0];
pstd = [4;1];

% Generate inputs
switch distr
    case 'uniform'
        p = diag(pstd)*(rand(r,q)-0.5)*sqrt(12)+pmean*ones(1,q);
    case 'normal'
        p = diag(pstd)*randn(r,q)+pmean*ones(1,q);
    otherwise
        disp('Not a valid distribution type.')
        return
end


% Histogram of inputs
figure
%subplot(2,1,1), histogram(p(1,:),25,'BinLimit',[-2 2])
subplot(2,1,1), histogram(p(1,:),25)
title('Histogram of Inputs')
xlabel('First Input')
%subplot(2,1,2), histogram(p(2,:),25,'BinLimit',[-2 2])
subplot(2,1,2), histogram(p(2,:),25)
xlabel('Second Input')

% Batchnorm
if bnorm
    pmean = mean(p')';
    pstd = std(p')';
    p = (p - pmean*ones(1,q))./(pstd*ones(1,q));
else
    p = p;
end

% Histogram of normalized inputs
figure
%subplot(2,1,1), histogram(p(1,:),25,'BinLimit',[-2 2])
subplot(2,1,1), histogram(p(1,:),25)
title('Histogram of Normalized Inputs')
xlabel('First Input')
%subplot(2,1,2), histogram(p(2,:),25,'BinLimit',[-2 2])
subplot(2,1,2), histogram(p(2,:),25)
xlabel('Second Input')

% Range of inputs
pr = [min(p')' max(p')'];

% Initialize weights
switch initial
    case 'nw'     
        n = [-1 1];
        [w,b] = calcnw(pr,s,n);
    case 'xav'
        stdw = sqrt(2/(s+r));
        w = stdw*randn(s,r);
        b = zeros(s,1);
    case 'kai'
        stdw = sqrt(2/r);
        w = stdw*randn(s,r);
        b = zeros(s,1);
    case 'smr'
        stdw = 0.1;
        w = stdw*randn(s,r);
        b = zeros(s,1);        
    otherwise
        disp('Not a valid weight initialization type.')
        return
end

net.w = w;
net.b = b;

% plot the network response
plotfcn3d(net,pr)

% compute network outputs
[a,n] = net1lay(net,p);

% plot histograms of layer outputs
plothist(a,'Layer Output')

% plot histograms of net inputs
plothist(n,'Net Input')

end

function plothist(a,name)
%
% a    - set of net inputs or layer outputs
% name - 'Layer Output' or 'Net Input'
%

% find number of rows and columns of subplots
[s,q] = size(a);
[num1,num2] = getClosestFactors(s);

figure('NumberTitle', 'off', 'Name', [name ' Histogram']);


switch name
    case 'Layer Output'
        titletext = 'a_';
    case 'Net Input'
        titletext = 'n_';
end

k = 1;
for i=1:num1
    for j=1:num2
        subplot(num1,num2,k), histogram(a(k,:),35,'BinLimit',[-2 2]);
        title([titletext num2str(k)])
        k = k+1;
        if k>s
            break
        end
    end
end

end

function plotfcn3d(net,pr)
%
% net - structure containing network weight, bias and activation function
% pr  - range of input to the network: pr = [Pmin Pmax]

% Create the input
p1 = linspace(pr(1,1),pr(1,2),20);
p2 = linspace(pr(2,1),pr(2,2),20);

[X,Y] = meshgrid(p1,p2);
[n1,n2] = size(X);
nump = n1*n2;

pp1 = reshape(X,1,nump);
pp2 = reshape(Y,1,nump);

ptot = [pp1;pp2];


% Find the network response
a = net1lay(net,ptot);
[s,~] = size(a);
[num1,num2] = getClosestFactors(s);

% Make the plots
figure('NumberTitle', 'off', 'Name', 'Network Response');
k = 1;
for i=1:num1
    for j=1:num2
        aa = reshape(a(k,:),n1,n2);
        subplot(num1,num2,k), mesh(p1,p2,aa);
%        zlabel(['a_' num2str(k)],'Rotation',0)
        title(['a_' num2str(k)])
        xlabel('p_1');ylabel('p_2')
        ax = axis;
        if isequal(net.tf1,@poslin1)
            axis([pr(1,1),pr(1,2) pr(2,1),pr(2,2) 0 2])
        else
            axis([pr(1,1),pr(1,2) pr(2,1),pr(2,2) -1 1])
        end
        k = k+1;
        if k>s
            break
        end
    end
end

end

function [num1,num2] = getClosestFactors(input)
%
% Find two numbers close together whose product is input
%

  num1 = ceil(sqrt(input));
  num2 = fix(input/num1);
  while num1*num2<input
      num2 = num2 + 1;
  end
%   while mod(input,num1) ~= 0
%     num1 = num1-1;
%   end
%   num2 = input / num1;
end

function [a,n] = net1lay(net,p)
%
% net  - structure with network weight, bias and activation function
% p    - input to network
% n    - net input
% a    - network ouput

[~,q] = size(p);
n = net.w*p + net.b*ones(1,q);
a = net.tf1(n);

end

function a = tansig1(n)

a = tanh(n);

end

function a = poslin1(n)
a = max(0,n);
end


%===========================================================
function [w,b]=calcnw(pr,s,n)
%CALCNW Calculates Nugyen-Widrow initial conditions.
%
%  PR - Range of input vectors PR = [Pmin Pmax].
%  S  - Number of neurons.
%  N  - Active region of transfer function N = [Nmin Nmax].

% # inputs
r = size(pr,1);

% Nguyen-Widrow Method
% Assume inputs and net inputs range in [-1 1].
% --------------------

wMag = 0.7*s^(1/r);
wDir = randnr(s,r);
w = wMag*wDir;

if (s==1)
  b = 0;
else
  b = wMag*linspace(-1,1,s)'.*sign(w(:,1));
end

% --------------------

% Conversion of net inputs of [-1 1] to [Nmin Nmax]
x = 0.5*(n(2)-n(1));
y = 0.5*(n(2)+n(1));
w = x*w;
b = x*b+y;

% Conversion of inputs of PR to [-1 1]
x = 2./(pr(:,2)-pr(:,1));
y = 1-pr(:,2).*x;
xp = x';
b = w*y+b;
w = w.*xp(ones(1,s),:);

end
%===========================================================