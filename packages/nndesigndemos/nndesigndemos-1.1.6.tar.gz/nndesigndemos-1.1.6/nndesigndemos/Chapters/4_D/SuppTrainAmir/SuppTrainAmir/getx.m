function x=getx(net)
%GETX Get all network weight and bias values as a single vector.
%
%	Syntax
%
%	  X = getx(net)
%
%	Description
%
%	  This function gets a networks weight and biases as
%	  a vector of values.
%
%	  X = GETX(NET)
%	    NET - Neural network.
%	    X   - Vector of weight and bias values.
%


x = zeros(net.dimX,1);
M = length(net.f);
x = [];
for i=1:M
    x = [x; net.w{i}(:)];
    x = [x; net.b{i}];
end
