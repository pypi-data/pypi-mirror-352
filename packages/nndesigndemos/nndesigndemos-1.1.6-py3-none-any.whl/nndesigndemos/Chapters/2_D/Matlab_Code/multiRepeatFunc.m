function multiRepeatFunc(nr)
%
% This function plots the iterated triangle function.
%
% The input nr is the number of iterations. (The number of layers of the
% network would be nr+1.)

% Set up input range
p1 = 0:.01:1;

% Initial setting for plotting the cascaded function
if nargin==0,
    nr = 2;
end

% Compute second layer output for single triangle function
a2 = net1(p1);

% Plot the single triangle function and the line p=p
figure; plot(p1,p1,'g')
hold on
plot(p1,a2,'b','LineWidth',2)

% Get the connections showing the initial cascade
[xx,yy] = getxx(0.01,nr);

% Plot the initial cascade
h1 = plot(xx,yy,'ko-');
h2 = plot(xx(end),yy(end),'ro','MarkerSize',10);
hold off

% Iterate through the domain from 0 to 1, and show how the cascaded
% function is created
ht = [];
for pi=0.01:0.01:0.99,
    hx = draw(h1,h2,pi,nr);
    ht = [ht hx];
end
set(h1,'visible','off')

% In this section the user can enter different inputs and different numbers
% of cascades. The program will show the new cascades.
% If the user changes the number of iterations, the previously drawn
% function is erased and the new one is drawn.
flag = true;
while flag
   nr1 = input('Enter # of iterations (Return to quit) : ');
   if isempty(nr1)
       flag = false;
   else
      if nr1~=nr,
          for i=1:length(ht);
              delete(ht(i));
          end
          ht = [];
          nr = nr1;
          for pi=0.01:0.01:0.99,
             hx = draw(h1,h2,pi,nr);
             ht = [ht hx];
          end
          set(h1,'visible','off')
      end
      
      flag1 = true;
      while flag1
          pi = input('Enter input (Return to select new # of iter.): ');
          if exist('hh')
              delete(hh)
              clear hh
          end
          if isempty(pi)
              flag1 = false;
          else
              if pi<0.01,
                  pi = 0.01;
              elseif pi>0.99,
                  pi = 0.99;
              end
              hh = draw(h1,h2,pi,nr);
          end

      end
   end
end
end

function [xx,yy] = getxx(p,nr)
%
% This function creates the cascade going from an input value to the output
% of the first two layers, and then on to the cascaded function output,
% which is the output of the third layer.
xx=[];
yy=[];
x = p;

for i=1:nr,
    y = net1(x);
    xx = [xx x x x y];
    yy = [yy x y y y];
    x = y;
end

yy(1) = 0;
xx(end) = p;
end


function y = net1(x)
%
% This function calculates the two layer network output, which creates a
% single triangle function
w1 = [1;1];
b1 = [0; -0.5];
w2 = [2 -4];
b2 = 0;

a1 = poslin1(w1*x+b1*ones(1,length(x)));
y = w2*a1 + b2*ones(1,length(x));

end

function a = poslin1(n)
a = max(0,n);
end

function [h3] = draw(h1,h2,pi,nr)
pauset = 0.025;
[xx,yy] = getxx(pi,nr);
set(h1,'visible','on')
set(h1,'XData',xx)
set(h1,'YData',yy)
drawnow
pause(pauset)
set(h2,'XData',xx(end))
set(h2,'YData',yy(end))
%set(h1,'visible','off')
drawnow
pause(pauset)
hold on
h3 = plot(xx(end),yy(end),'ro');
hold off
end

