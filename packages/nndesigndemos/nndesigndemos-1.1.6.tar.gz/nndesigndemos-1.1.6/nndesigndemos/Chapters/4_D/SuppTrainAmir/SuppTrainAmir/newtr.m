function tr=newtr(epochs,varargin)
%NEWTR New training record with any number of optional fields.
%
%	Syntax
%
%	  tr = newtr(epochs,'fieldname1','fieldname2',...)
%	  tr = newtr([firstEpoch epochs],'fieldname1','fieldname2',...)
%
%	Warning!!
%
%	  This function may be altered or removed in future
%	  releases of the Neural Network Toolbox. We recommend
%	  you do not write code which calls this function.

% Mark Beale, 11-31-97
% Copyright (c) 1992-1998 The MathWorks, Inc.
% $Revision: 1.3 $

if nargin < 1,error('Not enough input arguments.'),end

names = varargin;
tr.epoch = 0:epochs;
blank = zeros(1,epochs+1)+NaN;
for i=1:length(names)
  eval(['tr.' names{i} '=blank;']);
end
