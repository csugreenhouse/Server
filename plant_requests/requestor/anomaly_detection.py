# purpose of this is to remove images whose amount of pixels that are detected as "plant" are outside of the
# "normal" as found by a fit Gaussian model.
import numpy as np
from scipy.stats import norm

def anomaly_detection(data, mult_param):
    # data is input array of ratios of pixels defined as "plant" to overall number of pixels
    # mult_param is the percentage of probability distribution kept (ex. 0.4 will keep images where
    # probability of occurrence is >= 40% of the maximum probability in the dataset)
    gauss_model = norm.pdf(data, np.mean(data), np.std(data))

    # identify cutoff probability parameter as x percentage of maximum probability
    prob_param = mult_param * np.max(gauss_model)

    # find the nearest probability to this parameter in the data -- won't be in the actual dataset,
    # but we'll get close
    prob_estimate = [abs(prob_param - gauss_model[i]) for i in range(len(gauss_model))]

    # find the data point at which we are cutting off at -- this point is a probability of occurrence
    # using the probability that is closest to our original parameter
    prob_cutoff = gauss_model[prob_estimate.index(np.min(prob_estimate))]

    # get boolean mask
    filter_mask = gauss_model >= prob_cutoff

    return filter_mask