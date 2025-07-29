from numpy import array, ndarray, pad, conj, fft, max as np_max, min as np_min, abs as np_abs, argmax as np_argmax
import warnings


def check_inputs_define_limits(s1,s2,method,padded):

    # Check if s1 and s2 are not None and are list or numpy array
    if s1 is None or s2 is None:
        raise ValueError("Input signals s1 and s2 must not be None.")
    if not (isinstance(s1, (list, ndarray)) and isinstance(s2, (list, ndarray))):
        raise ValueError("Input signals s1 and s2 must be lists or numpy arrays.")

    # Ensure s1 and s2 are numpy arrays
    if not isinstance(s1, ndarray):
        s1 = array(s1)
    if not isinstance(s2, ndarray):
        s2 = array(s2)

    # Check if s1 and s2 are 1D arrays
    if s1.ndim != 1 or s2.ndim != 1:
        raise ValueError("Both s1 and s2 must be 1D arrays.")

    # Check if method is valid
    valid_methods = ["fft", "analytic"]
    if method not in valid_methods:
        raise ValueError(f"Invalid method '{method}'. Supported methods are {valid_methods}.")
    #check if s1 and s2 have the same length
    if s1.shape[0] != s2.shape[0]:
        #if shape1>shape2:
        big, small = "s2", "s1"

        if s1.shape[0] > s2.shape[0]:
            big, small = "s1", "s2"

        if padded:
            #if s2 bigger: pad s2, otherwise pad s1
            if s1.shape[0] > s2.shape[0]:
                #pad s1 to s2 length
                s1 = pad(s1, (0, s2.shape[0] - s1.shape[0]), mode='constant')
            else:
                #pad s2 to s1 length
                s2 = pad(s2, (0, s1.shape[0] - s2.shape[0]), mode='constant')
            
            #raise info: big is padded to small length
            warnings.warn(f"{big} is padded to {small} length")
        else:        
            #raise warnings.warn("s2 is truncated to s1 length")
            warnings.warn(f"{big} is truncated to {small} length")
            s2 = s2[:s1.shape[0]]

    return s1,s2


def cyclic_corr(s1,s2, method="fft", padded=True, normalized=True):
    """Compute the normalized maximum of the cyclic cross-correlation."""

    s1,s2= check_inputs_define_limits(s1,s2,method,padded)

    range_limit = max(s1.shape[0], s2.shape[0]) if padded else min(s1.shape[0], s2.shape[0])

    if method == "analytic":
        Z=[]
        for t in range(0,range_limit):
            Zk=0
            for k in range(0, range_limit):
                Zk+=s1[k]*conj(s2[(k+t)%(s2.shape[0])])
                
            Zl=0
            for l in range(0,range_limit):


                Zl+=conj(s1[k])*s2[(k+t)%(s2.shape[0])]
            
            Z.append(Zk*Zl)

        if(normalized): 
            Z=Z//(range_limit**2)
    else:

        X = fft.fft(s1)
        Y = fft.fft(s2)
        Z = fft.ifft(X * conj(Y))
        if(normalized):
            Z = Z / (range_limit)

    max_val = np_max(np_abs(Z))
    min_val=np_min(np_abs(Z))
    #max_val = np.abs(cyclic_cross_corr[30])
    t_max = np_argmax(np_abs(Z))


    return Z,max_val, t_max, min_val

