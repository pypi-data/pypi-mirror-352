function [net] = newmultilay(params)
%NEWMULTILAY Create a multilayer network
%
%	Syntax
%	
%	  [net] = newmultilay(params)
%	  info = newmultilay(code)
%
%	Description
%
%	  NEWMULTILAY creates a feedforward multilayer network
%
%	NEWMULTILAY(params) takes these inputs,
%     a parameter structure:
%	    params.f    - A cell array containing layer activation functions
%       params.perf - Performance function (e.g., @ce
%	    params.S    - A cell array containing layer sizes
%       param.R     - Number of elements in input vector
%	    params.Init - A code for the weight initialization:
%                        'xav'  - Xavier initialization
%                        'kai'  - Kaiming initialization
%                        'smr'  - small random number initialization
%	  and returns,
%	    NET - Network structure with initialized weights
%
%
%	  TRAINSCG(CODE) returns useful information for each CODE string:
%	    'pdefaults' - Default training parameters.
%
%
%	Example
%
%   Here a two layer network is created, with two inputs and two neurons in
%   each layer. Xavier initialization is used for the weights.
%
%      params.f = {@tansig, @softmax};
%      params.R = 2;
%      params.S = {2, 2};
%      params.Init = 'xav';
%
%	    % Create the Network
%	    net = newmultilay(params);
%	    a = sim(net,p)
%

if ischar(params)
  switch (params)
    case 'pdefaults'
      trainParam.f = {@tansig0, @softmax0};
      trainParam.R = 2;
      trainParam.S = {2, 2};
      trainParam.Init = 'xav';
      trainParam.perf = @crossentr;
      trainParam.do = {1, 0};
      trainParam.doflag = 0;
	  net = trainParam;
    otherwise
	  error('Unrecognized code.')
  end
  return
end

r = params.R;
f = params.f;
s = params.S;
initial = params.Init;

% Layer sizes
rr = {r s{1:(end-1)}}; 
M = length(s);

% Input size
net.R = params.R;

% Layer sizes
net.S = s;

% Assign activation functions
net.f = f;

% Assign performance function
net.perf = params.perf;

dimX = 0;
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
    net.mask{m} = ones(s{m},1);
    net.b{m} = b;
    [s1,s2] = size(w);
    dimX = dimX + s1*(s2+1);
end

net.dimX = dimX;

net.do = params.do;

net.doflag = params.doflag;


