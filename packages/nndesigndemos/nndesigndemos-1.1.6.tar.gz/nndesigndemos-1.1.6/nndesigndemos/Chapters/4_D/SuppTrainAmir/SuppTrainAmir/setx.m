function net=setx(net,x)
%SETX Set all network weight and bias values with a single vector.
%
%	Syntax
%
%	  net = setx(net,X)
%
%	Description
%
%	  This function sets a networks weight and biases to
%	  a vector of values.
%
%	  NET = SETX(NET,X)
%	    NET - Neural network.
%	    X   - Vector of weight and bias values.
%
%	Examples
%
%	  Here we create a network with a 2-element input, and one
%	  layer of 3 neurons.
%
%	    net = newff([0 1; -1 1],[3]);
%
%	  The network has six weights (3 neurons * 2 input elements)
%	  and three biases (3 neurons) for a total of 9 weight and bias
%	  values.  We can set them to random values as follows:
%
%	    net = setx(net,rand(9,1));
%
%	  We can then view the weight and bias values as follows:
%
%	    net.iw{1,1}
%	    net.b{1}
%
%	See also GETX, FORMX.


M = length(net.f);
ind1 = 1;
for i=1:M
    dim = numel(net.w{i});
    ind2 = ind1+dim-1;
    range = ind1:ind2;
    net.w{i}(:) = x(range);
    dim = length(net.b{i});
    ind3 = ind2+dim;
    range = (ind2+1):ind3;
    net.b{i}(:) = x(range);
    ind1 = ind3+1;
end
