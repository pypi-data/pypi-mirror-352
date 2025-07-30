function [perf,a] = calcperf0(net,p,t)


M = length(net.f);

a = simnet(net,p);

perf = net.perf(a{M},t,'f');

