import numpy as np


class averaging_network:
    def __init__(self, iw, p_tdl=[]):
        self.iw = np.array(iw)
        
        if len(p_tdl) > 0:
            self.p_tdl = np.array(p_tdl)
        else:
            if len(self.iw) > 0:
                self.p_tdl = np.zeros(len(self.iw) - 1)
            else:
                self.p_tdl = np.zeros(0)
    
    def step(self, p):
        a = self.iw[0] * p
        
        for i in range(len(self.p_tdl)):
            a += self.iw[i + 1] * self.p_tdl[i]
        
        if len(self.p_tdl) > 0:
            self.p_tdl = np.roll(self.p_tdl, 1)
            self.p_tdl[0] = p
        
        return a
    
    def process(self, input_sequence):
        output = np.zeros(len(input_sequence))
        tdl_history = []

        for i in range(len(input_sequence)):
            tdl_history.append(self.p_tdl.copy())
            output[i] = self.step(input_sequence[i])

        return output, tdl_history
    

if __name__ == "__main__":
    # Example usage
    # Input weights
    iw = [0, 0.5, 0.5]

    # Input sequence
    p = [0, 1, 2, 3, 2, 1, 0, 0, 0]

    # Define the network
    net = averaging_network(iw)

    # Run the input through the network
    a, tdl_history = net.process(p)

    print('Input sequence:')
    print(p)
    print('Output sequence:')
    print(a)
    print('TDL history:')
    print(tdl_history)
