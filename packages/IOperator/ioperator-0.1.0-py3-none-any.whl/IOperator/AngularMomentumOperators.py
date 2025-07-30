import numpy as np

def SingleSpinI(S, Axis):
    if S == 1/2:
        if Axis == 'x':
            s = 1/2 * np.array([[0, 1], [1, 0]])
        elif Axis == 'y':
            s = 1/(2*1j) * np.array([[0, 1], [-1, 0]])
        elif Axis == 'z':
            s = 1/2 * np.array([[1, 0], [0, -1]])
        elif Axis == '+':
            s = np.array([[0, 1], [0, 0]])
        elif Axis == '-':
            s = np.array([[0, 0], [1, 0]])
        else:
            s = np.eye(2)
            print('WARNING: ', Axis, ' is not a defined operator type.')
    else:
        Dim=np.int32(2*S+1)
        a = np.transpose(np.tile(np.arange(1, Dim+1), (Dim, 1)))
        b = np.tile(np.arange(1, Dim+1), (Dim, 1))
        delta_abp1 = a - b
        delta_abp1[delta_abp1 != 1] = 0
        delta_abm1 = b - a
        delta_abm1[delta_abm1 != 1] = 0
        if Axis == 'x':
            s = (delta_abp1 + delta_abm1) / 2 * np.sqrt((S+1) * (a + b - 1) - a * b)
        elif Axis == 'y':
            s = 1j * (delta_abp1 - delta_abm1) / 2 * np.sqrt((S+1) * (a + b - 1) - a * b)
        elif Axis == 'z':
            s = np.eye(Dim) * (S+1 - b)
        elif Axis == '+':
            s = delta_abm1 * np.sqrt((S+1) * (a + b - 1) - a * b)
        elif Axis == '-':
            s = delta_abp1 * np.sqrt((S+1) * (a + b - 1) - a * b)
        else:
            s = np.eye(Dim)
            print('WARNING: ', Axis, ' is not a defined operator type.')
    return s

def I(S, *args):
    # Total number of spins
    N = len(S)
    # Reorganization of the input variables
    if len(args) == 1:
        # Example case: I(S,'x')
        Operation = 'sum'
        mu = args[0]
        k = list(range(0, len(S)))
    else:
        if args[1] == 'dot':
            # Example case: I(S,[1 2],'dot',3)
            Operation = 'dot'
            k1 = args[0]
            if type(k1) == int:
                k1 = [k1]
            if len(args) == 2:
                k = np.zeros((N, N))
                for i in range(len(k1)):
                    for j in range(i+1, len(k1)):
                        k[k1[i]][k1[j]] = 1
            elif len(args) == 3:
                k2 = args[2]
                if type(k2) == int:
                    k2 = [k2]
                k = [[0]*N for _ in range(N)]
                for i in range(len(k1)):
                    for j in range(len(k2)):
                        k[k1[i]][k2[j]] = 1
                        k[k2[j]][k1[i]] = 1
            else:
                k = [[0]*N for _ in range(N)]
                print('WARNING: DOT does not support this number of arguments.')
        else:
            if len(args) == 2:
                # Example case: I(S,[1 2],'x')
                Operation = 'sum'
                k = args[0]
                mu = args[1]
            else:
                # Example case: I(S,[1 2],'x',[3 4],'z')
                Operation = 'prod'
                K = len(args) // 2
                NumberOfOperators = 1
                for i in range(K):
                    if type(args[2*i]) != int:
                        NumberOfOperators = NumberOfOperators * len(args[2*i])
                k = np.zeros((K, NumberOfOperators))
                mu = ()
                for i in range(K):
                    k_=1
                    for j in range(K):
                      if j == i:
                        k_ = np.kron(k_, args[2*j])
                      else:
                        if type(args[2*j]) == int:
                          l = 1
                        else:
                          l = len(args[2*j])
                        k_ = np.kron(k_, np.ones(l))
                    k[i] = k_
                    mu = mu + (args[2*i+1],)

    if type(k) == int:
        k = [k]

    # Creation of the operator
    if Operation == 'sum':
        # List of the spins for which the operator is computed
        K = [0] * N
        for i in range(N):
            for j in range(len(k)):
                if k[j] == i:
                    K[i] = 1
        Dim=int(np.squeeze(np.prod(2*np.array(S)+1)))
        Iout = np.zeros((Dim, Dim))
        # Iteration over all spins
        for k in range(N):
            # Case where the operator contains spin k
            if K[k] == 1:
                # Initialization of the operator
                I_ = 1
                # Loop to contruct the operator for spin k
                for i in range(N):
                    # Case of spin k
                    if k == i:
                        I_ = np.kron(I_, SingleSpinI(S[k], mu))
                    # Case of non-spin / identity matrix
                    else:
                        I_ = np.kron(I_, np.eye(int(np.squeeze(2*S[i]+1))))
                Iout = Iout + I_
    elif Operation == 'prod':
        Dim=int(np.squeeze(np.prod(2*np.array(S)+1)))
        Iout = np.zeros((Dim, Dim))
        # Iteration over all operators
        for i in range(NumberOfOperators):
          # Initialization of the operator as the identity
          Ii = np.eye(Dim)
          # Iteration over all spins for a particular operator
          for j in range(K):
            Ii = Ii@I(S,int(k[j][i]),mu[j])
          Iout = Iout + Ii
    elif Operation == 'dot':
        Dim=int(np.squeeze(np.prod(2*np.array(S)+1)))
        Iout = np.zeros((Dim, Dim))
        for i in range(N):
            for j in range(i, N):
                    if k[i][j] == 1:
                        Iout = Iout + I(S, i, 'x', j, 'x') + I(S, i, 'y', j, 'y') + I(S, i, 'z', j, 'z')
    return Iout