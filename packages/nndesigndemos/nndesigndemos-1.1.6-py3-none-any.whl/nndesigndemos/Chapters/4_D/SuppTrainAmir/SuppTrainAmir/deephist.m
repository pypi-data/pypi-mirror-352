function deephist()
%

% Input dimension
r = 4;

% Number of examples
q = 500;

% mean and variance of the input (set to zero and one for most cases)
pmean = zeros(r,1);
pstd = ones(r,1);

% Generate the inputs
p = diag(pstd)*randn(r,q)+pmean*ones(1,q);

% set the weight initialization algorithm
initial = 'xav'; % Xavier initialization
%initial = 'kai'; % Kaiming initialization
%initial = 'smr'; % small random initialization

% Layer sizes
s = {4,4,4,4};
rr = {r s{1:(end-1)}}; 
M = length(s);

% Activation functions
net.tf = {@tansig1,@tansig1,@tansig1,@tansig1};
%net.tf = {@poslin1,@poslin1,@poslin1,@poslin1};

% Initial weights

for m = 1:M,
    switch initial
        case 'xav'
            stdw = sqrt(2/(s{m}+rr{m}));
            w = stdw*randn(s{m},rr{m});
            b = zeros(s{m},1);
        case 'kai'
            stdw = sqrt(2/rr{m});
            w = stdw*randn(s{m},rr{m});
            b = zeros(s{m},1);
        case 'smr'
            stdw = 0.1;
            w = stdw*randn(s{m},rr{m});
            b = zeros(s{m},1);        
        otherwise
            disp([initial 'is not a valid weight initialization type.'])
            return
    end
    net.w{m} = w;
    net.b{m} = b;
end

% Run the network

a = simdeep(net,p);

% Plot the histograms

plothist(a)

end

function a = simdeep(net,p)

    M = length(net.tf);
    [~,q] = size(p);
    a = cell(1,M+1);
    a{1} = p;

    for m=1:M
        a{m+1} = net.tf{m}(net.w{m}*a{m}+net.b{m}*ones(1,q));
    end

end

function plothist(a)
%
% a    - set of inputs and layer outputs
%

% find number of columns of subplots
M1 = length(a);

figure('NumberTitle', 'off', 'Name', ['Histograms of Inputs & Layer Outputs']);

for k=1:M1
    subplot(1,M1,k), histogram(a{k}(:),20,'BinLimit',[-3 3]);
    title(['a_' num2str(k-1)])
%     ax = axis;
%     ax(1) = -3; ax(2) = 3;
%     axis(ax);
end

end

function a = tansig1(n)

a = tanh(n);

end

function a = poslin1(n)
a = max(0,n);
end


