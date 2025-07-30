function repeatFunc()

% Set up input range and weights
p1 = 0:.01:1;
w1 = [1;1];
b1 = [0; -0.5];
w2 = [2 -4];
b2 = 0;
w1p = w1*w2;
b1p = w1*b2 + b1;

% Compute first layer output
a1 = poslin1(w1*p1+b1*ones(1,length(p1)));

% Compute second layer output for single triangle function
a2 = w2*a1 + b2;

% Compute third layer output for double triangle function
a = w2*poslin1(w1p*a1+b1p*ones(1,length(p1)))+b2;

% Plot the single and double triangle functions

figure; plot(p1,p1,'g')
hold on
plot(p1,a2,'b','LineWidth',2)
plot(p1,a,'r','LineWidth',2)

% Initial setting for plotting the cascaded function
p = 0.9;

% Get the connections showing the cascade
[xx,yy] = getxx(p);

% Plot the cascade
h1 = plot(xx,yy,'ko-');

hold off

% Iterate through the domain from 0 to 1, and show how the cascaded
% function is created
% This could be replaced with a slider, so the user could adjust the domain
% value
for pi=0.01:0.01:0.99,
    [xx,yy] = getxx(pi);
    set(h1,'XData',xx)
    set(h1,'YData',yy)
    drawnow
    pause(0.1)
end

% In this section the user can enter different inputs and the program will
% show the new cascades.
flag = true;
while flag
   pi = input('Enter the input (just Return to quit): ');
   if isempty(pi)
       flag = false;
   else
       if pi<0.01,
           pi = 0.01;
       elseif pi>0.99,
           pi = 0.99;
       end
       [xx,yy] = getxx(pi);
       set(h1,'XData',xx)
       set(h1,'YData',yy)
       drawnow
   end

end
end

function [xx,yy] = getxx(p)
%
% This function creates the cascade going from an input value to the output
% of the first two layers, and then on to the cascaded function output,
% which is the output of the third layer.
y = net1(p);
ys = net1(y);
x1 = [p p];
y1 = [0 y];
x2 = [p y];
y2 = [y y];
x3 = [y y];
y3 = [y ys];
x4 = [y p];
y4 = [ys ys];

xx = [x1 x2 x3 x4];
yy = [y1 y2 y3 y4];

end

function y = net1(x)
%
% This function calculates the two layer network output, which creates a
% single triangle function
w1 = [1;1];
b1 = [0; -0.5];
w2 = [2 -4];
b2 = 0;

a1 = poslin1(w1*x+b1);
y = w2*a1 + b2;

end

function a = poslin1(n)
a = max(0,n);
end

